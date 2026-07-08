import json
from collections.abc import Iterable
from typing import Any

from sqlalchemy.orm import Session

from services.identity.models import (
    AssemblyConstituencyDB,
    DistrictDB,
    ParliamentaryConstituencyDB,
    StateDB,
    VillageDB,
    WardDB,
)

Point = tuple[float, float]


def _load_geojson(geojson_str: str) -> dict[str, Any]:
    try:
        return json.loads(geojson_str)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON format.") from exc


def _iter_geometries(data: dict[str, Any]) -> Iterable[dict[str, Any]]:
    data_type = data.get("type")
    if data_type == "FeatureCollection":
        features = data.get("features")
        if not isinstance(features, list) or not features:
            raise ValueError(
                "FeatureCollection must contain a non-empty list of features."
            )
        for feature in features:
            geometry = feature.get("geometry")
            if not geometry or not isinstance(geometry, dict):
                raise ValueError("Feature must contain a geometry dictionary.")
            yield geometry
        return

    if data_type == "Feature":
        geometry = data.get("geometry")
        if not geometry or not isinstance(geometry, dict):
            raise ValueError("Feature must contain a geometry dictionary.")
        yield geometry
        return

    yield data


def _is_number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _normalize_ring(ring: list[Any]) -> list[Point]:
    if len(ring) < 4:
        raise ValueError("Each polygon ring must contain at least 4 coordinates.")

    normalized_ring: list[Point] = []
    for point in ring:
        if not isinstance(point, list | tuple) or len(point) < 2:
            raise ValueError(
                "Each point in the polygon ring must be [longitude, latitude]."
            )

        longitude, latitude = point[0], point[1]
        if not _is_number(longitude) or not _is_number(latitude):
            raise ValueError("Polygon coordinates must be numeric.")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Longitude {longitude} out of bounds (-180, 180).")
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Latitude {latitude} out of bounds (-90, 90).")

        normalized_ring.append((float(longitude), float(latitude)))

    if normalized_ring[0] != normalized_ring[-1]:
        raise ValueError(
            "Polygon ring must be closed (first and last coordinate must be identical)."
        )

    return normalized_ring


def _orientation(point_a: Point, point_b: Point, point_c: Point) -> int:
    cross_product = (point_b[1] - point_a[1]) * (point_c[0] - point_b[0]) - (
        point_b[0] - point_a[0]
    ) * (point_c[1] - point_b[1])
    if abs(cross_product) < 1e-12:
        return 0
    return 1 if cross_product > 0 else 2


def _point_on_segment(point_a: Point, point_b: Point, point_c: Point) -> bool:
    return min(point_a[0], point_c[0]) <= point_b[0] <= max(
        point_a[0], point_c[0]
    ) and min(point_a[1], point_c[1]) <= point_b[1] <= max(point_a[1], point_c[1])


def _segments_intersect(
    first_start: Point,
    first_end: Point,
    second_start: Point,
    second_end: Point,
) -> bool:
    first_orientation = _orientation(first_start, first_end, second_start)
    second_orientation = _orientation(first_start, first_end, second_end)
    third_orientation = _orientation(second_start, second_end, first_start)
    fourth_orientation = _orientation(second_start, second_end, first_end)

    if (
        first_orientation != second_orientation
        and third_orientation != fourth_orientation
    ):
        return True

    if first_orientation == 0 and _point_on_segment(
        first_start, second_start, first_end
    ):
        return True
    if second_orientation == 0 and _point_on_segment(
        first_start, second_end, first_end
    ):
        return True
    if third_orientation == 0 and _point_on_segment(
        second_start, first_start, second_end
    ):
        return True
    return fourth_orientation == 0 and _point_on_segment(
        second_start,
        first_end,
        second_end,
    )


def _validate_ring_self_intersections(ring: list[Point]) -> None:
    segment_count = len(ring) - 1
    for first_index in range(segment_count):
        first_segment = (ring[first_index], ring[first_index + 1])
        for second_index in range(first_index + 1, segment_count):
            if abs(first_index - second_index) <= 1:
                continue
            if first_index == 0 and second_index == segment_count - 1:
                continue

            second_segment = (ring[second_index], ring[second_index + 1])
            if _segments_intersect(
                first_segment[0],
                first_segment[1],
                second_segment[0],
                second_segment[1],
            ):
                raise ValueError(
                    "Polygon ring contains self-intersections and is invalid."
                )


def _validate_polygon_coords(polygon_coords: list[Any]) -> None:
    if not polygon_coords or not isinstance(polygon_coords, list):
        raise ValueError("Polygon coordinates must be a non-empty list of rings.")

    for ring in polygon_coords:
        if not isinstance(ring, list):
            raise ValueError("Each polygon ring must be a list of coordinates.")
        normalized_ring = _normalize_ring(ring)
        _validate_ring_self_intersections(normalized_ring)


def validate_geojson_polygon(geojson_str: str) -> bool:
    """Validate GeoJSON polygons before accepting them as jurisdiction boundaries."""

    data = _load_geojson(geojson_str)
    for geometry in _iter_geometries(data):
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")
        if geometry_type not in {"Polygon", "MultiPolygon"}:
            raise ValueError(
                f"Geometry type '{geometry_type}' is not supported. Must be Polygon or MultiPolygon."
            )
        if not isinstance(coordinates, list):
            raise ValueError("Coordinates must be a list.")

        if geometry_type == "Polygon":
            _validate_polygon_coords(coordinates)
            continue

        for polygon in coordinates:
            _validate_polygon_coords(polygon)

    return True


def _point_in_ring(latitude: float, longitude: float, ring: list[Any]) -> bool:
    normalized_ring = _normalize_ring(ring)
    inside = False
    ring_size = len(normalized_ring) - 1

    for index in range(ring_size):
        start_longitude, start_latitude = normalized_ring[index]
        end_longitude, end_latitude = normalized_ring[index + 1]

        if _orientation(
            (start_longitude, start_latitude),
            (end_longitude, end_latitude),
            (longitude, latitude),
        ) == 0 and _point_on_segment(
            (start_longitude, start_latitude),
            (longitude, latitude),
            (end_longitude, end_latitude),
        ):
            return True

        crosses_edge = (start_latitude > latitude) != (end_latitude > latitude)
        if not crosses_edge:
            continue

        intersect_longitude = start_longitude + (
            (latitude - start_latitude)
            * (end_longitude - start_longitude)
            / (end_latitude - start_latitude)
        )
        if intersect_longitude == longitude:
            return True
        if intersect_longitude > longitude:
            inside = not inside

    return inside


def _point_in_polygon(
    latitude: float, longitude: float, polygon_coords: list[Any]
) -> bool:
    if not polygon_coords:
        return False

    if not _point_in_ring(latitude, longitude, polygon_coords[0]):
        return False

    for hole_ring in polygon_coords[1:]:
        if _point_in_ring(latitude, longitude, hole_ring):
            return False

    return True


def is_point_in_geojson(
    latitude: float, longitude: float, geojson_str: str | None
) -> bool:
    if not geojson_str:
        return False

    try:
        data = _load_geojson(geojson_str)
        geometries = list(_iter_geometries(data))
    except ValueError:
        return False

    for geometry in geometries:
        geometry_type = geometry.get("type")
        coordinates = geometry.get("coordinates")
        if geometry_type == "Polygon" and _point_in_polygon(
            latitude, longitude, coordinates
        ):
            return True
        if geometry_type == "MultiPolygon":
            for polygon in coordinates:
                if _point_in_polygon(latitude, longitude, polygon):
                    return True

    return False


def _find_first_boundary_match(
    records: Iterable[Any], latitude: float, longitude: float
) -> Any | None:
    for record in records:
        if is_point_in_geojson(latitude, longitude, record.geojson_boundary):
            return record
    return None


def resolve_jurisdiction_entities(
    db: Session, latitude: float, longitude: float
) -> dict[str, Any]:
    assembly_constituency = _find_first_boundary_match(
        db.query(AssemblyConstituencyDB)
        .filter(AssemblyConstituencyDB.is_active.is_(True))
        .all(),
        latitude,
        longitude,
    )
    parliamentary_constituency = _find_first_boundary_match(
        db.query(ParliamentaryConstituencyDB)
        .filter(ParliamentaryConstituencyDB.is_active.is_(True))
        .all(),
        latitude,
        longitude,
    )

    ward = None
    village = None
    if assembly_constituency:
        ward = _find_first_boundary_match(
            db.query(WardDB)
            .filter(
                WardDB.assembly_constituency_id == assembly_constituency.id,
                WardDB.is_active.is_(True),
            )
            .all(),
            latitude,
            longitude,
        )
        village = _find_first_boundary_match(
            db.query(VillageDB)
            .filter(
                VillageDB.assembly_constituency_id == assembly_constituency.id,
                VillageDB.is_active.is_(True),
            )
            .all(),
            latitude,
            longitude,
        )

    if not assembly_constituency and ward:
        assembly_constituency = (
            db.query(AssemblyConstituencyDB)
            .filter(AssemblyConstituencyDB.id == ward.assembly_constituency_id)
            .first()
        )
    if not assembly_constituency and village:
        assembly_constituency = (
            db.query(AssemblyConstituencyDB)
            .filter(AssemblyConstituencyDB.id == village.assembly_constituency_id)
            .first()
        )

    district = None
    state = None
    if assembly_constituency:
        district = (
            db.query(DistrictDB)
            .filter(DistrictDB.id == assembly_constituency.district_id)
            .first()
        )
        if (
            assembly_constituency.parliamentary_constituency_id
            and not parliamentary_constituency
        ):
            parliamentary_constituency = (
                db.query(ParliamentaryConstituencyDB)
                .filter(
                    ParliamentaryConstituencyDB.id
                    == assembly_constituency.parliamentary_constituency_id
                )
                .first()
            )

    if parliamentary_constituency:
        state = (
            db.query(StateDB)
            .filter(StateDB.id == parliamentary_constituency.state_id)
            .first()
        )

    if district and not state:
        state = db.query(StateDB).filter(StateDB.id == district.state_id).first()

    return {
        "state": state,
        "district": district,
        "parliamentary_constituency": parliamentary_constituency,
        "assembly_constituency": assembly_constituency,
        "ward": ward,
        "village": village,
    }


def resolve_jurisdiction_ids(
    db: Session, latitude: float, longitude: float
) -> dict[str, str | None]:
    entities = resolve_jurisdiction_entities(db, latitude, longitude)
    return {
        "state_id": entities["state"].id if entities["state"] else None,
        "district_id": entities["district"].id if entities["district"] else None,
        "parliamentary_constituency_id": (
            entities["parliamentary_constituency"].id
            if entities["parliamentary_constituency"]
            else None
        ),
        "assembly_constituency_id": (
            entities["assembly_constituency"].id
            if entities["assembly_constituency"]
            else None
        ),
        "ward_id": entities["ward"].id if entities["ward"] else None,
        "village_id": entities["village"].id if entities["village"] else None,
    }


def lookup_jurisdiction(
    db: Session, latitude: float, longitude: float
) -> dict[str, dict[str, Any] | None]:
    entities = resolve_jurisdiction_entities(db, latitude, longitude)

    state = entities["state"]
    district = entities["district"]
    parliamentary_constituency = entities["parliamentary_constituency"]
    assembly_constituency = entities["assembly_constituency"]
    ward = entities["ward"]
    village = entities["village"]

    return {
        "state": (
            {"id": state.id, "name": state.name, "code": state.code} if state else None
        ),
        "district": (
            {
                "id": district.id,
                "name": district.name,
                "code": district.code,
            }
            if district
            else None
        ),
        "parliamentary_constituency": (
            {
                "id": parliamentary_constituency.id,
                "name": parliamentary_constituency.name,
                "code": parliamentary_constituency.code,
                "boundary_version": parliamentary_constituency.boundary_version,
                "area_metadata": parliamentary_constituency.area_metadata,
                "population_metadata": parliamentary_constituency.population_metadata,
            }
            if parliamentary_constituency
            else None
        ),
        "assembly_constituency": (
            {
                "id": assembly_constituency.id,
                "name": assembly_constituency.name,
                "code": assembly_constituency.code,
                "boundary_version": assembly_constituency.boundary_version,
                "area_metadata": assembly_constituency.area_metadata,
                "population_metadata": assembly_constituency.population_metadata,
            }
            if assembly_constituency
            else None
        ),
        "ward": (
            {
                "id": ward.id,
                "name": ward.name,
                "code": ward.code,
                "assembly_constituency_id": ward.assembly_constituency_id,
            }
            if ward
            else None
        ),
        "village": (
            {
                "id": village.id,
                "name": village.name,
                "code": village.code,
                "assembly_constituency_id": village.assembly_constituency_id,
            }
            if village
            else None
        ),
    }

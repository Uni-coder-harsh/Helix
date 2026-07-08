import json
import uuid

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from helix_platform.persistence import SessionLocal
from helix_platform.security import CurrentUser, Permissions
from services.governance import IssueCreateSchema, submit_issue
from services.governance.application.services import IssueApplicationService
from services.governance.infrastructure.models import IssueDB
from services.governance.infrastructure.repositories import SQLAlchemyIssueRepository
from services.identity.models import UserDB
from services.identity.routes import (
    add_assembly_constituency,
    add_country,
    add_district,
    add_parliamentary_constituency,
    add_state,
    add_village,
    add_ward,
    lookup_jurisdiction_coords,
)
from services.identity.schemas import (
    AssemblyConstituencyCreate,
    CountryCreate,
    DistrictCreate,
    ParliamentaryConstituencyCreate,
    StateCreate,
    VillageCreate,
    WardCreate,
)


def _square_geojson(
    min_longitude: float,
    min_latitude: float,
    max_longitude: float,
    max_latitude: float,
) -> str:
    return json.dumps(
        {
            "type": "Polygon",
            "coordinates": [
                [
                    [min_longitude, min_latitude],
                    [max_longitude, min_latitude],
                    [max_longitude, max_latitude],
                    [min_longitude, max_latitude],
                    [min_longitude, min_latitude],
                ]
            ],
        }
    )


def _admin_user(db: Session) -> UserDB:
    admin = db.query(UserDB).filter(UserDB.email == "admin@helix.gov").first()
    assert admin is not None
    return admin


def _create_hierarchy(
    admin_user: UserDB,
    suffix: str,
    *,
    point_latitude: float,
    point_longitude: float,
) -> tuple[dict[str, str], Session]:
    db: Session = SessionLocal()
    base_latitude = point_latitude - 0.5
    base_longitude = point_longitude - 0.5

    country = add_country(
        CountryCreate(name=f"Jurisdiction Country {suffix}", code=f"JC-{suffix}"),
        current_user=admin_user,
        db=db,
    )
    state = add_state(
        StateCreate(
            name=f"Jurisdiction State {suffix}",
            country_id=country.id,
            code=f"JS-{suffix}",
        ),
        current_user=admin_user,
        db=db,
    )
    district = add_district(
        DistrictCreate(
            name=f"Jurisdiction District {suffix}",
            state_id=state.id,
            code=f"JD-{suffix}",
        ),
        current_user=admin_user,
        db=db,
    )
    parliamentary_constituency = add_parliamentary_constituency(
        ParliamentaryConstituencyCreate(
            name=f"Jurisdiction PC {suffix}",
            state_id=state.id,
            code=f"PC-{suffix}",
            geojson_boundary=_square_geojson(
                base_longitude,
                base_latitude,
                base_longitude + 1.0,
                base_latitude + 1.0,
            ),
            area_metadata="regional",
            population_metadata="100000",
        ),
        current_user=admin_user,
        db=db,
    )
    assembly_constituency = add_assembly_constituency(
        AssemblyConstituencyCreate(
            name=f"Jurisdiction AC {suffix}",
            district_id=district.id,
            parliamentary_constituency_id=parliamentary_constituency.id,
            code=f"AC-{suffix}",
            geojson_boundary=_square_geojson(
                base_longitude + 0.1,
                base_latitude + 0.1,
                base_longitude + 0.9,
                base_latitude + 0.9,
            ),
            area_metadata="local",
            population_metadata="25000",
        ),
        current_user=admin_user,
        db=db,
    )
    ward = add_ward(
        WardCreate(
            name=f"Ward {suffix}",
            assembly_constituency_id=assembly_constituency.id,
            code=f"W-{suffix}",
            geojson_boundary=_square_geojson(
                base_longitude + 0.2,
                base_latitude + 0.2,
                base_longitude + 0.8,
                base_latitude + 0.8,
            ),
        ),
        current_user=admin_user,
        db=db,
    )
    village = add_village(
        VillageCreate(
            name=f"Village {suffix}",
            assembly_constituency_id=assembly_constituency.id,
            code=f"V-{suffix}",
            geojson_boundary=_square_geojson(
                base_longitude + 0.3,
                base_latitude + 0.3,
                base_longitude + 0.7,
                base_latitude + 0.7,
            ),
        ),
        current_user=admin_user,
        db=db,
    )

    return (
        {
            "state_id": state.id,
            "district_id": district.id,
            "parliamentary_constituency_id": parliamentary_constituency.id,
            "assembly_constituency_id": assembly_constituency.id,
            "ward_id": ward.id,
            "village_id": village.id,
        },
        db,
    )


def test_system_admin_can_manage_hierarchy_and_lookup() -> None:
    seed_db: Session = SessionLocal()
    try:
        admin_user = _admin_user(seed_db)
    finally:
        seed_db.close()

    suffix = uuid.uuid4().hex[:8]
    latitude = 21.125
    longitude = 81.125
    hierarchy_ids, db = _create_hierarchy(
        admin_user,
        suffix,
        point_latitude=latitude,
        point_longitude=longitude,
    )
    try:
        lookup_payload = lookup_jurisdiction_coords(latitude, longitude, db=db)
        assert lookup_payload["state"]["id"] == hierarchy_ids["state_id"]
        assert lookup_payload["district"]["id"] == hierarchy_ids["district_id"]
        assert (
            lookup_payload["parliamentary_constituency"]["id"]
            == hierarchy_ids["parliamentary_constituency_id"]
        )
        assert (
            lookup_payload["assembly_constituency"]["id"]
            == hierarchy_ids["assembly_constituency_id"]
        )
        assert lookup_payload["ward"]["id"] == hierarchy_ids["ward_id"]
        assert lookup_payload["village"]["id"] == hierarchy_ids["village_id"]

        with pytest.raises(HTTPException) as exc_info:
            add_parliamentary_constituency(
                ParliamentaryConstituencyCreate(
                    name=f"Broken PC {suffix}",
                    state_id=hierarchy_ids["state_id"],
                    code=f"BAD-{suffix}",
                    geojson_boundary=json.dumps(
                        {
                            "type": "Polygon",
                            "coordinates": [
                                [
                                    [81.0, 21.0],
                                    [81.2, 21.0],
                                    [81.2, 21.2],
                                    [81.0, 21.2],
                                ]
                            ],
                        }
                    ),
                ),
                current_user=admin_user,
                db=db,
            )

        assert exc_info.value.status_code == 400
    finally:
        db.close()


@pytest.mark.asyncio
async def test_issue_submission_persists_jurisdiction_resolution() -> None:
    seed_db: Session = SessionLocal()
    try:
        admin_user = _admin_user(seed_db)
    finally:
        seed_db.close()

    suffix = uuid.uuid4().hex[:8]
    latitude = 24.425
    longitude = 84.425
    hierarchy_ids, db = _create_hierarchy(
        admin_user,
        suffix,
        point_latitude=latitude,
        point_longitude=longitude,
    )
    try:
        issue_service = IssueApplicationService(SQLAlchemyIssueRepository(db))
        current_user = CurrentUser(
            user_id=None,
            role="Citizen",
            permissions={Permissions.ISSUES_CREATE},
        )
        payload = IssueCreateSchema(
            citizen_id="00000000-0000-0000-0000-000000000000",
            title=f"Jurisdiction Issue {suffix}",
            description="A complaint that should resolve into the configured administrative hierarchy.",
            category="sanitation",
            latitude=latitude,
            longitude=longitude,
            formatted_address=f"Test Address {suffix}",
        )

        issue_payload = await submit_issue(
            payload=payload,
            issue_service=issue_service,
            db=db,
            _current_user=current_user,
        )
        assert (
            issue_payload["jurisdiction"]["assembly_constituency"]["id"]
            == hierarchy_ids["assembly_constituency_id"]
        )

        issue = (
            db.query(IssueDB).filter(IssueDB.id == issue_payload["issue_id"]).first()
        )
        assert issue is not None
        assert issue.state_id == hierarchy_ids["state_id"]
        assert issue.district_id == hierarchy_ids["district_id"]
        assert (
            issue.parliamentary_constituency_id
            == hierarchy_ids["parliamentary_constituency_id"]
        )
        assert (
            issue.assembly_constituency_id == hierarchy_ids["assembly_constituency_id"]
        )
        assert issue.ward_id == hierarchy_ids["ward_id"]
        assert issue.village_id == hierarchy_ids["village_id"]
    finally:
        db.close()

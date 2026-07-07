import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from typing import Any

from helix_platform.config import get_settings

logger = logging.getLogger("helix.spatial.providers")


class GeoProvider(ABC):
    @abstractmethod
    def geocode(self, address: str) -> dict[str, Any] | None:
        """Geocodes address string to coordinates."""
        pass

    @abstractmethod
    def reverse_geocode(self, lat: float, lng: float) -> str | None:
        """Reverse geocodes coordinate to formatted address."""
        pass


class PlacesProvider(ABC):
    @abstractmethod
    def search_places(
        self, lat: float, lng: float, radius_m: int, place_type: str
    ) -> list[dict[str, Any]]:
        """Searches nearby civic assets."""
        pass


class SimpleTTLCache:
    """In-memory size-limited TTL cache to respect public Nominatim and Overpass policies."""

    def __init__(self, ttl_seconds: int, max_entries: int = 1000) -> None:
        self.ttl = ttl_seconds
        self.max_entries = max_entries
        self.cache: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        if key in self.cache:
            timestamp, val = self.cache[key]
            if time.time() - timestamp < self.ttl:
                logger.info(f"[Spatial Cache] Hit for key: {key}")
                return val
            logger.info(f"[Spatial Cache] Expired key: {key}")
            del self.cache[key]
        logger.info(f"[Spatial Cache] Miss for key: {key}")
        return None

    def set(self, key: str, value: Any) -> None:
        # Evict oldest entry if size limit exceeded
        if len(self.cache) >= self.max_entries:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][0])
            logger.info(f"[Spatial Cache] Evicting oldest key: {oldest_key}")
            del self.cache[oldest_key]
        self.cache[key] = (time.time(), value)


# Global cache caches
geocoding_cache = SimpleTTLCache(ttl_seconds=600, max_entries=1000)  # 10 minutes cache
places_cache = SimpleTTLCache(ttl_seconds=300, max_entries=1000)  # 5 minutes cache


def fetch_url_with_retry_and_backoff(
    provider_name: str,
    url: str,
    headers: dict[str, str],
    timeout_s: float = 3.0,
    retries: int = 1,
) -> bytes | None:
    """Utility method execution with dynamic timeouts and exponential backoff retries.

    Only retries on timeouts, connection failures, rate limits (429), or server errors (5xx).
    Does NOT retry on user errors (400, 401, 403, 404).
    """
    logger.info(f"Spatial request using provider: {provider_name}")
    start_time = time.perf_counter()
    retry_count = 0

    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, method="GET")
            for k, v in headers.items():
                req.add_header(k, v)
            with urllib.request.urlopen(req, timeout=timeout_s) as response:
                latency = time.perf_counter() - start_time
                logger.info(
                    f"[{provider_name}] Success. Latency: {latency:.4f}s, Retries: {retry_count}"
                )
                return response.read()
        except urllib.error.HTTPError as e:
            latency = time.perf_counter() - start_time
            # Retry only on specific server errors or rate limits
            if e.code in [429, 500, 502, 503, 504]:
                if attempt < retries:
                    retry_count += 1
                    logger.warning(
                        f"[{provider_name}] HTTP {e.code}. Retrying ({retry_count}/{retries}) in backoff..."
                    )
                    time.sleep(0.5 * (2**attempt))
                    continue
                logger.error(
                    f"[{provider_name}] Failed after {retry_count} retries. HTTP Error {e.code}. Latency: {latency:.4f}s"
                )
                break
            # Do not retry on client/authorization errors (400, 401, 403, 404, etc.)
            logger.error(
                f"[{provider_name}] Non-retryable HTTP Error {e.code}. Failure Reason: Client/Auth error. Latency: {latency:.4f}s"
            )
            break
        except urllib.error.URLError as e:
            latency = time.perf_counter() - start_time
            # Retry on connection errors/timeouts
            if attempt < retries:
                retry_count += 1
                logger.warning(
                    f"[{provider_name}] Connection error: {e.reason}. Retrying ({retry_count}/{retries})..."
                )
                time.sleep(0.5 * (2**attempt))
                continue
            logger.error(
                f"[{provider_name}] Connection failed after {retry_count} retries. Reason: {e.reason}. Latency: {latency:.4f}s"
            )
            break
        except Exception as e:
            latency = time.perf_counter() - start_time
            logger.error(
                f"[{provider_name}] Unexpected error: {e!s}. Latency: {latency:.4f}s"
            )
            break
    return None


class NominatimGeoProvider(GeoProvider):
    """Geocoding provider implementing OpenStreetMap's Nominatim REST API."""

    def geocode(self, address: str) -> dict[str, Any] | None:
        cache_key = f"geocode:{address.strip().lower()}"
        cached = geocoding_cache.get(cache_key)
        if cached is not None:
            return cached

        settings = get_settings()
        base_url = settings.GEOCODER_BASE_URL.rstrip("/")
        encoded_addr = urllib.parse.quote(address)
        url = f"{base_url}/search?q={encoded_addr}&format=json&limit=1"

        headers = {"User-Agent": "Helix-Governance-Platform/1.0.0 (contact@helix.gov)"}
        resp_bytes = fetch_url_with_retry_and_backoff(
            "Nominatim (Geocode)", url, headers, timeout_s=3.0, retries=1
        )
        if not resp_bytes:
            return None

        try:
            resp_data = json.loads(resp_bytes.decode("utf-8"))
            if resp_data:
                res = resp_data[0]
                coords = {
                    "latitude": float(res["lat"]),
                    "longitude": float(res["lon"]),
                    "formatted_address": res.get("display_name"),
                }
                geocoding_cache.set(cache_key, coords)
                return coords
        except Exception:
            pass
        return None

    def reverse_geocode(self, lat: float, lng: float) -> str | None:
        cache_key = f"reverse_geocode:{lat:.5f}:{lng:.5f}"
        cached = geocoding_cache.get(cache_key)
        if cached is not None:
            return cached

        settings = get_settings()
        base_url = settings.GEOCODER_BASE_URL.rstrip("/")
        url = f"{base_url}/reverse?lat={lat}&lon={lng}&format=json"

        headers = {"User-Agent": "Helix-Governance-Platform/1.0.0 (contact@helix.gov)"}
        resp_bytes = fetch_url_with_retry_and_backoff(
            "Nominatim (Reverse Geocode)", url, headers, timeout_s=3.0, retries=1
        )
        if not resp_bytes:
            return None

        try:
            resp_data = json.loads(resp_bytes.decode("utf-8"))
            if resp_data:
                addr = resp_data.get("display_name")
                geocoding_cache.set(cache_key, addr)
                return addr
        except Exception:
            pass
        return None


class OverpassPlacesProvider(PlacesProvider):
    """Places provider implementing OpenStreetMap's Overpass API."""

    def search_places(
        self, lat: float, lng: float, radius_m: int, place_type: str
    ) -> list[dict[str, Any]]:
        cache_key = (
            f"places:{lat:.5f}:{lng:.5f}:{radius_m}:{place_type.strip().lower()}"
        )
        cached = places_cache.get(cache_key)
        if cached is not None:
            return cached

        # Map place type query strings to OSM tags
        osm_tag = "[amenity=school]"
        if place_type == "hospital":
            osm_tag = "[amenity~'hospital|clinic']"
        elif place_type == "park":
            osm_tag = "[leisure~'park|playground']"

        settings = get_settings()
        base_url = settings.PLACES_BASE_URL.rstrip("/")
        query = f"[out:json];node(around:{radius_m},{lat},{lng}){osm_tag};out;"
        encoded_query = urllib.parse.quote(query)
        url = f"{base_url}?data={encoded_query}"

        headers = {"User-Agent": "Helix-Governance-Platform/1.0.0 (contact@helix.gov)"}
        resp_bytes = fetch_url_with_retry_and_backoff(
            "Overpass (Places)", url, headers, timeout_s=4.0, retries=1
        )
        if not resp_bytes:
            return []

        try:
            resp_data = json.loads(resp_bytes.decode("utf-8"))
            elements = resp_data.get("elements", [])
            places = []
            for item in elements:
                tags = item.get("tags", {})
                name = (
                    tags.get("name")
                    or tags.get("official_name")
                    or f"Civic {place_type.capitalize()}"
                )
                places.append(
                    {
                        "name": name,
                        "latitude": item.get("lat"),
                        "longitude": item.get("lon"),
                        "place_id": f"osm-{item.get('id')}",
                        "address": tags.get("addr:street")
                        or tags.get("addr:suburb")
                        or "Local Area, Bengaluru",
                        "rating": 4.2,
                    }
                )
            places_cache.set(cache_key, places)
            return places
        except Exception:
            pass
        return []

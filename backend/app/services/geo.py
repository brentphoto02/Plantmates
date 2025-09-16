from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Optional

EARTH_RADIUS_MILES = 3958.8


def haversine_distance_miles(
    origin_lat: Optional[float],
    origin_lng: Optional[float],
    target_lat: Optional[float],
    target_lng: Optional[float],
) -> Optional[float]:
    """Calculate the geodesic distance in miles between two coordinates."""

    if (
        origin_lat is None
        or origin_lng is None
        or target_lat is None
        or target_lng is None
    ):
        return None

    origin_lat_rad = radians(origin_lat)
    origin_lng_rad = radians(origin_lng)
    target_lat_rad = radians(target_lat)
    target_lng_rad = radians(target_lng)

    delta_lat = target_lat_rad - origin_lat_rad
    delta_lng = target_lng_rad - origin_lng_rad

    a = sin(delta_lat / 2) ** 2 + cos(origin_lat_rad) * cos(target_lat_rad) * sin(delta_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    return EARTH_RADIUS_MILES * c

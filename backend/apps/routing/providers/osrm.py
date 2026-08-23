import urllib.request
import json
from typing import List, Optional
from django.conf import settings
from apps.eta.predictors.rule_based import CITY_COORDINATES, DEFAULT_CORRIDOR_DISTANCES_KM, haversine_distance_km
from .base import BaseRoutingProvider, RouteCandidate, RouteLegCandidate

class OSRMRoutingProvider(BaseRoutingProvider):
    """
    OSRM Routing Provider integration.
    Queries OSRM server (configured via OSRM_BASE_URL), with geodesic corridor fallback if unreachable or offline.
    """
    def calculate_candidate_routes(
        self,
        origin_city: str,
        destination_city: str,
        origin_lat: Optional[float] = None,
        origin_lon: Optional[float] = None,
        dest_lat: Optional[float] = None,
        dest_lon: Optional[float] = None
    ) -> List[RouteCandidate]:
        orig_key = origin_city.strip().lower()
        dest_key = destination_city.strip().lower()
        
        orig_coords = (origin_lat, origin_lon) if (origin_lat is not None and origin_lon is not None) else CITY_COORDINATES.get(orig_key)
        dest_coords = (dest_lat, dest_lon) if (dest_lat is not None and dest_lon is not None) else CITY_COORDINATES.get(dest_key)

        candidates: List[RouteCandidate] = []

        if orig_coords and dest_coords:
            osrm_url = getattr(settings, 'OSRM_BASE_URL', 'http://localhost:5000')
            request_url = f"{osrm_url}/route/v1/driving/{orig_coords[1]},{orig_coords[0]};{dest_coords[1]},{dest_coords[0]}?overview=full&geometries=geojson&alternatives=true"
            try:
                req = urllib.request.Request(request_url, headers={'User-Agent': 'TradeFlow-Routing/1.0'})
                with urllib.request.urlopen(req, timeout=3) as resp:
                    if resp.status == 200:
                        data = json.loads(resp.read().decode('utf-8'))
                        if data.get('code') == 'Ok' and data.get('routes'):
                            for idx, r in enumerate(data['routes']):
                                dist_km = round(r['distance'] / 1000.0, 2)
                                dur_min = round(r['duration'] / 60.0)
                                fuel_l = round(dist_km * 0.35, 2)
                                fuel_cost = round(fuel_l * 90.0, 2)
                                geometry = r.get('geometry', {})
                                leg_item = RouteLegCandidate(
                                    sequence=1,
                                    start_point=origin_city,
                                    end_point=destination_city,
                                    distance_km=dist_km,
                                    duration_minutes=dur_min,
                                    estimated_fuel_liters=fuel_l,
                                    security_risk_score=0.10 + (idx * 0.05)
                                )
                                candidates.append(RouteCandidate(
                                    provider='OSRM',
                                    provider_route_id=f"osrm-rt-{idx+1}",
                                    origin_city=origin_city,
                                    destination_city=destination_city,
                                    distance_km=dist_km,
                                    duration_minutes=dur_min,
                                    estimated_fuel_liters=fuel_l,
                                    estimated_fuel_cost=fuel_cost,
                                    risk_score=0.10 + (idx * 0.05),
                                    legs=[leg_item],
                                    geometry_json=geometry
                                ))
            except Exception:
                pass

        if not candidates:
            if orig_coords and dest_coords:
                base_dist = haversine_distance_km(orig_coords[0], orig_coords[1], dest_coords[0], dest_coords[1])
            else:
                base_dist = DEFAULT_CORRIDOR_DISTANCES_KM.get((orig_key, dest_key)) or DEFAULT_CORRIDOR_DISTANCES_KM.get((dest_key, orig_key)) or 300.0

            d1 = round(base_dist, 2)
            t1 = round((base_dist / 50.0) * 60)
            f1 = round(d1 * 0.35, 2)
            candidates.append(RouteCandidate(
                provider='GeodesicCorridor',
                provider_route_id='gc-primary',
                origin_city=origin_city,
                destination_city=destination_city,
                distance_km=d1,
                duration_minutes=t1,
                estimated_fuel_liters=f1,
                estimated_fuel_cost=round(f1 * 90.0, 2),
                risk_score=0.10,
                legs=[RouteLegCandidate(
                    sequence=1, start_point=origin_city, end_point=destination_city,
                    distance_km=d1, duration_minutes=t1, estimated_fuel_liters=f1, security_risk_score=0.10
                )],
                geometry_json={"type": "LineString", "coordinates": [[orig_coords[1], orig_coords[0]], [dest_coords[1], dest_coords[0]]]} if (orig_coords and dest_coords) else {}
            ))

            d2 = round(base_dist * 1.08, 2)
            t2 = round((d2 / 55.0) * 60)
            f2 = round(d2 * 0.35, 2)
            candidates.append(RouteCandidate(
                provider='GeodesicCorridor',
                provider_route_id='gc-alternative',
                origin_city=origin_city,
                destination_city=destination_city,
                distance_km=d2,
                duration_minutes=t2,
                estimated_fuel_liters=f2,
                estimated_fuel_cost=round(f2 * 90.0, 2),
                risk_score=0.05,
                legs=[RouteLegCandidate(
                    sequence=1, start_point=origin_city, end_point=destination_city,
                    distance_km=d2, duration_minutes=t2, estimated_fuel_liters=f2, security_risk_score=0.05
                )],
                geometry_json={"type": "LineString", "coordinates": [[orig_coords[1], orig_coords[0]], [dest_coords[1], dest_coords[0]]]} if (orig_coords and dest_coords) else {}
            ))

        return candidates

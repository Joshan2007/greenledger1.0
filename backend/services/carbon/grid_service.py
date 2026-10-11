"""
GreenLedger - Dynamic Real-Time Carbon Grid Intelligence Service
Novelty 2: Temporal Workload Orchestration & Dynamic Grid Carbon Intensity.
Models live grid carbon intensity, regional diurnal solar/wind curves,
and awards clean-grid bonuses during fossil peaker periods.
"""

import time
import datetime
import urllib.request
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("GreenLedger.GridService")

# Regional Base Factors & Diurnal Profiles
GRID_ZONES = {
    "IN-SR": {
        "zone": "IN-SR",
        "name": "India (Southern Regional Grid - SR)",
        "country": "India",
        "base_intensity": 0.680,
        "solar_penetration": 0.28,
        "wind_penetration": 0.18,
        "peak_hours": [18, 19, 20, 21],
        "solar_hours": [10, 11, 12, 13, 14, 15]
    },
    "IN-NATIONAL": {
        "zone": "IN-NATIONAL",
        "name": "India (National Grid Average)",
        "country": "India",
        "base_intensity": 0.710,
        "solar_penetration": 0.20,
        "wind_penetration": 0.12,
        "peak_hours": [18, 19, 20, 21],
        "solar_hours": [10, 11, 12, 13, 14, 15]
    },
    "US-CAISO": {
        "zone": "US-CAISO",
        "name": "USA (California ISO - CAISO)",
        "country": "United States",
        "base_intensity": 0.260,
        "solar_penetration": 0.45,
        "wind_penetration": 0.15,
        "peak_hours": [17, 18, 19, 20, 21],
        "solar_hours": [9, 10, 11, 12, 13, 14, 15, 16]
    },
    "US-NATIONAL": {
        "zone": "US-NATIONAL",
        "name": "USA (EPA eGRID National Average)",
        "country": "United States",
        "base_intensity": 0.385,
        "solar_penetration": 0.15,
        "wind_penetration": 0.12,
        "peak_hours": [17, 18, 19, 20],
        "solar_hours": [10, 11, 12, 13, 14, 15]
    },
    "GB-NATIONAL": {
        "zone": "GB-NATIONAL",
        "name": "United Kingdom (National Grid ESO)",
        "country": "United Kingdom",
        "base_intensity": 0.165,
        "solar_penetration": 0.10,
        "wind_penetration": 0.38,
        "peak_hours": [17, 18, 19],
        "solar_hours": [11, 12, 13, 14]
    },
    "EU-GERMANY": {
        "zone": "EU-GERMANY",
        "name": "Germany (Agora / UBA Grid)",
        "country": "Germany",
        "base_intensity": 0.348,
        "solar_penetration": 0.25,
        "wind_penetration": 0.30,
        "peak_hours": [17, 18, 19, 20],
        "solar_hours": [10, 11, 12, 13, 14, 15]
    },
    "NORDIC": {
        "zone": "NORDIC",
        "name": "Nordic Clean Hydro/Nuclear",
        "country": "Norway / Sweden",
        "base_intensity": 0.045,
        "solar_penetration": 0.05,
        "wind_penetration": 0.25,
        "peak_hours": [],
        "solar_hours": [10, 11, 12, 13, 14]
    }
}


class GridCarbonService:
    def __init__(self):
        self._cached_grid_state: Optional[Dict[str, Any]] = None
        self._cache_timestamp: float = 0.0
        self._selected_zone: str = "IN-SR"
        self._auto_detected_zone: Optional[str] = None
        self._detect_location()

    def _detect_location(self):
        """Attempts to auto-detect country/region via local IP."""
        try:
            req = urllib.request.Request(
                "http://ip-api.com/json/?fields=country,countryCode,regionName,city",
                headers={"User-Agent": "GreenLedger-GridClient/1.0"}
            )
            with urllib.request.urlopen(req, timeout=1.8) as resp:
                data = json.loads(resp.read().decode())
                country_code = data.get("countryCode", "").upper()
                region = data.get("regionName", "")
                city = data.get("city", "")

                if country_code == "IN":
                    self._auto_detected_zone = "IN-SR" if any(s in region.lower() for s in ["tamil", "kerala", "karnataka", "andhra"]) else "IN-NATIONAL"
                elif country_code == "US":
                    self._auto_detected_zone = "US-CAISO" if "california" in region.lower() else "US-NATIONAL"
                elif country_code == "GB":
                    self._auto_detected_zone = "GB-NATIONAL"
                elif country_code == "DE":
                    self._auto_detected_zone = "EU-GERMANY"
                else:
                    self._auto_detected_zone = "IN-SR"

                self._selected_zone = self._auto_detected_zone
                logger.info(f"Auto-detected location: {city}, {region}, {country_code} -> Grid Zone: {self._selected_zone}")
        except Exception as e:
            logger.debug(f"Geo-IP detection note: {e}")
            self._selected_zone = "IN-SR"

    def set_zone(self, zone_id: str) -> bool:
        """Allows manual user override of the grid zone."""
        if zone_id in GRID_ZONES:
            self._selected_zone = zone_id
            self._cached_grid_state = None
            self._cache_timestamp = 0.0
            return True
        return False

    def get_available_zones(self) -> Dict[str, Any]:
        """Returns list of supported grid zones."""
        return {
            k: {
                "name": v["name"],
                "country": v["country"],
                "base_intensity": v["base_intensity"],
                "is_current": (k == self._selected_zone)
            }
            for k, v in GRID_ZONES.items()
        }

    def _fetch_live_uk_intensity(self) -> Optional[float]:
        """Queries the official UK National Grid ESO Live API."""
        try:
            req = urllib.request.Request(
                "https://api.carbonintensity.org.uk/intensity",
                headers={"User-Agent": "GreenLedger-GridClient/1.0"}
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                intensity_g = data["data"][0]["intensity"]["actual"] or data["data"][0]["intensity"]["forecast"]
                return round(intensity_g / 1000.0, 4)
        except Exception:
            return None

    def get_current_grid_state(self) -> Dict[str, Any]:
        """
        Calculates real-time dynamic carbon intensity based on current hour,
        solar/wind penetration curves, and live APIs.
        """
        now = time.time()
        if self._cached_grid_state and (now - self._cache_timestamp) < 60.0:
            return self._cached_grid_state

        zone_data = GRID_ZONES.get(self._selected_zone, GRID_ZONES["IN-SR"])
        local_time = datetime.datetime.now()
        current_hour = local_time.hour
        
        base = zone_data["base_intensity"]
        intensity = base

        # Try live API if UK zone selected
        if self._selected_zone == "GB-NATIONAL":
            live_uk = self._fetch_live_uk_intensity()
            if live_uk is not None:
                intensity = live_uk

        # If not live API, compute physics-based diurnal curve
        if self._selected_zone != "GB-NATIONAL" or intensity == base:
            # Diurnal Solar Curve Modulation (solar peak midday decreases intensity by up to 35%)
            if current_hour in zone_data["solar_hours"]:
                # Curve peaks at 13:00 (1:00 PM)
                distance_from_peak = abs(current_hour - 13)
                solar_factor = max(0.0, 1.0 - (distance_from_peak * 0.25))
                solar_reduction = zone_data["solar_penetration"] * solar_factor * 0.40
                intensity = base * (1.0 - solar_reduction)
            
            # Evening Peak Demand (peaker gas/coal plants spin up from 18:00 - 22:00)
            elif current_hour in zone_data["peak_hours"]:
                peaker_markup = 0.22  # +22% dirty emission surge during peaker plant dispatch
                intensity = base * (1.0 + peaker_markup)

        intensity = round(max(0.02, intensity), 4)
        intensity_g = round(intensity * 1000.0, 1)

        # Classify grid cleanliness
        if intensity < 0.200:
            status = "clean"
            status_label = "Clean Renewable Window"
            badge_color = "emerald"
            multiplier = 1.0
            recommendation = "Grid is powered heavily by renewables. Ideal window for background compilation, backups, and ML inference."
        elif intensity < 0.550:
            status = "moderate"
            status_label = "Moderate Grid Load"
            badge_color = "amber"
            multiplier = 1.3
            recommendation = "Standard grid mix active. Safe for normal tasks; heavy batch processing recommended during solar peak."
        else:
            status = "dirty_peak"
            status_label = "Fossil Peaker Grid Alert"
            badge_color = "rose"
            multiplier = 1.8
            recommendation = "High carbon intensity! Fossil peaker plants are active. Optimizing now averts maximum emissions; earns 1.8x Green Credits."

        # Compute renewable percentage estimate
        approx_renewable_pct = round(max(5.0, min(95.0, (1.0 - (intensity / 0.850)) * 100.0)), 1)

        state = {
            "zone": zone_data["zone"],
            "zone_name": zone_data["name"],
            "country": zone_data["country"],
            "intensity_kg_per_kwh": intensity,
            "intensity_g_per_kwh": intensity_g,
            "status": status,
            "status_label": status_label,
            "badge_color": badge_color,
            "renewable_percentage": approx_renewable_pct,
            "carbon_multiplier": multiplier,
            "peak_hours_text": "6:00 PM - 10:00 PM",
            "clean_window_text": "11:00 AM - 3:00 PM (Solar Peak)",
            "current_hour": current_hour,
            "recommendation": recommendation,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        self._cached_grid_state = state
        self._cache_timestamp = now
        return state


# Global singleton service
grid_carbon_service = GridCarbonService()

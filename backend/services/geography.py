"""
CITADEL KEBBI - Geographic Accuracy Module
Provides accurate distances, boundaries, and locations for Kebbi State
"""
import math
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass

@dataclass
class Location:
    """Geographic location with metadata"""
    name: str
    lat: float
    lon: float
    type: str  # 'border', 'river', 'town', 'landmark'
    description: str = ""


# ACCURATE KEBBI STATE BOUNDARY (Approximate polygon)
KEBBI_BOUNDARY = {
    "north": 13.5,      # Niger Republic border
    "south": 10.8,      # Sokoto State border
    "east": 5.9,        # Zamfara State border
    "west": 3.5,        # Niger Republic / Benin border
    "center": {"lat": 12.0, "lon": 4.2}
}

# ACCURATE BORDER CROSSING POINTS
BORDER_POINTS = {
    "niger_republic": {
        "northwest": {"lat": 13.45, "lon": 3.8, "name": "Kamba Border"},
        "northeast": {"lat": 13.42, "lon": 4.5, "name": "Giro Border"},
        "center_north": {"lat": 13.1, "lon": 3.9, "name": "Bagudo Border"},
    },
    "benin_republic": {
        "west": {"lat": 11.2, "lon": 3.5, "name": "Benin Border"},
    },
    "sokoto_state": {
        "south": {"lat": 10.8, "lon": 4.5, "name": "Sokoto Border"},
    },
    "zamfara_state": {
        "east": {"lat": 12.0, "lon": 5.9, "name": "Zamfara Border"},
    },
    "niger_state": {
        "southeast": {"lat": 10.9, "lon": 5.5, "name": "Niger Border"},
    }
}

# MAJOR RIVERS IN KEBBI
RIVERS = {
    "rima": {
        "name": "Rima River",
        "start": {"lat": 12.8, "lon": 4.5},
        "end": {"lat": 11.0, "lon": 4.3},
        "description": "Major tributary of Sokoto River, flows through Argungu and Birnin Kebbi",
        "closest_towns": ["Argungu", "Birnin Kebbi", "Jega"]
    },
    "sokoto": {
        "name": "Sokoto River",
        "start": {"lat": 13.0, "lon": 4.0},
        "end": {"lat": 10.5, "lon": 4.2},
        "description": "Major river forming part of southern boundary",
        "closest_towns": ["Shanga", "Bagudo"]
    },
    "niger": {
        "name": "Niger River",
        "start": {"lat": 12.5, "lon": 3.8},
        "end": {"lat": 11.5, "lon": 3.7},
        "description": "Forms part of western boundary with Niger Republic",
        "closest_towns": ["Kamba", "Dandi"]
    }
}

# MAJOR TOWNS WITH ACCURATE COORDINATES
MAJOR_TOWNS = {
    "birnin_kebbi": Location("Birnin Kebbi", 12.4539, 4.1975, "town", "State Capital"),
    "argungu": Location("Argungu", 12.7448, 4.5251, "town", "Famous for Argungu Fishing Festival"),
    "yauri": Location("Yauri", 12.5086, 4.5607, "town", "Historic town with hydroelectric dam"),
    "zuru": Location("Zuru", 11.4308, 5.2309, "town", "Headquarters of Zuru LGA"),
    "jega": Location("Jega", 12.2236, 4.3791, "town", "Major commercial center"),
    "kamba": Location("Kamba", 11.8516, 3.6542, "town", "Border town with Niger Republic"),
    "bagudo": Location("Bagudo", 11.4045, 4.2249, "town", "Western Kebbi border area"),
    "fakai": Location("Fakai", 11.6333, 4.8333, "town", "Southeastern Kebbi, Zamfara border"),
    "sakaba": Location("Sakaba", 11.4500, 5.3500, "town", "Northeastern border area"),
    "wasagu": Location("Wasagu", 11.3500, 5.4500, "town", "Border with Zamfara"),
    "danko": Location("Danko", 11.4000, 5.5000, "town", "Border area"),
}

# HIGH-RISK BORDER LGAs
HIGH_RISK_LGAS = {
    "bagudo": {"risk": "high", "border": "niger_republic", "distance_km": 15},
    "dandi": {"risk": "high", "border": "niger_republic", "distance_km": 20},
    "kamba": {"risk": "critical", "border": "benin_niger", "distance_km": 5},
    "fakai": {"risk": "high", "border": "zamfara", "distance_km": 25},
    "sakaba": {"risk": "high", "border": "zamfara_niger", "distance_km": 30},
    "wasagu": {"risk": "critical", "border": "zamfara", "distance_km": 15},
    "zuru": {"risk": "medium", "border": "sokoto", "distance_km": 40},
}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


def get_nearest_border(lat: float, lon: float) -> Dict:
    """Find the nearest international or state border"""
    borders = []
    
    # Check Niger Republic borders
    for name, point in BORDER_POINTS["niger_republic"].items():
        dist = haversine_distance(lat, lon, point["lat"], point["lon"])
        borders.append({
            "name": f"Niger Republic ({point['name']})",
            "distance_km": round(dist, 1),
            "direction": calculate_direction(lat, lon, point["lat"], point["lon"]),
            "type": "international"
        })
    
    # Check Benin border
    if "benin_republic" in BORDER_POINTS:
        for name, point in BORDER_POINTS["benin_republic"].items():
            dist = haversine_distance(lat, lon, point["lat"], point["lon"])
            borders.append({
                "name": f"Benin Republic ({point['name']})",
                "distance_km": round(dist, 1),
                "direction": calculate_direction(lat, lon, point["lat"], point["lon"]),
                "type": "international"
            })
    
    # Check state borders
    for state, points in BORDER_POINTS.items():
        if state in ["sokoto_state", "zamfara_state", "niger_state"]:
            for name, point in points.items():
                dist = haversine_distance(lat, lon, point["lat"], point["lon"])
                borders.append({
                    "name": f"{state.replace('_', ' ').title()} ({point['name']})",
                    "distance_km": round(dist, 1),
                    "direction": calculate_direction(lat, lon, point["lat"], point["lon"]),
                    "type": "state"
                })
    
    # Sort by distance and return nearest
    borders.sort(key=lambda x: x["distance_km"])
    return borders[0] if borders else None


def get_nearest_river(lat: float, lon: float) -> Dict:
    """Find the nearest major river"""
    rivers = []
    
    for river_id, river in RIVERS.items():
        # Calculate distance to river line (simplified: closest endpoint)
        dist_start = haversine_distance(lat, lon, river["start"]["lat"], river["start"]["lon"])
        dist_end = haversine_distance(lat, lon, river["end"]["lat"], river["end"]["lon"])
        dist = min(dist_start, dist_end)
        
        # Find closest point on river (midpoint approximation)
        mid_lat = (river["start"]["lat"] + river["end"]["lat"]) / 2
        mid_lon = (river["start"]["lon"] + river["end"]["lon"]) / 2
        dist_mid = haversine_distance(lat, lon, mid_lat, mid_lon)
        
        closest_dist = min(dist, dist_mid)
        
        rivers.append({
            "name": river["name"],
            "distance_km": round(closest_dist, 1),
            "direction": calculate_direction(lat, lon, mid_lat, mid_lon),
            "description": river["description"]
        })
    
    rivers.sort(key=lambda x: x["distance_km"])
    return rivers[0] if rivers else None


def get_nearest_town(lat: float, lon: float) -> Dict:
    """Find the nearest major town"""
    towns = []
    
    for town_id, town in MAJOR_TOWNS.items():
        dist = haversine_distance(lat, lon, town.lat, town.lon)
        towns.append({
            "name": town.name,
            "distance_km": round(dist, 1),
            "direction": calculate_direction(lat, lon, town.lat, town.lon),
            "description": town.description
        })
    
    towns.sort(key=lambda x: x["distance_km"])
    return towns[0] if towns else None


def calculate_direction(lat1: float, lon1: float, lat2: float, lon2: float) -> str:
    """Calculate cardinal direction from point 1 to point 2"""
    dy = lat2 - lat1
    dx = lon2 - lon1
    
    angle = math.degrees(math.atan2(dx, dy))
    
    # Convert angle to cardinal direction
    if -22.5 <= angle < 22.5:
        return "north"
    elif 22.5 <= angle < 67.5:
        return "northeast"
    elif 67.5 <= angle < 112.5:
        return "east"
    elif 112.5 <= angle < 157.5:
        return "southeast"
    elif 157.5 <= angle <= 180 or -180 <= angle < -157.5:
        return "south"
    elif -157.5 <= angle < -112.5:
        return "southwest"
    elif -112.5 <= angle < -67.5:
        return "west"
    elif -67.5 <= angle < -22.5:
        return "northwest"
    
    return "unknown"


def get_lga_from_coordinates(lat: float, lon: float) -> str:
    """Determine which LGA coordinates belong to (approximate)"""
    # Simple bounding box check for major LGAs
    lga_bounds = {
        "Birnin Kebbi": {"lat_min": 12.3, "lat_max": 12.6, "lon_min": 4.0, "lon_max": 4.4},
        "Argungu": {"lat_min": 12.6, "lat_max": 12.9, "lon_min": 4.3, "lon_max": 4.7},
        "Yauri": {"lat_min": 12.4, "lat_max": 12.7, "lon_min": 4.4, "lon_max": 4.8},
        "Zuru": {"lat_min": 11.2, "lat_max": 11.7, "lon_min": 5.0, "lon_max": 5.5},
        "Jega": {"lat_min": 12.1, "lat_max": 12.4, "lon_min": 4.2, "lon_max": 4.6},
        "Kamba": {"lat_min": 11.7, "lat_max": 12.0, "lon_min": 3.4, "lon_max": 3.9},
        "Bagudo": {"lat_min": 11.2, "lat_max": 11.6, "lon_min": 4.0, "lon_max": 4.5},
        "Fakai": {"lat_min": 11.5, "lat_max": 11.8, "lon_min": 4.6, "lon_max": 5.1},
        "Sakaba": {"lat_min": 11.3, "lat_max": 11.7, "lon_min": 5.2, "lon_max": 5.6},
        "Wasagu": {"lat_min": 11.1, "lat_max": 11.5, "lon_min": 5.3, "lon_max": 5.7},
    }
    
    for lga, bounds in lga_bounds.items():
        if (bounds["lat_min"] <= lat <= bounds["lat_max"] and 
            bounds["lon_min"] <= lon <= bounds["lon_max"]):
            return lga
    
    # If not in any bounds, return nearest
    nearest = get_nearest_town(lat, lon)
    return nearest["name"] if nearest else "Unknown LGA"


def get_geographic_context(lat: float, lon: float) -> Dict:
    """
    Get comprehensive geographic context for any coordinates in Kebbi State
    This is what the AI should use instead of making up distances
    """
    context = {
        "coordinates": {"lat": round(lat, 4), "lon": round(lon, 4)},
        "estimated_lga": get_lga_from_coordinates(lat, lon),
    }
    
    # Get nearest border
    nearest_border = get_nearest_border(lat, lon)
    if nearest_border:
        context["nearest_border"] = nearest_border
    
    # Get nearest river
    nearest_river = get_nearest_river(lat, lon)
    if nearest_river:
        context["nearest_river"] = nearest_river
    
    # Get nearest town
    nearest_town = get_nearest_town(lat, lon)
    if nearest_town:
        context["nearest_town"] = nearest_town
    
    # Check if in high-risk LGA
    lga = context["estimated_lga"]
    if lga in HIGH_RISK_LGAS:
        context["security_assessment"] = {
            "risk_level": HIGH_RISK_LGAS[lga]["risk"],
            "proximity_to_border": f"{HIGH_RISK_LGAS[lga]['distance_km']} km from {HIGH_RISK_LGAS[lga]['border']}",
            "note": "High-risk border area - increased bandit activity reported"
        }
    
    return context


def format_geographic_description(lat: float, lon: float) -> str:
    """Format geographic information for AI responses"""
    context = get_geographic_context(lat, lon)
    
    parts = []
    
    # Location
    parts.append(f"Coordinates: {context['coordinates']['lat']}°N, {context['coordinates']['lon']}°E")
    parts.append(f"Estimated Location: {context['estimated_lga']} LGA, Kebbi State")
    
    # Border proximity
    if "nearest_border" in context:
        border = context["nearest_border"]
        parts.append(f"Border Proximity: {border['distance_km']} km {border['direction']} of {border['name']}")
    
    # River proximity
    if "nearest_river" in context:
        river = context["nearest_river"]
        parts.append(f"River Proximity: {river['distance_km']} km {river['direction']} of {river['name']}")
    
    # Town proximity
    if "nearest_town" in context:
        town = context["nearest_town"]
        parts.append(f"Nearest Town: {town['name']} ({town['distance_km']} km {town['direction']})")
    
    # Security note
    if "security_assessment" in context:
        sec = context["security_assessment"]
        parts.append(f"Security Assessment: {sec['risk_level'].upper()} risk area - {sec['proximity_to_border']}")
    
    return "\n".join(parts)


# Test function
if __name__ == "__main__":
    # Test with coordinates from Fakai LGA
    test_lat = 11.6333
    test_lon = 4.8333
    
    print("Testing Geographic Module")
    print("=" * 50)
    print(format_geographic_description(test_lat, test_lon))

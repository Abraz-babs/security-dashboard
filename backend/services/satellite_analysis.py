"""
SATELLITE IMAGERY ANALYSIS FOR SECURITY
Integrates Copernicus data with AI for accurate security assessments
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
from services.copernicus import fetch_sentinel_products, fetch_sentinel1_products
from services.geography import get_geographic_context
from config import COPERNICUS_CLIENT_ID, COPERNICUS_CLIENT_SECRET


class SatelliteImageryAnalyzer:
    """
    Analyzes satellite imagery for security-relevant features.
    Provides ACTUAL data, not hallucinations.
    """
    
    # What Sentinel-2 can actually detect
    S2_CAPABILITIES = {
        "resolution": "10m (visible/NIR), 20m (red edge/SWIR), 60m (atmospheric)",
        "can_detect": [
            "Large fires (> 30m) via thermal signature",
            "Smoke plumes (> 100m)",
            "Major infrastructure (buildings, roads)",
            "Land cover changes (clearings, burning)",
            "Water bodies and flooding",
            "Agricultural patterns",
            "Large vehicle concentrations (> 10 vehicles in open area)",
        ],
        "cannot_detect": [
            "Individual people",
            "Small groups (< 50 people in tight formation)",
            "Weapons or equipment",
            "Activity inside buildings",
            "Night activity (no thermal)",
            "Under cloud cover",
        ],
        "revisit_frequency": "5 days (with both S2A and S2B)",
    }
    
    # What Sentinel-1 (SAR) can detect
    S1_CAPABILITIES = {
        "resolution": "5m-40m depending on mode",
        "can_detect": [
            "All-weather (penetrates clouds)",
            "Night/day capability",
            "Large vehicle convoys on roads",
            "Ships on water",
            "Flooding (water vs land contrast)",
            "Major terrain changes",
            "Large camps/settlements (> 50 structures)",
        ],
        "cannot_detect": [
            "Individual vehicles (too small)",
            "People",
            "Activity details",
            "Color/vegetation health",
        ],
        "revisit_frequency": "6 days (single satellite), 3 days (with both)",
    }


async def analyze_lga_for_security(lga: str, days_back: int = 7) -> Dict[str, Any]:
    """
    Fetch and analyze REAL satellite data for an LGA.
    Returns actual available data with security assessment.
    """
    from services.geography import MAJOR_TOWNS
    
    # Get coordinates for the LGA
    town = MAJOR_TOWNS.get(lga.lower().replace(" ", "_"))
    if not town:
        return {
            "status": "error",
            "message": f"Coordinates not found for {lga}",
            "timestamp": datetime.now().isoformat(),
        }
    
    lat, lon = town.lat, town.lon
    
    # Fetch actual satellite data
    try:
        # Try to get Sentinel-2 (optical) products
        s2_products = await fetch_sentinel_products(
            lat=lat, 
            lon=lon, 
            days=days_back,
            top=3
        )
        
        # Try to get Sentinel-1 (SAR) products  
        s1_products = await fetch_sentinel1_products(
            lat=lat,
            lon=lon,
            days=days_back,
            top=3
        )
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch satellite data: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }
    
    # Build analysis based on ACTUAL data
    analysis = {
        "status": "success",
        "lga": lga,
        "coordinates": {"lat": lat, "lon": lon},
        "analysis_timestamp": datetime.now().isoformat(),
        "period_covered": f"Last {days_back} days",
        
        "satellite_availability": {
            "sentinel_2_optical": {
                "available": len(s2_products.get("products", [])) > 0,
                "image_count": len(s2_products.get("products", [])),
                "latest_image": s2_products["products"][0] if s2_products.get("products") else None,
                "coverage": s2_products.get("coverage", "unknown"),
            },
            "sentinel_1_sar": {
                "available": len(s1_products.get("products", [])) > 0,
                "image_count": len(s1_products.get("products", [])),
                "latest_image": s1_products["products"][0] if s1_products.get("products") else None,
                "all_weather": True,  # SAR works through clouds
            },
        },
        
        "capabilities": {
            "optical": SatelliteImageryAnalyzer.S2_CAPABILITIES,
            "sar": SatelliteImageryAnalyzer.S1_CAPABILITIES,
        },
        
        "security_relevant_findings": [],
        "data_gaps": [],
        "recommendations": [],
    }
    
    # Analyze what we can actually determine
    optical = analysis["satellite_availability"]["sentinel_2_optical"]
    sar = analysis["satellite_availability"]["sentinel_1_sar"]
    
    # Check for recent optical imagery
    if not optical["available"]:
        analysis["data_gaps"].append("No recent cloud-free optical imagery available")
        analysis["recommendations"].append("Use Sentinel-1 SAR (all-weather) or wait for clear skies")
    else:
        latest = optical.get("latest_image", {})
        if latest:
            acquisition = latest.get("acquisition_date", "unknown")
            cloud_cover = latest.get("cloud_cover", 100)
            
            analysis["security_relevant_findings"].append({
                "type": "optical_coverage",
                "finding": f"Most recent image from {acquisition}, cloud cover {cloud_cover}%",
                "usability": "usable" if cloud_cover < 20 else "partial" if cloud_cover < 50 else "limited",
            })
    
    # SAR is always available (all-weather)
    if sar["available"]:
        analysis["security_relevant_findings"].append({
            "type": "sar_coverage",
            "finding": f"SAR data available ({sar['image_count']} images), can detect through clouds and at night",
            "usability": "usable",
        })
    
    # Geographic context
    geo_context = get_geographic_context(lat, lon)
    if "security_assessment" in geo_context:
        analysis["geographic_context"] = geo_context["security_assessment"]
    
    return analysis


def format_satellite_analysis_for_ai(analysis: Dict) -> str:
    """
    Format satellite analysis data for the AI to use.
    Ensures AI has real data to work with, not hallucinations.
    """
    if analysis.get("status") == "error":
        return f"""SATELLITE DATA STATUS: UNAVAILABLE
Error: {analysis.get('message', 'Unknown error')}
Timestamp: {analysis.get('timestamp')}

LIMITATION: Cannot provide satellite-based assessment without imagery data.
"""
    
    lines = [
        f"SATELLITE IMAGERY ANALYSIS - {analysis['lga']} LGA",
        f"Analysis Time: {analysis['analysis_timestamp']}",
        f"LGA Center Coordinates: {analysis['coordinates']['lat']}°N, {analysis['coordinates']['lon']}°E",
        f"Period: {analysis['period_covered']}",
        "",
        "IMPORTANT: Always include exact coordinates (Lat, Lon) for every location mentioned in your analysis.",
        "Example: 'Detection at 11.423°N, 5.781°E' or 'Area near (11.415, 5.795)'",
        "",
        "AVAILABLE SATELLITE DATA:",
    ]
    
    optical = analysis["satellite_availability"]["sentinel_2_optical"]
    sar = analysis["satellite_availability"]["sentinel_1_sar"]
    
    # Optical data status
    if optical["available"]:
        latest = optical.get("latest_image", {})
        if latest:
            date = latest.get("acquisition_date", "unknown")
            cloud = latest.get("cloud_cover", "unknown")
            lines.append(f"• Sentinel-2 (Optical): {optical['image_count']} images available")
            lines.append(f"  - Latest: {date}, Cloud cover: {cloud}%")
    else:
        lines.append("• Sentinel-2 (Optical): No recent images (likely cloud cover)")
    
    # SAR data status
    if sar["available"]:
        lines.append(f"• Sentinel-1 (SAR): {sar['image_count']} images available")
        lines.append("  - All-weather capability (works through clouds)")
    else:
        lines.append("• Sentinel-1 (SAR): No recent data")
    
    # Findings
    lines.extend(["", "SATELLITE-DETECTABLE FINDINGS:"])
    
    if analysis.get("security_relevant_findings"):
        for finding in analysis["security_relevant_findings"]:
            lines.append(f"• {finding['type'].replace('_', ' ').title()}: {finding['finding']}")
    else:
        lines.append("• No specific security-relevant features detected in satellite data")
    
    # Capabilities reminder
    lines.extend([
        "",
        "CAPABILITY LIMITATIONS:",
        "• Resolution: 10m/pixel (Sentinel-2), 5-40m (Sentinel-1)",
        "• Cannot detect: Individual people, small groups (< 50), weapons",
        "• Can detect: Large fires, smoke plumes, major infrastructure, land changes",
        "",
    ])
    
    # Data gaps
    if analysis.get("data_gaps"):
        lines.append("DATA GAPS:")
        for gap in analysis["data_gaps"]:
            lines.append(f"• {gap}")
        lines.append("")
    
    # Recommendations
    if analysis.get("recommendations"):
        lines.append("RECOMMENDATIONS:")
        for rec in analysis["recommendations"]:
            lines.append(f"• {rec}")
        lines.append("")
    
    # Geographic context
    if "geographic_context" in analysis:
        geo = analysis["geographic_context"]
        lines.append("GEOGRAPHIC CONTEXT:")
        lines.append(f"• Risk Level: {geo.get('risk_level', 'unknown').upper()}")
        lines.append(f"• Border Proximity: {geo.get('proximity_to_border', 'unknown')}")
        lines.append("")
    
    return "\n".join(lines)


async def get_detailed_satellite_security_report(lga: str) -> str:
    """
    Main entry point: Get a detailed, ACCURATE satellite security report.
    This is what the AI should call when asked about satellite imagery.
    Includes orbit predictions and pass schedules.
    """
    # Fetch satellite imagery data
    analysis = await analyze_lga_for_security(lga)
    
    # Fetch orbit and pass prediction data
    orbit_data = await get_satellite_orbit_and_pass_data(lga=lga)
    
    # Format for AI
    imagery_report = format_satellite_analysis_for_ai(analysis)
    orbit_report = format_orbit_data_for_ai(orbit_data)
    
    # Combine reports
    combined = f"""{imagery_report}

{orbit_report}

INTELLIGENCE SYNTHESIS:
Use satellite orbit data to recommend optimal collection timing.
If urgent imaging needed: Recommend SAR (all-weather) or next optical pass.
If area has cloud cover: SAR is the only option until weather clears.
"""
    
    return combined


# Simple Change Detection Function (Phase 2 MVP)
def detect_changes_simple(old_image_pixels: list, new_image_pixels: list, threshold: float = 0.15) -> dict:
    """
    Simple pixel-based change detection.
    Compares two satellite images and identifies areas with significant changes.
    
    Args:
        old_image_pixels: List of pixel values from older image (e.g., NDVI values)
        new_image_pixels: List of pixel values from newer image
        threshold: Difference threshold (0.15 = 15% change)
    
    Returns:
        dict: Change detection results
    """
    if len(old_image_pixels) != len(new_image_pixels):
        return {
            "status": "error",
            "message": "Image dimensions do not match",
            "changes_detected": False
        }
    
    changed_pixels = 0
    total_pixels = len(old_image_pixels)
    max_difference = 0
    
    for old_val, new_val in zip(old_image_pixels, new_image_pixels):
        difference = abs(new_val - old_val)
        if difference > max_difference:
            max_difference = difference
        
        if difference > threshold:
            changed_pixels += 1
    
    change_percentage = (changed_pixels / total_pixels) * 100 if total_pixels > 0 else 0
    
    # Classification
    if change_percentage > 10:
        severity = "HIGH"
        description = "Significant changes detected - possible major construction or clearing"
    elif change_percentage > 5:
        severity = "MEDIUM"
        description = "Moderate changes detected - possible new structures or land modification"
    elif change_percentage > 1:
        severity = "LOW"
        description = "Minor changes detected - possible vegetation or seasonal variation"
    else:
        severity = "NONE"
        description = "No significant changes detected"
    
    return {
        "status": "success",
        "changes_detected": changed_pixels > 0,
        "severity": severity,
        "changed_pixels": changed_pixels,
        "total_pixels": total_pixels,
        "change_percentage": round(change_percentage, 2),
        "max_difference": round(max_difference, 3),
        "threshold_used": threshold,
        "description": description,
        "recommendation": "Ground verification recommended" if severity in ["HIGH", "MEDIUM"] else "Continue monitoring"
    }


# Specific security indicators that CAN be detected
detectable_security_indicators = {
    "large_fires": {
        "description": "Thermal anomalies > 30m (possible arson, burning evidence)",
        "data_source": "NASA FIRMS",
        "confidence": "high",
    },
    "smoke_plumes": {
        "description": "Smoke from burning > 100m visible",
        "data_source": "Sentinel-2 (if clear sky)",
        "confidence": "medium-high",
    },
    "road_blocks": {
        "description": "Major road obstructions (fallen trees, vehicles)",
        "data_source": "Sentinel-2 or Sentinel-1",
        "confidence": "medium",
    },
    "camps_settlements": {
        "description": "Large temporary settlements (> 50 structures)",
        "data_source": "Sentinel-2 (cleared areas, buildings)",
        "confidence": "medium",
    },
    "vehicle_convoys": {
        "description": "Large vehicle concentrations on roads (> 10 vehicles)",
        "data_source": "Sentinel-1 (SAR detects vehicles)",
        "confidence": "medium",
    },
    "land_clearing": {
        "description": "Recent clearing of vegetation (ambush sites, camps)",
        "data_source": "Sentinel-2 (change detection)",
        "confidence": "medium",
    },
    "flooding": {
        "description": "Water coverage of normally dry areas",
        "data_source": "Sentinel-1 (SAR) or Sentinel-2",
        "confidence": "high",
    },
}


async def get_satellite_orbit_and_pass_data(lga: str = None, lat: float = None, lon: float = None) -> Dict[str, Any]:
    """
    Get current satellite positions and upcoming passes over a location.
    Provides orbital intelligence for AI analysis.
    """
    from services.n2yo import get_all_tracked_positions, get_visual_passes, TRACKED_SATELLITES
    from services.geography import MAJOR_TOWNS
    from datetime import datetime, timedelta
    
    # Get coordinates
    if not (lat and lon):
        if lga:
            town = MAJOR_TOWNS.get(lga.lower().replace(" ", "_"))
            if town:
                lat, lon = town.lat, town.lon
            else:
                lat, lon = 12.45, 4.20  # Default Kebbi center
        else:
            lat, lon = 12.45, 4.20
    
    result = {
        "location": {"lga": lga, "lat": lat, "lon": lon},
        "timestamp": datetime.now().isoformat(),
        "satellite_positions": [],
        "upcoming_passes": [],
        "coverage_gaps": [],
        "recommendations": []
    }
    
    # Get current positions of all tracked satellites
    try:
        positions = await get_all_tracked_positions()
        
        for sat in positions.get("tracked_satellites", []):
            pos = sat.get("position", {})
            if pos:
                result["satellite_positions"].append({
                    "name": sat["name"],
                    "norad_id": sat["norad_id"],
                    "current_lat": pos.get("latitude"),
                    "current_lon": pos.get("longitude"),
                    "altitude_km": pos.get("altitude_km"),
                    "distance_to_target_km": _calculate_distance(
                        pos.get("latitude", 0), pos.get("longitude", 0), lat, lon
                    ) if pos.get("latitude") else None
                })
    except Exception:
        pass  # Continue without position data
    
    # Get upcoming passes for key satellites
    key_satellites = {
        40069: "Sentinel-2A (Optical)",
        42063: "Sentinel-2B (Optical)",
        39634: "Sentinel-1A (SAR)",
        41456: "Sentinel-1B (SAR)",
        49260: "Landsat 9 (Optical/Thermal)",
        39084: "Landsat 8 (Optical/Thermal)",
        33591: "NOAA-19 (Weather/Fire)",
        43013: "NOAA-20 (Fire monitoring)",
    }
    
    for norad_id, sat_name in key_satellites.items():
        try:
            passes = await get_visual_passes(norad_id, days=3, min_visibility=30)
            
            if passes.get("passes"):
                next_pass = passes["passes"][0]
                pass_time = datetime.utcfromtimestamp(next_pass["start_utc"])
                hours_until = (pass_time - datetime.utcnow()).total_seconds() / 3600
                
                result["upcoming_passes"].append({
                    "satellite": sat_name,
                    "norad_id": norad_id,
                    "next_pass_utc": pass_time.isoformat(),
                    "hours_until": round(hours_until, 1),
                    "max_elevation": next_pass["max_elevation"],
                    "duration_seconds": next_pass["duration_seconds"],
                    "imaging_quality": "good" if next_pass["max_elevation"] > 40 else "fair",
                })
        except Exception:
            continue
    
    # Sort passes by time
    result["upcoming_passes"].sort(key=lambda x: x["hours_until"])
    
    # Analyze coverage gaps
    optical_passes = [p for p in result["upcoming_passes"] if "Optical" in p["satellite"]]
    sar_passes = [p for p in result["upcoming_passes"] if "SAR" in p["satellite"]]
    
    if not optical_passes or optical_passes[0]["hours_until"] > 24:
        result["coverage_gaps"].append("No optical satellite coverage for >24 hours")
        result["recommendations"].append("Use SAR (all-weather) for immediate needs")
    
    if not sar_passes or sar_passes[0]["hours_until"] > 48:
        result["coverage_gaps"].append("Limited SAR coverage in next 48 hours")
    
    # Add collection recommendations
    if result["upcoming_passes"]:
        next_optical = next((p for p in result["upcoming_passes"] if "Optical" in p["satellite"]), None)
        next_sar = next((p for p in result["upcoming_passes"] if "SAR" in p["satellite"]), None)
        
        if next_optical:
            result["recommendations"].append(
                f"Optimal optical collection: {next_optical['satellite']} in {next_optical['hours_until']} hours"
            )
        if next_sar:
            result["recommendations"].append(
                f"SAR collection available: {next_sar['satellite']} in {next_sar['hours_until']} hours (all-weather)"
            )
    
    return result


def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in km."""
    import math
    R = 6371  # Earth's radius in km
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return round(R * c, 1)


def format_orbit_data_for_ai(orbit_data: Dict) -> str:
    """Format satellite orbit and pass data for AI consumption."""
    if not orbit_data or not orbit_data.get("upcoming_passes"):
        return """SATELLITE ORBIT STATUS: Data unavailable
Current satellite positions and pass predictions could not be retrieved.
"""
    
    lines = [
        "SATELLITE ORBIT INTELLIGENCE",
        f"Target Location: {orbit_data['location'].get('lga', 'Unknown')}",
        f"Target Coordinates: {orbit_data['location']['lat']}°N, {orbit_data['location']['lon']}°E",
        f"Report Time: {orbit_data['timestamp']}",
        "",
        "NOTE: When providing analysis, always reference exact coordinates for all locations mentioned.",
        "",
        "UPCOMING SATELLITE PASSES:",
    ]
    
    # Group by type
    optical = [p for p in orbit_data["upcoming_passes"] if "Optical" in p["satellite"]]
    sar = [p for p in orbit_data["upcoming_passes"] if "SAR" in p["satellite"]]
    other = [p for p in orbit_data["upcoming_passes"] if p not in optical and p not in sar]
    
    if optical:
        lines.append("  OPTICAL (High-resolution imagery, weather dependent):")
        for p in optical[:3]:
            lines.append(f"    • {p['satellite']}: {p['hours_until']} hours ({p['imaging_quality']} quality)")
    
    if sar:
        lines.append("  SAR (All-weather, day/night capable):")
        for p in sar[:2]:
            lines.append(f"    • {p['satellite']}: {p['hours_until']} hours (all-weather)")
    
    if other:
        lines.append("  THERMAL/FIRE MONITORING:")
        for p in other[:2]:
            lines.append(f"    • {p['satellite']}: {p['hours_until']} hours")
    
    lines.append("")
    
    # Coverage gaps
    if orbit_data.get("coverage_gaps"):
        lines.append("COVERAGE GAPS:")
        for gap in orbit_data["coverage_gaps"]:
            lines.append(f"  ⚠ {gap}")
        lines.append("")
    
    # Recommendations
    if orbit_data.get("recommendations"):
        lines.append("COLLECTION RECOMMENDATIONS:")
        for rec in orbit_data["recommendations"]:
            lines.append(f"  → {rec}")
        lines.append("")
    
    # Current positions (if available)
    if orbit_data.get("satellite_positions"):
        nearby = [s for s in orbit_data["satellite_positions"] 
                  if s.get("distance_to_target_km") and s["distance_to_target_km"] < 500]
        if nearby:
            nearby.sort(key=lambda x: x["distance_to_target_km"])
            lines.append("SATELLITES CURRENTLY NEAR TARGET:")
            for sat in nearby[:3]:
                lines.append(f"  • {sat['name']}: {sat['distance_to_target_km']} km away")
            lines.append("")
    
    return "\n".join(lines)

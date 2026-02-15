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
        f"Coordinates: {analysis['coordinates']['lat']}°N, {analysis['coordinates']['lon']}°E",
        f"Period: {analysis['period_covered']}",
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
    """
    # Fetch real data
    analysis = await analyze_lga_for_security(lga)
    
    # Format for AI
    formatted_data = format_satellite_analysis_for_ai(analysis)
    
    return formatted_data


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

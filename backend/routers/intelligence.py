"""
COMPREHENSIVE INTELLIGENCE ROUTER
Multi-source security analysis and threat detection
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/intel", tags=["Intelligence"])


@router.get("/comprehensive/{lga}")
async def comprehensive_security_report(
    lga: str,
    days: int = Query(7, description="Number of days to analyze"),
    include_mining: bool = Query(True, description="Include illegal mining analysis"),
    include_border: bool = Query(True, description="Include border activity analysis"),
    include_fires: bool = Query(True, description="Include fire/thermal analysis"),
):
    """
    Get comprehensive security intelligence report for an LGA.
    
    Integrates:
    - NASA FIRMS (fire/thermal anomalies)
    - Sentinel satellites (change detection)
    - OSINT feeds (news/reports)
    - Multi-source correlation
    
    Detects:
    - Illegal mining operations
    - Bandit camps/activity
    - Border crossing patterns
    - Arson/evidence burning
    - Human trafficking indicators
    - Drug trafficking routes
    """
    from services.security_intelligence_engine import ComprehensiveSecurityReport, format_security_report_for_ai
    
    try:
        # Generate comprehensive report
        report = await ComprehensiveSecurityReport.generate_full_report(lga, days)
        
        # Format for API response
        formatted = format_security_report_for_ai(report)
        
        return {
            "status": "success",
            "lga": lga,
            "timestamp": datetime.utcnow().isoformat(),
            "report": report,
            "formatted_analysis": formatted,
            "data_sources": [
                "NASA FIRMS (fire/thermal)",
                "Copernicus Sentinel-2 (optical)",
                "Copernicus Sentinel-1 (SAR)",
                "Multi-source OSINT",
            ],
            "detection_capabilities": {
                "illegal_mining": "Thermal signatures of kilns, land clearing detection",
                "bandit_camps": "Cooking fire detection in remote areas",
                "border_activity": "SAR movement detection, path analysis",
                "arson": "High-intensity fire detection",
                "human_trafficking": "Large gathering detection (50+ people)",
                "drug_trafficking": "Unusual agricultural patterns, airstrip detection",
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "lga": lga,
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/fires/security-analysis")
async def analyze_fires_for_security(
    lga: Optional[str] = None,
    days: int = Query(2, description="Days to analyze"),
):
    """
    Analyze NASA FIRMS fire data specifically for security threats.
    
    Classifies fires as:
    - Illegal mining (artisanal kilns)
    - Arson/evidence burning
    - Bandit camps (cooking fires)
    - Bush refining
    """
    from services.firms import fetch_all_sensors
    from services.security_intelligence_engine import FIRMSecurityAnalyzer
    
    # Fetch fire data
    fire_data = await fetch_all_sensors(days=days)
    hotspots = fire_data.get("hotspots", [])
    
    # Filter to LGA if specified
    if lga:
        from services.geography import MAJOR_TOWNS, haversine_distance
        town = MAJOR_TOWNS.get(lga.lower().replace(" ", "_"))
        if town:
            # Filter to fires within 50km of LGA center
            hotspots = [
                h for h in hotspots 
                if haversine_distance(
                    h.get("latitude"), h.get("longitude"),
                    town.lat, town.lon
                ) <= 50
            ]
    
    # Analyze for security indicators
    analyzer = FIRMSecurityAnalyzer()
    indicators = analyzer.analyze_fires_for_security(hotspots, lga)
    
    return {
        "status": "success",
        "lga": lga or "All LGAs",
        "period": f"Last {days} days",
        "total_fires": len(hotspots),
        "security_indicators": [
            {
                "type": i.indicator_type,
                "source": i.source,
                "location": i.location,
                "confidence": i.confidence,
                "severity": i.severity,
                "description": i.description,
                "recommended_action": i.recommended_action,
            }
            for i in indicators
        ],
        "summary": {
            "mining_suspected": len([i for i in indicators if "mining" in i.indicator_type]),
            "arson_suspected": len([i for i in indicators if "arson" in i.indicator_type]),
            "bandit_camps_suspected": len([i for i in indicators if "bandit" in i.indicator_type]),
            "total_threats": len(indicators),
        }
    }


@router.get("/mining/detection")
async def detect_illegal_mining(
    lga: Optional[str] = None,
    include_sentinel: bool = Query(True, description="Include satellite imagery analysis"),
):
    """
    Specialized endpoint for illegal mining detection.
    
    Uses:
    - Fire detection (kilns/furnaces)
    - Land clearing detection
    - River pollution indicators
    - Historical mining site monitoring
    """
    from services.security_intelligence_engine import SatelliteActivityDetector
    
    detector = SatelliteActivityDetector()
    
    # This would include actual image analysis in production
    indicators = detector.analyze_for_illegal_mining([], lga)
    
    # Also get fire-based mining indicators
    from services.firms import fetch_all_sensors
    from services.security_intelligence_engine import FIRMSecurityAnalyzer
    
    fire_data = await fetch_all_sensors(days=7)
    fire_analyzer = FIRMSecurityAnalyzer()
    fire_indicators = fire_analyzer.analyze_fires_for_security(
        fire_data.get("hotspots", []), lga
    )
    mining_fires = [i for i in fire_indicators if "mining" in i.indicator_type]
    
    return {
        "status": "success",
        "lga": lga or "All LGAs",
        "detection_methods": [
            "Thermal anomalies (mining kilns)",
            "Land use change detection",
            "Water quality indicators",
            "Unauthorized infrastructure",
        ],
        "indicators": {
            "fire_based": len(mining_fires),
            "imagery_based": len(indicators),
        },
        "findings": [
            {
                "type": i.indicator_type,
                "description": i.description,
                "severity": i.severity,
                "confidence": i.confidence,
            }
            for i in mining_fires + indicators
        ],
        "recommendations": [
            "Deploy mining enforcement to suspected locations",
            "Verify with ground reconnaissance",
            "Check for unauthorized mining equipment",
            "Monitor water sources for pollution",
        ]
    }


@router.get("/border/activity")
async def monitor_border_activity(
    border_zone: str = Query(..., description="Border zone: niger_republic, benin, zamfara, sokoto"),
    days: int = Query(7, description="Days to analyze"),
):
    """
    Monitor border crossing activity using Sentinel-1 SAR.
    
    SAR capabilities:
    - Detects vehicle movement day/night
    - Works through clouds
    - Detects track formation
    - Monitors unofficial crossing points
    """
    from services.security_intelligence_engine import SatelliteActivityDetector
    
    detector = SatelliteActivityDetector()
    indicators = detector.analyze_border_activity(border_zone, [])
    
    border_info = {
        "niger_republic": {
            "name": "Niger Republic Border",
            "lgas": ["Kamba", "Bagudo", "Dandi", "Maiyama"],
            "length_km": 250,
            "risk_level": "high",
        },
        "benin": {
            "name": "Benin Republic Border",
            "lgas": ["Bagudo", "Augie"],
            "length_km": 80,
            "risk_level": "medium",
        },
        "zamfara": {
            "name": "Zamfara State Border",
            "lgas": ["Wasagu", "Sakaba", "Fakai", "Zuru"],
            "length_km": 180,
            "risk_level": "critical",
        },
        "sokoto": {
            "name": "Sokoto State Border",
            "lgas": ["Gwandu", "Argungu", "Augie"],
            "length_km": 150,
            "risk_level": "medium",
        },
    }
    
    info = border_info.get(border_zone, {})
    
    return {
        "status": "success",
        "border_zone": border_zone,
        "border_name": info.get("name"),
        "monitoring_capabilities": {
            "sentinel_1_sar": "Day/night vehicle detection",
            "track_detection": "New path formation",
            "change_detection": "New structures/camps",
            "all_weather": "Works through clouds",
        },
        "affected_lgas": info.get("lgas", []),
        "risk_level": info.get("risk_level"),
        "indicators": [
            {
                "type": i.indicator_type,
                "description": i.description,
            }
            for i in indicators
        ],
        "recommendations": [
            "Increase patrol frequency on detected routes",
            "Deploy thermal imaging for night detection",
            "Establish checkpoints on unofficial crossing points",
            "Coordinate with neighboring state security",
        ]
    }

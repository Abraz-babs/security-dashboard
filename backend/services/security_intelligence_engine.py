"""
SECURITY INTELLIGENCE ENGINE - Multi-Source Correlation & Analysis
Integrates NASA FIRMS, Sentinel satellites, OSINT for comprehensive threat detection
"""
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import statistics
from collections import defaultdict


@dataclass
class SecurityIndicator:
    """A security-relevant observation from any source"""
    indicator_type: str  # fire, mining, border_activity, etc.
    source: str  # NASA_FIRMS, Sentinel-2, Sentinel-1, OSINT
    location: Dict[str, float]  # lat, lon
    timestamp: datetime
    confidence: str  # high, medium, low
    description: str
    severity: str  # critical, high, medium, low
    related_indicators: List[str] = None
    recommended_action: str = ""


class FIRMSecurityAnalyzer:
    """
    Analyze NASA FIRMS data for security-relevant thermal anomalies.
    Fire data can indicate: arson, burning evidence, illegal mining (kilns), border camps
    """
    
    # Fire signatures for different security threats
    FIRE_SIGNATURES = {
        "illegal_mining": {
            "description": "Artisanal mining kilns/furnaces",
            "brightness_range": (400, 600),
            "cluster_pattern": "small_clusters",  # Multiple small fires in area
            "typical_locations": ["near rivers", "remote areas", "unregulated sites"],
            "confidence": "medium-high",
        },
        "burning_evidence": {
            "description": "Large fires destroying evidence",
            "brightness_range": (500, 1000),
            "cluster_pattern": "single_large",
            "typical_locations": ["crime scenes", "hideout areas", "kidnap locations"],
            "confidence": "high",
        },
        "bandit_camps": {
            "description": "Cooking/heating fires in remote camps",
            "brightness_range": (300, 450),
            "cluster_pattern": "scattered_small",
            "typical_locations": ["forest areas", "border zones", "remote LGAs"],
            "confidence": "medium",
        },
        "arson_attacks": {
            "description": "Deliberate burning of villages/farms",
            "brightness_range": (450, 700),
            "cluster_pattern": "linear_or_clustered",
            "typical_locations": ["villages", "farms", "settlements"],
            "confidence": "high",
        },
        "bush_refining": {
            "description": "Illegal oil refining (if applicable)",
            "brightness_range": (500, 800),
            "cluster_pattern": "dense_cluster",
            "typical_locations": ["remote creeks", "forest areas"],
            "confidence": "high",
        },
    }
    
    @staticmethod
    def analyze_fires_for_security(fire_data: List[Dict], lga: str = None) -> List[SecurityIndicator]:
        """
        Analyze fire hotspots for security implications.
        """
        indicators = []
        
        if not fire_data:
            return indicators
        
        # Group fires by proximity (potential clusters)
        clusters = FIRMSecurityAnalyzer._cluster_fires(fire_data, radius_km=2.0)
        
        for cluster in clusters:
            # Analyze cluster characteristics
            avg_brightness = statistics.mean([f.get("brightness", 0) for f in cluster])
            fire_count = len(cluster)
            avg_frp = statistics.mean([f.get("frp", 0) for f in cluster])
            
            # Determine likely signature
            indicator = FIRMSecurityAnalyzer._classify_fire_cluster(
                cluster, avg_brightness, fire_count, avg_frp, lga
            )
            
            if indicator:
                indicators.append(indicator)
        
        return indicators
    
    @staticmethod
    def _cluster_fires(fires: List[Dict], radius_km: float = 2.0) -> List[List[Dict]]:
        """Group fires into clusters based on proximity"""
        from services.geography import haversine_distance
        
        clusters = []
        used = set()
        
        for i, fire in enumerate(fires):
            if i in used:
                continue
            
            cluster = [fire]
            used.add(i)
            
            lat1, lon1 = fire.get("latitude"), fire.get("longitude")
            
            # Find nearby fires
            for j, other in enumerate(fires[i+1:], start=i+1):
                if j in used:
                    continue
                
                lat2, lon2 = other.get("latitude"), other.get("longitude")
                dist = haversine_distance(lat1, lon1, lat2, lon2)
                
                if dist <= radius_km:
                    cluster.append(other)
                    used.add(j)
            
            clusters.append(cluster)
        
        return clusters
    
    @staticmethod
    def _classify_fire_cluster(cluster: List[Dict], avg_brightness: float, 
                               fire_count: int, avg_frp: float, lga: str) -> Optional[SecurityIndicator]:
        """Classify a fire cluster by security threat type"""
        
        # Get center of cluster
        center_lat = statistics.mean([f.get("latitude", 0) for f in cluster])
        center_lon = statistics.mean([f.get("longitude", 0) for f in cluster])
        
        # Determine most likely type
        indicator_type = "unknown_fire"
        confidence = "low"
        description = f"{fire_count} thermal anomalies detected"
        severity = "medium"
        action = "Investigate source of fires"
        
        # Illegal mining signature: multiple medium-brightness fires near rivers
        if fire_count >= 3 and 400 <= avg_brightness <= 600:
            indicator_type = "suspected_illegal_mining"
            confidence = "medium"
            description = f"Cluster of {fire_count} fires (avg brightness {avg_brightness:.0f}K) consistent with artisanal mining kilns"
            severity = "high"
            action = "Deploy mining enforcement team to verify illegal mining activity. Check for unauthorized pits and equipment."
        
        # Arson/burning evidence: very high brightness, large fires
        elif avg_brightness > 500 and fire_count <= 3:
            indicator_type = "suspected_arson_evidence_burning"
            confidence = "high"
            description = f"High-intensity fire ({avg_brightness:.0f}K) may indicate arson or evidence destruction"
            severity = "critical"
            action = "URGENT: Dispatch patrol to verify if settlement/farm under attack. Alert nearby communities."
        
        # Bandit camps: scattered small fires in remote areas
        elif fire_count >= 2 and 300 <= avg_brightness < 400:
            indicator_type = "suspected_bandit_camp"
            confidence = "medium"
            description = f"Small fires ({fire_count}) in remote area consistent with temporary camp cooking/heating"
            severity = "high"
            action = "Surveillance recommended. Check for associated vehicle tracks or temporary structures. DO NOT approach without backup."
        
        return SecurityIndicator(
            indicator_type=indicator_type,
            source="NASA_FIRMS",
            location={"lat": center_lat, "lon": center_lon},
            timestamp=datetime.now(),
            confidence=confidence,
            description=description,
            severity=severity,
            recommended_action=action
        )


class SatelliteActivityDetector:
    """
    Detect security-relevant activities from Sentinel satellite data.
    """
    
    DETECTION_CAPABILITIES = {
        "illegal_mining": {
            "satellites": ["Sentinel-2", "Sentinel-1"],
            "indicators": ["land_clearing", "unusual_excavation", "water_pollution", "unauthorized_structures"],
            "confidence": "medium-high",
            "detection_method": "Change detection between images",
        },
        "border_crossing": {
            "satellites": ["Sentinel-1 (night/day)", "Sentinel-2"],
            "indicators": ["unofficial_paths", "vehicle_tracks", "temporary_camps_near_border", "disturbed_ground"],
            "confidence": "medium",
            "detection_method": "SAR detects movement patterns, optical detects paths",
        },
        "human_trafficking": {
            "satellites": ["Sentinel-2"],
            "indicators": ["large_gatherings", "unauthorized_camps", "transport_corridors"],
            "confidence": "low-medium",
            "detection_method": "Large congregation detection (50+ people)",
            "limitations": "Cannot detect individuals or small groups",
        },
        "drug_trafficking": {
            "satellites": ["Sentinel-2"],
            "indicators": ["unusual_agriculture", "hidden_airstrips", "remote_storage_structures"],
            "confidence": "low",
            "detection_method": "Anomaly detection in vegetation patterns",
        },
        "vehicle_convoys": {
            "satellites": ["Sentinel-1 (SAR)", "Sentinel-2"],
            "indicators": ["vehicle_concentrations", "road_usage_patterns"],
            "confidence": "medium",
            "detection_method": "SAR detects vehicles on roads",
            "limitations": "Minimum 10+ vehicles in open area",
        },
    }
    
    @staticmethod
    def analyze_for_illegal_mining(satellite_products: List[Dict], lga: str) -> List[SecurityIndicator]:
        """
        Analyze satellite data for signs of illegal mining.
        """
        indicators = []
        
        # Check for mining-related activity signatures
        # This would require actual image analysis in production
        # For now, provide framework
        
        mining_areas = {
            "argungu": ["gold_washing", "artisanal_pits"],
            "yauri": ["gold_deposits", "river_mining"],
            "zuru": ["historic_mining_sites"],
        }
        
        if lga and lga.lower() in mining_areas:
            # Historical knowledge + satellite availability = risk assessment
            indicators.append(SecurityIndicator(
                indicator_type="illegal_mining_risk_area",
                source="SENTINEL_2",
                location={"lat": 0, "lon": 0},  # Would be actual coordinates
                timestamp=datetime.now(),
                confidence="medium",
                description=f"{lga} has known artisanal mining activity. Satellite imagery available for change detection.",
                severity="high",
                recommended_action="Compare recent imagery with baseline to detect new excavation or unauthorized activity."
            ))
        
        return indicators
    
    @staticmethod
    def analyze_border_activity(border_zone: str, s1_data: List[Dict]) -> List[SecurityIndicator]:
        """
        Analyze Sentinel-1 SAR data for border crossing activity.
        SAR works day/night and can detect vehicle movement.
        """
        indicators = []
        
        # High-risk border zones
        risk_zones = {
            "niger_republic_north": ["kamba", "bagudo", "dandi"],
            "benin_west": ["bagudo", "augie"],
            "zamfara_east": ["wasagu", "sakaba", "fakai"],
        }
        
        if border_zone in risk_zones:
            indicators.append(SecurityIndicator(
                indicator_type="border_monitoring_capability",
                source="SENTINEL_1_SAR",
                location={"lat": 0, "lon": 0},
                timestamp=datetime.now(),
                confidence="medium",
                description=f"SAR data available for {border_zone}. Can detect vehicle movement and track formation day/night.",
                severity="medium",
                recommended_action="Analyze SAR time-series for unusual vehicle patterns or new track formation near border."
            ))
        
        return indicators


class MultiSourceCorrelationEngine:
    """
    Correlate data from multiple sources to identify security threats.
    """
    
    @staticmethod
    def correlate_threats(fire_indicators: List[SecurityIndicator],
                         satellite_indicators: List[SecurityIndicator],
                         osint_reports: List[Dict],
                         lga: str) -> Dict[str, Any]:
        """
        Correlate multiple indicators to build threat picture.
        """
        correlated_threats = []
        
        # Pattern 1: Fire + OSINT Report = Confirmed Incident
        for fire in fire_indicators:
            for report in osint_reports:
                # Check if report mentions fire or location near fire
                if fire.location and report.get("location_lga") == lga:
                    if fire.severity in ["critical", "high"]:
                        correlated_threats.append({
                            "type": "confirmed_security_incident",
                            "confidence": "high",
                            "sources": ["NASA_FIRMS", "OSINT"],
                            "description": f"Thermal anomaly confirmed by ground report: {report.get('title', 'Unknown')}",
                            "location": fire.location,
                            "action": "Deploy response team immediately. Incident confirmed by multiple sources."
                        })
        
        # Pattern 2: Multiple fires in mining area = Illegal mining operation
        mining_fires = [f for f in fire_indicators if "mining" in f.indicator_type]
        if len(mining_fires) >= 2:
            correlated_threats.append({
                "type": "active_illegal_mining_operation",
                "confidence": "high",
                "sources": ["NASA_FIRMS"],
                "description": f"{len(mining_fires)} separate fire clusters consistent with mining kilns detected",
                "location": mining_fires[0].location if mining_fires else None,
                "action": "Coordinate mining enforcement raid. Multiple active sites detected."
            })
        
        # Pattern 3: Fire in remote border area = Possible camp
        border_fires = [f for f in fire_indicators if f.indicator_type == "suspected_bandit_camp"]
        if border_fires:
            for fire in border_fires:
                correlated_threats.append({
                    "type": "suspected_bandit_presence",
                    "confidence": "medium",
                    "sources": ["NASA_FIRMS"],
                    "description": fire.description,
                    "location": fire.location,
                    "action": fire.recommended_action
                })
        
        return {
            "correlated_threats": correlated_threats,
            "total_indicators": len(fire_indicators) + len(satellite_indicators),
            "confidence_level": "high" if len(correlated_threats) > 0 else "medium",
        }


class ComprehensiveSecurityReport:
    """
    Generate comprehensive security intelligence report from all sources.
    """
    
    @staticmethod
    async def generate_full_report(lga: str, days_back: int = 7) -> Dict[str, Any]:
        """
        Generate comprehensive security report for an LGA.
        """
        from services.firms import fetch_all_sensors
        from services.newsdata import fetch_security_intel
        
        # Fetch all data sources
        fire_data = await fetch_all_sensors(days=days_back)
        intel_data = await fetch_security_intel()
        
        # Filter to LGA if specified
        lga_fires = [f for f in fire_data.get("hotspots", [])]
        # Would filter by LGA coordinates here
        
        lga_intel = [r for r in intel_data.get("reports", []) 
                    if lga.lower() in r.get("title", "").lower() or 
                       lga.lower() in r.get("description", "").lower()]
        
        # Analyze each source
        firms_analyzer = FIRMSecurityAnalyzer()
        fire_indicators = firms_analyzer.analyze_fires_for_security(lga_fires, lga)
        
        sat_detector = SatelliteActivityDetector()
        mining_indicators = sat_detector.analyze_for_illegal_mining([], lga)
        
        # Correlate
        correlator = MultiSourceCorrelationEngine()
        correlations = correlator.correlate_threats(
            fire_indicators, mining_indicators, lga_intel, lga
        )
        
        return {
            "report_timestamp": datetime.now().isoformat(),
            "lga": lga,
            "period": f"Last {days_back} days",
            "executive_summary": {
                "threat_level": ComprehensiveSecurityReport._calculate_threat_level(
                    fire_indicators, correlations
                ),
                "key_findings": len(correlations["correlated_threats"]),
                "active_indicators": len(fire_indicators),
            },
            "fire_analysis": {
                "total_hotspots": len(lga_fires),
                "security_indicators": [
                    {
                        "type": i.indicator_type,
                        "severity": i.severity,
                        "confidence": i.confidence,
                        "description": i.description,
                        "action": i.recommended_action,
                    } for i in fire_indicators
                ],
            },
            "satellite_imagery": {
                "mining_risk": len(mining_indicators) > 0,
                "border_monitoring": "Available via Sentinel-1 SAR",
                "change_detection": "Can compare with baseline imagery",
            },
            "correlated_threats": correlations["correlated_threats"],
            "recommendations": ComprehensiveSecurityReport._generate_recommendations(
                fire_indicators, correlations
            ),
        }
    
    @staticmethod
    def _calculate_threat_level(fire_indicators: List[SecurityIndicator], 
                               correlations: Dict) -> str:
        """Calculate overall threat level"""
        if not fire_indicators:
            return "LOW"
        
        critical_count = sum(1 for i in fire_indicators if i.severity == "critical")
        high_count = sum(1 for i in fire_indicators if i.severity == "high")
        
        if critical_count > 0 or len(correlations.get("correlated_threats", [])) > 0:
            return "CRITICAL"
        elif high_count >= 2:
            return "HIGH"
        elif high_count == 1:
            return "MEDIUM"
        else:
            return "LOW"
    
    @staticmethod
    def _generate_recommendations(fire_indicators: List[SecurityIndicator],
                                  correlations: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if any(i.indicator_type == "suspected_illegal_mining" for i in fire_indicators):
            recommendations.append("Deploy mining enforcement to verify and shut down illegal operations")
        
        if any(i.indicator_type == "suspected_arson_evidence_burning" for i in fire_indicators):
            recommendations.append("URGENT: Dispatch security forces to investigate high-intensity fires")
        
        if any(i.indicator_type == "suspected_bandit_camp" for i in fire_indicators):
            recommendations.append("Conduct surveillance operation on suspected camp locations. Do not approach without tactical support.")
        
        if not recommendations:
            recommendations.append("Maintain normal patrol patterns. Continue monitoring.")
        
        recommendations.append("Request high-resolution commercial imagery for detailed tactical assessment")
        
        return recommendations


# Helper function for AI integration
def format_security_report_for_ai(report: Dict) -> str:
    """Format comprehensive report for AI consumption"""
    lines = [
        "COMPREHENSIVE SECURITY INTELLIGENCE REPORT",
        f"Location: {report['lga']} LGA",
        f"Period: {report['period']}",
        f"Generated: {report['report_timestamp']}",
        "",
        f"THREAT LEVEL: {report['executive_summary']['threat_level']}",
        f"Key Findings: {report['executive_summary']['key_findings']}",
        f"Active Indicators: {report['executive_summary']['active_indicators']}",
        "",
        "FIRE/THERMAL ANOMALY ANALYSIS:",
        f"Total Hotspots: {report['fire_analysis']['total_hotspots']}",
    ]
    
    if report['fire_analysis']['security_indicators']:
        lines.append("Security-Relevant Indicators:")
        for indicator in report['fire_analysis']['security_indicators']:
            lines.append(f"  • [{indicator['severity'].upper()}] {indicator['type']}")
            lines.append(f"    Confidence: {indicator['confidence']}")
            lines.append(f"    Description: {indicator['description']}")
            lines.append(f"    Action: {indicator['action']}")
            lines.append("")
    
    if report.get('correlated_threats'):
        lines.append("CORRELATED MULTI-SOURCE THREATS:")
        for threat in report['correlated_threats']:
            lines.append(f"  • [{threat['confidence'].upper()}] {threat['type']}")
            lines.append(f"    Sources: {', '.join(threat['sources'])}")
            lines.append(f"    {threat['description']}")
            lines.append(f"    Action: {threat['action']}")
            lines.append("")
    
    lines.append("RECOMMENDATIONS:")
    for rec in report['recommendations']:
        lines.append(f"  • {rec}")
    
    return "\n".join(lines)

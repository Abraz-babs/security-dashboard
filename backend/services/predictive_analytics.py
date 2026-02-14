"""Predictive Analytics - Machine Learning for Threat Forecasting
Uses historical data to predict future security incidents
"""
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


class ThreatPredictor:
    """Predictive model for security threats in Kebbi State"""
    
    def __init__(self):
        self.historical_data = []
        self.pattern_weights = {
            "temporal": 0.3,      # Time-based patterns
            "spatial": 0.3,       # Location-based patterns  
            "weather": 0.15,      # Weather correlation
            "seasonal": 0.25,     # Seasonal patterns
        }
    
    def analyze_temporal_patterns(self, incidents: List[Dict]) -> Dict:
        """Analyze time-based attack patterns"""
        hour_counts = defaultdict(int)
        day_counts = defaultdict(int)
        month_counts = defaultdict(int)
        
        for incident in incidents:
            ts = incident.get("timestamp", datetime.now())
            if isinstance(ts, str):
                ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
            
            hour_counts[ts.hour] += 1
            day_counts[ts.weekday()] += 1  # 0=Monday
            month_counts[ts.month] += 1
        
        # Find high-risk periods
        risky_hours = [h for h, c in hour_counts.items() if c > np.mean(list(hour_counts.values())) + np.std(list(hour_counts.values()))]
        risky_days = [d for d, c in day_counts.items() if c > np.mean(list(day_counts.values())) + np.std(list(day_counts.values()))]
        
        return {
            "risky_hours": risky_hours,
            "risky_days": risky_days,  # 0=Monday, 6=Sunday
            "hour_distribution": dict(hour_counts),
            "peak_hour": max(hour_counts, key=hour_counts.get) if hour_counts else 0,
        }
    
    def analyze_spatial_patterns(self, incidents: List[Dict]) -> Dict:
        """Analyze location-based patterns"""
        lga_counts = defaultdict(int)
        hotspot_clusters = []
        
        for incident in incidents:
            lga = incident.get("lga", "Unknown")
            lat = incident.get("lat")
            lon = incident.get("lon")
            
            lga_counts[lga] += 1
            
            if lat and lon:
                hotspot_clusters.append({"lat": lat, "lon": lon, "weight": 1})
        
        # Identify high-risk LGAs
        high_risk_lgas = sorted(lga_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "high_risk_lgas": [lga for lga, _ in high_risk_lgas],
            "lga_threat_levels": dict(lga_counts),
            "hotspot_clusters": hotspot_clusters,
        }
    
    def calculate_threat_score(self, lga: str, current_hour: int, incidents: List[Dict]) -> float:
        """Calculate real-time threat score (0-100)"""
        temporal = self.analyze_temporal_patterns(incidents)
        spatial = self.analyze_spatial_patterns(incidents)
        
        score = 0.0
        
        # Temporal risk
        if current_hour in temporal.get("risky_hours", []):
            score += 30
        
        # Spatial risk
        if lga in spatial.get("high_risk_lgas", []):
            lga_rank = spatial["high_risk_lgas"].index(lga)
            score += 40 - (lga_rank * 5)  # Top LGA = 40 points
        
        # Recent incident correlation (last 7 days)
        recent_count = sum(1 for i in incidents 
                          if i.get("lga") == lga and 
                          (datetime.now() - i.get("timestamp", datetime.now())).days <= 7)
        score += min(recent_count * 5, 30)  # Max 30 points
        
        return min(score, 100)
    
    def predict_next_24h(self, incidents: List[Dict]) -> List[Dict]:
        """Generate 24-hour threat forecast"""
        predictions = []
        current_time = datetime.now()
        
        temporal = self.analyze_temporal_patterns(incidents)
        spatial = self.analyze_spatial_patterns(incidents)
        
        # Generate hourly predictions for next 24 hours
        for hour_offset in range(24):
            forecast_time = current_time + timedelta(hours=hour_offset)
            hour = forecast_time.hour
            
            # Check if this hour is historically risky
            is_risky_hour = hour in temporal.get("risky_hours", [])
            
            if is_risky_hour:
                for lga in spatial.get("high_risk_lgas", [])[:3]:
                    threat_score = self.calculate_threat_score(lga, hour, incidents)
                    
                    if threat_score > 50:  # Only report significant threats
                        predictions.append({
                            "time": forecast_time.isoformat(),
                            "hour": hour,
                            "lga": lga,
                            "threat_score": round(threat_score, 1),
                            "risk_level": "HIGH" if threat_score > 70 else "MEDIUM",
                            "factors": [
                                "Historical pattern match" if is_risky_hour else None,
                                f"{lga} high-incident zone" if lga in spatial["high_risk_lgas"] else None,
                            ],
                            "recommended_action": self._recommend_action(threat_score, lga),
                        })
        
        # Sort by threat score
        predictions.sort(key=lambda x: x["threat_score"], reverse=True)
        return predictions[:10]  # Top 10 predictions
    
    def _recommend_action(self, threat_score: float, lga: str) -> str:
        """Generate actionable recommendation"""
        if threat_score > 80:
            return f"Deploy patrol teams to {lga}. Alert DPO and NSCDC. Monitor all entry/exit points."
        elif threat_score > 60:
            return f"Increase vigilance in {lga}. Brief community leaders. Activate informant network."
        else:
            return f"Maintain normal operations in {lga}. Continue monitoring."
    
    def generate_weekly_forecast(self, incidents: List[Dict]) -> Dict:
        """Generate 7-day strategic forecast"""
        temporal = self.analyze_temporal_patterns(incidents)
        spatial = self.analyze_spatial_patterns(incidents)
        
        now = datetime.now()
        
        # Predict high-risk days
        high_risk_days = []
        for day_offset in range(7):
            date = now + timedelta(days=day_offset)
            weekday = date.weekday()
            
            if weekday in temporal.get("risky_days", []):
                high_risk_days.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "day_name": date.strftime("%A"),
                    "risk_level": "HIGH",
                    "lgas_at_risk": spatial.get("high_risk_lgas", [])[:3],
                })
        
        return {
            "forecast_period": "Next 7 Days",
            "high_risk_days": high_risk_days,
            "safest_days": [d for d in range(7) if d not in temporal.get("risky_days", [])],
            "lgas_requiring_attention": spatial.get("high_risk_lgas", [])[:5],
            "overall_trend": "INCREASING" if len(incidents) > 20 else "STABLE",
        }


class PatternAnalyzer:
    """Advanced pattern recognition for bandit behavior"""
    
    @staticmethod
    def detect_retaliation_pattern(incidents: List[Dict]) -> Optional[Dict]:
        """Detect if recent attacks are retaliatory"""
        # Look for back-to-back incidents in same area
        recent = [i for i in incidents if 
                 (datetime.now() - i.get("timestamp", datetime.now())).days <= 3]
        
        if len(recent) >= 3:
            lgas = [i.get("lga") for i in recent]
            if len(set(lgas)) <= 2:  # Same 1-2 LGAs
                return {
                    "pattern": "ESCALATION",
                    "confidence": "MEDIUM",
                    "lgas_involved": list(set(lgas)),
                    "assessment": "Possible retaliation or turf war. Monitor for further escalation.",
                }
        return None
    
    @staticmethod
    def identify_mobility_routes(incidents: List[Dict]) -> List[Dict]:
        """Identify likely bandit movement corridors"""
        # Group incidents by proximity
        routes = []
        
        # Known border crossing points
        border_corridors = [
            {"name": "Niger Republic Border", "lgas": ["Bagudo", "Dandi", "Maiyama"]},
            {"name": "Zamfara Corridor", "lgas": ["Shanga", "Suru", "Danko"]},
            {"name": "Sokoto Corridor", "lgas": ["Gwandu", "Argungu", "Augie"]},
        ]
        
        for corridor in border_corridors:
            incidents_in_corridor = [i for i in incidents if i.get("lga") in corridor["lgas"]]
            if len(incidents_in_corridor) >= 3:
                routes.append({
                    "corridor": corridor["name"],
                    "incident_count": len(incidents_in_corridor),
                    "lgas_affected": corridor["lgas"],
                    "recommendation": f"Deploy border patrol along {corridor['name']}",
                })
        
        return sorted(routes, key=lambda x: x["incident_count"], reverse=True)


# Global predictor instance
predictor = ThreatPredictor()

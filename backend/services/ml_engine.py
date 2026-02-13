"""Machine Learning Engine for CITADEL KEBBI — Anomaly Detection, Trend Analysis, Threat Prediction"""
import math
from datetime import datetime, timedelta
from config import KEBBI_LGAS


def detect_anomalies(hotspots: list, baseline_mean: float = 5.0, baseline_std: float = 3.0):
    """Statistical anomaly detection on fire/thermal hotspot data.
    Uses Z-score method against historical baseline."""
    if not hotspots:
        return {"anomalies_detected": False, "count": 0, "details": [], "score": 0.0}

    count = len(hotspots)
    z_score = (count - baseline_mean) / max(baseline_std, 0.1)

    # Check for spatial clustering
    clusters = _detect_spatial_clusters(hotspots, distance_threshold_km=15)

    # Check for brightness anomalies
    brightnesses = [h.get("brightness", 300) for h in hotspots if h.get("brightness")]
    brightness_anomalies = [b for b in brightnesses if b > 400]  # Unusually bright

    anomaly_details = []
    if z_score > 2.0:
        anomaly_details.append({
            "type": "frequency_spike",
            "description": f"Hotspot count ({count}) is {z_score:.1f} standard deviations above baseline ({baseline_mean})",
            "severity": "critical" if z_score > 3 else "high",
            "score": min(z_score / 5, 1.0),
        })
    if len(clusters) > 0:
        for cluster in clusters:
            if cluster["size"] >= 3:
                anomaly_details.append({
                    "type": "spatial_cluster",
                    "description": f"Cluster of {cluster['size']} hotspots near ({cluster['center_lat']:.4f}°N, {cluster['center_lon']:.4f}°E)",
                    "severity": "high" if cluster["size"] >= 5 else "medium",
                    "center": {"lat": cluster["center_lat"], "lon": cluster["center_lon"]},
                    "score": min(cluster["size"] / 10, 1.0),
                })
    if brightness_anomalies:
        anomaly_details.append({
            "type": "brightness_anomaly",
            "description": f"{len(brightness_anomalies)} hotspots with unusually high brightness (>400K)",
            "severity": "high",
            "max_brightness": max(brightness_anomalies),
            "score": min(max(brightness_anomalies) / 600, 1.0),
        })

    overall_score = max([a["score"] for a in anomaly_details], default=0)

    return {
        "anomalies_detected": len(anomaly_details) > 0,
        "count": len(anomaly_details),
        "details": anomaly_details,
        "score": round(overall_score, 3),
        "z_score": round(z_score, 2),
        "hotspot_count": count,
    }


def analyze_trends(reports: list, time_window_hours: int = 168):
    """Analyze temporal trends in intel reports (default 7-day window)."""
    if not reports:
        return {"trend": "stable", "direction": "flat", "details": {}}

    # Count reports by severity
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    category_counts = {}
    hourly_distribution = [0] * 24

    for r in reports:
        sev = r.get("severity", "low")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        cat = r.get("category", "general")
        category_counts[cat] = category_counts.get(cat, 0) + 1

    total = len(reports)
    threat_ratio = (severity_counts["critical"] * 4 + severity_counts["high"] * 3) / max(total, 1)

    if threat_ratio > 2.0:
        trend = "escalating"
        direction = "up"
    elif threat_ratio > 1.0:
        trend = "elevated"
        direction = "up"
    elif threat_ratio > 0.5:
        trend = "moderate"
        direction = "stable"
    else:
        trend = "stable"
        direction = "down"

    return {
        "trend": trend,
        "direction": direction,
        "threat_ratio": round(threat_ratio, 2),
        "total_reports": total,
        "severity_breakdown": severity_counts,
        "category_breakdown": category_counts,
        "dominant_category": max(category_counts, key=category_counts.get) if category_counts else "none",
        "recommendation": _trend_recommendation(trend),
    }


def predict_threats(lga_data: list = None, intel_reports: list = None, hotspots: list = None):
    """Threat prediction model using weighted scoring of multiple indicators."""
    if lga_data is None:
        lga_data = KEBBI_LGAS

    predictions = []
    risk_weights = {"critical": 1.0, "high": 0.75, "medium": 0.5, "low": 0.25}

    for lga in lga_data:
        base_risk = risk_weights.get(lga.get("risk", "low"), 0.25)

        # Proximity to reported hotspots
        fire_proximity_score = 0
        if hotspots:
            for h in hotspots:
                dist = _haversine(lga["lat"], lga["lon"], h.get("latitude", 0), h.get("longitude", 0))
                if dist < 30:  # Within 30km
                    fire_proximity_score = max(fire_proximity_score, 1.0 - (dist / 30))

        # Intel reports mentioning this LGA
        intel_score = 0
        if intel_reports:
            lga_mentions = sum(1 for r in intel_reports
                               if lga["name"].lower() in (r.get("title", "") + r.get("description", "")).lower())
            intel_score = min(lga_mentions / 5, 1.0)

        # Border proximity (cross-border threat multiplier)
        border_lgas = {"Dandi", "Augie", "Argungu", "Bagudo"}
        border_multiplier = 1.2 if lga["name"] in border_lgas else 1.0

        # Southern corridor multiplier (known high-risk)
        southern_corridor = {"Fakai", "Sakaba", "Wasagu/Danko", "Zuru"}
        corridor_multiplier = 1.3 if lga["name"] in southern_corridor else 1.0

        # Composite threat score
        composite = (
            base_risk * 0.4 +
            fire_proximity_score * 0.2 +
            intel_score * 0.2 +
            0.2  # baseline awareness
        ) * border_multiplier * corridor_multiplier

        composite = min(composite, 1.0)

        # Determine predicted level
        if composite > 0.75:
            predicted = "critical"
        elif composite > 0.55:
            predicted = "high"
        elif composite > 0.35:
            predicted = "medium"
        else:
            predicted = "low"

        predictions.append({
            "lga": lga["name"],
            "lat": lga["lat"],
            "lon": lga["lon"],
            "current_risk": lga.get("risk", "low"),
            "predicted_risk": predicted,
            "composite_score": round(composite, 3),
            "factors": {
                "base_risk": round(base_risk, 2),
                "fire_proximity": round(fire_proximity_score, 2),
                "intel_correlation": round(intel_score, 2),
                "border_factor": border_multiplier,
                "corridor_factor": corridor_multiplier,
            },
            "risk_change": "↑" if risk_weights.get(predicted, 0) > base_risk else ("↓" if risk_weights.get(predicted, 0) < base_risk else "→"),
        })

    predictions.sort(key=lambda x: x["composite_score"], reverse=True)

    return {
        "predictions": predictions,
        "timestamp": datetime.now().isoformat(),
        "highest_risk": predictions[0] if predictions else None,
        "escalating_lgas": [p for p in predictions if p["risk_change"] == "↑"],
        "de_escalating_lgas": [p for p in predictions if p["risk_change"] == "↓"],
        "model": "CITADEL-THREAT-PRED-v2",
    }


def _detect_spatial_clusters(hotspots, distance_threshold_km=15):
    """Simple distance-based spatial clustering."""
    clusters = []
    visited = set()

    for i, h1 in enumerate(hotspots):
        if i in visited:
            continue
        cluster = [h1]
        visited.add(i)
        for j, h2 in enumerate(hotspots):
            if j in visited:
                continue
            dist = _haversine(
                h1.get("latitude", 0), h1.get("longitude", 0),
                h2.get("latitude", 0), h2.get("longitude", 0)
            )
            if dist < distance_threshold_km:
                cluster.append(h2)
                visited.add(j)

        if len(cluster) >= 2:
            center_lat = sum(h.get("latitude", 0) for h in cluster) / len(cluster)
            center_lon = sum(h.get("longitude", 0) for h in cluster) / len(cluster)
            clusters.append({
                "size": len(cluster),
                "center_lat": center_lat,
                "center_lon": center_lon,
            })

    return clusters


def _haversine(lat1, lon1, lat2, lon2):
    """Calculate km distance between two points."""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(a))


def _trend_recommendation(trend):
    """Generate recommendation based on trend."""
    recs = {
        "escalating": "ALERT: Threat level is escalating. Recommend increased surveillance, force repositioning to high-risk corridors, and enhanced border monitoring.",
        "elevated": "CAUTION: Elevated threat activity detected. Maintain heightened alert posture and continue monitoring key indicators.",
        "moderate": "ADVISORY: Moderate threat activity. Continue standard surveillance operations with attention to emerging patterns.",
        "stable": "NORMAL: Threat environment is stable. Maintain routine operations and scheduled patrols.",
    }
    return recs.get(trend, "Continue monitoring.")

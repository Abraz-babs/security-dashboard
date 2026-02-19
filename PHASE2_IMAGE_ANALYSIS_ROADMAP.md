# CITADEL KEBBI - Phase 2 Image Analysis Roadmap
## Satellite Imagery Interpretation & AI-Powered Detection

**Document Version:** 1.0  
**Date:** February 2026  
**Classification:** INTERNAL - Technical Roadmap  
**Status:** Planned for Phase 2 Implementation

---

## 🎯 EXECUTIVE SUMMARY

**Current State (Phase 1):**
- Satellite metadata display (pass times, coordinates, cloud cover)
- Fire/thermal detection via NASA FIRMS
- Manual interpretation by AI chatbot (filename analysis only)

**Phase 2 Goal:**
- Automated image analysis extracting actionable intelligence
- Change detection (new structures, cleared areas)
- Vehicle/convoy detection
- Agricultural anomaly detection

**Investment Required:** ₦15-50M depending on implementation path

---

## 📊 CURRENT vs TARGET CAPABILITIES

| Capability | Phase 1 (Current) | Phase 2 (Target) |
|------------|-------------------|------------------|
| Fire detection | ✅ NASA FIRMS | ✅ Enhanced with context |
| Land clearing | ❌ Manual only | ✅ Automated change detection |
| Vehicle detection | ❌ Not possible | ✅ SAR-based vehicle counts |
| Structure detection | ❌ Not possible | ✅ New building identification |
| Crop monitoring | ❌ Not possible | ✅ Agricultural anomaly alerts |
| Night activity | ❌ Limited | ✅ SAR 24/7 monitoring |
| Real-time alerts | ❌ Batch only | ✅ Near real-time processing |

---

## 🏗️ TECHNICAL ARCHITECTURE OPTIONS

### OPTION A: Google Earth Engine (GEE) - RECOMMENDED

**Overview:** Google's cloud-based geospatial analysis platform with pre-built algorithms

**Architecture:**
```
Sentinel-2/1 (Acquisition)
    ↓
Google Earth Engine (Cloud Processing)
    - Change detection algorithms
    - NDVI/NDWI analysis
    - Cloud masking
    ↓
CITADEL API (Results ingestion)
    ↓
Dashboard (Visual alerts)
```

**Pros:**
- ✅ FREE for research/non-commercial use
- ✅ Pre-built algorithms (no ML training needed)
- ✅ Scalable (Google infrastructure)
- ✅ Python/JavaScript API
- ✅ Historical data back to 1984

**Cons:**
- ❌ Requires Google Cloud project setup
- ❌ Learning curve for Earth Engine API
- ❌ Export limits (computation free, export limited)
- ❌ Internet dependency

**Cost:** $0-100/month (depending on export volume)

**Timeline:** 3-4 weeks development

**Implementation Steps:**
1. Create Google Cloud project (1 day)
2. Set up Earth Engine access (1 day)
3. Develop change detection scripts (1 week)
4. Build API integration (1 week)
5. Dashboard visualization (1 week)

**Sample Detection Script:**
```javascript
// GEE JavaScript for change detection
var sentinel = ee.ImageCollection("COPERNICUS/S2_SR")
    .filterBounds(kebbiGeometry)
    .filterDate('2026-01-01', '2026-02-15')
    .sort('CLOUDY_PIXEL_PERCENTAGE');

// NDVI calculation for vegetation monitoring
var addNDVI = function(image) {
  var ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI');
  return image.addBands(ndvi);
};

var withNDVI = sentinel.map(addNDVI);

// Detect significant vegetation loss (possible clearing)
var baseline = withNDVI.filterDate('2026-01-01', '2026-01-15').mean();
var current = withNDVI.filterDate('2026-02-01', '2026-02-15').mean();
var change = current.select('NDVI').subtract(baseline.select('NDVI'));

var clearedAreas = change.lt(-0.2); // NDVI drop > 0.2
```

---

### OPTION B: Sentinel Hub + Custom Processing

**Overview:** Commercial service providing processed Sentinel data with custom algorithms

**Architecture:**
```
Sentinel Satellites
    ↓
Sentinel Hub (Processed data)
    ↓
AWS Lambda / Cloud Function (Custom analysis)
    - YOLOv8 for vehicle detection
    - Change detection algorithms
    ↓
CITADEL Database (Results)
    ↓
Dashboard
```

**Pros:**
- ✅ Simple API integration
- ✅ Custom evalscripts (band math)
- ✅ OGC services (WMS/WFS)
- ✅ Good documentation
- ✅ Fast image delivery

**Cons:**
- ❌ €50-500/month cost
- ❌ Still requires custom ML for advanced detection
- ❌ Rate limits on free tier

**Cost:** €100-300/month (Processing + storage)

**Timeline:** 4-6 weeks development

**Best For:** Organizations needing reliable, fast image access with moderate customization

---

### OPTION C: AWS SageMaker + ML Models (ADVANCED)

**Overview:** Custom machine learning pipeline for specific security use cases

**Architecture:**
```
Sentinel Data (Copernicus/Open Data)
    ↓
AWS S3 (Raw imagery storage)
    ↓
SageMaker Processing (Custom ML models)
    - YOLOv8 for vehicle detection
    - U-Net for change segmentation
    - Random Forest for classification
    ↓
API Gateway (REST endpoints)
    ↓
Dashboard
```

**Pros:**
- ✅ Fully customizable
- ✅ Can train on Nigerian-specific data
- ✅ Scalable to any use case
- ✅ Integration with other AWS services

**Cons:**
- ❌ HIGH cost ($500-2000/month)
- ❌ Requires ML expertise
- ❌ Need labeled training data
- ❌ 2-3 months development time

**Cost:** $1000-3000/month (Compute + storage + training)

**Timeline:** 2-3 months development

**Best For:** Large-scale operations with dedicated ML team

---

### OPTION D: Planet Labs / Airbus (Commercial Imagery)

**Overview:** Subscription to commercial high-resolution imagery with built-in analytics

**Architecture:**
```
Planet/Airbus Satellites
    ↓
Commercial API (Analyzed data)
    - Pre-processed change detection
    - Vehicle counts
    - Structure identification
    ↓
CITADEL API (Direct integration)
    ↓
Dashboard
```

**Pros:**
- ✅ 3-5m resolution (vs 10m Sentinel)
- ✅ Daily coverage (vs 5-day Sentinel)
- ✅ Built-in analytics
- ✅ Ready-to-use intelligence

**Cons:**
- ❌ VERY EXPENSIVE ($5000-20000/month)
- ❌ Contract lock-in
- ❌ Overkill for most use cases

**Cost:** $5000-15000/month

**Best For:** Military/critical infrastructure with large budgets

---

## 🔍 SPECIFIC DETECTION CAPABILITIES

### 1. CHANGE DETECTION (Priority 1)

**What it detects:**
- New buildings/structures
- Cleared land (mining, camps)
- Road construction
- Agricultural pattern changes

**Method:** Pixel differencing between time periods

**Data Source:** Sentinel-2 (optical) or Sentinel-1 (SAR)

**Accuracy:** 70-85% depending on size of change

**Minimum Detectable:** 30m x 30m area (9 pixels)

**Implementation:**
```python
# Python pseudo-code for change detection
def detect_changes(bbox, date_range):
    old_image = fetch_sentinel(bbox, date_range[0])
    new_image = fetch_sentinel(bbox, date_range[1])
    
    # Calculate difference
    diff = new_image - old_image
    
    # Threshold for significant change
    changes = diff > threshold
    
    return {
        "area_changed": calculate_area(changes),
        "confidence": confidence_score,
        "coordinates": get_coordinates(changes)
    }
```

---

### 2. VEHICLE DETECTION (Priority 2)

**What it detects:**
- Vehicle convoys on roads
- Concentrations at camps
- Unusual traffic patterns

**Method:**
- SAR (Sentinel-1) detects metal objects
- Optical (Sentinel-2) for large groups (>10 vehicles)
- ML model for classification

**Data Source:** Sentinel-1 (SAR) preferred for all-weather

**Accuracy:** 60-75% (difficult with 10m resolution)

**Minimum Detectable:** 10+ vehicles in open area

**Limitation:** Cannot identify vehicle type, only "metal objects"

---

### 3. AGRICULTURAL ANOMALY (Priority 3)

**What it detects:**
- Crop stress (drought, disease)
- Unauthorized farming in protected areas
- Massive crop destruction (arson)

**Method:** NDVI (Normalized Difference Vegetation Index) analysis

**Data Source:** Sentinel-2 (optical)

**Accuracy:** 80-90%

**Use Case:** Food security monitoring, illegal farming detection

---

### 4. FIRE/THERMAL ENHANCEMENT (Current System Upgrade)

**Current:** NASA FIRMS (fire location only)

**Enhancement:**
- Contextual analysis (near settlements, roads)
- Temporal patterns (frequency, timing)
- Correlation with weather data
- Automated classification (mining kiln vs bush burning)

**Implementation:** Rule-based + ML classification

---

## 📅 IMPLEMENTATION TIMELINE

### Phase 2A: Foundation (Weeks 1-4)
- [ ] Set up Google Earth Engine project
- [ ] Implement basic change detection
- [ ] Integrate with existing dashboard
- [ ] Train operators on interpretation

### Phase 2B: Enhancement (Weeks 5-8)
- [ ] Add vehicle detection (SAR-based)
- [ ] Implement agricultural monitoring
- [ ] Automated alert system
- [ ] Mobile app notifications

### Phase 2C: Advanced (Weeks 9-12)
- [ ] Custom ML model training
- [ ] Historical trend analysis
- [ ] Predictive analytics
- [ ] Integration with ground sensors

---

## 💰 BUDGET ESTIMATES

### Option A: Google Earth Engine (RECOMMENDED)

| Item | Cost (₦) | Timeline |
|------|----------|----------|
| Development (4 weeks) | ₦2-3M | One-time |
| Google Cloud hosting | ₦50-150K/month | Recurring |
| Training | ₦200K | One-time |
| **Total Year 1** | **₦4-6M** | |

### Option B: Sentinel Hub

| Item | Cost (₦) | Timeline |
|------|----------|----------|
| Development (6 weeks) | ₦3-4M | One-time |
| Sentinel Hub subscription | ₦80-400K/month | Recurring |
| AWS processing | ₦100-200K/month | Recurring |
| **Total Year 1** | **₦6-10M** | |

### Option C: AWS SageMaker (Advanced)

| Item | Cost (₦) | Timeline |
|------|----------|----------|
| Development (3 months) | ₦8-12M | One-time |
| AWS infrastructure | ₦500K-2M/month | Recurring |
| ML engineer (contract) | ₦2M/month | 6 months |
| **Total Year 1** | **₦25-40M** | |

---

## 🎯 SUCCESS METRICS

### Technical KPIs:
- **Detection accuracy:** >75% for changes >50m x 50m
- **False positive rate:** <20%
- **Processing time:** <30 minutes from image capture to alert
- **Coverage:** 100% of Kebbi State every 5 days

### Operational KPIs:
- **Time to detection:** <24 hours for significant changes
- **Alert delivery:** <5 minutes from analysis completion
- **User adoption:** >80% of operators using daily
- **Cost per sq km monitored:** <₦100/month

---

## ⚠️ RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Cloud cover blocking optical | High | Medium | Use SAR (Sentinel-1) as backup |
| False positives overwhelming users | Medium | High | Implement confidence thresholds |
| Internet connectivity issues | Medium | High | Local caching + SMS fallback |
| Insufficient training data | Medium | Medium | Start with rule-based, add ML later |
| Google/AWS service outages | Low | High | Multi-cloud backup strategy |

---

## 📋 DECISION MATRIX

| Criteria | GEE | Sentinel Hub | AWS SageMaker | Planet |
|----------|-----|--------------|---------------|--------|
| Cost | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐ |
| Speed to deploy | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| Customization | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Resolution | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Support in Nigeria | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| **Overall** | **⭐⭐⭐⭐** | **⭐⭐⭐** | **⭐⭐⭐** | **⭐⭐** |

**Recommendation:** Start with Google Earth Engine (Option A) for cost-effectiveness and scalability.

---

## 🔗 INTEGRATION ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                             │
├─────────────────────────────────────────────────────────────┤
│  Sentinel-2  │  Sentinel-1  │  NASA FIRMS  │  Weather API   │
└──────┬───────┴──────┬───────┴──────┬───────┴──────┬─────────┘
       │              │              │              │
       └──────────────┴──────────────┴──────────────┘
                      │
       ┌──────────────▼──────────────┐
       │   GOOGLE EARTH ENGINE       │
       │   - Change Detection        │
       │   - NDVI Analysis           │
       │   - Cloud Masking           │
       └──────────────┬──────────────┘
                      │
       ┌──────────────▼──────────────┐
       │   CITADEL PROCESSING LAYER  │
       │   - Alert Generation        │
       │   - Priority Scoring        │
       │   - Database Storage        │
       └──────────────┬──────────────┘
                      │
       ┌──────────────▼──────────────┐
       │      CITADEL DASHBOARD      │
       │   - Visual Alerts           │
       │   - Map Visualization       │
       │   - Report Generation       │
       └─────────────────────────────┘
```

---

## 🚀 NEXT STEPS

### Immediate (Post-Presentation):
1. Secure Phase 2 funding commitment
2. Set up Google Earth Engine project
3. Hire Python/GEE developer (contract)
4. Begin change detection algorithm development

### 30-Day Targets:
1. Basic change detection operational
2. Integration with existing dashboard
3. Operator training completed
4. First automated alerts generated

### 90-Day Targets:
1. Full Kebbi State coverage
2. Vehicle detection (SAR) implemented
3. Mobile alert system active
4. Historical trend analysis available

---

**Document Owner:** CITADEL KEBBI Technical Team  
**Review Date:** Post-Phase 1 presentation  
**Approval:** Pending government contract award

---

**APPENDIX A: GEE Code Examples**
**APPENDIX B: API Integration Samples**  
**APPENDIX C: Training Data Requirements**
**APPENDIX D: Vendor Contact Information**

*(Appendices available upon request)*

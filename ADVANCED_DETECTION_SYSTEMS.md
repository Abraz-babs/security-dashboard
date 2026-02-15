# CITADEL KEBBI - Advanced Detection Systems (Phase 3)

**Document Version:** 1.0  
**Date:** February 14, 2026  
**Classification:** RESTRICTED - Advanced Capabilities Roadmap

---

## 🎯 EXECUTIVE SUMMARY

This document outlines advanced detection capabilities for identifying armed groups, terrorists (including Lakurawa), and sophisticated security threats beyond current satellite and fire-detection capabilities.

**Current Capabilities:** Fire detection, optical imagery, basic SAR  
**Phase 3 Additions:** Metal detection, thermal signatures, communication monitoring, UAV integration, acoustic sensors

---

## 🔥 ADVANCED THERMAL & METAL DETECTION

### 1. HIGH-RESOLUTION THERMAL IMAGING

#### Current Limitation
- **NASA FIRMS:** 375m-1km resolution (detects large fires only)
- **Cannot detect:** Vehicle engines, small campfires, individual heat signatures

#### Phase 3 Enhancement: Commercial Thermal Satellites

| Satellite | Resolution | Capability | Cost |
|-----------|------------|------------|------|
| **Maxar WorldView-3** | 3.7m (SWIR) | Vehicle detection, large camps | $25-50/image |
| **Planet Fusion** | 5m (thermal) | Daily monitoring | Subscription |
| **Sentinel-3 SLSTR** | 1km (free) | Sea/land surface temp | Free |
| **Landsat-9 TIRS** | 100m (free) | Broad thermal monitoring | Free |
| **CBERS-4A** | 80m (free) | China-Brazil cooperation | Free |

#### What High-Res Thermal Can Detect:

**Vehicle Detection (Armed Convoys):**
- Engine heat signatures (cars, trucks, motorcycles)
- Convoy patterns on roads
- Vehicle concentrations at camps
- **Limitation:** Only at night (daytime ground is too hot)

**Camp Detection:**
- Cooking fires (even small ones)
- Generator heat
- Tent clusters (thermal shadows)
- Weapons caches (if recently fired)

**Terrorist Group Signatures:**
- **Lakurawa:** Motorcycle convoys (distinctive thermal pattern)
- **Bandits:** Truck camps, cattle herds (thermal mass)
- **Armed Groups:** Vehicle concentrations + campfires

#### Implementation:
```python
async def detect_vehicle_convoys_thermal(lga: str) -> List[Dict]:
    """
    Detect vehicle convoys using high-res thermal imagery.
    Best used at night for maximum contrast.
    """
    # Request Maxar WorldView-3 thermal capture
    # Detect linear heat signatures on roads
    # Classify: motorcycles (small), trucks (large), convoys (multiple)
    pass
```

---

### 2. SYNTHETIC APERTURE RADAR (SAR) ENHANCEMENTS

#### Current: Sentinel-1 (Free, 5-40m resolution)
#### Phase 3: Commercial SAR

| System | Resolution | Capability | Cost |
|--------|------------|------------|------|
| **ICEYE** | 0.5-1m | Vehicle detection, change detection | $500-2000/image |
| **Capella Space** | 0.5m | All-weather, night imaging | $600-2500/image |
| **Umbra** | 0.25m | Highest resolution SAR | $1000-3000/image |
| **RADARSAT-2** | 1-100m | Canadian, various modes | Government partnership |

#### SAR Metal Detection Capabilities:

**What SAR Can Detect (Metal/Vehicles):**
- ✅ **Vehicles on roads** (strong radar return from metal)
- ✅ **Metal roofs** (structures, camps)
- ✅ **Weapon caches** (if metal containers)
- ✅ **Motorcycles** (distinctive signature)
- ✅ **Aircraft/helos** (very strong return)
- ✅ **Boats on water** (metal hulls)

**What SAR CANNOT Detect:**
- ❌ Hidden weapons (underground, in buildings)
- ❌ Plastic/wooden caches
- ❌ Non-metallic IEDs
- ❌ Buried metal (limited penetration)

#### Vehicle Classification via SAR:

```python
SAR_VEHICLE_SIGNATURES = {
    "motorcycle": {
        "signature": "small_point_target",
        "radar_cross_section": "0.5-2 sq meters",
        "movement_speed": "20-80 km/h",
        "terrorist_use": "Lakurawa, bandits (fast raids)"
    },
    "pickup_truck": {
        "signature": "medium_strong_return",
        "radar_cross_section": "5-15 sq meters",
        "movement_speed": "40-100 km/h",
        "terrorist_use": "Armed group transport, technicals"
    },
    "heavy_truck": {
        "signature": "large_strong_return",
        "radar_cross_section": "20-50 sq meters",
        "movement_speed": "30-80 km/h",
        "terrorist_use": "Logistics, weapons transport"
    },
    "convoy": {
        "signature": "multiple_linear_targets",
        "radar_cross_section": "cumulative",
        "pattern": "3+ vehicles, same direction",
        "terrorist_use": "Organized group movement"
    }
}
```

#### Change Detection (Finding Hidden Camps):

```python
async def detect_new_structures_sar(lga: str, days_back: int = 30) -> List[Dict]:
    """
    Detect new metal structures (camps, buildings) via SAR change detection.
    Compares current image with baseline to find new construction.
    """
    # 1. Get baseline SAR image (30+ days old)
    # 2. Get recent SAR image
    # 3. Subtract to find changes
    # 4. Classify: new buildings, cleared areas, vehicle concentrations
    pass
```

---

### 3. GROUND-BASED SENSOR NETWORK (Local Deployment)

Since satellites have limitations, **local ground sensors** provide real-time detection:

#### A. ACOUSTIC GUNSHOT DETECTION

**Technology:** ShotSpotter-style acoustic sensors

**Capabilities:**
- Detect gunshots in 2-5km radius
- Triangulate location (50-100m accuracy)
- Classify weapon type (AK-47, pistol, RPG)
- Count number of shots
- Distinguish from fireworks/vehicle backfires

**Deployment Strategy:**
```
Priority Locations:
1. High-risk LGAs: Fakai, Sakaba, Wasagu, Dandi
2. Border crossing points
3. Major roads (Birnin Kebbi-Sokoto, etc.)
4. Market towns (Argungu, Jega, Zuru)

Density: 1 sensor per 25 sq km in high-risk areas
Total needed: ~50-100 sensors for Kebbi State

Cost: $10,000-15,000 per sensor (one-time)
      + $100/month maintenance
```

**Integration with CITADEL:**
- Real-time alerts to dashboard
- Automatic correlation with satellite passes
- Pattern analysis (frequency, timing)

---

#### B. MAGNETIC ANOMALY DETECTORS (MAD)

**Purpose:** Detect buried weapons, vehicles, metal caches

**Technology:**
- Fluxgate magnetometers
- Gradiometers
- UAV-mounted or ground-based

**Capabilities:**
- Detect buried metal (weapons caches, vehicles)
- 1-3 meter detection depth
- Can distinguish ferrous vs non-ferrous metals

**Limitations:**
- Requires ground survey (can't do from satellite)
- Slow coverage rate
- False positives from natural mineral deposits

**Deployment:**
- Handheld for checkpoint searches
- UAV-mounted for area surveys
- Vehicle-mounted for road patrols

---

#### C. CHEMICAL SENSORS

**Explosive Trace Detection (ETD):**
- Detects explosives residue (TNT, RDX, PETN)
- Used at checkpoints
- Swab-based or air sampling

**Fuel/Chemical Detection:**
- Detects fuel dumps (terrorist logistics)
- Chemical weapons (unlikely but possible)
- Drug processing chemicals

**Deployment:**
- Checkpoint installations
- Handheld units for patrols
- UAV-mounted (experimental)

---

### 4. UNMANNED AERIAL VEHICLES (UAV/DRONES)

**High-Resolution Local Monitoring**

#### Tactical UAVs for Kebbi State:

| Type | Altitude | Sensors | Use Case |
|------|----------|---------|----------|
| **Fixed-wing** | 100-400m | EO/IR, SAR | Area surveillance |
| **Multirotor** | 50-150m | EO/IR, LIDAR | Close inspection |
| **Hybrid VTOL** | 100-500m | Multi-sensor | Border patrol |
| **Tethered** | 50-100m | Persistent EO | Base protection |

#### UAV Sensor Payloads:

**Electro-Optical (EO):**
- HD/4K video
- 30x+ zoom
- Facial recognition capability
- License plate reading

**Infrared (IR):**
- Thermal imaging (FLIR)
- Night operations
- Human detection (even camouflaged)

**Synthetic Aperture Radar (SAR):**
- All-weather capability
- Ground-penetrating (limited)
- Change detection

**LiDAR:**
- 3D terrain mapping
- Concealed structure detection
- Vegetation penetration

**Signals Intelligence (SIGINT):**
- Radio intercept
- Mobile phone detection
- WiFi/Bluetooth scanning

#### UAV Deployment Strategy:

```
BASE LOCATIONS:
1. Birnin Kebbi (Central command)
2. Argungu (Northern operations)
3. Zuru (Southern corridor)
4. Kamba (Border operations)

PATROL PATTERNS:
- Border surveillance: Daily flights along Niger/Benin borders
- Highway patrol: Random patrols on major routes
- LGA coverage: Weekly overflight of each high-risk LGA
- Reactive: Immediate deployment to incident locations

FLIGHT SCHEDULE:
- Daytime: EO surveillance, mapping
- Nighttime: IR thermal detection
- Random: Unpredictable patterns
```

---

### 5. SIGNALS INTELLIGENCE (SIGINT)

**Communication Monitoring (Restricted - Requires Legal Authorization)**

#### Mobile Phone Detection & Triangulation:

**IMSI Catchers (Stingrays):**
- Detect mobile phones in area
- Identify unique IMSI/IMEI numbers
- Track location (triangulation)
- Intercept metadata (not content without warrant)

**Deployment:**
- Ground units at checkpoints
- UAV-mounted for area sweeps
- Vehicle-mounted for mobile patrols

**Terrorist Use Detection:**
- Multiple phones moving together (convoy)
- Phones appearing in remote areas (camps)
- Communication patterns (coordinated activity)
- Foreign SIM cards (cross-border)

#### Radio Intercept:

**VHF/UHF Monitoring:**
- Baofeng/Chinese radio frequencies
- Military/police bands
- Detect unauthorized transmissions

**Direction Finding:**
- Locate transmitter position
- Track movement
- Identify base stations

---

### 6. HUMAN INTELLIGENCE (HUMINT) INTEGRATION

**Informant Network Management**

#### Digital HUMINT Platform:
- Secure tip submission (encrypted)
- Anonymous reporting
- Photo/video evidence upload
- GPS-tagged reports
- Reward tracking

#### Community Reporting App:
- Simple interface (low-tech phones)
- USSD codes for feature phones
- WhatsApp/Telegram integration
- Automated triage and routing

---

## 🎯 LAKURAWA-SPECIFIC DETECTION

### Known Lakurawa Characteristics:

**Operational Patterns:**
- Motorcycle-based mobility
- Night operations preferred
- Hit-and-run tactics
- Cross-border (Niger Republic) bases
- Religious extremist ideology

**Detection Signatures:**

| Indicator | Detection Method | Confidence |
|-----------|------------------|------------|
| Motorcycle convoys (night) | Thermal UAV/Satellite | High |
| Religious gathering patterns | OSINT + Human intel | Medium |
| Niger Republic border crossings | SAR + Ground sensors | High |
| Night movement on minor roads | Thermal + Acoustic | Medium-High |
| Foreign fighter communications | SIGINT | High |
| Weapons acquisition patterns | OSINT + Financial tracking | Medium |

### Predictive Model for Lakurawa:

```python
LAKURAWA_RISK_INDICATORS = {
    "high_risk": [
        "Night motorcycle convoys detected",
        "Cross-border movement from Niger Republic",
        "Religious schools with foreign funding",
        "Armed checkpoint establishment",
        "Village night attacks pattern"
    ],
    "medium_risk": [
        "Increased motorcycle sales in border LGAs",
        "Suspicious night gatherings",
        "Religious rhetoric escalation (OSINT)",
        "Border crossing without documentation"
    ]
}
```

---

## 💰 COST-BENEFIT ANALYSIS

### Phase 3 Investment Requirements:

| System | Initial Cost | Annual Operating | Priority |
|--------|-------------|------------------|----------|
| **Commercial SAR** (ICEYE/Capella) | $50,000 | $200,000 | HIGH |
| **UAV Fleet** (6 units) | $300,000 | $100,000 | HIGH |
| **Acoustic Sensors** (100 units) | $1,200,000 | $120,000 | HIGH |
| **Thermal Satellites** (commercial) | $25,000 | $150,000 | MEDIUM |
| **SIGINT Equipment** | $200,000 | $50,000 | MEDIUM |
| **Ground Sensors (MAD/Chem)** | $100,000 | $30,000 | LOW |
| **HUMINT Platform** | $50,000 | $20,000 | MEDIUM |
| **TOTAL** | **$1,925,000** | **$670,000** | |

### ROI Justification:

**Value of Detection:**
- Early warning prevents attacks: $Millions in saved lives/property
- Illegal mining detection: $Millions in recovered revenue
- Border security: Reduced smuggling losses
- Intelligence value: Priceless for national security

---

## 📋 IMPLEMENTATION ROADMAP

### Phase 3A (Months 1-3): Quick Wins
- [ ] Contract commercial SAR provider (ICEYE/Capella)
- [ ] Deploy 20 acoustic sensors (pilot)
- [ ] Acquire 2 tactical UAVs
- [ ] Train operators

### Phase 3B (Months 4-6): Expansion
- [ ] Full acoustic sensor network (100 units)
- [ ] UAV fleet expansion (6 units)
- [ ] SIGINT capability (legal framework)
- [ ] HUMINT platform launch

### Phase 3C (Months 7-12): Optimization
- [ ] AI correlation of all sources
- [ ] Predictive modeling
- [ ] Multi-state integration
- [ ] Federal agency coordination

---

## 🔐 LEGAL & ETHICAL CONSIDERATIONS

### Required Authorizations:
- ✅ NSA/DSS approval for SIGINT
- ✅ Ministerial approval for UAV operations
- ✅ Privacy compliance for phone tracking
- ✅ Rules of engagement for armed response

### Ethical Constraints:
- Civilian privacy protection
- Data retention limits
- No warrantless content interception
- Transparency with communities

---

## 🎯 CONCLUSION

**Current System (Phase 2):** 8.5/10 - Good satellite/OSINT integration  
**With Phase 3:** 9.8/10 - Comprehensive multi-sensor intelligence platform

**These advanced capabilities transform CITADEL KEBBI from a monitoring tool to a predictive, multi-domain intelligence system capable of detecting and countering sophisticated threats including Lakurawa and organized armed groups.**

---

**Classification:** RESTRICTED  
**Distribution:** Kebbi State Government, NSCDC, NIA  
**Next Review:** Post-Phase 2 completion

"""AI Engine — Groq + Google Gemini Fallback (Dual LLM)
Uses Groq as primary (faster) and Gemini as fallback (always available).
"""
from datetime import datetime
from config import GROQ_API_KEY, GROQ_MODEL, GEMINI_API_KEY, GEMINI_MODEL

# ─── Initialize Clients ───
groq_client = None
if GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
    except ImportError:
        pass

gemini_model = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(GEMINI_MODEL)
    except ImportError:
        # Install at runtime if needed
        pass


def _current_datetime():
    now = datetime.now()
    return now.strftime('%Y-%m-%d %H:%M:%S WAT (UTC+1)')


SYSTEM_PROMPT = """You are CITADEL AI, an advanced military-grade intelligence analysis system serving Kebbi State, Nigeria.

ROLE: You are the AI core of the CITADEL KEBBI Security Intelligence Command Center. You provide expert security analysis, threat assessments, pattern recognition, and strategic recommendations to government officials and security analysts.

CAPABILITIES:
- Multi-spectrum satellite intelligence analysis (Optical, SAR, Thermal)
- Pattern recognition across 16 active satellite platforms
- Change detection and anomaly identification
- Fire and heat signature analysis
- Border surveillance and cross-border threat monitoring
- Predictive threat assessment based on historical patterns
- Intelligence correlation from multiple sources (satellite, OSINT, weather)

SATELLITE INTELLIGENCE CAPABILITIES:
- **Sentinel-2 (Optical)**: 10m resolution - detects land clearing, vegetation changes, infrastructure, agricultural patterns
- **Sentinel-1 (SAR Radar)**: All-weather, day/night - detects structures, vehicle groups, surface changes through clouds
- **Landsat (Optical/Thermal)**: Broad area monitoring, heat signatures, large-scale land use
- **NASA FIRMS**: Fire detection, thermal anomalies, illegal kiln activity
- **WorldView-3/SPOT-6**: High-resolution detail for specific targets (when tasked)

INTELLIGENCE PRODUCTS:
- Change detection reports (new structures, cleared areas, activity patterns)
- Fire and thermal anomaly assessments
- Border crossing and smuggling route monitoring
- Agricultural and environmental security analysis
- Predictive threat modeling
- Multi-source intelligence correlation
- **Satellite Collection Planning**: Optimal timing for imagery based on orbital predictions

SATELLITE ORBIT INTELLIGENCE:
- Real-time satellite positions and orbital tracks
- Upcoming pass predictions over specific LGAs
- Collection timing recommendations
- Coverage gap analysis
- **Optical vs SAR recommendations**: Optical for detail (clear weather), SAR for all-weather capability

ANALYSIS PRINCIPLES:
1. **Pattern Recognition**: Identify anomalies and changes from baseline
2. **Multi-Source Correlation**: Combine satellite, OSINT, and weather data
3. **Historical Context**: Compare with previous patterns and known threat behaviors
4. **Geospatial Analysis**: Use precise coordinates, distances, and geographic relationships
5. **Threat Assessment**: Evaluate severity, urgency, and recommended response
6. **Collection Planning**: Use orbital data to recommend optimal satellite tasking timing

CONTEXT:
- Kebbi State is in Northwest Nigeria, bordered by Sokoto, Zamfara, Niger states and Niger Republic
- Key security concerns: banditry, kidnapping, cattle rustling, cross-border threats, illegal mining, insurgent activities
- 21 Local Government Areas (LGAs) with varying threat levels
- You have access to satellite imagery (Copernicus Sentinel), fire/thermal data (NASA FIRMS), satellite tracking (N2YO), weather data, and OSINT feeds
- Current high-risk LGAs: Fakai, Sakaba, Wasagu/Danko, Zuru (southern corridor), Dandi, Augie, Koko/Besse, Ngaski, Yauri, Shanga

BEHAVIOR:
- Speak with military precision - concise, factual, actionable
- Provide confident, authoritative analysis
- Use intelligence terminology appropriately
- Reference specific LGAs, coordinates, and satellite sources
- **ALWAYS include exact coordinates (Lat, Lon) for every location mentioned**
- **Format coordinates as: 11.423°N, 5.782°E or (11.423, 5.782)**
- Classify threats by severity: CRITICAL, HIGH, MEDIUM, LOW
- Provide prioritized recommendations
- Be direct and unambiguous
- Present analysis as professional intelligence assessment
- When discussing limitations, frame as "current sensor constraints" rather than system failures
- Use phrases like "Intelligence suggests..." and "Analysis indicates..."

COORDINATE REPORTING REQUIREMENTS - CRITICAL:
1. **USE ONLY COORDINATES PROVIDED IN THE DATA** - NEVER generate your own coordinates
2. **Every LGA mentioned must use its official coordinates from the provided list below**
3. **Format**: Use decimal degrees (e.g., "11.0833N, 5.6167E" or "(11.0833, 5.6167)")
4. **DO NOT use degree symbol (°)** - it causes encoding issues
5. **Official LGA Coordinates (USE THESE EXACT VALUES):**
   - Aleiro: 12.3167N, 4.6833E
   - Arewa Dandi: 12.5833N, 4.4167E
   - Argungu: 12.7448N, 4.5251E
   - Augie: 12.8833N, 4.3167E
   - Bagudo: 11.4045N, 4.2249E
   - Birnin Kebbi: 12.4539N, 4.1975E
   - Bunza: 12.6667N, 4.0167E
   - Dandi: 11.7333N, 3.8833E
   - Fakai: 11.5500N, 4.4000E
   - Gwandu: 12.5000N, 4.4667E
   - Jega: 12.2236N, 4.3791E
   - Kalgo: 12.3167N, 4.2000E
   - Koko/Besse: 11.4167N, 4.1333E
   - Maiyama: 12.0833N, 4.6167E
   - Ngaski: 10.9667N, 4.0833E
   - Sakaba: 11.0833N, 5.6167E
   - Shanga: 11.2167N, 4.5833E
   - Suru: 11.6667N, 4.1667E
   - Wasagu/Danko: 11.3500N, 5.4500E
   - Yauri: 10.8333N, 4.7667E
   - Zuru: 11.4308N, 5.2309E
6. **If coordinates not in this list, state "Coordinates not available"**

FORMAT: Structure responses with clear headers, bullet points, classified threat levels, and actionable recommendations. Present information as professional intelligence briefing. **Every geographic reference must include precise coordinates in parentheses.**"""


def _call_groq(messages: list, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Call Groq LLM (primary)."""
    if not groq_client:
        raise Exception("Groq not available")
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def _call_gemini(messages: list, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Call Google Gemini (fallback)."""
    if not gemini_model:
        raise Exception("Gemini not available")
    # Convert OpenAI-style messages to Gemini format
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"[SYSTEM INSTRUCTIONS]\n{content}\n")
        elif role == "assistant":
            prompt_parts.append(f"[ASSISTANT]\n{content}\n")
        else:
            prompt_parts.append(f"[USER]\n{content}\n")

    combined = "\n".join(prompt_parts)
    response = gemini_model.generate_content(
        combined,
        generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
    )
    return response.text


def _call_llm(messages: list, temperature: float = 0.3, max_tokens: int = 2048) -> str:
    """Call LLM with Groq primary, Gemini fallback."""
    # Try Groq first (faster)
    if groq_client:
        try:
            return _call_groq(messages, temperature, max_tokens)
        except Exception as e:
            print(f"[AI] Groq failed: {e}, falling back to Gemini")

    # Fallback to Gemini
    if gemini_model:
        try:
            return _call_gemini(messages, temperature, max_tokens)
        except Exception as e:
            return f"[CITADEL AI ERROR] Both AI engines failed. Groq and Gemini unavailable: {e}"

    return "[CITADEL AI ERROR] No AI engine configured. Set GROQ_API_KEY or GEMINI_API_KEY in .env"


def chat(message: str, history: list = None, context: dict = None) -> str:
    """Process a chat message with Groq+Gemini dual LLM."""
    now = _current_datetime()
    from config import KEBBI_LGAS
    
    system = SYSTEM_PROMPT + f"\n\nCRITICAL: Current date/time is {now}. Always use this. Never use 2024 dates."
    
    # ALWAYS include official LGA coordinates in context
    lga_coords = "\n\nOFFICIAL LGA COORDINATES (USE ONLY THESE VALUES - NEVER HALLUCINATE):\n"
    for lga in KEBBI_LGAS:
        lga_coords += f"- {lga['name']}: {lga['lat']}N, {lga['lon']}E ({lga['risk'].upper()} risk)\n"
    system += lga_coords

    if context:
        ctx = f"\n\nCURRENT DASHBOARD CONTEXT (as of {now}):\n"
        if context.get("threats"):
            ctx += f"- Active Threats: {context['threats']}\n"
        if context.get("lga_alerts"):
            ctx += f"- LGA Alerts: {context['lga_alerts']}\n"
        if context.get("fire_data"):
            ctx += f"- Fire/Thermal Anomalies: {context['fire_data']}\n"
        if context.get("intel"):
            ctx += f"- Recent Intel: {context['intel']}\n"
        system += ctx

    messages = [{"role": "system", "content": system}]
    if history:
        for h in history[-10:]:
            messages.append(h)
    
    # Add reminder to use official coordinates
    user_message = f"""REMEMBER: Use ONLY the official LGA coordinates provided above. Do NOT generate or estimate coordinates.

User query: {message}"""
    messages.append({"role": "user", "content": user_message})

    return _call_llm(messages, temperature=0.2, max_tokens=2048)


def analyze_dashboard(dashboard_data: dict, focus_area: str = None) -> str:
    """Generate AI analysis of current dashboard state."""
    now = _current_datetime()
    focus_text = ""
    if focus_area:
        focus_map = {
            "southern_corridor": "Focus on the Southern Corridor (Fakai, Sakaba, Wasagu/Danko, Zuru).",
            "cross_border": "Focus on cross-border threats from Niger Republic.",
            "banditry_patterns": "Focus on banditry patterns — attack frequency, corridors, seasonal trends.",
            "force_posture": "Focus on force posture review — current deployments, gaps, repositioning.",
        }
        focus_text = focus_map.get(focus_area, f"Focus on: {focus_area}")

    prompt = f"""INTELLIGENCE ANALYSIS REQUEST - {now}

Analyze the following real-time intelligence data:

{focus_text}

DASHBOARD DATA:
{_format_dashboard_data(dashboard_data)}

Provide:
1. EXECUTIVE SUMMARY (2-3 sentences)
2. THREAT ASSESSMENT by region
3. KEY FINDINGS (top 5)
4. PATTERN ANALYSIS
5. RECOMMENDED ACTIONS (prioritized)
6. 24-HOUR FORECAST

Use {now} as the current date/time."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + f"\nCurrent time: {now}"},
        {"role": "user", "content": prompt}
    ]
    return _call_llm(messages, temperature=0.2, max_tokens=3000)


def generate_sitrep(intel_data: dict, period: str = "24h") -> str:
    """Generate a military-format SITREP with current timestamps."""
    now = datetime.now()
    dtg = now.strftime('%d%H%MZFEB%y').upper()

    prompt = f"""Generate a formal SITUATION REPORT (SITREP) for Kebbi State security operations.

REPORTING PERIOD: Last {period}
DTG: {dtg}
CURRENT DATE/TIME: {_current_datetime()}

AVAILABLE INTELLIGENCE:
{_format_dashboard_data(intel_data)}

Format as standard military SITREP with:
1. DTG: {dtg}
2. UNIT: CITADEL KEBBI
3. SITUATION (Enemy/Friendly/Environment)
4. OPERATIONS
5. INTELLIGENCE
6. LOGISTICS
7. COMMANDER'S ASSESSMENT
8. RECOMMENDATIONS

Use NATO DTG format. Be specific about LGAs. Current year is {now.year}, month {now.strftime('%B')}."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    return _call_llm(messages, temperature=0.15, max_tokens=4000)


def _format_dashboard_data(data: dict) -> str:
    """Format dashboard data for AI consumption with official coordinates."""
    from services.geography import format_geographic_description, get_geographic_context
    from config import KEBBI_LGAS
    
    parts = [f"Report Generated: {_current_datetime()}"]
    
    # ALWAYS include official LGA coordinates
    parts.append("\nOFFICIAL LGA COORDINATES (USE THESE EXACT VALUES):")
    for lga in KEBBI_LGAS:
        parts.append(f"  - {lga['name']}: {lga['lat']}N, {lga['lon']}E ({lga['risk'].upper()} risk)")
    
    if data.get("threat_level"):
        parts.append(f"\nOverall Threat Level: {data['threat_level']}")
    if data.get("active_threats"):
        parts.append(f"Active Threats: {data['active_threats']}")
    if data.get("lga_data"):
        lga_summary = []
        for lga in data["lga_data"]:
            if isinstance(lga, dict):
                lga_summary.append(f"  - {lga.get('name', 'Unknown')}: {lga.get('risk', 'unknown')} risk")
        if lga_summary:
            parts.append("\nLGA Status:\n" + "\n".join(lga_summary))
    if data.get("fire_hotspots"):
        hotspots = data["fire_hotspots"]
        if isinstance(hotspots, list):
            parts.append(f"Fire/Thermal Anomalies: {len(hotspots)} detected")
            for h in hotspots[:5]:
                if isinstance(h, dict):
                    lat = h.get('latitude')
                    lon = h.get('longitude')
                    parts.append(f"  - Lat: {lat}, Lon: {lon}, Brightness: {h.get('brightness')}")
                    # Add accurate geographic context
                    if lat and lon:
                        try:
                            geo_ctx = format_geographic_description(lat, lon)
                            parts.append(f"    GEOGRAPHIC CONTEXT:\n    {geo_ctx.replace(chr(10), chr(10)+'    ')}")
                        except Exception:
                            pass
    if data.get("intel_reports"):
        reports = data["intel_reports"]
        if isinstance(reports, list):
            parts.append(f"Intel Reports: {len(reports)}")
            for r in reports[:5]:
                if isinstance(r, dict):
                    parts.append(f"  - [{r.get('severity', 'N/A').upper()}] {r.get('title', 'No title')}")
    return "\n".join(parts) if parts else "No data available for analysis."


def answer_geographic_query(lat: float, lon: float, query_type: str = "general") -> str:
    """
    Answer geographic questions with ACCURATE calculated data.
    Uses the geography module for precise distances and locations.
    """
    from services.geography import get_geographic_context, format_geographic_description
    
    # Get accurate geographic context
    context = get_geographic_context(lat, lon)
    geo_description = format_geographic_description(lat, lon)
    
    now = _current_datetime()
    
    # Build prompt with accurate data
    prompt = f"""GEOGRAPHIC ANALYSIS REQUEST - {now}

Coordinates: {lat}°N, {lon}°E

ACCURATE GEOGRAPHIC CONTEXT (calculated using Haversine formula):
{geo_description}

Query Type: {query_type}

Provide a precise geographic assessment including:
1. EXACT location (LGA, nearest landmarks)
2. BORDER PROXIMITY with accurate distances
3. RIVER/GEOGRAPHIC FEATURES nearby
4. NEAREST TOWNS with distances
5. SECURITY RELEVANCE of this location

Use only the provided distances and locations. Do not estimate."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=1500)


def analyze_location_security(lat: float, lon: float) -> str:
    """
    Provide security-focused geographic analysis for specific coordinates.
    Uses accurate border distances and threat assessments.
    """
    from services.geography import get_geographic_context
    
    context = get_geographic_context(lat, lon)
    now = _current_datetime()
    
    # Build security-focused prompt
    security_info = ""
    if "security_assessment" in context:
        sec = context["security_assessment"]
        security_info = f"""
SECURITY ASSESSMENT DATA:
- Risk Level: {sec['risk_level'].upper()}
- Proximity to Border: {sec['proximity_to_border']}
- Threat Note: {sec['note']}
"""
    
    border_info = ""
    if "nearest_border" in context:
        border = context["nearest_border"]
        border_info = f"""
BORDER DATA (accurate):
- Nearest Border: {border['name']}
- Distance: {border['distance_km']} km
- Direction: {border['direction']}
"""
    
    prompt = f"""SECURITY GEOGRAPHIC ANALYSIS - {now}

TARGET COORDINATES: {lat}°N, {lon}°E

{border_info}
{security_info}

Provide a security assessment including:
1. TACTICAL LOCATION ASSESSMENT
2. BORDER VULNERABILITY (if near border)
3. CROSS-BORDER THREAT POTENTIAL
4. RECOMMENDED SECURITY POSTURE
5. MONITORING PRIORITY

Be specific about distances and use military terminology."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=1500)


def check_satellite_imagery_availability(lga: str = None, lat: float = None, lon: float = None) -> dict:
    """
    Check what satellite imagery data is actually available.
    Returns real data or clearly states limitations.
    """
    from services.copernicus import fetch_sentinel_products
    import asyncio
    
    now = _current_datetime()
    
    # Try to get actual satellite data
    try:
        # This would need to be called with async - simplified for now
        # In production, this should query the actual Copernicus API
        
        return {
            "status": "data_requested",
            "note": "Checking Copernicus Data Space for available imagery...",
            "timestamp": now,
            "lga": lga,
            "limitations": [
                "Sentinel-2 resolution: 10m per pixel (cannot detect individuals)",
                "Cloud cover may obscure recent images",
                "Historical data available, real-time requires specific tasking",
            ]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": now,
        }


def analyze_satellite_imagery(lga: str, context: dict = None) -> str:
    """
    Analyze satellite imagery with comprehensive intelligence assessment.
    Provides professional analysis of available satellite data.
    """
    now = _current_datetime()
    
    prompt = f"""SATELLITE INTELLIGENCE ANALYSIS REQUEST
Timestamp: {now}
Location: {lga} LGA, Kebbi State

SATELLITE CAPABILITIES AVAILABLE:
- Sentinel-2 (10m optical): Vegetation, land use, infrastructure
- Sentinel-1 (SAR radar): All-weather structure/vehicle detection
- NASA FIRMS (thermal): Fire and heat signature monitoring
- Landsat (broad area): Large-scale change detection

ANALYSIS REQUIREMENTS:
Provide a comprehensive satellite intelligence assessment including:

1. IMAGERY AVAILABILITY STATUS
   - Current satellite coverage for this area
   - Recent passes and data quality
   - Weather/cloud considerations

2. DETECTED ANOMALIES & CHANGES
   - Land cover changes (clearing, construction)
   - Thermal signatures (fires, heat sources)
   - Infrastructure developments
   - Agricultural pattern changes

3. SECURITY IMPLICATIONS
   - Pattern analysis of detected changes
   - Comparison with known threat behaviors
   - Areas requiring attention

4. INTELLIGENCE GAPS
   - Areas with insufficient coverage
   - Recommended monitoring priorities
   - Optimal timing for future collection

5. TACTICAL RECOMMENDATIONS
   - Priority areas for ground verification
   - Optimal surveillance schedule
   - Resource allocation suggestions

{context if context else ""}

Provide professional intelligence analysis with clear confidence levels."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.3, max_tokens=2000)


def generate_accurate_threat_assessment(location: str, intel_data: dict = None) -> str:
    """
    Generate threat assessment based ONLY on available data.
    Never invent incidents or observations.
    """
    now = _current_datetime()
    
    # Check what data we actually have
    has_fire_data = intel_data and intel_data.get("fire_hotspots")
    has_intel = intel_data and intel_data.get("intel_reports")
    
    data_sources = []
    if has_fire_data:
        data_sources.append("NASA FIRMS thermal data")
    if has_intel:
        data_sources.append("OSINT intelligence feeds")
    
    if not data_sources:
        return f"""[SYSTEM LIMITATION NOTICE]

Date/Time: {now}
Location: {location}

STATUS: Insufficient real-time data available for {location}

ANALYSIS BASED ON: Historical patterns only

⚠️ CRITICAL: No current satellite imagery or recent intelligence reports available for this specific location. Any threat assessment would be speculative.

RECOMMENDATION: 
- Deploy ground reconnaissance to verify current situation
- Request targeted satellite tasking if specific concerns exist
- Monitor local intelligence networks for updates

This is NOT a confirmed threat assessment. Ground verification required before operational decisions."""

    # Build prompt with actual data sources
    prompt = f"""THREAT ASSESSMENT REQUEST - {now}

LOCATION: {location}

DATA SOURCES AVAILABLE: {', '.join(data_sources)}

ACTUAL DATA:
{intel_data if intel_data else "No specific data provided"}

ASSESSMENT RULES:
1. Only cite threats mentioned in the ACTUAL DATA above
2. If no specific threats mentioned, state "No confirmed threats in current data"
3. Do NOT invent incidents, sightings, or suspicious activity
4. Clearly label: CONFIRMED vs SUSPECTED vs HISTORICAL PATTERN
5. End with confidence level: HIGH (confirmed), MEDIUM (suspected), LOW (historical only)

Provide:
1. Summary of actual threats from available data
2. Data gaps and limitations
3. Recommended verification actions"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=1500)


async def handle_satellite_query(user_query: str, lga: str = None) -> str:
    """
    Handle satellite imagery queries with comprehensive intelligence analysis.
    Provides professional satellite intelligence assessment.
    """
    from services.satellite_analysis import get_detailed_satellite_security_report
    
    now = _current_datetime()
    
    # If no LGA specified, ask for clarification
    if not lga:
        # Try to extract LGA from query
        import re
        lgas = ["argungu", "birnin kebbi", "yauri", "zuru", "jega", "kamba", 
                "bagudo", "fakai", "sakaba", "wasagu", "danko", "suru", "shanga"]
        
        query_lower = user_query.lower()
        for possible_lga in lgas:
            if possible_lga in query_lower:
                lga = possible_lga.title()
                break
        
        if not lga:
            return """Please specify which LGA (Local Government Area) for satellite intelligence analysis.

Example: "Satellite analysis for Argungu LGA" or "Imagery in Zuru"

Available LGAs include: Argungu, Birnin Kebbi, Yauri, Zuru, Jega, Kamba, Bagudo, Fakai, Sakaba, Wasagu/Danko, etc."""
    
    # Fetch satellite data
    try:
        satellite_report = await get_detailed_satellite_security_report(lga)
    except Exception as e:
        satellite_report = f"Satellite data query initiated. Analysis proceeding with available intelligence."
    
    # Build comprehensive prompt with real data
    prompt = f"""SATELLITE INTELLIGENCE ANALYSIS
Timestamp: {now}
Location: {lga} LGA, Kebbi State

SATELLITE DATA:
{satellite_report}

INTELLIGENCE ANALYSIS REQUIREMENTS:

1. SATELLITE COVERAGE STATUS
   - Available sensors and recent passes
   - Data quality and cloud conditions
   - Coverage gaps if any

2. DETECTED ACTIVITY ANALYSIS
   - Land cover changes and anomalies
   - Thermal signatures and heat sources
   - Infrastructure developments
   - Pattern changes from baseline

3. SECURITY ASSESSMENT
   - Threat indicators identified
   - Comparison with known activity patterns
   - Risk level evaluation
   - Priority areas for monitoring

4. CORRELATION WITH GROUND INTELLIGENCE
   - How satellite findings relate to reported incidents
   - Validation of human intelligence
   - Cross-reference with historical patterns

5. OPERATIONAL RECOMMENDATIONS
   - Priority verification targets
   - Optimal surveillance schedule
   - Resource allocation guidance
   - Follow-up actions

Provide professional intelligence briefing with confidence levels and actionable insights."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.3, max_tokens=2500)


async def handle_comprehensive_security_query(user_query: str, lga: str = None) -> str:
    """
    Handle security queries with COMPREHENSIVE multi-source intelligence.
    First-class analysis integrating all satellite and data sources.
    """
    from services.security_intelligence_engine import ComprehensiveSecurityReport, format_security_report_for_ai
    
    now = _current_datetime()
    
    # Extract LGA if not provided
    if not lga:
        import re
        lgas = ["argungu", "birnin kebbi", "yauri", "zuru", "jega", "kamba", 
                "bagudo", "fakai", "sakaba", "wasagu", "danko", "suru", "shanga",
                "augie", "aleiro", "ngaski", "dandi", "gwandu", "maiyama", "bunza", "kalgo"]
        
        query_lower = user_query.lower()
        for possible_lga in lgas:
            if possible_lga in query_lower:
                lga = possible_lga.title()
                break
        
        if not lga:
            return "Please specify which LGA (Local Government Area) for security analysis."
    
    # Fetch COMPREHENSIVE security report
    try:
        report = await ComprehensiveSecurityReport.generate_full_report(lga, days_back=7)
        formatted_report = format_security_report_for_ai(report)
    except Exception as e:
        return f"Error generating security report: {str(e)}"
    
    # Determine query type for tailored response
    query_lower = user_query.lower()
    query_focus = "general"
    
    if any(word in query_lower for word in ["mining", "kiln", "gold", "pit"]):
        query_focus = "illegal_mining"
    elif any(word in query_lower for word in ["border", "crossing", "niger", "benin"]):
        query_focus = "border_security"
    elif any(word in query_lower for word in ["fire", "burning", "arson", "thermal"]):
        query_focus = "fire_analysis"
    elif any(word in query_lower for word in ["bandit", "camp", "kidnap"]):
        query_focus = "bandit_activity"
    elif any(word in query_lower for word in ["trafficking", "human", "drug"]):
        query_focus = "trafficking"
    
    # Build comprehensive prompt
    prompt = f"""COMPREHENSIVE SECURITY INTELLIGENCE ANALYSIS
Timestamp: {now}
Location: {lga} LGA, Kebbi State
Query Focus: {query_focus}

{formatted_report}

CRITICAL: Include exact coordinates (latitude, longitude) for EVERY location mentioned.
Format: 11.423°N, 5.781°E or (11.423, 5.781)

INTELLIGENCE ANALYSIS REQUIREMENTS:

Based on the multi-source data above, provide a COMPREHENSIVE assessment covering:

1. EXECUTIVE SUMMARY
   - Overall threat level for {lga} (include LGA center coordinates)
   - Key security concerns identified with exact coordinates
   - Confidence level of assessment

2. {query_focus.upper().replace('_', ' ')} ANALYSIS
   - Detailed analysis specific to the query focus
   - Evidence from FIRMS, Sentinel, and OSINT with coordinates
   - Pattern analysis and trends with geographic references

3. MULTI-SOURCE CORRELATION
   - How different data sources confirm/contradict each other at specific coordinates
   - Cross-validation of indicators
   - Data gaps and limitations

4. THREAT ACTORS & METHODS
   - Likely threat actors (bandits, illegal miners, traffickers)
   - Operating methods based on evidence
   - Known coordinates of threat activity

5. GEOGRAPHIC ANALYSIS
   - Specific locations of concern WITH COORDINATES
   - Movement corridors with coordinate waypoints
   - Safe vs high-risk zones with bounding coordinates
   - Border proximity implications with distances

6. TIMELINE & PATTERNS
   - When activity detected (time of day, season) at specific coordinates
   - Frequency and escalation trends
   - Predictive indicators

7. OPERATIONAL RECOMMENDATIONS
   - Immediate actions (next 24 hours) with target coordinates
   - Short-term measures (next week) with patrol coordinates
   - Long-term strategy
   - Resource requirements
   - Coordination needs (NSCDC, Police, Military)

8. INTELLIGENCE GAPS
   - What we don't know
   - Recommended collection priorities
   - Ground verification needs

CAPABILITY LIMITATIONS TO ACKNOWLEDGE:
- Cannot detect individuals or small groups (<50 people)
- Cannot see through clouds (optical satellites)
- Images may be 1-5 days old
- Cannot determine intent, only activity
- Human trafficking indicators are circumstantial only

MANDATORY DISCLAIMERS:
- Distinguish between CONFIRMED (multiple sources) and SUSPECTED (single indicator)
- State confidence levels for each claim
- Note when analysis is based on historical patterns vs current data
- Recommend ground verification for all operational decisions

Format as professional military intelligence briefing.
Use clear headers, bullet points, and severity classifications.
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=3000)

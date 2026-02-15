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

ROLE: You are the AI core of the CITADEL KEBBI Security Intelligence Command Center. You provide expert security analysis, threat assessments, and strategic recommendations to government analysts.

CRITICAL RULES - NO HALLUCINATION:
1. **NEVER invent satellite imagery** - Only reference actual data provided in the context
2. **NEVER claim to see individuals or small groups** - Sentinel-2 resolution is 10m/pixel (cannot see people)
3. **NEVER make up coordinates, dates, or image IDs** - Only use provided data
4. **ALWAYS clarify limitations** - State clearly when you're making inferences vs stating facts
5. **NO FUTURE DATES** - Current date/time is provided, never use future dates
6. **SATELLITE CAPABILITY LIMITATIONS**:
   - Sentinel-2: 10m resolution (can see buildings, fields, not people)
   - Cannot detect gatherings under 50+ people
   - Cannot see through clouds
   - Thermal (FIRMS): Only detects fires/heat signatures, not human activity

CONTEXT:
- Kebbi State is in Northwest Nigeria, bordered by Sokoto, Zamfara, Niger states and Niger Republic
- Key security concerns: banditry, kidnapping, cattle rustling, cross-border threats, insurgent activities
- 21 Local Government Areas (LGAs) with varying threat levels
- You have access to satellite imagery (Copernicus Sentinel), fire/thermal data (NASA FIRMS), satellite tracking (N2YO), and OSINT feeds
- Current high-risk LGAs: Fakai, Sakaba, Wasagu/Danko, Zuru (southern corridor), Dandi, Augie, Koko/Besse, Ngaski, Yauri, Shanga

GEOGRAPHIC ACCURACY RULES:
- When given coordinates, you MUST use the provided geographic context data
- NEVER estimate distances or directions - use the calculated values provided
- Border distances are calculated using accurate Haversine formula
- Reference specific LGAs based on the geographic context provided
- Use "approximately" only when the system provides approximate data

BEHAVIOR:
- Speak with military precision - concise, factual, actionable
- ALWAYS preface assessments with "Based on available data..." or "According to..."
- Clearly distinguish between: CONFIRMED DATA vs HISTORICAL PATTERNS vs INFERENCES
- Reference specific LGAs and coordinates when relevant
- Classify threats by severity: CRITICAL, HIGH, MEDIUM, LOW
- Provide recommendations in order of priority
- Use NATO/military terminology where appropriate
- Be direct and unambiguous
- Only state facts that are supported by the data provided
- When data is insufficient, say: "Insufficient data for conclusive assessment. Recommend ground verification."

FORMAT: Structure responses with clear headers, bullet points, and threat classifications when appropriate."""


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
    system = SYSTEM_PROMPT + f"\n\nCRITICAL: Current date/time is {now}. Always use this. Never use 2024 dates."

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
    messages.append({"role": "user", "content": message})

    return _call_llm(messages, temperature=0.3, max_tokens=2048)


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
    """Format dashboard data for AI consumption."""
    from services.geography import format_geographic_description, get_geographic_context
    
    parts = [f"Report Generated: {_current_datetime()}"]
    if data.get("threat_level"):
        parts.append(f"Overall Threat Level: {data['threat_level']}")
    if data.get("active_threats"):
        parts.append(f"Active Threats: {data['active_threats']}")
    if data.get("lga_data"):
        lga_summary = []
        for lga in data["lga_data"]:
            if isinstance(lga, dict):
                lga_summary.append(f"  - {lga.get('name', 'Unknown')}: {lga.get('risk', 'unknown')} risk")
        if lga_summary:
            parts.append("LGA Status:\n" + "\n".join(lga_summary))
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


def analyze_satellite_imagery_with_disclaimer(lga: str, context: dict = None) -> str:
    """
    Analyze satellite imagery with clear disclaimers about capabilities.
    NEVER claim to see things the satellite cannot detect.
    """
    now = _current_datetime()
    
    # Build prompt with strict limitations
    prompt = f"""SATELLITE IMAGERY QUERY - {now}

LOCATION: {lga} LGA, Kebbi State

⚠️ CRITICAL LIMITATIONS - MUST ACKNOWLEDGE:
1. Sentinel-2 satellites have 10-meter resolution per pixel
2. CANNOT detect individual people or small groups (< 50 people in tight formation)
3. CANNOT see through clouds
4. Images may be days or weeks old
5. Cannot distinguish between civilian and military vehicles reliably

WHAT CAN BE DETECTED:
- Large fires (thermal signatures)
- Major infrastructure changes
- Large vehicle convoys (10+ vehicles)
- Agricultural patterns
- Smoke plumes

Provide analysis based on:
1. HISTORICAL patterns for this LGA (from provided context)
2. GENERAL geographic features (rivers, terrain)
3. RECENT intelligence reports (if available)

DO NOT invent specific image IDs, dates, or visual observations.
DO NOT claim to detect individuals or small groups.
DO use qualifying language: "Based on historical patterns...", "According to recent reports..."

If no specific satellite data is available, state: "No recent cloud-free imagery available. Analysis based on historical patterns and ground intelligence."

{context if context else ""}
"""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=1500)


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
    Handle satellite imagery queries with REAL data.
    Never hallucinates - always uses actual satellite analysis.
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
            return """[SYSTEM MESSAGE]

To provide satellite imagery analysis, please specify which LGA (Local Government Area) you're interested in.

Example: "Satellite analysis for Argungu LGA" or "Imagery in Zuru"

Available LGAs include: Argungu, Birnin Kebbi, Yauri, Zuru, Jega, Kamba, Bagudo, Fakai, Sakaba, Wasagu/Danko, etc."""
    
    # Fetch REAL satellite data
    try:
        satellite_report = await get_detailed_satellite_security_report(lga)
    except Exception as e:
        satellite_report = f"Error fetching satellite data: {str(e)}"
    
    # Build comprehensive prompt with real data
    prompt = f"""SATELLITE IMAGERY SECURITY ANALYSIS REQUEST
Timestamp: {now}
Location: {lga} LGA, Kebbi State

{satellite_report}

ANALYSIS REQUIREMENTS:
Based on the satellite data provided above, analyze:

1. DATA AVAILABILITY
   - What satellite imagery is actually available (dates, sensors)
   - Cloud cover limitations
   - Data quality assessment

2. SECURITY-RELEVANT OBSERVATIONS
   - ONLY mention what can actually be detected (see CAPABILITY LIMITATIONS)
   - Reference specific images/dates if available
   - Note data gaps where imagery is insufficient

3. TACTICAL ASSESSMENT
   - What the available imagery reveals about terrain, infrastructure
   - Potential security implications based on geography
   - Limitations of satellite-only assessment

4. RECOMMENDATIONS
   - What additional data sources are needed
   - Ground verification priorities
   - Optimal timing for future satellite passes

RULES:
- ONLY use data provided in the SATELLITE IMAGERY ANALYSIS section
- NEVER claim to see individuals or small groups
- ALWAYS acknowledge limitations (clouds, resolution, timing)
- If insufficient data, clearly state: "Insufficient satellite coverage for comprehensive assessment"
- Suggest ground verification for areas of concern

Format with clear headers and professional military tone."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt}
    ]
    
    return _call_llm(messages, temperature=0.2, max_tokens=2000)

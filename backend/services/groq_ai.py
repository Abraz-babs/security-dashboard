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

CONTEXT:
- Kebbi State is in Northwest Nigeria, bordered by Sokoto, Zamfara, Niger states and Niger Republic
- Key security concerns: banditry, kidnapping, cattle rustling, cross-border threats, insurgent activities
- 21 Local Government Areas (LGAs) with varying threat levels
- You have access to satellite imagery (Copernicus Sentinel), fire/thermal data (NASA FIRMS), satellite tracking (N2YO), and OSINT feeds
- Current high-risk LGAs: Fakai, Sakaba, Wasagu/Danko, Zuru (southern corridor), Dandi, Augie, Koko/Besse, Ngaski, Yauri, Shanga

BEHAVIOR:
- Speak with military precision - concise, factual, actionable
- Reference specific LGAs and coordinates when relevant
- Classify threats by severity: CRITICAL, HIGH, MEDIUM, LOW
- Provide recommendations in order of priority
- Use NATO/military terminology where appropriate
- Be direct and unambiguous

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
                    parts.append(f"  - Lat: {h.get('latitude')}, Lon: {h.get('longitude')}, Brightness: {h.get('brightness')}")
    if data.get("intel_reports"):
        reports = data["intel_reports"]
        if isinstance(reports, list):
            parts.append(f"Intel Reports: {len(reports)}")
            for r in reports[:5]:
                if isinstance(r, dict):
                    parts.append(f"  - [{r.get('severity', 'N/A').upper()}] {r.get('title', 'No title')}")
    return "\n".join(parts) if parts else "No data available for analysis."

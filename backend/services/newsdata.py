# pyre-ignore-all-errors
"""Multi-Source Intel Engine — GNews + GDELT + RSS + Serper (Free, No Limits)
Replaces single NewsData.io dependency with 4 free sources for always-flowing data.
"""
import httpx
import asyncio
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from config import GNEWS_API_KEY, SERPER_API_KEY  # type: ignore

# ─── RSS Sources (Completely Free, No API Key) ───
# Prioritize Northern/Northwest Nigeria focused sources for Kebbi relevance
RSS_FEEDS = [
    # Major national sources (comprehensive coverage)
    {"name": "Premium Times", "url": "https://www.premiumtimesng.com/category/news/top-news/feed", "bias": "neutral", "region": "national"},
    {"name": "Daily Trust", "url": "https://dailytrust.com/feed/", "bias": "neutral", "region": "north"},  # Northern focused
    {"name": "Sahara Reporters", "url": "https://saharareporters.com/rss.xml", "bias": "neutral", "region": "national"},
    {"name": "Channels TV", "url": "https://www.channelstv.com/feed/", "bias": "neutral", "region": "national"},
    {"name": "Vanguard", "url": "https://www.vanguardngr.com/feed/", "bias": "neutral", "region": "national"},
    {"name": "The Guardian NG", "url": "https://guardian.ng/feed/", "bias": "neutral", "region": "national"},
    {"name": "The Nation", "url": "https://thenationonlineng.net/feed/", "bias": "neutral", "region": "national"},
    {"name": "Punch Nigeria", "url": "https://punchng.com/feed/", "bias": "neutral", "region": "national"},
    {"name": "Legit.ng", "url": "https://www.legit.ng/rss.xml", "bias": "neutral", "region": "national"},
]

# ─── STRICTLY KEBBI + BORDER STATES/COUNTRIES FOCUS ───
# Security Keywords for Relevance Scoring
CRITICAL_WORDS = {"attack", "kill", "dead", "bomb", "kidnap", "abduct", "bandit", "terrorist", "massacre", "ambush", "explosion", "slain", "murder", "slaughter", "behead"}
HIGH_WORDS = {"arrest", "military", "operation", "raid", "security", "threat", "armed", "gunmen", "robbery", "ransom", "troops", "insurgent", "cattle rustling", "rustling"}
MEDIUM_WORDS = {"warning", "alert", "tension", "clash", "conflict", "unrest", "crisis", "displaced", "refugee", "protest", "smuggling", "border"}

# KEBBI + NEIGHBORING BORDER STATES & COUNTRIES (Security issues here directly affect Kebbi)
KEBBI_REGION_WORDS = {
    # Kebbi State LGAs
    "kebbi", "birnin kebbi", "argungu", "yauri", "zuru", "sakaba", "fakai", "wasagu", "danko",
    "jega", "bunza", "kalgo", "aleiro", "augie", "bagudo", "dandi", "gwandu", "maiyama", 
    "ngaski", "arewa dandi", "shanga", "suru", "koko", "besse",
    
    # Border States (Nigeria) - Security issues here spill into Kebbi
    "sokoto", "sokoto state",                    # Northern neighbor (Nigerian state)
    "zamfara", "zamfara state",                  # Eastern neighbor (Nigerian state)
    "niger state",                               # Southeastern neighbor (NIGERIAN STATE - capital Minna)
    "katsina", "katsina state",                  # Northeast (Nigerian state)
    
    # Border Countries (International) - DIFFERENT from Nigerian states!
    "niger republic",                            # Country to the NORTH (DIFFERENT from Niger State! Capital Niamey)
    "benin republic", "benin",                   # Country to the WEST
    
    # Regional security terms
    "northwest nigeria", "north west", "north-west", "sahel", "sahelian",
    "cross-border", "border security", "border attack", "border infiltration"
}

# Secondary relevance - nearby states that can affect regional stability
NEARBY_STATES = {"kaduna", "kano", "plateau", "borno", "yobe", "adamawa"}

# Only show reports from last 7 days (fresh intel)
MAX_REPORT_AGE_DAYS = 7


def _is_recent_report(date_str: str) -> bool:
    """Check if report is within last MAX_REPORT_AGE_DAYS days."""
    try:
        # Parse various date formats
        parsed_date = None
        
        # ISO format
        try:
            parsed_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            pass
        
        # GDELT format: 20250211T143000Z
        if parsed_date is None and len(date_str) >= 14:
            try:
                parsed_date = datetime.strptime(date_str[:14], "%Y%m%dT%H%M%S")
            except:
                pass
        
        # RSS format
        if parsed_date is None:
            try:
                parsed_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z")
            except:
                pass
        
        if parsed_date is None:
            return True  # If we can't parse, include it
        
        # Make timezone-aware if needed
        if parsed_date.tzinfo is None:
            from datetime import timezone
            parsed_date = parsed_date.replace(tzinfo=timezone.utc)
        
        now = datetime.now(parsed_date.tzinfo)
        age_days = (now - parsed_date).total_seconds() / (24 * 3600)
        
        return age_days <= MAX_REPORT_AGE_DAYS
    except Exception:
        return True  # Include if parsing fails


def _classify_severity(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in CRITICAL_WORDS):
        return "critical"
    elif any(w in text_lower for w in HIGH_WORDS):
        return "high"
    elif any(w in text_lower for w in MEDIUM_WORDS):
        return "medium"
    return "low"


def _classify_category(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["military", "army", "soldier", "troop", "defense", "airforce", "navy"]):
        return "military"
    elif any(w in text_lower for w in ["bandit", "kidnap", "robbery", "crime", "criminal"]):
        return "criminal"
    elif any(w in text_lower for w in ["terror", "boko haram", "iswap", "insurgent"]):
        return "terrorism"
    elif any(w in text_lower for w in ["political", "governor", "government", "election"]):
        return "political"
    return "general"


def _is_security_related(text: str) -> bool:
    """Check if text is security-related AND STRICTLY relevant to Kebbi region.
    EXCLUDES general Nigeria political news.
    """
    text_lower = text.lower()
    
    # STRICT: Must contain at least one CRITICAL security keyword
    # (bandit, kidnap, attack, kill, terrorist, etc.)
    critical_security = CRITICAL_WORDS | {"bandit", "kidnap", "abduct", "ambush", "raid", "firefight", "clash"}
    has_critical_security = any(w in text_lower for w in critical_security)
    
    # Also allow HIGH security words but require explicit Kebbi region mention
    high_security = HIGH_WORDS
    has_high_security = any(w in text_lower for w in high_security)
    
    # STRICT REGION FILTER:
    # Must explicitly mention Kebbi State or bordering states (Sokoto, Zamfara, Niger, Katsina)
    # OR explicitly mention "northwest" + security
    # NO general "Nigeria" references allowed
    strict_region = KEBBI_REGION_WORDS | NEARBY_STATES | {"northwest"}
    has_strict_region = any(w in text_lower for w in strict_region)
    
    # Reject obvious non-security political topics
    political_noise = {
        "el-rufai", "ribadu", "tinubu", "fubara", "impeach", "kwankwaso", "election", 
        "campaign", "vote", "party", "pdp", "apc", "nnpp", "senator", "senate",
        "health security", "food security", "aid", "foreign aid", "health sovereignty",
        "job seeker", "recruitment", "promotion", "nba", "bar association", "transparency",
        "el rufai", "ndlea", "drug fight", "anti-drug", "marwa"
    }
    has_political_noise = any(w in text_lower for w in political_noise)
    
    # STRICT RULES:
    # 1. Must have critical security incident (attack, kidnap, kill, etc.)
    # 2. Must explicitly mention Kebbi region OR northwest
    # 3. Must NOT be political noise
    
    if has_political_noise:
        return False  # Reject political news
    
    if has_critical_security and has_strict_region:
        return True  # Critical incident in Kebbi region
    
    if has_critical_security and "northwest" in text_lower:
        return True  # Critical incident in northwest
        
    return False  # Everything else rejected


# ─── Source 1: GNews API (Free 100 req/day) ───
async def fetch_gnews(query: str = "Kebbi Sokoto Zamfara security", max_results: int = 10) -> list:
    """Fetch news from GNews.io API - STRICTLY KEBBI + BORDER FOCUS."""
    if not GNEWS_API_KEY:
        print("[GNews] No API key configured")
        return []
    try:
        url = "https://gnews.io/api/v4/search"
        # Focused query on Kebbi and neighboring states
        kebbi_queries = [
            "Kebbi state security bandit",
            "Sokoto state bandit attack", 
            "Zamfara state security",
            "Niger state border security",
            "Niger Republic border Nigeria",
        ]
        
        all_reports = []
        seen_titles = set()
        
        # Try multiple targeted queries
        query_limit = min(3, len(kebbi_queries))
        for q in kebbi_queries[:query_limit]:  # Limit to 3 queries to save API calls
            params = {
                "q": q,
                "lang": "en",
                "max": min(max_results // 3 + 2, 5),
                "sortby": "publishedAt",
                "apikey": GNEWS_API_KEY,
            }
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    continue
                data = resp.json()

                for article in data.get("articles", []):
                    title = article.get("title", "")
                    if title.lower() in seen_titles:
                        continue
                    seen_titles.add(title.lower())
                    
                    desc = article.get("description", "") or ""
                    combined = f"{title} {desc}"

                    # STRICT: Must be security-related AND Kebbi-region relevant
                    if not _is_security_related(combined):
                        continue

                    # Calculate relevance score
                    kebbi_score = sum(1 for w in KEBBI_REGION_WORDS if w in combined.lower())
                    
                    all_reports.append({
                        "title": title,
                        "description": desc,
                        "source": article.get("source", {}).get("name", "GNews"),
                        "published_at": article.get("publishedAt", datetime.now().isoformat()),
                        "url": article.get("url", ""),
                        "image_url": article.get("image"),
                        "severity": _classify_severity(combined),
                        "category": _classify_category(combined),
                        "kebbi_relevant": kebbi_score > 0,
                        "kebbi_score": kebbi_score,
                        "feed_source": "gnews",
                    })
        
        # Sort by Kebbi relevance then severity
        all_reports.sort(key=lambda r: (-r.get("kebbi_score", 0), 
                                        {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r["severity"], 4)))
        
        print(f"[GNews] Returning {len(all_reports)} Kebbi-region security reports")
        result_limit = min(max_results, len(all_reports))
        return all_reports[:result_limit]
    except Exception as e:
        import traceback
        print(f"[GNews] Error: {e}")
        traceback.print_exc()
        return []


# ─── Source 2: Serper API (Google Search) ───
async def fetch_serper(query: str = "Kebbi state security bandit", max_results: int = 8) -> list:
    """Fetch news from Serper API (Google Search API) - CREDIT OPTIMIZED.
    Uses single query to save credits, fetches recent news only.
    """
    if not SERPER_API_KEY:
        print("[Serper] No API key configured")
        return []
    
    try:
        url = "https://google.serper.dev/news"
        
        # Single comprehensive query to save credits (2500 free/month)
        # Combining all key terms into one search
        search_query = "Kebbi OR Sokoto OR Zamfara (bandit OR kidnapping OR attack OR security)"
        
        all_reports = []
        seen_titles = set()
        
        payload = {
            "q": search_query,
            "num": min(max_results, 8),  # Limit to 8 results
            "gl": "ng",  # Nigeria
            "hl": "en",
            "tbs": "qdr:w"  # Last 7 days only
        }
        
        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.post(url, json=payload, headers=headers)
            
            if resp.status_code != 200:
                print(f"[Serper] API error: {resp.status_code}")
                return []
            
            data = resp.json()
            news_items = data.get("news", [])
            
            for item in news_items:
                title = item.get("title", "").strip()
                if not title or title.lower() in seen_titles:
                    continue
                seen_titles.add(title.lower())
                
                # Check date - only recent reports
                pub_date = item.get("date", datetime.now().isoformat())
                if not _is_recent_report(pub_date):
                    continue
                
                desc = item.get("snippet", "") or ""
                combined = f"{title} {desc}"
                
                # STRICT: Must be security-related AND Kebbi-region relevant
                if not _is_security_related(combined):
                    continue
                
                # Calculate Kebbi relevance score
                kebbi_score = sum(1 for w in KEBBI_REGION_WORDS if w in combined.lower())
                
                all_reports.append({
                    "title": title,
                    "description": desc,
                    "source": item.get("source", "Serper"),
                    "published_at": pub_date,
                    "url": item.get("link", ""),
                    "image_url": item.get("imageUrl"),
                    "severity": _classify_severity(combined),
                    "category": _classify_category(combined),
                    "kebbi_relevant": kebbi_score > 0,
                    "kebbi_score": kebbi_score,
                    "feed_source": "serper",
                })
        
        # Sort by Kebbi relevance then severity
        all_reports.sort(key=lambda r: (-r.get("kebbi_score", 0), 
                                        {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(r["severity"], 4)))
        
        print(f"[Serper] Returning {len(all_reports)} fresh Kebbi-region reports (last {MAX_REPORT_AGE_DAYS} days)")
        result_limit = min(max_results, len(all_reports))
        return all_reports[:result_limit]
    except Exception as e:
        import traceback
        print(f"[Serper] Error: {e}")
        traceback.print_exc()
        return []


# ─── Source 3: GDELT Project (Free, Unlimited) ───
async def fetch_gdelt(query: str = "Nigeria security", max_results: int = 15) -> list:
    """Fetch events from GDELT Project API (free, unlimited)."""
    try:
        # Updated GDELT v2 API endpoint
        url = "https://api.gdeltproject.org/api/v2/doc/doc"
        
        # Simplified query format - GDELT works better with simpler queries
        # Remove special characters that might break the query
        clean_query = query.replace(" ", "+").replace("/", "+").replace("-", "+")
        gdelt_query = f"{clean_query}+Nigeria"
        
        params = {
            "query": gdelt_query,
            "mode": "ArtList",
            "maxrecords": min(max_results, 50),
            "format": "json",
            "sort": "DateDesc",
        }
        
        print(f"[GDELT] Requesting: {url} with query: {gdelt_query}")
        
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, params=params)
            print(f"[GDELT] Response status: {resp.status_code}, content length: {len(resp.text)}")
            
            if resp.status_code != 200:
                print(f"[GDELT] API error: {resp.status_code}, body: {resp.text[:200]}")
                return []
            
            # GDELT might return HTML error page even with 200 status
            if resp.text.strip().startswith('<') or not resp.text.strip():
                print(f"[GDELT] Got HTML/empty response instead of JSON")
                return []
            
            try:
                data = resp.json()
            except Exception as e:
                print(f"[GDELT] JSON parse error: {e}, first 200 chars: {resp.text[:200]}")
                return []

        articles = data.get("articles", [])
        print(f"[GDELT] Fetched {len(articles)} articles for query: {query}")

        reports = []
        for article in articles:
            title = article.get("title", "").strip()
            if not title:
                continue
                
            # GDELT doesn't always have descriptions in artlist mode
            desc = article.get("description", "") or title
            combined = f"{title} {desc}"

            # Calculate Kebbi relevance score for GDELT
            kebbi_score_gdelt = sum(1 for w in KEBBI_REGION_WORDS if w in combined.lower())
            reports.append({
                "title": title,
                "description": desc[:500],
                "source": article.get("domain", "GDELT"),
                "published_at": _parse_gdelt_date(article.get("seendate", "")),
                "url": article.get("url", ""),
                "image_url": article.get("socialimage") if article.get("socialimage") else None,
                "severity": _classify_severity(combined),
                "category": _classify_category(combined),
                "kebbi_relevant": kebbi_score_gdelt > 0,
                "kebbi_score": kebbi_score_gdelt,
                "feed_source": "gdelt",
            })
        
        print(f"[GDELT] Returning {len(reports)} reports")
        return reports
    except Exception as e:
        print(f"[GDELT] Error: {e}")
        return []


def _parse_gdelt_date(datestr: str) -> str:
    """Parse GDELT date format (YYYYMMDDTHHMMSSZ)."""
    try:
        if len(datestr) >= 8:
            return f"{datestr[:4]}-{datestr[4:6]}-{datestr[6:8]}T{datestr[9:11]}:{datestr[11:13]}:{datestr[13:15]}Z"
    except Exception:
        pass
    return datetime.now().isoformat()


# ─── Source 3: RSS Feeds (Completely Free) ───
async def fetch_rss_feed(feed: dict) -> list:
    """Parse a single RSS feed for security-related articles."""
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=True) as client:
            resp = await client.get(feed["url"], headers={"User-Agent": "CITADEL-KEBBI/2.0"})
            if resp.status_code != 200:
                return []

        root = ET.fromstring(resp.text)
        reports = []

        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            desc_raw = (item.findtext("description") or "").strip()
            desc = re.sub(r'<[^>]+>', '', desc_raw)[:500]  # Strip HTML
            link = (item.findtext("link") or "").strip()
            pub_date = (item.findtext("pubDate") or "").strip()
            combined = f"{title} {desc}"

            # Check date - only recent reports
            if not _is_recent_report(pub_date):
                continue

            if not _is_security_related(combined):
                continue

            # Calculate Kebbi relevance score for RSS
            kebbi_score_rss = sum(1 for w in KEBBI_REGION_WORDS if w in combined.lower())
            reports.append({
                "title": title,
                "description": desc,
                "source": feed["name"],
                "published_at": _parse_rss_date(pub_date),
                "url": link,
                "image_url": None,
                "severity": _classify_severity(combined),
                "category": _classify_category(combined),
                "kebbi_relevant": kebbi_score_rss > 0,
                "kebbi_score": kebbi_score_rss,
                "feed_source": "rss",
            })

        feed_limit = min(10, len(reports))
        return reports[:feed_limit]
    except Exception:
        return []


def _parse_rss_date(datestr: str) -> str:
    """Parse RSS date formats."""
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(datestr, fmt).isoformat()
        except ValueError:
            continue
    return datetime.now().isoformat()


async def fetch_all_rss() -> list:
    """Fetch security news from all RSS feeds concurrently."""
    # Use individual timeouts to prevent one slow feed from blocking all
    # Reduced to 2.5s per feed to ensure total timeout < 15s
    tasks = []
    for feed in RSS_FEEDS:
        task = asyncio.wait_for(fetch_rss_feed(feed), timeout=2.5)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_reports = []
    for result in results:
        if isinstance(result, list):
            all_reports.extend(result)
    return all_reports


# ─── Single Feed Fetch (for /feed endpoint) ───
async def fetch_intel_feed(query: str = "Nigeria security", max_results: int = 10) -> dict:
    """Fetch a single intel feed with raw results (Serper + GNews + GDELT + RSS)."""
    serper_task = fetch_serper(query, max_results)
    gnews_task = fetch_gnews(query, max_results)
    gdelt_task = fetch_gdelt(query, max_results)
    rss_task = fetch_all_rss()

    results = await asyncio.gather(
        serper_task, gnews_task, gdelt_task, rss_task,
        return_exceptions=True
    )

    all_reports = []
    seen_titles = set()
    source_counts = {"serper": 0, "gnews": 0, "gdelt": 0, "rss": 0}

    for result in results:
        if isinstance(result, Exception):
            continue
        if isinstance(result, list):
            for report in result:
                title_lower = report["title"].strip().lower()
                title_key = title_lower[:min(80, len(title_lower))]
                if title_key and title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_reports.append(report)
                    src = report.get("feed_source", "unknown")
                    source_counts[src] = source_counts.get(src, 0) + 1

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_reports.sort(key=lambda r: severity_order.get(r["severity"], 4))

    return {
        "reports": all_reports[:max_results],
        "total": len(all_reports),
        "query": query,
        "source": "multi_source",
        "sources": source_counts,
        "fetched_at": datetime.now().isoformat(),
    }


# ─── Combined Multi-Source Fetch ───
async def fetch_security_intel() -> dict:
    """Fetch security intelligence - STRICTLY KEBBI + BORDER STATES/REGION FOCUS.
    Serper + GNews + GDELT + RSS — always returns data, zero cost.
    """
    # STRICT KEBBI REGION QUERIES
    # Only fetch news relevant to Kebbi and bordering states/countries
    kebbi_region_queries = [
        "Kebbi bandit attack",
        "Kebbi kidnapping",
        "Sokoto bandit",
        "Zamfara bandit attack", 
        "Niger state bandit",
        "northwest nigeria security",
    ]
    
    # Run all sources in parallel with short timeouts
    serper_task = fetch_serper("Kebbi state security bandit", 10)
    gnews_task = fetch_gnews("Kebbi border security", 10)
    
    # GDELT with Kebbi-specific queries
    gdelt_task1 = fetch_gdelt("Kebbi Sokoto Zamfara bandit", 8)
    gdelt_task2 = fetch_gdelt("northwest nigeria security", 8)
    
    # RSS is the most reliable for Nigerian news
    rss_task = fetch_all_rss()

    results = await asyncio.gather(
        serper_task, gnews_task, gdelt_task1, gdelt_task2, rss_task,
        return_exceptions=True
    )

    all_reports = []
    seen_titles = set()
    source_counts = {"serper": 0, "gnews": 0, "gdelt": 0, "rss": 0}

    for result in results:
        if isinstance(result, Exception):
            print(f"[Intel] Source failed: {result}")
            continue
        if isinstance(result, list):
            for report in result:
                title_lower = report["title"].strip().lower()
                title_key = title_lower[:min(80, len(title_lower))]
                if title_key and title_key not in seen_titles:
                    seen_titles.add(title_key)
                    all_reports.append(report)
                    src = report.get("feed_source", "unknown")
                    source_counts[src] = source_counts.get(src, 0) + 1

    # Sort: Kebbi-region relevant first, then by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_reports.sort(key=lambda r: (
        0 if r.get("kebbi_relevant") else 1,
        -r.get("kebbi_score", 0),
        severity_order.get(r["severity"], 4)
    ))
    
    # Log summary
    kebbi_count = sum(1 for r in all_reports if r.get("kebbi_relevant"))
    print(f"[Intel] Total reports: {len(all_reports)}, Kebbi-region: {kebbi_count}")

    return {
        "reports": all_reports,
        "total": len(all_reports),
        "kebbi_region_count": kebbi_count,
        "source": "multi_source_kebbi_focus",
        "sources": source_counts,
        "fetched_at": datetime.now().isoformat(),
    }

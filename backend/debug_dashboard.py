import asyncio
from routers.dashboard import get_dashboard_overview, get_lga_data

async def test():
    print("=== Testing Dashboard API ===")
    
    print("\n1. Testing LGA data...")
    try:
        lgas = await asyncio.wait_for(get_lga_data(), timeout=30.0)
        print(f"LGAs: {lgas.get('total', 0)}")
        print(f"Summary: {lgas.get('summary', {})}")
    except Exception as e:
        print(f"LGA ERROR: {e}")
    
    print("\n2. Testing Dashboard overview...")
    try:
        overview = await asyncio.wait_for(get_dashboard_overview(), timeout=30.0)
        print(f"Stats: {overview.get('stats', {})}")
        print(f"Threat: {overview.get('threat_level')}")
        print(f"Fire: {overview.get('stats', {}).get('fire_hotspots')}")
    except Exception as e:
        print(f"OVERVIEW ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test())

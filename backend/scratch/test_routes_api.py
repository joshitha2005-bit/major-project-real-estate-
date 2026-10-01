import asyncio
import httpx

async def test_endpoint():
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=30.0) as client:
        # Test with origin lat/lon (Majestic coordinates)
        r = await client.get("/api/v1/properties/1/routes?origin_lat=12.9774&origin_lon=77.5708")
        print("Status code (coords):", r.status_code)
        if r.status_code == 200:
            data = r.json()
            print("Origin:", data.get("origin"))
            print("Destination:", data.get("destination"))
            routes = data.get("routes", {})
            for k, v in routes.items():
                print(f"  {k}: status={v.get('status')}, dist={v.get('distance_km')} km, time={v.get('time_minutes')} mins, error={v.get('error_message')}")

        # Test with origin_text string
        r2 = await client.get("/api/v1/properties/1/routes?origin_text=Indiranagar, Bangalore")
        print("\nStatus code (text):", r2.status_code)
        if r2.status_code == 200:
            data2 = r2.json()
            print("Origin address:", data2.get("origin", {}).get("address"))
            for k, v in data2.get("routes", {}).items():
                print(f"  {k}: status={v.get('status')}, dist={v.get('distance_km')} km, time={v.get('time_minutes')} mins")

if __name__ == "__main__":
    asyncio.run(test_endpoint())

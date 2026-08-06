import asyncio
import httpx

API_KEY = "7e57c95ce01147f38a78dab8029c635a"

async def test():
    url = f"https://api.geoapify.com/v2/places?categories=education.school,education.college,healthcare.hospital,public_transport,catering.restaurant,commercial.shopping_mall,service.financial.bank,leisure.park&filter=circle:77.6241999,12.9410352,5000&bias=proximity:77.6241999,12.9410352&limit=40&apiKey={API_KEY}"
    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            r = await client.get(url)
            print("HTTPX Status:", r.status_code)
            data = r.json()
            features = data.get("features", [])
            print("HTTPX Features count:", len(features))
            for f in features[:3]:
                print("  -", f.get("properties", {}).get("name"), f.get("properties", {}).get("categories"))
        except Exception as e:
            print("HTTPX Error:", e)

if __name__ == "__main__":
    asyncio.run(test())

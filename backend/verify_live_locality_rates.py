import httpx
import sys

# Ensure UTF-8 output encoding for Windows terminals
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def verify_live():
    client = httpx.Client(timeout=10.0)
    test_queries = [
        "Whitefield", "Koramangala", "HSR Layout", "Kanakpura Road", 
        "Sarjapur Road", "Electronic City", "Hebbal", "Yelahanka", 
        "JP Nagar", "Jayanagar", "Malleshwaram", "Raja Rajeshwari Nagar"
    ]
    
    print("\n" + "=" * 75)
    print(f"{'Locality Query':<25} | {'Live Avg Rate':<18} | {'Google Market Range':<25}")
    print("=" * 75)

    for q in test_queries:
        try:
            r = client.get(f"http://127.0.0.1:8000/api/v1/location/search-location?query={q}")
            if r.status_code == 200:
                data = r.json()
                avg_rate = data.get("estimated_price_sqft", 0)
                rng = data.get("price_range", "")
                print(f"{q:<25} | Rs. {avg_rate:,.2f} / sqft | {rng:<25}")
            else:
                print(f"{q:<25} | Status {r.status_code}: {r.text[:50]}")
        except Exception as e:
            print(f"{q:<25} | Connection Error (Is server running?): {e}")

if __name__ == "__main__":
    verify_live()

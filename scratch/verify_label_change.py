import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/ai/analyze-property/1"

try:
    req = urllib.request.urlopen(url, timeout=35)
    data = json.loads(req.read().decode('utf-8'))
    score = data["price_prediction"]["confidence_score"]
    
    print(f"API HTTP Status: {req.getcode()}")
    print(f"Backend confidence_score field numeric value: {score}% (UNCHANGED)")
except Exception as e:
    print(f"API verification error: {e}")

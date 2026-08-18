import urllib.request
import json

print("=== VERIFYING PDF REPORT AND ANALYZE PROPERTY ENDPOINTS ===")

# Test 1: PDF Report Endpoint
pdf_url = "http://127.0.0.1:8000/api/v1/ai/property-report/1/pdf"
try:
    req_pdf = urllib.request.urlopen(pdf_url, timeout=35)
    pdf_status = req_pdf.getcode()
    pdf_content_type = req_pdf.headers.get("Content-Type")
    pdf_data = req_pdf.read()
    
    print("\n--- TEST 1: PDF REPORT ENDPOINT ---")
    print(f"HTTP Status: {pdf_status}")
    print(f"Content-Type: {pdf_content_type}")
    print(f"PDF Generated Successfully: {'Yes' if len(pdf_data) > 1000 and pdf_data.startswith(b'%PDF') else 'No'}")
    print(f"PDF File Size: {len(pdf_data)} bytes")
except Exception as e:
    print(f"PDF test error: {e}")

# Test 2: Analyze Property Endpoint
ai_url = "http://127.0.0.1:8000/api/v1/ai/analyze-property/1"
try:
    req_ai = urllib.request.urlopen(ai_url, timeout=35)
    ai_status = req_ai.getcode()
    data = json.loads(req_ai.read().decode('utf-8'))
    
    print("\n--- TEST 2: ANALYZE PROPERTY ENDPOINT ---")
    print(f"HTTP Status: {ai_status}")
    print(f"Root Keys Present: {list(data.keys())}")
    print(f"Predicted Price: INR {round(data['price_prediction']['predicted_selling_price']):,}")
    print(f"Safety Rating: {data['safety_guard']['overall_rating']}")
    print(f"CNN Model: {data['image_ai']['cnn_model']}")
    print(f"TF-IDF Sentiment: {data['text_ai']['sentiment_label']}")
except Exception as e:
    print(f"Analyze property test error: {e}")

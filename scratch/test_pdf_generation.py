import urllib.request

url = "http://127.0.0.1:8000/api/v1/ai/property-report/1/pdf"
try:
    req = urllib.request.urlopen(url, timeout=30)
    status_code = req.getcode()
    content_type = req.headers.get("Content-Type")
    pdf_bytes = req.read()
    print(f"PDF Endpoint Status: {status_code}")
    print(f"Content-Type: {content_type}")
    print(f"Downloaded PDF size: {len(pdf_bytes)} bytes")
except Exception as e:
    print(f"PDF test error: {e}")

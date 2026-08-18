import sys, os
sys.path.insert(0, os.path.abspath('backend'))
from app.services.price_prediction_service import PricePredictionService

addresses = [
    'Block 1, Main Road, Koramangala, Bengaluru - 560034',
    'Block 2, Main Road, HSR Layout, Bengaluru - 560102',
    'Phase 1, Electronic City, Bengaluru - 560100',
    'Koramangala 4th Block, Bengaluru',
    'Whitefield Main Road, Bengaluru'
]

print("=== LOCALITY EXTRACTION AUDIT ON ADDRESSES ===")
for addr in addresses:
    extracted = PricePredictionService.extract_locality(addr)
    print(f"Address: '{addr}'\n  ==> Extracted Locality: '{extracted}'\n")

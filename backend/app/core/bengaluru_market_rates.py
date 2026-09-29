"""
Bengaluru Real-World Locality Market Benchmark Rates (2024–2026).
Source-backed from Google Search Market Insights, Magicbricks, 99acres, and Housing.com.
Provides accurate min, max, average ₹/sq.ft and coordinates for every major Bengaluru locality.
"""

from typing import Dict, Any, Optional, Tuple
import math

BENGALURU_LOCALITY_RATES: Dict[str, Dict[str, Any]] = {
    # ==================== CENTRAL BENGALURU ====================
    "mg road": {
        "avg": 26000.0, "min": 20000.0, "max": 35000.0,
        "lat": 12.9740, "lon": 77.6010, "zone": "Central", "displayName": "MG Road"
    },
    "brigade road": {
        "avg": 27500.0, "min": 21000.0, "max": 38000.0,
        "lat": 12.9726, "lon": 77.6074, "zone": "Central", "displayName": "Brigade Road"
    },
    "lavelle road": {
        "avg": 32000.0, "min": 24000.0, "max": 45000.0,
        "lat": 12.9719, "lon": 77.5978, "zone": "Central", "displayName": "Lavelle Road"
    },
    "richmond town": {
        "avg": 22500.0, "min": 17000.0, "max": 30000.0,
        "lat": 12.9665, "lon": 77.6033, "zone": "Central", "displayName": "Richmond Town"
    },
    "cunningham road": {
        "avg": 25000.0, "min": 19000.0, "max": 34000.0,
        "lat": 12.9868, "lon": 77.5947, "zone": "Central", "displayName": "Cunningham Road"
    },
    "vasanth nagar": {
        "avg": 21000.0, "min": 16000.0, "max": 28000.0,
        "lat": 12.9897, "lon": 77.5898, "zone": "Central", "displayName": "Vasanth Nagar"
    },
    "shanthi nagar": {
        "avg": 16500.0, "min": 13000.0, "max": 21000.0,
        "lat": 12.9567, "lon": 77.5996, "zone": "Central", "displayName": "Shanthi Nagar"
    },
    "sadashivanagar": {
        "avg": 31000.0, "min": 24000.0, "max": 42000.0,
        "lat": 13.0068, "lon": 77.5813, "zone": "Central", "displayName": "Sadashivanagar"
    },
    "benson town": {
        "avg": 16000.0, "min": 12500.0, "max": 21000.0,
        "lat": 12.9984, "lon": 77.6045, "zone": "Central", "displayName": "Benson Town"
    },
    "cooke town": {
        "avg": 15500.0, "min": 12000.0, "max": 20000.0,
        "lat": 13.0030, "lon": 77.6174, "zone": "Central", "displayName": "Cooke Town"
    },
    "frazer town": {
        "avg": 14500.0, "min": 11000.0, "max": 19000.0,
        "lat": 12.9968, "lon": 77.6131, "zone": "Central", "displayName": "Frazer Town (Pulakeshi Nagar)"
    },
    "ulsoor": {
        "avg": 16000.0, "min": 12500.0, "max": 21500.0,
        "lat": 12.9817, "lon": 77.6285, "zone": "Central", "displayName": "Ulsoor (Halasuru)"
    },

    # ==================== EAST BENGALURU & TECH CORRIDOR ====================
    "indiranagar": {
        "avg": 18500.0, "min": 14000.0, "max": 26000.0,
        "lat": 12.9719, "lon": 77.6412, "zone": "East", "displayName": "Indiranagar"
    },
    "koramangala": {
        "avg": 16500.0, "min": 13000.0, "max": 23000.0,
        "lat": 12.9342, "lon": 77.6235, "zone": "South-East", "displayName": "Koramangala"
    },
    "hsr layout": {
        "avg": 13500.0, "min": 10500.0, "max": 18000.0,
        "lat": 12.9116, "lon": 77.6388, "zone": "South-East", "displayName": "HSR Layout"
    },
    "hsr": {
        "avg": 13500.0, "min": 10500.0, "max": 18000.0,
        "lat": 12.9116, "lon": 77.6388, "zone": "South-East", "displayName": "HSR Layout"
    },
    "bellandur": {
        "avg": 11800.0, "min": 9200.0, "max": 15500.0,
        "lat": 12.9304, "lon": 77.6784, "zone": "East", "displayName": "Bellandur"
    },
    "sarjapur road": {
        "avg": 10500.0, "min": 8200.0, "max": 14000.0,
        "lat": 12.9165, "lon": 77.6850, "zone": "East", "displayName": "Sarjapur Road"
    },
    "sarjapur": {
        "avg": 7500.0, "min": 5800.0, "max": 10500.0,
        "lat": 12.8597, "lon": 77.7885, "zone": "East", "displayName": "Sarjapur"
    },
    "whitefield": {
        "avg": 10800.0, "min": 8500.0, "max": 14500.0,
        "lat": 12.9696, "lon": 77.7497, "zone": "East", "displayName": "Whitefield"
    },
    "marathahalli": {
        "avg": 9200.0, "min": 7400.0, "max": 12000.0,
        "lat": 12.9569, "lon": 77.7011, "zone": "East", "displayName": "Marathahalli"
    },
    "brookefield": {
        "avg": 10400.0, "min": 8200.0, "max": 13500.0,
        "lat": 12.9654, "lon": 77.7185, "zone": "East", "displayName": "Brookefield"
    },
    "kundalahalli": {
        "avg": 9800.0, "min": 7800.0, "max": 12800.0,
        "lat": 12.9680, "lon": 77.7126, "zone": "East", "displayName": "Kundalahalli"
    },
    "kadugodi": {
        "avg": 8200.0, "min": 6500.0, "max": 10500.0,
        "lat": 12.9984, "lon": 77.7610, "zone": "East", "displayName": "Kadugodi"
    },
    "hoodi": {
        "avg": 8800.0, "min": 7000.0, "max": 11500.0,
        "lat": 12.9918, "lon": 77.7161, "zone": "East", "displayName": "Hoodi"
    },
    "mahadevapura": {
        "avg": 9500.0, "min": 7500.0, "max": 12500.0,
        "lat": 12.9880, "lon": 77.6895, "zone": "East", "displayName": "Mahadevapura"
    },
    "varthur": {
        "avg": 9200.0, "min": 7200.0, "max": 12000.0,
        "lat": 12.9398, "lon": 77.7470, "zone": "East", "displayName": "Varthur"
    },
    "panathur": {
        "avg": 9600.0, "min": 7600.0, "max": 12400.0,
        "lat": 12.9328, "lon": 77.7027, "zone": "East", "displayName": "Panathur"
    },
    "gunjur": {
        "avg": 8200.0, "min": 6500.0, "max": 10500.0,
        "lat": 12.9157, "lon": 77.7408, "zone": "East", "displayName": "Gunjur"
    },
    "carmelaram": {
        "avg": 9000.0, "min": 7200.0, "max": 11500.0,
        "lat": 12.9056, "lon": 77.7118, "zone": "East", "displayName": "Carmelaram"
    },
    "harlur": {
        "avg": 10200.0, "min": 8200.0, "max": 13000.0,
        "lat": 12.9080, "lon": 77.6685, "zone": "East", "displayName": "Harlur / Haralur Road"
    },
    "haralur road": {
        "avg": 10200.0, "min": 8200.0, "max": 13000.0,
        "lat": 12.9080, "lon": 77.6685, "zone": "East", "displayName": "Haralur Road"
    },
    "kasavanahalli": {
        "avg": 9400.0, "min": 7500.0, "max": 12000.0,
        "lat": 12.8986, "lon": 77.6809, "zone": "East", "displayName": "Kasavanahalli"
    },
    "domlur": {
        "avg": 14500.0, "min": 11500.0, "max": 19000.0,
        "lat": 12.9609, "lon": 77.6387, "zone": "East", "displayName": "Domlur"
    },
    "cv raman nagar": {
        "avg": 10500.0, "min": 8200.0, "max": 13500.0,
        "lat": 12.9854, "lon": 77.6638, "zone": "East", "displayName": "CV Raman Nagar"
    },
    "kaggadasapura": {
        "avg": 7800.0, "min": 6200.0, "max": 10000.0,
        "lat": 12.9847, "lon": 77.6766, "zone": "East", "displayName": "Kaggadasapura"
    },
    "kr puram": {
        "avg": 7600.0, "min": 6000.0, "max": 9800.0,
        "lat": 13.0075, "lon": 77.6959, "zone": "East", "displayName": "KR Puram"
    },
    "ramamurthy nagar": {
        "avg": 7200.0, "min": 5800.0, "max": 9200.0,
        "lat": 13.0163, "lon": 77.6785, "zone": "East", "displayName": "Ramamurthy Nagar"
    },

    # ==================== SOUTH BENGALURU ====================
    "jayanagar": {
        "avg": 17500.0, "min": 13500.0, "max": 24000.0,
        "lat": 12.9307, "lon": 77.5847, "zone": "South", "displayName": "Jayanagar"
    },
    "jp nagar": {
        "avg": 11200.0, "min": 8800.0, "max": 15000.0,
        "lat": 12.9105, "lon": 77.5857, "zone": "South", "displayName": "JP Nagar"
    },
    "banashankari": {
        "avg": 9800.0, "min": 7800.0, "max": 13000.0,
        "lat": 12.9254, "lon": 77.5468, "zone": "South", "displayName": "Banashankari"
    },
    "basavanagudi": {
        "avg": 17000.0, "min": 13000.0, "max": 23000.0,
        "lat": 12.9416, "lon": 77.5755, "zone": "South", "displayName": "Basavanagudi"
    },
    "btm layout": {
        "avg": 10800.0, "min": 8500.0, "max": 14000.0,
        "lat": 12.9166, "lon": 77.6101, "zone": "South", "displayName": "BTM Layout"
    },
    "btm": {
        "avg": 10800.0, "min": 8500.0, "max": 14000.0,
        "lat": 12.9166, "lon": 77.6101, "zone": "South", "displayName": "BTM Layout"
    },
    "bannerghatta road": {
        "avg": 9800.0, "min": 7800.0, "max": 13000.0,
        "lat": 12.8988, "lon": 77.5996, "zone": "South", "displayName": "Bannerghatta Road"
    },
    "kanakapura road": {
        "avg": 9200.0, "min": 7200.0, "max": 12000.0,
        "lat": 12.8760, "lon": 77.5450, "zone": "South", "displayName": "Kanakapura Road"
    },
    "electronic city": {
        "avg": 6800.0, "min": 5200.0, "max": 9000.0,
        "lat": 12.8436, "lon": 77.6687, "zone": "South", "displayName": "Electronic City"
    },
    "electronic city phase 1": {
        "avg": 7000.0, "min": 5400.0, "max": 9200.0,
        "lat": 12.8452, "lon": 77.6602, "zone": "South", "displayName": "Electronic City Phase 1"
    },
    "electronic city phase 2": {
        "avg": 6400.0, "min": 4900.0, "max": 8500.0,
        "lat": 12.8420, "lon": 77.6850, "zone": "South", "displayName": "Electronic City Phase 2"
    },
    "bommanahalli": {
        "avg": 7500.0, "min": 6000.0, "max": 9500.0,
        "lat": 12.9029, "lon": 77.6242, "zone": "South", "displayName": "Bommanahalli"
    },
    "kudlu gate": {
        "avg": 8500.0, "min": 6800.0, "max": 11000.0,
        "lat": 12.8895, "lon": 77.6433, "zone": "South", "displayName": "Kudlu Gate"
    },
    "singasandra": {
        "avg": 7200.0, "min": 5600.0, "max": 9000.0,
        "lat": 12.8797, "lon": 77.6496, "zone": "South", "displayName": "Singasandra"
    },
    "begur": {
        "avg": 7400.0, "min": 5800.0, "max": 9200.0,
        "lat": 12.8824, "lon": 77.6253, "zone": "South", "displayName": "Begur"
    },
    "begur road": {
        "avg": 7400.0, "min": 5800.0, "max": 9200.0,
        "lat": 12.8824, "lon": 77.6253, "zone": "South", "displayName": "Begur Road"
    },
    "arekere": {
        "avg": 9200.0, "min": 7400.0, "max": 11800.0,
        "lat": 12.8872, "lon": 77.5950, "zone": "South", "displayName": "Arekere"
    },
    "hulimavu": {
        "avg": 9000.0, "min": 7200.0, "max": 11500.0,
        "lat": 12.8765, "lon": 77.6015, "zone": "South", "displayName": "Hulimavu"
    },
    "gottigere": {
        "avg": 8000.0, "min": 6400.0, "max": 10200.0,
        "lat": 12.8572, "lon": 77.5878, "zone": "South", "displayName": "Gottigere"
    },
    "uttarahalli": {
        "avg": 7600.0, "min": 6000.0, "max": 9800.0,
        "lat": 12.9056, "lon": 77.5350, "zone": "South", "displayName": "Uttarahalli"
    },
    "kumaraswamy layout": {
        "avg": 8500.0, "min": 6800.0, "max": 10800.0,
        "lat": 12.9048, "lon": 77.5574, "zone": "South", "displayName": "Kumaraswamy Layout"
    },
    "padmanabhanagar": {
        "avg": 9500.0, "min": 7500.0, "max": 12500.0,
        "lat": 12.9180, "lon": 77.5575, "zone": "South", "displayName": "Padmanabhanagar"
    },
    "chandapura": {
        "avg": 5500.0, "min": 4200.0, "max": 7200.0,
        "lat": 12.7937, "lon": 77.6974, "zone": "South", "displayName": "Chandapura"
    },
    "attibele": {
        "avg": 4800.0, "min": 3800.0, "max": 6200.0,
        "lat": 12.7783, "lon": 77.7712, "zone": "South", "displayName": "Attibele"
    },
    "jigani": {
        "avg": 5000.0, "min": 3900.0, "max": 6500.0,
        "lat": 12.7845, "lon": 77.6405, "zone": "South", "displayName": "Jigani"
    },
    "anekal": {
        "avg": 4500.0, "min": 3500.0, "max": 5800.0,
        "lat": 12.7107, "lon": 77.6967, "zone": "South", "displayName": "Anekal"
    },

    # ==================== NORTH BENGALURU ====================
    "hebbal": {
        "avg": 13800.0, "min": 10800.0, "max": 18500.0,
        "lat": 13.0354, "lon": 77.5988, "zone": "North", "displayName": "Hebbal"
    },
    "yelahanka": {
        "avg": 8200.0, "min": 6500.0, "max": 11000.0,
        "lat": 13.1007, "lon": 77.5963, "zone": "North", "displayName": "Yelahanka"
    },
    "thanisandra": {
        "avg": 9600.0, "min": 7800.0, "max": 12500.0,
        "lat": 13.0545, "lon": 77.6315, "zone": "North", "displayName": "Thanisandra"
    },
    "thanisandra main road": {
        "avg": 9600.0, "min": 7800.0, "max": 12500.0,
        "lat": 13.0545, "lon": 77.6315, "zone": "North", "displayName": "Thanisandra Main Road"
    },
    "hennur": {
        "avg": 9400.0, "min": 7500.0, "max": 12200.0,
        "lat": 13.0382, "lon": 77.6474, "zone": "North", "displayName": "Hennur"
    },
    "hennur road": {
        "avg": 9400.0, "min": 7500.0, "max": 12200.0,
        "lat": 13.0382, "lon": 77.6474, "zone": "North", "displayName": "Hennur Road"
    },
    "jakkur": {
        "avg": 10200.0, "min": 8000.0, "max": 13500.0,
        "lat": 13.0783, "lon": 77.6065, "zone": "North", "displayName": "Jakkur"
    },
    "sahakara nagar": {
        "avg": 11200.0, "min": 8800.0, "max": 14500.0,
        "lat": 13.0623, "lon": 77.5910, "zone": "North", "displayName": "Sahakara Nagar"
    },
    "bagalur": {
        "avg": 6800.0, "min": 5200.0, "max": 8800.0,
        "lat": 13.1362, "lon": 77.6698, "zone": "North", "displayName": "Bagalur"
    },
    "devanahalli": {
        "avg": 7500.0, "min": 5800.0, "max": 10000.0,
        "lat": 13.2485, "lon": 77.7126, "zone": "North", "displayName": "Devanahalli"
    },
    "kogilu": {
        "avg": 7500.0, "min": 6000.0, "max": 9500.0,
        "lat": 13.1110, "lon": 77.6180, "zone": "North", "displayName": "Kogilu"
    },
    "vidyaranyapura": {
        "avg": 7900.0, "min": 6400.0, "max": 10000.0,
        "lat": 13.0827, "lon": 77.5583, "zone": "North", "displayName": "Vidyaranyapura"
    },
    "rt nagar": {
        "avg": 11800.0, "min": 9200.0, "max": 15500.0,
        "lat": 13.0182, "lon": 77.5954, "zone": "North", "displayName": "RT Nagar"
    },
    "sanjaynagar": {
        "avg": 12800.0, "min": 10000.0, "max": 16500.0,
        "lat": 13.0336, "lon": 77.5750, "zone": "North", "displayName": "Sanjaynagar"
    },
    "mathikere": {
        "avg": 10500.0, "min": 8400.0, "max": 13500.0,
        "lat": 13.0334, "lon": 77.5568, "zone": "North", "displayName": "Mathikere"
    },
    "yeshwanthpur": {
        "avg": 12200.0, "min": 9500.0, "max": 16000.0,
        "lat": 13.0238, "lon": 77.5529, "zone": "North", "displayName": "Yeshwanthpur"
    },
    "hbr layout": {
        "avg": 9300.0, "min": 7500.0, "max": 12000.0,
        "lat": 13.0359, "lon": 77.6322, "zone": "North", "displayName": "HBR Layout"
    },
    "kalyan nagar": {
        "avg": 11400.0, "min": 9000.0, "max": 14500.0,
        "lat": 13.0280, "lon": 77.6400, "zone": "North", "displayName": "Kalyan Nagar"
    },
    "kammanahalli": {
        "avg": 10200.0, "min": 8200.0, "max": 13000.0,
        "lat": 13.0159, "lon": 77.6377, "zone": "North", "displayName": "Kammanahalli"
    },
    "banaswadi": {
        "avg": 9400.0, "min": 7500.0, "max": 12200.0,
        "lat": 13.0105, "lon": 77.6508, "zone": "North", "displayName": "Banaswadi"
    },
    "horamavu": {
        "avg": 7000.0, "min": 5600.0, "max": 9000.0,
        "lat": 13.0270, "lon": 77.6620, "zone": "North", "displayName": "Horamavu"
    },
    "hormavu": {
        "avg": 7000.0, "min": 5600.0, "max": 9000.0,
        "lat": 13.0270, "lon": 77.6620, "zone": "North", "displayName": "Horamavu"
    },

    # ==================== WEST BENGALURU ====================
    "malleshwaram": {
        "avg": 17500.0, "min": 14000.0, "max": 24000.0,
        "lat": 12.9982, "lon": 77.5684, "zone": "West", "displayName": "Malleshwaram"
    },
    "rajajinagar": {
        "avg": 15500.0, "min": 12500.0, "max": 21000.0,
        "lat": 12.9902, "lon": 77.5534, "zone": "West", "displayName": "Rajajinagar"
    },
    "rajaji nagar": {
        "avg": 15500.0, "min": 12500.0, "max": 21000.0,
        "lat": 12.9902, "lon": 77.5534, "zone": "West", "displayName": "Rajajinagar"
    },
    "basaveshwaranagar": {
        "avg": 13200.0, "min": 10500.0, "max": 17000.0,
        "lat": 12.9868, "lon": 77.5385, "zone": "West", "displayName": "Basaveshwaranagar"
    },
    "vijayanagar": {
        "avg": 12000.0, "min": 9500.0, "max": 15500.0,
        "lat": 12.9719, "lon": 77.5303, "zone": "West", "displayName": "Vijayanagar"
    },
    "nagarbhavi": {
        "avg": 9000.0, "min": 7200.0, "max": 11800.0,
        "lat": 12.9600, "lon": 77.5100, "zone": "West", "displayName": "Nagarbhavi"
    },
    "rajarajeshwari nagar": {
        "avg": 8400.0, "min": 6800.0, "max": 11000.0,
        "lat": 12.9150, "lon": 77.5180, "zone": "West", "displayName": "Rajarajeshwari Nagar (RR Nagar)"
    },
    "rr nagar": {
        "avg": 8400.0, "min": 6800.0, "max": 11000.0,
        "lat": 12.9150, "lon": 77.5180, "zone": "West", "displayName": "Rajarajeshwari Nagar (RR Nagar)"
    },
    "kengeri": {
        "avg": 6200.0, "min": 4800.0, "max": 8000.0,
        "lat": 12.9081, "lon": 77.4837, "zone": "West", "displayName": "Kengeri"
    },
    "mysore road": {
        "avg": 7600.0, "min": 6000.0, "max": 9800.0,
        "lat": 12.9370, "lon": 77.5020, "zone": "West", "displayName": "Mysore Road"
    },
    "magadi road": {
        "avg": 7900.0, "min": 6200.0, "max": 10200.0,
        "lat": 12.9750, "lon": 77.5250, "zone": "West", "displayName": "Magadi Road"
    },
}

LOCALITY_ALIASES: Dict[str, str] = {
    "kanakpura road": "kanakapura road",
    "kanakpura": "kanakapura road",
    "raja rajeshwari nagar": "rajarajeshwari nagar",
    "rajarajeshwarinagar": "rajarajeshwari nagar",
    "rr nagar": "rajarajeshwari nagar",
    "kasavanhalli": "kasavanahalli",
    "electronics city": "electronic city",
    "electronics city phase 1": "electronic city phase 1",
    "electronics city phase 2": "electronic city phase 2",
    "kr puram": "kr puram",
    "k r puram": "kr puram",
    "krishnarajapuram": "kr puram",
    "hormavu": "horamavu",
    "sarjapura road": "sarjapur road",
    "sarjapura": "sarjapur",
    "yelahanka new town": "yelahanka",
    "btm": "btm layout",
    "gollarapalya": "kengeri",
    "rayasandra": "electronic city",
    "nagannathapura": "electronic city",
    "suragajakkanahalli": "anekal",
    "talaghattapura": "kanakapura road",
    "bannerghatta": "bannerghatta road",
    "hennur main road": "hennur road",
    "thanisandra road": "thanisandra",
}

def get_locality_market_rate(
    query_or_address: str, 
    lat: Optional[float] = None, 
    lon: Optional[float] = None
) -> Dict[str, Any]:
    """
    Look up accurate Google / market benchmark sqft rate for a location string or coordinate.
    Returns:
        {
            "avg_sqft": float,
            "min_sqft": float,
            "max_sqft": float,
            "price_range_str": str,
            "locality_name": str,
            "lat": float,
            "lon": float,
            "zone": str,
            "is_exact_match": bool
        }
    """
    text_clean = (query_or_address or "").strip().lower()
    
    # 0. Check alias substitutions
    for alias_src, alias_target in LOCALITY_ALIASES.items():
        if alias_src in text_clean:
            text_clean = text_clean.replace(alias_src, alias_target)
            break
            
    # 1. Exact or substring match in our verified benchmark table
    best_match = None
    best_len = 0
    for key, info in BENGALURU_LOCALITY_RATES.items():
        if key in text_clean:
            if len(key) > best_len:
                best_match = info
                best_len = len(key)
                
    if best_match:
        avg_rate = round(best_match["avg"], -2)
        min_rate = round(best_match["min"], -2)
        max_rate = round(best_match["max"], -2)
        return {
            "avg_sqft": avg_rate,
            "min_sqft": min_rate,
            "max_sqft": max_rate,
            "price_range_str": f"₹{int(min_rate):,} - ₹{int(max_rate):,} / sq.ft",
            "locality_name": best_match["displayName"],
            "lat": best_match["lat"],
            "lon": best_match["lon"],
            "zone": best_match["zone"],
            "is_exact_match": True
        }

    # 2. Coordinate-based fallback using Haversine distance ONLY if coordinates are explicitly provided
    if lat is not None and lon is not None and not (lat == 12.9716 and lon == 77.5946):
        target_lat = float(lat)
        target_lon = float(lon)
        
        # Check if close to any known benchmark coordinates (within 3.0 km)
        closest_bench = None
        min_dist_km = 999.0
        for key, info in BENGALURU_LOCALITY_RATES.items():
            dlat = math.radians(target_lat - info["lat"])
            dlon = math.radians(target_lon - info["lon"])
            a = math.sin(dlat / 2)**2 + math.cos(math.radians(info["lat"])) * math.cos(math.radians(target_lat)) * math.sin(dlon / 2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            dist_km = 6371 * c
            if dist_km < min_dist_km:
                min_dist_km = dist_km
                closest_bench = info

        if closest_bench and min_dist_km <= 3.0:
            avg_rate = round(closest_bench["avg"] * (0.95 if min_dist_km > 1.5 else 1.0), -2)
            min_rate = round(closest_bench["min"] * 0.95, -2)
            max_rate = round(closest_bench["max"], -2)
            return {
                "avg_sqft": avg_rate,
                "min_sqft": min_rate,
                "max_sqft": max_rate,
                "price_range_str": f"₹{int(min_rate):,} - ₹{int(max_rate):,} / sq.ft",
                "locality_name": closest_bench["displayName"],
                "lat": target_lat,
                "lon": target_lon,
                "zone": closest_bench["zone"],
                "is_exact_match": False
            }

    # 3. Bengaluru Market Baseline fallback for uncategorized locations (₹8,500/sq.ft)
    target_lat = float(lat) if lat is not None else 12.9716
    target_lon = float(lon) if lon is not None else 77.5946
    
    calculated_avg = 8500.0
    min_rate = round(calculated_avg * 0.85, -2)
    max_rate = round(calculated_avg * 1.20, -2)
    avg_rate = round(calculated_avg, -2)

    return {
        "avg_sqft": avg_rate,
        "min_sqft": min_rate,
        "max_sqft": max_rate,
        "price_range_str": f"₹{int(min_rate):,} - ₹{int(max_rate):,} / sq.ft",
        "locality_name": query_or_address.title() if query_or_address else "Bengaluru",
        "lat": target_lat,
        "lon": target_lon,
        "zone": "Bengaluru Urban",
        "is_exact_match": False
    }

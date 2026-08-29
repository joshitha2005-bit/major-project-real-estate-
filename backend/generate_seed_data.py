import json
import hashlib

LOCALITIES = [
    {"name": "Koramangala", "lat": 12.9357, "lon": 77.6240, "base_price": 12500, "pin": "560034"},
    {"name": "Electronic City", "lat": 12.8436, "lon": 77.6687, "base_price": 5600, "pin": "560100"},
    {"name": "Whitefield", "lat": 12.9696, "lon": 77.7497, "base_price": 7800, "pin": "560066"},
    {"name": "HSR Layout", "lat": 12.9116, "lon": 77.6389, "base_price": 9500, "pin": "560102"},
    {"name": "Indiranagar", "lat": 12.9733, "lon": 77.6405, "base_price": 14000, "pin": "560038"},
    {"name": "Marathahalli", "lat": 12.9591, "lon": 77.6974, "base_price": 7200, "pin": "560037"},
    {"name": "Bellandur", "lat": 12.9279, "lon": 77.6756, "base_price": 8200, "pin": "560103"},
    {"name": "Sarjapur Road", "lat": 12.9107, "lon": 77.6970, "base_price": 6800, "pin": "560035"},
    {"name": "JP Nagar", "lat": 12.9077, "lon": 77.5854, "base_price": 8800, "pin": "560078"},
    {"name": "Jayanagar", "lat": 12.9250, "lon": 77.5938, "base_price": 11500, "pin": "560041"},
    {"name": "Banashankari", "lat": 12.9255, "lon": 77.5468, "base_price": 7500, "pin": "560085"},
    {"name": "Hebbal", "lat": 13.0358, "lon": 77.5970, "base_price": 9200, "pin": "560024"},
    {"name": "Yelahanka", "lat": 13.1007, "lon": 77.5963, "base_price": 6100, "pin": "560064"},
    {"name": "KR Puram", "lat": 13.0075, "lon": 77.6959, "base_price": 5800, "pin": "560036"},
    {"name": "Mahadevapura", "lat": 12.9902, "lon": 77.6874, "base_price": 6400, "pin": "560048"},
    {"name": "BTM Layout", "lat": 12.9166, "lon": 77.6101, "base_price": 8500, "pin": "560076"},
    {"name": "Bannerghatta Road", "lat": 12.8950, "lon": 77.5990, "base_price": 7200, "pin": "560076"},
    {"name": "Thanisandra", "lat": 13.0547, "lon": 77.6338, "base_price": 6900, "pin": "560077"},
    {"name": "Hennur", "lat": 13.0258, "lon": 77.6341, "base_price": 6500, "pin": "560043"},
    {"name": "Vijayanagar", "lat": 12.9708, "lon": 77.5350, "base_price": 8200, "pin": "560040"},
    {"name": "Rajajinagar", "lat": 12.9882, "lon": 77.5549, "base_price": 10500, "pin": "560010"},
    {"name": "Malleshwaram", "lat": 13.0031, "lon": 77.5643, "base_price": 13000, "pin": "560003"},
    {"name": "Basavanagudi", "lat": 12.9421, "lon": 77.5752, "base_price": 11000, "pin": "560004"},
    {"name": "Brookefield", "lat": 12.9658, "lon": 77.7183, "base_price": 7500, "pin": "560037"},
    {"name": "Chandapura", "lat": 12.8004, "lon": 77.7063, "base_price": 4500, "pin": "560099"}
]

PROPERTY_TYPES = [
    {"type": "Apartment", "bhk": 2, "area": 1200, "baths": 2, "balc": 1},
    {"type": "Apartment", "bhk": 3, "area": 1650, "baths": 3, "balc": 2},
    {"type": "Villa", "bhk": 4, "area": 3200, "baths": 4, "balc": 3},
    {"type": "Independent House", "bhk": 3, "area": 2200, "baths": 3, "balc": 2},
    {"type": "Plot", "bhk": 0, "area": 1800, "baths": 0, "balc": 0}
]

BUILDERS = ["Prestige", "Sobha", "Brigade", "Godrej", "Puravankara", "Salarpuria Sattva", "Mantri", "Assetz"]
OWNERS = [
    ("Rajesh Kumar", "+91 98860 12345"),
    ("Suresh Narayanan", "+91 98450 67890"),
    ("Anil Kumar", "+91 99001 88345"),
    ("Vikram Malhotra", "+91 98110 99887"),
    ("Priya Sharma", "+91 98801 33456"),
    ("Deepak Mehta", "+91 97400 22341"),
    ("Karthik Reddy", "+91 98440 66789"),
    ("Siddharth Rao", "+91 98866 55432"),
    ("Naveen Hegde", "+91 98451 77654"),
    ("Sunil Dutt", "+91 98800 33210")
]

IMAGES_POOL = [
    [
        "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1567496898669-ee935f5f647a?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=800&q=80"
    ],
    [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=800&q=80"
    ]
]

all_properties = []

count = 1
for loc in LOCALITIES:
    for i in range(4):  # 4 properties per locality = 100 properties total
        ptype_info = PROPERTY_TYPES[i % len(PROPERTY_TYPES)]
        builder = BUILDERS[(count + i) % len(BUILDERS)]
        owner = OWNERS[(count + i) % len(OWNERS)]
        ptype_lower = ptype_info["type"].lower()
        title = f"{builder} {loc['name']} {ptype_info['bhk']}BHK {ptype_info['type']}" if ptype_info['bhk'] > 0 else f"{builder} {loc['name']} Premium {ptype_info['type']}"
        h_str = f"{title}_{count}"
        h = hashlib.md5(h_str.encode('utf-8')).hexdigest()
        h_val = int(h, 16)
        
        if ptype_lower == "apartment":
            images = [f"/static/images/apartment_{(h_val % 15) + 1}.jpg"]
        elif ptype_lower == "villa":
            images = [f"/static/images/villa_{(h_val % 15) + 1}.jpg"]
        elif ptype_lower == "independent house":
            images = [f"/static/images/house_{(h_val % 15) + 1}.jpg"]
        else:
            images = [f"/static/images/apartment_{(h_val % 15) + 1}.jpg"]
        
        # Vary area slightly
        area = ptype_info["area"] + ((i * 120) % 350)
        
        # Calculate price based on locality base price
        price = round((loc["base_price"] * area * (1 + (i * 0.08))), -4)
        
        # Micro offsets for coordinates within locality
        lat_offset = (i * 0.003) - 0.0045
        lon_offset = (i * 0.0025) - 0.003
        
        address = f"Block {i+1}, Main Road, {loc['name']}, Bengaluru - {loc['pin']}"
        
        desc = (
            f"Premium {ptype_info['type']} in prime {loc['name']} built by {builder}. "
            f"Features {ptype_info['bhk']} BHK spacious layout, modern interior woodwork, "
            f"24/7 security, power backup, covered parking, and close access to schools, hospitals, and Metro connectivity."
        )
        
        prop_rec = {
            "title": title,
            "property_type": ptype_info["type"],
            "bhk": ptype_info["bhk"],
            "area_sqft": float(area),
            "bathrooms": ptype_info["baths"],
            "balconies": ptype_info["balc"],
            "floor": (i * 2) + 1 if ptype_info["type"] == "Apartment" else 1,
            "total_floors": 12 if ptype_info["type"] == "Apartment" else 2,
            "property_age": "1-5 yrs" if i % 2 == 0 else "New",
            "facing": ["East", "North", "North-East", "West"][i % 4],
            "parking": "Covered" if ptype_info["type"] != "Plot" else "None",
            "furnishing": "Semi-Furnished" if i % 2 == 0 else "Fully Furnished",
            "price": float(price),
            "address": address,
            "latitude": round(loc["lat"] + lat_offset, 6),
            "longitude": round(loc["lon"] + lon_offset, 6),
            "owner_name": owner[0],
            "owner_phone": owner[1],
            "description": desc,
            "images": images
        }
        all_properties.append(prop_rec)
        count += 1

print(f"Total properties generated: {len(all_properties)}")

# Write to file
seed_service_code = f'''from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.user import User
from app.models.property import Property
from app.core.security import get_password_hash

SEEDED_PROPERTIES = {json.dumps(all_properties, indent=4)}

class SeedService:
    @staticmethod
    def seed_properties(db: Session):
        """Seed 100+ realistic Bangalore locality properties into database on startup."""
        try:
            # Check SQLite schema columns for properties table
            try:
                db.execute(text("ALTER TABLE properties ADD COLUMN owner_name VARCHAR(255) DEFAULT 'PropPulse Verified Owner'"))
                db.commit()
            except Exception:
                db.rollback()

            try:
                db.execute(text("ALTER TABLE properties ADD COLUMN owner_phone VARCHAR(50) DEFAULT '+91 98860 12345'"))
                db.commit()
            except Exception:
                db.rollback()

            # Dynamic migration for Phase 2 columns
            NEW_COLUMNS = [
                ("listing_type", "VARCHAR(100) DEFAULT 'Buy'"),
                ("locality", "VARCHAR(255) DEFAULT ''"),
                ("amenities", "JSON DEFAULT '[]'"),
                ("street_view_available", "BOOLEAN DEFAULT 0"),
                ("seller_type", "VARCHAR(100) DEFAULT 'Owner'"),
                ("seller_name", "VARCHAR(255) DEFAULT 'PropPulse Verified Seller'"),
                ("phone", "VARCHAR(100) DEFAULT '+91 98860 12345'"),
                ("verification_status", "VARCHAR(100) DEFAULT 'Verified'"),
                ("source_type", "VARCHAR(100) DEFAULT 'demo_dataset'"),
                ("source", "VARCHAR(255) DEFAULT 'PropPulse Direct'"),
                ("source_url", "VARCHAR(500) DEFAULT ''"),
                ("image_source", "VARCHAR(500) DEFAULT ''"),
                ("verified", "BOOLEAN DEFAULT 1"),
                ("updated_at", "DATETIME DEFAULT NULL")

            ]
            for col_name, col_type in NEW_COLUMNS:
                try:
                    db.execute(text(f"ALTER TABLE properties ADD COLUMN {{col_name}} {{col_type}}"))
                    db.commit()
                except Exception:
                    db.rollback()

            # Check if default admin user exists
            default_user = db.query(User).first()
            if not default_user:
                default_user = User(
                    email="admin@realestateai.com",
                    full_name="Real Estate AI Admin",
                    hashed_password=get_password_hash("Admin123!"),
                    is_active=True
                )
                db.add(default_user)
                db.commit()
                db.refresh(default_user)

            # Check existing properties count
            existing_count = db.query(Property).count()
            if existing_count < 90:
                print("Seeding 100+ realistic Bangalore locality properties into DB...")
                db.query(Property).delete()
                db.commit()

                for idx, item in enumerate(SEEDED_PROPERTIES):
                    # Extract locality name
                    title_words = item["title"].split()
                    locality_clean = ""
                    for word in title_words:
                        w_lower = word.lower()
                        if w_lower in ["koramangala", "whitefield", "hsr", "indiranagar", "electronic", "chandapura", "marathahalli", "bellandur", "sarjapur", "jp", "jayanagar", "hebbal", "yelahanka", "banashankari", "kr", "mahadevapura", "btm"]:
                            locality_clean = word
                            break
                    if not locality_clean:
                        parts = item["address"].split(",")
                        if len(parts) > 2:
                            locality_clean = parts[2].strip().replace("Bengaluru", "").replace("-", "").strip()
                        else:
                            locality_clean = "Bengaluru"

                    listing_type = "Rent" if idx % 3 == 0 else "Buy"
                    street_view_avail = True if idx % 2 == 0 else False

                    amenities_list = ["Security", "Power Backup", "Water Supply"]
                    if item["property_type"] == "Apartment":
                        amenities_list += ["Lift", "Gym", "Clubhouse"]
                    elif item["property_type"] == "Villa":
                        amenities_list += ["Private Garden", "Swimming Pool", "Car Parking"]

                    p = Property(
                        user_id=default_user.id,
                        title=item["title"],
                        property_type=item["property_type"],
                        listing_type=listing_type,
                        bhk=item["bhk"],
                        area_sqft=item["area_sqft"],
                        bathrooms=item["bathrooms"],
                        balconies=item["balconies"],
                        floor=item["floor"],
                        total_floors=item["total_floors"],
                        property_age=item["property_age"],
                        facing=item["facing"],
                        parking=item["parking"],
                        furnishing=item["furnishing"],
                        price=item["price"],
                        description=item["description"],
                        address=item["address"],
                        locality=locality_clean,
                        latitude=item["latitude"],
                        longitude=item["longitude"],
                        owner_name=item["owner_name"],
                        owner_phone=item["owner_phone"],
                        images=item["images"],
                        nearby_places=[],
                        amenities=amenities_list,
                        street_view_available=street_view_avail,
                        seller_type="Owner" if idx % 2 == 0 else "Broker",
                        seller_name=item["owner_name"],
                        phone=item["owner_phone"],
                        verification_status="Historical / Research",
                        source_type="demo_dataset",
                        source="Kaggle Research Dataset",
                        verified=False
                    )
                    db.add(p)
                db.commit()
                print(f"Successfully seeded {{len(SEEDED_PROPERTIES)}} properties into database!")
        except Exception as e:
            print(f"Error seeding properties: {{e}}")
'''

with open("app/services/seed_service.py", "w", encoding="utf-8") as f:
    f.write(seed_service_code)

print("Saved seed_service.py successfully!")

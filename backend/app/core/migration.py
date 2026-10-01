import os
import sqlite3
from app.core.config import settings

def run_migrations(target_path: str = None):
    """Safely apply database schema updates for role and subscription models."""
    if target_path:
        db_path = target_path
    else:
        db_url = settings.DATABASE_URL
        if not db_url.startswith("sqlite:///"):
            print(f"Migration: DATABASE_URL is not sqlite ({db_url}). Skipping manual migration.")
            return

        db_path = db_url.replace("sqlite:///", "")
    
    # Resolve relative paths relative to backend CWD
    if not os.path.isabs(db_path):
        # Locate it relative to backend root
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        db_path = os.path.join(backend_dir, db_path)

    print(f"Migration: Checking database file at {db_path}...")
    if not os.path.exists(db_path):
        print("Migration: Database file does not exist yet. It will be created by SQLAlchemy.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Check if 'users' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if 'role' column exists in 'users'
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "role" not in columns:
                print("Migration: Adding 'role' column to 'users' table...")
                cursor.execute("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'USER'")
                # Update existing records to ensure they have 'USER'
                cursor.execute("UPDATE users SET role = 'USER' WHERE role IS NULL")
                conn.commit()
                print("Migration: 'role' column added successfully.")
            else:
                print("Migration: 'role' column already exists in 'users' table.")
        else:
            print("Migration: 'users' table does not exist. Handled by SQLAlchemy create_all.")
            
        # 2. Add 'subscriptions' table check/creation (as backup to SQLAlchemy create_all)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscriptions'")
        sub_exists = cursor.fetchone()
        if not sub_exists:
            print("Migration: Creating 'subscriptions' table (backup)...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    plan_name VARCHAR(50) DEFAULT 'PRO_299' NOT NULL,
                    status VARCHAR(50) DEFAULT 'FREE' NOT NULL,
                    start_date DATETIME NOT NULL,
                    end_date DATETIME,
                    payment_reference VARCHAR(255),
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                )
            ''')
            conn.commit()
            print("Migration: 'subscriptions' table created successfully.")

        # 3. Phase B migrations for properties table columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='properties'")
        prop_exists = cursor.fetchone()
        if prop_exists:
            cursor.execute("PRAGMA table_info(properties)")
            prop_cols = [col[1] for col in cursor.fetchall()]

            prop_new_cols = {
                "source_name": "VARCHAR(255) DEFAULT 'Bengaluru_House_Data.csv'",
                "listing_status": "VARCHAR(50) DEFAULT 'HISTORICAL'",
                "availability_date": "VARCHAR(100)",
                "listed_at": "DATETIME",
                "image_provenance": "VARCHAR(100) DEFAULT 'NO_IMAGE'",
                "image_count": "INTEGER DEFAULT 0",
                "owner_or_agent_type": "VARCHAR(50) DEFAULT 'Owner'",
                "contact_available": "BOOLEAN DEFAULT 0",
                "contact_source": "VARCHAR(255) DEFAULT 'Historical Dataset - No Contact'",
                "data_timestamp": "DATETIME",
                "anomaly_flags": "JSON DEFAULT '[]'",
                # Objective 20B columns
                "image_status": "VARCHAR(100) DEFAULT 'NO_IMAGE'",
                "image_source_url": "VARCHAR(500)",
                "image_authorization_status": "VARCHAR(100) DEFAULT 'NO_IMAGE'",
                "cnn_analysis_status": "VARCHAR(100) DEFAULT 'UNAVAILABLE'",
                "cnn_embedding_dimensions": "INTEGER",
                "contact_type": "VARCHAR(100) DEFAULT 'Owner'",
                "contact_number": "VARCHAR(100)",
                "contact_source_url": "VARCHAR(500)",
                "contact_verified_at": "DATETIME",
                "contact_display_permission": "BOOLEAN DEFAULT 0",
                "source_platform": "VARCHAR(100)",
                "source_listing_url": "VARCHAR(500)",
                "dataset_category": "VARCHAR(50) DEFAULT 'REFERENCE_HISTORICAL'",
                "is_main_ai_ready": "BOOLEAN DEFAULT 0" 
            }

            for col_name, col_type in prop_new_cols.items():
                if col_name not in prop_cols:
                    print(f"Migration: Adding '{col_name}' column to 'properties' table...")
                    cursor.execute(f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}")

            conn.commit()

        # 4. Phase B migrations for property_images table columns
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='property_images'")
        img_exists = cursor.fetchone()
        if img_exists:
            cursor.execute("PRAGMA table_info(property_images)")
            img_cols = [col[1] for col in cursor.fetchall()]

            img_new_cols = {
                "image_hash": "VARCHAR(255)",
                "width": "INTEGER",
                "height": "INTEGER",
                "image_provenance": "VARCHAR(100) DEFAULT 'OWNER_UPLOADED'",
                "verification_status": "VARCHAR(50) DEFAULT 'Verified'",
                "image_quality_score": "FLOAT",
                "image_validation_status": "VARCHAR(50) DEFAULT 'Valid'"
            }

            for col_name, col_type in img_new_cols.items():
                if col_name not in img_cols:
                    print(f"Migration: Adding '{col_name}' column to 'property_images' table...")
                    cursor.execute(f"ALTER TABLE property_images ADD COLUMN {col_name} {col_type}")

            conn.commit()

        # 5. Phase B MarketReference table creation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_references'")
        mref_exists = cursor.fetchone()
        if not mref_exists:
            print("Migration: Creating 'market_references' table...")
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_references (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name VARCHAR(255) NOT NULL,
                    source_listing_id VARCHAR(100),
                    locality VARCHAR(255) NOT NULL,
                    property_type VARCHAR(100) NOT NULL,
                    bhk INTEGER NOT NULL,
                    area_sqft FLOAT NOT NULL,
                    price_inr FLOAT NOT NULL,
                    price_per_sqft FLOAT NOT NULL,
                    listing_url VARCHAR(500),
                    observed_at DATETIME,
                    reference_status VARCHAR(50) DEFAULT 'REFERENCE'
                )
            ''')
            conn.commit()
            print("Migration: 'market_references' table created successfully.")

        # 5. Add 'voice_callback_requests' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voice_callback_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                user_id INTEGER,
                phone_number VARCHAR(50) NOT NULL,
                session_id VARCHAR(100) NOT NULL UNIQUE,
                call_sid VARCHAR(100),
                status VARCHAR(50) DEFAULT 'calling',
                inquiry_text TEXT,
                error_message TEXT,
                created_at DATETIME,
                updated_at DATETIME,
                FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vcr_session_id ON voice_callback_requests (session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_vcr_call_sid ON voice_callback_requests (call_sid)")

        # 6. Add 'property_inquiries' table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS property_inquiries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER NOT NULL,
                user_id INTEGER,
                phone_number VARCHAR(50) NOT NULL,
                session_id VARCHAR(100),
                question_or_request TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'PENDING',
                created_at DATETIME,
                FOREIGN KEY (property_id) REFERENCES properties (id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
            )
        ''')
        conn.commit()
        print("Migration: 'voice_callback_requests' and 'property_inquiries' tables checked/created.")

    except Exception as e:
        conn.rollback()
        print(f"Migration ERROR: {e}")
        raise e
    finally:
        conn.close()


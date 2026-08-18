import os
import sqlite3
from app.core.config import settings

def run_migrations():
    """Safely apply database schema updates for role and subscription models."""
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
            
    except Exception as e:
        conn.rollback()
        print(f"Migration ERROR: {e}")
        raise e
    finally:
        conn.close()

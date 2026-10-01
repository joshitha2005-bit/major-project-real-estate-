import sqlite3

def migrate():
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()

    # Check columns in property_images
    cursor.execute("PRAGMA table_info(property_images)")
    columns = [row[1] for row in cursor.fetchall()]
    print("Current columns in property_images table:", columns)

    # Add missing columns safely if not present
    new_cols = [
        ("source_type", "VARCHAR(50) DEFAULT 'owner_upload'"),
        ("source_name", "VARCHAR(255) DEFAULT 'Owner Uploaded'"),
        ("source_url", "VARCHAR(500) DEFAULT ''"),
        ("is_primary", "BOOLEAN DEFAULT 0"),
        ("uploaded_by", "INTEGER REFERENCES users(id)")
    ]

    for col_name, col_type in new_cols:
        if col_name not in columns:
            print(f"Adding column {col_name}...")
            cursor.execute(f"ALTER TABLE property_images ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()
    print("Database table property_images migration complete!")

if __name__ == '__main__':
    migrate()

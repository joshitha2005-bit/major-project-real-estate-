import sqlite3
import json

def main():
    conn = sqlite3.connect('backend/real_estate.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [t[0] for t in cursor.fetchall()]
    print('Tables in DB:', tables)

    cursor.execute('SELECT count(*) FROM properties')
    total = cursor.fetchone()[0]
    print(f'Total properties in DB: {total}')

    cursor.execute('SELECT id, title, images, source_type, source FROM properties WHERE images IS NOT NULL AND images != "" AND images != "[]" LIMIT 10')
    rows = cursor.fetchall()
    print(f'\nSample properties with non-empty images JSON:')
    for r in rows:
        print(f"ID: {r[0]}, Title: {r[1]}, Images: {r[2]}, SourceType: {r[3]}, Source: {r[4]}")

    cursor.execute('SELECT count(*) FROM properties WHERE images IS NOT NULL AND images != "" AND images != "[]"')
    props_with_imgs = cursor.fetchone()[0]
    print(f'\nTotal properties with non-empty images JSON: {props_with_imgs}')
    print(f'Total properties without images: {total - props_with_imgs}')

    if 'property_images' in tables:
        cursor.execute('SELECT count(*) FROM property_images')
        pi_count = cursor.fetchone()[0]
        print(f'\nproperty_images table row count: {pi_count}')
        cursor.execute('SELECT * FROM property_images LIMIT 10')
        print('Sample property_images table rows:')
        for r in cursor.fetchall():
            print(r)

if __name__ == '__main__':
    main()

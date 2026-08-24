import csv
import sqlite3
import os

csv_path = os.path.abspath('datasets/Bengaluru_House_Data.csv')
db_path = os.path.abspath('real_estate.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Find HSR properties in DB and compare with CSV rows by matching sqft, price, bath, bhk
cursor.execute('SELECT id, title, locality, address, area_sqft, price, bhk, bathrooms FROM properties WHERE LOWER(locality) LIKE "%hsr%" ORDER BY id ASC LIMIT 15')
db_rows = cursor.fetchall()

print("DB HSR Properties:")
for r in db_rows:
    print(r)

conn.close()

import sqlite3
import json

conn = sqlite3.connect("real_estate.db")
c = conn.cursor()

stats = {}
stats["total"] = c.execute("SELECT COUNT(id) FROM properties").fetchone()[0]
stats["identity_resolved"] = c.execute("SELECT COUNT(id) FROM properties WHERE identity_confidence = 'IDENTITY_RESOLVED'").fetchone()[0]
stats["identity_partial"] = c.execute("SELECT COUNT(id) FROM properties WHERE identity_confidence = 'IDENTITY_PARTIAL'").fetchone()[0]
stats["identity_unresolved"] = c.execute("SELECT COUNT(id) FROM properties WHERE identity_confidence = 'IDENTITY_UNRESOLVED'").fetchone()[0]

stats["exact_coords"] = c.execute("SELECT COUNT(id) FROM properties WHERE coordinate_confidence = 'EXACT'").fetchone()[0]
stats["approx_coords"] = c.execute("SELECT COUNT(id) FROM properties WHERE coordinate_confidence = 'APPROXIMATE'").fetchone()[0]

stats["current_verified"] = c.execute("SELECT COUNT(id) FROM properties WHERE listing_status = 'CURRENT'").fetchone()[0]
stats["historical_market"] = c.execute("SELECT COUNT(id) FROM properties WHERE listing_status = 'HISTORICAL'").fetchone()[0]
stats["other_status"] = c.execute("SELECT COUNT(id) FROM properties WHERE listing_status NOT IN ('CURRENT', 'HISTORICAL')").fetchone()[0]

stats["genuine_images"] = c.execute("SELECT COUNT(id) FROM properties WHERE image_provenance IN ('OWNER_UPLOADED', 'AUTHORIZED_PROVIDER', 'LICENSED_EXTERNAL')").fetchone()[0]
stats["without_genuine_images"] = c.execute("SELECT COUNT(id) FROM properties WHERE image_provenance NOT IN ('OWNER_UPLOADED', 'AUTHORIZED_PROVIDER', 'LICENSED_EXTERNAL')").fetchone()[0]

top_unresolved = c.execute("SELECT source, COUNT(id) FROM properties WHERE identity_confidence = 'IDENTITY_UNRESOLVED' GROUP BY source ORDER BY COUNT(id) DESC").fetchall()
stats["top_unresolved_sources"] = [{"source": row[0], "count": row[1]} for row in top_unresolved]

top_resolved = c.execute("SELECT source, COUNT(id) FROM properties WHERE identity_confidence = 'IDENTITY_RESOLVED' GROUP BY source ORDER BY COUNT(id) DESC").fetchall()
stats["top_resolved_sources"] = [{"source": row[0], "count": row[1]} for row in top_resolved]

print(json.dumps(stats, indent=2))
conn.close()

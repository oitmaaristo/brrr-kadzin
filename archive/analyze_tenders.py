import sqlite3

conn = sqlite3.connect('/home/brrr/brrr-hankeradar/data/hankeradar.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("=== KOKKU ===")
cur.execute("SELECT COUNT(*) as n FROM tenders")
print("Total hanked:", cur.fetchone()['n'])

print("\n=== NÄIDISED - erinevad tüübid ===")
cur.execute("SELECT title, organization_name, url, description FROM tenders LIMIT 50")
rows = cur.fetchall()
for r in rows:
    print(f"ORG: {r['organization_name']}")
    print(f"TITLE: {r['title'][:100]}")
    print(f"URL: {r['url'][:80]}")
    print(f"DESC: {str(r['description'])[:100] if r['description'] else 'NULL'}")
    print("---")

print("\n=== URL MUSTRID ===")
cur.execute("SELECT DISTINCT substr(url, 1, 60) as url_prefix FROM tenders GROUP BY url_prefix ORDER BY COUNT(*) DESC LIMIT 20")
for r in cur.fetchall():
    print(r['url_prefix'])

print("\n=== DUPLIKAADID - sama tiitel ===")
cur.execute("SELECT title, COUNT(*) as n FROM tenders GROUP BY title HAVING n > 5 ORDER BY n DESC LIMIT 20")
for r in cur.fetchall():
    print(f"{r['n']}x {r['title'][:80]}")

import sqlite3
import json2latex

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('adoption.db')
cursor = conn.cursor()

# Query to get the count of each sig_status for each registry
query = '''
    SELECT p.registry, u.sig_status, COUNT(*) as count
    FROM units u
    JOIN versions v ON u.version_id = v.id
    JOIN packages p ON v.package_id = p.id
    GROUP BY p.registry, u.sig_status
'''

# Execute the query
cursor.execute(query)

# Fetch all rows
rows = cursor.fetchall()

# Close the database connection
conn.close()

# Organize the data in a dictionary
result = {}
for row in rows:
    registry = row[0]
    sig_status = row[1]
    count = row[2]

    if registry not in result:
        result[registry] = {}

    result[registry][sig_status] = count

with open('out.tex', 'w') as f:
    json2latex.dump('breakdown', result, f)

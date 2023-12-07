import sqlite3
import matplotlib.pyplot as plt

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
WITH FirstSignedUnit AS (
    SELECT DISTINCT
        p.id AS package_id,
        MIN(u.date) AS first_signed_date
    FROM
        packages p
    JOIN
        versions v ON p.id = v.package_id
    JOIN
        units u ON v.id = u.version_id
    WHERE
        u.has_sig = 1
        AND u.date BETWEEN '2015-01-01' AND '2023-09-30'
    GROUP BY
        p.id
)

SELECT
    p.registry,
    AVG(CASE WHEN u.has_sig = 1 AND u.date > fsu.first_signed_date THEN 1 ELSE 0 END) AS probability_subsequent_signed
FROM
    packages p
JOIN
    versions v ON p.id = v.package_id
JOIN
    units u ON v.id = u.version_id
JOIN
    FirstSignedUnit fsu ON p.id = fsu.package_id
WHERE
    u.date BETWEEN '2015-01-01' AND '2023-10-01'
GROUP BY
    p.registry
ORDER BY
    p.registry;
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

query = '''
SELECT p.registry,
       COUNT(u.id) AS total_units,
       SUM(CASE WHEN u.has_sig = 1 THEN 1 ELSE 0 END) AS signed_units,
       AVG(CASE WHEN u.has_sig = 1 THEN 1.0 ELSE 0.0 END) AS chance_signed
FROM packages p
JOIN versions v ON p.id = v.package_id
JOIN units u ON v.id = u.version_id
WHERE u.date BETWEEN '2015-01-01' AND '2023-10-01' -- Adjust the date range as needed
GROUP BY p.registry;
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results2 = cursor.fetchall()

print('Registry : chance after first | normal chance')
for x in range(0, len(results)):
    print(f'{results[x][0]}: {results[x][1]} | {results2[x][3]}')

# Close the database connection
conn.close()

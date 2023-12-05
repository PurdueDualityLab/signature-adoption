import sqlite3
import matplotlib.pyplot as plt

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
    SELECT p.registry,
           strftime('%Y-%m', u.date) AS month_start, 
           COUNT(u.id) AS total_units,
           SUM(u.has_sig) AS signed_units
    FROM versions v
    JOIN units u ON v.id = u.version_id
    JOIN packages p on p.id = v.package_id
    WHERE u.date BETWEEN '2015-01-01' and '2023-09-30'
    GROUP BY p.registry, month_start
'''

query = '''
    SELECT p.registry,
           strftime('%Y', u.date) AS year,
           CASE
                WHEN strftime('%m', u.date) BETWEEN '01' and '03' THEN 'Q1'
                WHEN strftime('%m', u.date) BETWEEN '04' and '06' THEN 'Q2'
                WHEN strftime('%m', u.date) BETWEEN '07' and '09' THEN 'Q3'
                WHEN strftime('%m', u.date) BETWEEN '10' and '12' THEN 'Q4'
           END AS quarter,
           COUNT(u.id) AS total_units,
           SUM(u.has_sig) AS signed_units
    FROM versions v
    JOIN units u ON v.id = u.version_id
    JOIN packages p on p.id = v.package_id
    WHERE u.date BETWEEN '2015-01-01' and '2023-09-30'
    GROUP BY p.registry, year, quarter
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

# Close the database connection
conn.close()

# Extract data for plotting
data = {
    "docker":
    {
        "months": [],
        "adoption_rates": []
    },
    "pypi":
    {
        "months": [],
        "adoption_rates": []
    },
    "maven":
    {
        "months": [],
        "adoption_rates": []
    },
    "huggingface":
    {
        "months": [],
        "adoption_rates": []
    },
}

# Calculate adoption rates and collect data for plotting
for registry, year, quarter, total_units, signed_units in results:
    time = year + '-' + quarter
    adoption_rate = (signed_units / total_units) * \
        100 if total_units != 0 else 0
    data[registry]['months'].append(time)
    data[registry]['adoption_rates'].append(adoption_rate)


# Plot the adoption rates over time
plt.plot(data['maven']['months'], data['maven']['adoption_rates'],
         marker='o', linestyle='-', label='Maven')
plt.plot(data['pypi']['months'], data['pypi']['adoption_rates'],
         marker='o', linestyle='-', label='PyPI')
plt.plot(data['docker']['months'], data['docker']['adoption_rates'],
         marker='o', linestyle='-', label='Docker Hub')
plt.plot(data['huggingface']['months'], data['huggingface']
         ['adoption_rates'], marker='o', linestyle='-', label='HuggingFace')
plt.xlabel('Quarter')
plt.ylabel('Signature Quantity (%)')
plt.title('Quantity of Signatures Over Time')
plt.xticks(data['maven']['months'], rotation=45)
plt.tight_layout()
plt.legend()
plt.show()

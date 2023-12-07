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
for registry, month_start, total_units, signed_units in results:
    adoption_rate = (signed_units / total_units) * \
        100 if total_units != 0 else 0
    data[registry]['months'].append(month_start)
    data[registry]['adoption_rates'].append(adoption_rate)


# Plot the adoption rates over time
plt.plot(data['maven']['months'], data['maven']['adoption_rates'],
         marker='o', linestyle='-', label='Maven')
plt.plot(data['docker']['months'], data['docker']['adoption_rates'],
         marker='o', linestyle='-', label='Docker Hub')
plt.plot(data['huggingface']['months'], data['huggingface']
         ['adoption_rates'], marker='o', linestyle='-', label='HuggingFace')
plt.plot(data['pypi']['months'], data['pypi']['adoption_rates'],
         marker='o', linestyle='-', label='PyPI')
plt.xlabel('Quarter')
plt.ylabel('Signature Quantity (%)')
plt.title('Quantity of Signatures Over Time')
plt.xticks(data['maven']['months'][::6], rotation=45)
plt.tight_layout()
plt.legend()
plt.savefig('data/results/combined_quantity_time.png')

import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
    SELECT p.registry,
           strftime('%Y-%W', v.date) AS week_start, 
           COUNT(u.id) AS total_units,
           SUM(u.has_sig) AS signed_units
    FROM versions v
    JOIN units u ON v.id = u.version_id
    JOIN packages p on p.id = v.package_id
    WHERE v.date >= date('2015-01-01') and v.date < date('2023-10-01')
    GROUP BY p.registry, week_start
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

# Close the database connection
conn.close()

# Extract data for plotting
data = {
    "docker": {
        "weeks": [],
        "adoption_rates": []},
    "pypi": {
        "weeks": [],
        "adoption_rates": []},
    "maven": {
        "weeks": [],
        "adoption_rates": []},
    "huggingface": {
        "weeks": [],
        "adoption_rates": []},
}

# Calculate adoption rates and collect data for plotting
for registry, week_start, total_units, signed_units in results:
    adoption_rate = (signed_units / total_units) * \
        100 if total_units != 0 else 0
    data[registry]['weeks'].append(week_start)
    data[registry]['adoption_rates'].append(adoption_rate)


# Plot the adoption rates over time
for registry in data.keys():
    plt.plot(data[registry]['weeks'], data[registry]['adoption_rates'], marker='o', linestyle='-')
    plt.xlabel('Week')
    plt.ylabel('Adoption Rate (%)')
    plt.title(f'{registry} Adoption Rates Over Time')
    plt.xticks(data[registry]['weeks'][::26], rotation=45)
    plt.tight_layout()
    plt.show()


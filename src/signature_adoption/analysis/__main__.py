import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
    SELECT strftime('%Y-%W', v.date) AS week_start, 
           COUNT(u.id) AS total_units,
           SUM(u.has_sig) AS signed_units
    FROM versions v
    JOIN units u ON v.id = u.version_id
    GROUP BY week_start
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

# Close the database connection
conn.close()

# Extract data for plotting
weeks, adoption_rates = [], []

# Calculate adoption rates and collect data for plotting
for week_start, total_units, signed_units in results:
    adoption_rate = (signed_units / total_units) * \
        100 if total_units != 0 else 0
    weeks.append(week_start)
    adoption_rates.append(adoption_rate)

# Plot the adoption rates over time
plt.plot(weeks, adoption_rates, marker='o', linestyle='-', color='blue')
plt.xlabel('Week')
plt.ylabel('Adoption Rate (%)')
plt.title('Adoption Rates Over Time')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

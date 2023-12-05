import sqlite3
import matplotlib.pyplot as plt

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
    SELECT p.registry,
           strftime('%Y-%m', v.date) AS month_start, 
           COUNT(u.id) AS total_units,
           SUM(u.has_sig) AS signed_units
    FROM versions v
    JOIN units u ON v.id = u.version_id
    JOIN packages p on p.id = v.package_id
    WHERE v.date >= date('2015-01-01') and v.date < date('2023-10-01')
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
        "total": []
    },
    "pypi": 
    {
        "months": [],
        "total": []
    },
    "maven": 
    {
        "months": [],
        "total": []
    },
    "huggingface": 
    {
        "months": [],
        "total": []
    },
}

# Calculate adoption rates and collect data for plotting
for registry, month_start, total_units, signed_units in results:
    data[registry]['months'].append(month_start)
    data[registry]['total'].append(total_units)


# Plot the adoption rates over time
plt.plot(data['maven']['months'], data['maven']['total'], marker='o', linestyle='-')
plt.xlabel('Month')
plt.ylabel('Units Published per Month')
plt.title('Published Units on Maven Central')
plt.xticks(data['maven']['months'][::4], rotation=45)
plt.tight_layout()
plt.show()

plt.plot(data['pypi']['months'], data['pypi']['total'], marker='o', linestyle='-')
plt.xlabel('Month')
plt.ylabel('Units Published per Month')
plt.title('Published Units on PyPI')
plt.xticks(data['pypi']['months'][::4], rotation=45)
plt.tight_layout()
plt.show()

plt.plot(data['docker']['months'], data['docker']['total'], marker='o', linestyle='-')
plt.xlabel('Month')
plt.ylabel('Units Published per Month')
plt.title('Published Units on Docker Hub')
plt.xticks(data['docker']['months'][::4], rotation=45)
plt.tight_layout()
plt.show()

plt.plot(data['huggingface']['months'], data['huggingface']['total'], marker='o', linestyle='-')
plt.xlabel('Month')
plt.ylabel('Units Published per Month')
plt.title('Published Units on HuggingFace')
plt.xticks(data['huggingface']['months'][::4], rotation=45)
plt.tight_layout()
plt.show()


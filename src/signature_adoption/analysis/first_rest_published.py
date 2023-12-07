import sqlite3
import matplotlib.pyplot as plt

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
WITH VersionRanked AS (
    SELECT
        p.registry,
        u.*,
        ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY v.date) AS version_rank
    FROM
        packages p
    JOIN
        versions v ON p.id = v.package_id
    JOIN
        units u ON v.id = u.version_id
    WHERE
        u.date BETWEEN '2015-01-01' AND '2023-10-01'
)
SELECT
    registry,
    strftime('%Y-%m', date) AS month,
    SUM(CASE WHEN version_rank = 1 THEN 1 ELSE 0 END) AS first_versions,
    SUM(CASE WHEN version_rank > 1 THEN 1 ELSE 0 END) AS non_first_versions
FROM
    VersionRanked
GROUP BY
    registry, month
ORDER BY
    registry, month;
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
        "first": [],
        "non_first": []
    },
    "pypi":
    {
        "months": [],
        "first": [],
        "non_first": []
    },
    "maven":
    {
        "months": [],
        "first": [],
        "non_first": []
    },
    "huggingface":
    {
        "months": [],
        "first": [],
        "non_first": []
    },
}

# Calculate adoption rates and collect data for plotting
for registry, month_start, first, non_first in results:
    data[registry]['months'].append(month_start)
    data[registry]['first'].append(first)
    data[registry]['non_first'].append(non_first)


# # Plot the maven adoption data
# plt.plot(data['maven']['months'], data['maven']['first'],
#          marker='o', linestyle='-', label='First Versions')
# plt.plot(data['maven']['months'], data['maven']['non_first'],
#          marker='o', linestyle='-', label='Non-First Versions')
# plt.xlabel('Month')
# plt.ylabel('Number of Units Published per Month')
# plt.title('First vs. Non-First Versions Published per Month on Maven Central')
# plt.xticks(data['maven']['months'][::4], rotation=45)
# plt.tight_layout()
# plt.legend()
# plt.show()


# Plot the pypi adoption data
plt.plot(data['pypi']['months'], data['pypi']['non_first'],
         linewidth=2, linestyle='-', label='Non-First Versions')
plt.plot(data['pypi']['months'], data['pypi']['first'],
         linewidth=2, linestyle='--', label='First Versions')
plt.xlabel('Month', fontsize=15)
plt.ylabel('Units Published per Month', fontsize=15)
plt.title('First vs. Non-First Artifacts on PyPI', fontsize=19)
plt.xticks(data['pypi']['months'][::6], rotation=45, fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()
plt.legend(fontsize=11)
plt.savefig('data/results/first_rest.png')


# Plot the docker adoption data
# plt.plot(data['docker']['months'], data['docker']['first'],
#          marker='o', linestyle='-', label='First Versions')
# plt.plot(data['docker']['months'], data['docker']['non_first'],
#          marker='o', linestyle='-', label='Non-First Versions')
# plt.xlabel('Month')
# plt.ylabel('Number of Units Published per Month')
# plt.title('First vs. Non-First Versions Published per Month on Docker Hub')
# plt.xticks(data['docker']['months'][::4], rotation=45)
# plt.tight_layout()
# plt.legend()
# plt.show()

# Plot the huggingface adoption data
# plt.plot(data['huggingface']['months'], data['huggingface']['first'],
#          marker='o', linestyle='-', label='First Versions')
# plt.plot(data['huggingface']['months'], data['huggingface']['non_first'],
#          marker='o', linestyle='-', label='Non-First Versions')
# plt.xlabel('Month')
# plt.ylabel('Number of Units Published per Month')
# plt.title('First vs. Non-First Versions Published per Month on HuggingFace')
# plt.xticks(data['huggingface']['months'][::4], rotation=45)
# plt.tight_layout()
# plt.legend()
# plt.show()

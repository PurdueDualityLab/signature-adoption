import sqlite3
import matplotlib.pyplot as plt

# Connect to the SQLite database
# Replace 'your_database.db' with the actual name of your database
conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
SELECT
    p.registry,
    strftime('%Y-%m', u.date) AS month,
    COUNT(CASE WHEN u.has_sig = 1 THEN 1 END) AS units_with_sig,
    COUNT(CASE WHEN u.sig_status = 'GOOD' THEN 1 END) AS units_with_good_status
FROM
    packages p
JOIN
    versions v ON p.id = v.package_id
JOIN
    units u ON v.id = u.version_id
WHERE
    (u.has_sig = 1 OR u.sig_status = 'GOOD')
    AND u.date BETWEEN '2015-01-01' AND '2023-10-01'
GROUP BY
    p.registry, month
ORDER BY
    p.registry, month;
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
for registry, month_start, total_signed, total_good in results:
    adoption_rate = (total_good / total_signed) * \
        100 if total_signed != 0 else 0
    data[registry]['months'].append(month_start)
    data[registry]['adoption_rates'].append(adoption_rate)


# Plot the adoption rates over time
plt.plot(data['maven']['months'], data['maven']['adoption_rates'],
         linestyle=':', label='Maven Central', linewidth=2)
plt.plot(data['docker']['months'], data['docker']['adoption_rates'],
         linestyle='-.', label='Docker Hub', linewidth=2)
plt.plot(data['huggingface']['months'], data['huggingface']['adoption_rates'],
         linestyle='--', label='HuggingFace', linewidth=2)
plt.plot(data['pypi']['months'], data['pypi']['adoption_rates'],
         linestyle='-', label='PyPI', linewidth=2)
plt.axvline(x='2018-03', color='k', linestyle='--', label='PyPI PGP De-emphasis')
plt.xlabel('Month', fontsize=15)
plt.ylabel('Signature Quality (% Good Signatures)', fontsize=15)
plt.title('Quality of Signatures Over Time', fontsize=19)
plt.xticks(data['maven']['months'][::6], rotation=45, fontsize=11)
plt.yticks(fontsize=11)
plt.tight_layout()
plt.legend(fontsize=11)
plt.savefig('data/results/combined_quality.png')

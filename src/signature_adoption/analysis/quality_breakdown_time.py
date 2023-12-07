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
    COUNT(CASE WHEN u.sig_status = 'GOOD' THEN 1 END) as good,
    COUNT(CASE WHEN u.sig_status = 'NO_SIG' THEN 1 END) as no_sig,
    COUNT(CASE WHEN u.sig_status = 'BAD_SIG' THEN 1 END) as bad_sig,
    COUNT(CASE WHEN u.sig_status = 'EXP_SIG' THEN 1 END) as exp_sig,
    COUNT(CASE WHEN u.sig_status = 'EXP_PUB' THEN 1 END) as exp_pub,
    COUNT(CASE WHEN u.sig_status = 'NO_PUB' THEN 1 END) as no_pub,
    COUNT(CASE WHEN u.sig_status = 'REV_PUB' THEN 1 END) as rev_pub,
    COUNT(CASE WHEN u.sig_status = 'BAD_PUB' THEN 1 END) as bad_pub
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
        "NO_SIG": [],
        "BAD_SIG": [],
        "EXP_SIG": [],
        "EXP_PUB": [],
        "NO_PUB": [],
        "REV_PUB": [],
        "BAD_PUB": [],
    },
    "pypi":
    {
        "months": [],
        "NO_SIG": [],
        "BAD_SIG": [],
        "EXP_SIG": [],
        "EXP_PUB": [],
        "NO_PUB": [],
        "REV_PUB": [],
        "BAD_PUB": [],
    },
    "maven":
    {
        "months": [],
        "NO_SIG": [],
        "BAD_SIG": [],
        "EXP_SIG": [],
        "EXP_PUB": [],
        "NO_PUB": [],
        "REV_PUB": [],
        "BAD_PUB": [],
    },
    "huggingface":
    {
        "months": [],
        "NO_SIG": [],
        "BAD_SIG": [],
        "EXP_SIG": [],
        "EXP_PUB": [],
        "NO_PUB": [],
        "REV_PUB": [],
        "BAD_PUB": [],
    },
}

# Calculate adoption rates and collect data for plotting
for registry, month_start, total_signed, total_good, total_no_sig, total_bad_sig, total_exp_sig, total_exp_pub, total_no_pub, total_rev_pub, total_bad_pub in results:
    denom = total_signed - total_good
    data[registry]['months'].append(month_start)
    data[registry]['BAD_SIG'].append(
        total_bad_sig / denom * 100 if denom != 0 else 0)
    data[registry]['EXP_SIG'].append(
        total_exp_sig / denom * 100 if denom != 0 else 0)
    data[registry]['EXP_PUB'].append(
        total_exp_pub / denom * 100 if denom != 0 else 0)
    data[registry]['NO_PUB'].append(
        total_no_pub / denom * 100 if denom != 0 else 0)
    data[registry]['REV_PUB'].append(
        total_rev_pub / denom * 100 if denom != 0 else 0)
    data[registry]['BAD_PUB'].append(
        total_bad_pub / denom * 100 if denom != 0 else 0)

# Plot for maven

for key in data:
    title = key.title()
    if key == 'docker':
        title = 'Docker Hub'
    if key == 'huggingface':
        title = 'HuggingFace'
    if key == 'pypi':
        title = 'PyPI'
    if key == 'maven':
        title = 'Maven Central'
    plt.plot(data[key]['months'], data[key]['BAD_SIG'],
             linewidth=2, linestyle='-', label='Bad Signature')
    plt.plot(data[key]['months'], data[key]['EXP_SIG'],
             linewidth=2, linestyle='-', label='Expired Signature')
    plt.plot(data[key]['months'], data[key]['EXP_PUB'],
             linewidth=2, linestyle='-', label='Expired Public Key')
    plt.plot(data[key]['months'], data[key]['NO_PUB'],
             linewidth=2, linestyle='-', label='No Public Key')
    plt.plot(data[key]['months'], data[key]['REV_PUB'],
             linewidth=2, linestyle='-', label='Revoked Public Key')
    plt.plot(data[key]['months'], data[key]['BAD_PUB'],
             linewidth=2, linestyle='-', label='Bad Public Key')
    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Percent of Signatures', fontsize=15)
    plt.title(f'{title} Failure Modes Over Time', fontsize=19)
    plt.xticks(data[key]['months'][::6], rotation=45, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=11)
    plt.savefig(f'data/results/failures_{key}.png')
    plt.clf()

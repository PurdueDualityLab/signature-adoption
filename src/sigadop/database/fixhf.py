#!/usr/bin/env python

'''fixhf.py: Fix HuggingFace data by scraping the web for commit signature
status.
'''

import sqlite3
import requests
from bs4 import BeautifulSoup

conn = sqlite3.connect('data/adoption.db')
cursor = conn.cursor()

# SQL query to get the adoption rates by week
query = '''
SELECT p.name,
       u.unit,
       p.id
FROM packages p
JOIN units u ON p.id=u.package_id
WHERE p.registry='huggingface' AND u.has_sig=1
'''

# Execute the query
cursor.execute(query)

# Fetch the results
results = cursor.fetchall()

repos = {}

# Iterate over the results and store them in a dictionary
for result in results:
    if result[0] not in repos:
        repos[result[0]] = {
            'commits': [result[1]],
            'id': result[2]
        }
    else:
        repos[result[0]]['commits'].append(result[1])


def get_commits_page(name, page=0):
    '''Get the commits page for a package and page number.'''
    url = f'https://huggingface.co/{name}/commits/main?p={page}'
    print(url)
    r = requests.get(url)

    if not r:
        return None

    if r.status_code == 200:
        return r.text

    return None


fixed = {}

# Iterate over the repos
for indx, (repo, repo_data) in enumerate(repos.items()):
    commits = repo_data['commits']
    package_id = repo_data['id']

    # Get the first 7 characters of the commit hash
    hash_7 = [commit[:7] for commit in commits]
    print(f'{indx+1}/{len(repos)}')

    fixed[repo] = []

    # Iterate over all pages
    page = 0
    while True:
        html = get_commits_page(repo, page)
        page += 1
        if not html:
            break

        soup = BeautifulSoup(html, 'html.parser')
        commit_elements = soup.find_all('article')

        print(repo, len(commit_elements))

        # Iterate over all commits on the page
        for commit_element in commit_elements:
            spans = commit_element.find_all('span')
            hash = spans[0].text.strip()
            if hash in hash_7:
                commit_sig_status = spans[1].text.strip()
                full_hash = commits[hash_7.index(hash)]
                sig_status = 'GOOD' if commit_sig_status.lower() == 'verified' else 'BAD_SIG'
                update_query = f'''
                UPDATE units
                SET sig_status='{sig_status}', sig_raw='{commit_sig_status}'
                WHERE unit='{full_hash}' AND package_id={package_id}
                '''
                cursor.execute(update_query)

        if len(commit_elements) < 50:
            break

    conn.commit()


# Close the database connection
conn.close()

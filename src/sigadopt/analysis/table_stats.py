'''
table_stats.py: This script is used to generate a LaTeX table for the
stats tests.
'''

import json
import json2latex
import logging
import re
import statistics
import scipy.stats
from datetime import datetime
from sigadopt.util.number_things import human_format, pc_str
from sigadopt.util.database import SignatureStatus, Registry
from sigadopt.analysis.anova import get_sample as anova_get_sample
from sigadopt.analysis.ttest import run as ttest_run

log = logging.getLogger(__name__)


def run(database, output, out_json=False):

    result = {}

    log.info('Getting data for ANOVA test')
    huggingface = anova_get_sample(database, Registry.HUGGINGFACE)
    docker = anova_get_sample(database, Registry.DOCKER)
    maven = anova_get_sample(database, Registry.MAVEN)
    pypi = anova_get_sample(database, Registry.PYPI)

    # Conduct ANOVA test
    log.info('Running ANOVA/Tukey test')

    f, anova_p = scipy.stats.f_oneway(maven, pypi, docker, huggingface)
    tukey = scipy.stats.tukey_hsd(
        maven, pypi, docker, huggingface)
    log.info(tukey)

    statistic = tukey.statistic
    tukey_p = tukey.pvalue

    # Add to results
    result['anova'] = {
        'f': '{:.2f}'.format(f),
        'p': '{:.3f}'.format(anova_p),
    }

    result['tukey'] = {
    }
    for i in range(4):
        i_text = Registry(i+1).name.lower()
        if i_text not in result['tukey']:
            result['tukey'][i_text] = {}
        for j in range(4):
            j_text = Registry(j+1).name.lower()
            if j_text not in result['tukey'][i_text]:
                result['tukey'][i_text][j_text] = {}
            result['tukey'][i_text][j_text] = {
                'statistic': '{:.2f}'.format(statistic[i][j]),
                'p': '{:.3f}'.format(tukey_p[i][j]),
            }

    log.info('Starting ttests')
    result['ttests'] = {
        'pypi_deemp':
            {
                'pypi': ttest_run(database, Registry.PYPI,      datetime.strptime('2018-03-22', '%Y-%m-%d'), 180, 'greater', None),
                'maven': ttest_run(database, Registry.MAVEN,    datetime.strptime('2018-03-22', '%Y-%m-%d'), 180, 'greater', None),
                'docker': ttest_run(database, Registry.DOCKER,  datetime.strptime('2018-03-22', '%Y-%m-%d'), 180, 'greater', None),
            },
        'docker_update':
            {
                'pypi': ttest_run(database, Registry.PYPI,     datetime.strptime('2019-09-05', '%Y-%m-%d'),  180, 'less', None),
                'maven': ttest_run(database, Registry.MAVEN,   datetime.strptime('2019-09-05', '%Y-%m-%d'), 180, 'less', None),
                'docker': ttest_run(database, Registry.DOCKER, datetime.strptime('2019-09-05', '%Y-%m-%d'), 180, 'less', None),
            },
        'docker_hack':
            {
                'pypi': ttest_run(database, Registry.PYPI,     datetime.strptime('2019-04-25', '%Y-%m-%d'), 180, 'less', None),
                'maven': ttest_run(database, Registry.MAVEN,   datetime.strptime('2019-04-25', '%Y-%m-%d'), 180, 'less', None),
                'docker': ttest_run(database, Registry.DOCKER, datetime.strptime('2019-04-25', '%Y-%m-%d'), 180, 'less', None),
            },
        'solarwinds':
            {
                'pypi': ttest_run(database, Registry.PYPI,      datetime.strptime('2021-12-14', '%Y-%m-%d'), 180, 'less', None),
                'maven': ttest_run(database, Registry.MAVEN,    datetime.strptime('2021-12-14', '%Y-%m-%d'), 180, 'less', None),
                'docker': ttest_run(database, Registry.DOCKER,  datetime.strptime('2021-12-14', '%Y-%m-%d'), 180, 'less', None),
            },

    }

    events = [
        result['ttests']['docker_hack']['pypi']['p_value'],
        result['ttests']['docker_hack']['maven']['p_value'],
        result['ttests']['docker_hack']['docker']['p_value'],
        result['ttests']['solarwinds']['pypi']['p_value'],
        result['ttests']['solarwinds']['maven']['p_value'],
        result['ttests']['solarwinds']['docker']['p_value'],
    ]
    adj_p_events = scipy.stats.false_discovery_control(events) 
    result['ttests']['docker_hack']['pypi']['adj_p'] = '{:.3f}'.format(adj_p_events[0])
    result['ttests']['docker_hack']['maven']['adj_p'] = '{:.3f}'.format(adj_p_events[1])
    result['ttests']['docker_hack']['docker']['adj_p'] = '{:.3f}'.format(adj_p_events[2])
    result['ttests']['solarwinds']['pypi']['adj_p'] = '{:.3f}'.format(adj_p_events[3])
    result['ttests']['solarwinds']['maven']['adj_p'] = '{:.3f}'.format(adj_p_events[4])
    result['ttests']['solarwinds']['docker']['adj_p'] = '{:.3f}'.format(adj_p_events[5])

    policies = [
        result['ttests']['pypi_deemp']['pypi']['p_value'],
        result['ttests']['pypi_deemp']['maven']['p_value'],
        result['ttests']['pypi_deemp']['docker']['p_value'],
        result['ttests']['docker_update']['pypi']['p_value'],
        result['ttests']['docker_update']['maven']['p_value'],
        result['ttests']['docker_update']['docker']['p_value'],
    ]
    adj_p_policies = scipy.stats.false_discovery_control(policies) 
    result['ttests']['pypi_deemp']['pypi']['adj_p'] = '{:.3f}'.format(adj_p_policies[0])
    result['ttests']['pypi_deemp']['maven']['adj_p'] = '{:.3f}'.format(adj_p_policies[1])
    result['ttests']['pypi_deemp']['docker']['adj_p'] = '{:.3f}'.format(adj_p_policies[2])
    result['ttests']['docker_update']['pypi']['adj_p'] = '{:.3f}'.format(adj_p_policies[3])
    result['ttests']['docker_update']['maven']['adj_p'] = '{:.3f}'.format(adj_p_policies[4])
    result['ttests']['docker_update']['docker']['adj_p'] = '{:.3f}'.format(adj_p_policies[5])

    # print(json.dumps(result, indent=4))
    log.info(f'Writing LaTeX table to {output}')
    with open(output, 'w') as f:
        if out_json:
            json.dump(result, f, indent=4)
        else:
            json2latex.dump('stats', result, f)

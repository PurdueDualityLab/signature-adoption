'''
plot_rsa.py: Plot the RSA data size over time.
'''
import matplotlib.pyplot as plt
import logging
from sigadopt.util.database import Registry

# Set up logging
log = logging.getLogger(__name__)


def run(database, output, registry):
    '''
    This function plots the quality of signatures over time for each registry.

    database: A database connection
    output: The path to write the LaTeX table to.
    registry: The registry to plot.
    '''

    results = None

    with database:

        cursor = database.cursor()

        # Execute the query
        log.info('Executing query...')

        # Get the time of the RSA
        cursor.execute(
            '''
            select
                strftime('%Y-%m', l.created, 'unixepoch') as month,
                ((((l.data-1)/512)+1)*512) as data_up,
                count(l.id) as occurrences
            from list_packets l
            join signatures s on l.signature_id = s.id
            join artifacts a on s.artifact_id = a.id
            join versions v on a.version_id = v.id
            join packages p on v.package_id = p.id
            where l.algo = 1
            and p.registry_id = ?
            and date(l.created, 'unixepoch') between '2015-01-01' and '2023-12-31'
            group by month, data_up
            ''',
            (registry,)
        )
        results = cursor.fetchall()


    log.info('Doing some analysis...')
    months = {}
    data_ups = [
        8192,
        4608,
        4096,
        3072,
        2048,
        1536,
        1024,
    ]
    for month, data_up, occurrences in results:
        if month not in months:
            months[month] = {}
        months[month][data_up] = occurrences

    # calculate percentages
    for month in months:
        for data_up in data_ups:
            if data_up not in months[month]:
                months[month][data_up] = 0
        total = sum(months[month].values())
        for data_up in data_ups:
            months[month][data_up] = months[month][data_up] / total * 100

    # plot the data
    log.info('Plotting...')
    for data_up in data_ups:
        plt.plot(
            [month for month in months],
            [months[month][data_up] for month in months],
            label=f'{data_up} bytes'
        )

    titles = {
        Registry.DOCKER: 'Docker',
        Registry.PYPI: 'PyPI',
        Registry.MAVEN: 'Maven Central',
        Registry.HUGGINGFACE: 'Hugging Face'
    }

    plt.xlabel('Month', fontsize=15)
    plt.ylabel('Percent of RSA Signatures', fontsize=15)
    plt.title(f'RSA Key Length on {titles[registry]}', fontsize=19)
    plt.xticks([month for month in months][::4],
               rotation=90, fontsize=11)
    plt.yticks(fontsize=11)
    plt.tight_layout()
    plt.legend(fontsize=10)
    plt.gca().set_ylim(top=100)
    plt.savefig(output, dpi=300)

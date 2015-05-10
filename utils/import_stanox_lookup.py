import requests
import re
import yaml
import functools
import rethinkdb as r
from bs4 import BeautifulSoup as soup

# This tool 'imports' the STANOX lookup table by
# actually just scraping a website which has this
# information in a rather bad format.

# The site we want to scrape
url_base = 'http://www.railwaycodes.org.uk/CRS/CRS{}.shtm'

# The alphabet
url_suffixes = [chr(c + 97) for c in range(26)]

# And one more thing (Crossrail codes are CRS1.shtm)
url_suffixes.append('1')


def get_page(url):
    """
    string -> string
    Get the page contents given the url
    """
    print('get_page {}'.format(url))
    resp = requests.get(url)
    if (resp.status_code == 200):
        return resp.text
    else:
        raise IOError('Non-OK code returned by request')


def extract_main_table(page):
    """
    string -> [[string, ...], ...]
    Read the relevant table on the site and return
    a list representation of it, sans headers.
    """
    the_soup = soup(page)
    return [
        [
            re.sub(r'^-$', '', str(column.string).strip())  # Get rid of dashes
            for column in row.find_all('td')
        ]
        for row in the_soup.table.div.table.find_all('tr')
        # We are only interested in full rows, but the table has some colspan
        # trickery. For now we ignore it.
        if len(row.find_all('td')) == 6
    ]

# Produce a mega-list of all the sub-tables on the site - this will be
# our STANOX lookup table.
the_list = functools.reduce(lambda l, s: l + s, [
                                extract_main_table(get_page(url_base
                                                            .format(suffix)))
                                for suffix in url_suffixes
                            ])

# Convert our list of rows into a list of documents for Rethink
the_docs = [
    {
        'name': elt[0],     # Station name
        'crs': elt[1],      # 3-letter station code
        'nlc': elt[2],      # National Reference Code?
        'tiploc': elt[3],   # Timing Point Location code
        'stanme': elt[4],   # Station name abbreviation for COBOL mainframes
        'stanox': elt[5]    # The STANOX code
    }
    for elt in the_list
]

# Read in the configuration file
conf = None
with open('../conf.yml') as conf_yml:
    conf = yaml.load(conf_yml.read())

# Connect to the database
conn = r.connect(**conf['database'])

print('Will now insert all of those into Rethink, grab a tea.')

# Insert all those documents. This will take a while.
for doc in the_docs:
    r.table('stanox_lookup').insert(doc).run(conn)

# Create an index on the STANOX field as we will be using it often
r.table('stanox_lookup').index_create('stanox')

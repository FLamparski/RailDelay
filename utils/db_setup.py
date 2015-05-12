import yaml
import rethinkdb as r

from os import path


def create_if_not_exists(name, conn, the_type='table'):
    """
    Create a RethinkDB entity if it does not exist. Can be
    used with either databases or tables.
    """
    if name not in getattr(r, the_type + '_list')().run(conn):
        print('Creating {} {}'.format(the_type, name))
        getattr(r, the_type + '_create')(name).run(conn)

conf_path = path.realpath(path.join(path.dirname(__file__), '..', 'conf.yml'))
print('Using configuration file {}'.format(conf_path))
db_conf = None
conn = None
with open(conf_path) as conf_yml:
    conf_contents = conf_yml.read()
    db_conf = yaml.load(conf_contents)['database']
    conn = r.connect(**db_conf)

create_if_not_exists(db_conf['db'], conn, the_type='db')

r.db(db_conf['db'])

TABLES = [
    'raw_messages',
    'train_movements',
    'stanox_lookup',
    'naptan_stops'
]

for tname in TABLES:
    create_if_not_exists(tname, conn)

import csv
import yaml
import argparse
import rethinkdb as r

from os import path


def find(func, dicts):
    for dikt in dicts:
        if func(dikt):
            return dikt


def get_stop_docs(stops, refs):
    the_docs = []
    for stop in stops:
        ref = find(lambda doc: doc['AtcoCode'] == stop['AtcoCode'], refs)
        the_doc = {
            'AtcoCode': stop['AtcoCode'],
            'TiplocCode': ref['TiplocCode'],
            'CommonName': stop['CommonName'],
            'StationName': ref['StationName'],
            'LocalityName': stop['LocalityName'],
            'CrsCode': ref['CrsCode'],
            'Location': r.point(float(stop['Longitude']), float(stop['Latitude']))
        }
        the_docs.append(the_doc)
    return the_docs


def run_import(stops_path=None, refs_path=None, db_config=None):
    conn = r.connect(**db_config)
    print('run_import: stops are in {}, refs are in {}'.format(stops_path, refs_path))
    the_stops = None
    the_refs = None

    with open(refs_path) as refs_csv:
        reader = csv.DictReader(refs_csv)
        the_refs = [ref for ref in reader]
    atco_codes = [ref['AtcoCode'] for ref in the_refs]
    with open('./Stops.csv', newline='', errors='surrogateescape') as stops_csv:
        reader = csv.DictReader(stops_csv)
        the_stops = [stop for stop in reader if stop['AtcoCode'] in atco_codes]

    the_docs = get_stop_docs(the_stops, the_refs)
    for doc in the_docs:
        r.table('naptan_stops').insert(doc).run(conn)
    r.table('naptan_stops').index_create('Location', geo=True).run(conn)
    r.table('naptan_stops').index_create('TiplocCode').run(conn)


def main():
    parser = argparse.ArgumentParser(description='Import NaPTAN stops and railway references')
    parser.add_argument('stops_path', type=str, help='Path to Stops.csv')
    parser.add_argument('refs_path', type=str, help='Path to RailReferences.csv')
    args = parser.parse_args()

    conf_path = path.realpath(path.join(path.dirname(__file__),
                                        '..', 'conf.yml'))
    print('Using configuration file {}'.format(conf_path))
    db_conf = None
    with open(conf_path) as conf_yml:
        db_conf = yaml.load(conf_yml.read())['database']
    run_import(stops_path=args.stops_path,
               refs_path=args.refs_path,
               db_config=db_conf)


if __name__ == '__main__':
    main()

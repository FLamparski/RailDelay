import csv
import yaml
import argparse
import rethinkdb as r

from os import path
from datetime import datetime
from pyproj import Proj, transform

TIMING_POINT_TYPES = {
    'T': 'TRUST',
    'M': 'mandatory',
    'O': 'optional'
}


def get_loc_data(data_path):
    data = None
    with open(data_path, errors='surrogateescape') as data_file:
        data = [line.split('\t') for line in data_file if line.startswith('LOC')]

    return data


def make_timestamp(field):
    try:
        return datetime.strptime(field, '%d-%m-%Y %H:%M:%S')
    except:
        return None


def convert_single_doc(record, v36, v84, vgrid):
    vlon36, vlat36 = vgrid(record[4], record[5], inverse=True)
    longitude, latitude = transform(v36, v84, vlon36, vlat36)
    return {
        'tiploc': record[0],
        'name': record[1],
        'created_at': make_timestamp(record[2]),
        'expires_at': make_timestamp(record[3]),
        'location': r.point(longitude, latitude),
        'timing_point_type': TIMING_POINT_TYPES[record[6]],
        'zone': record[7],
        'stanox': record[8],
        'off_network': bool(record[9] == 'Y')
    }


def convert_to_docs(location_data):
    v84 = Proj(proj="latlong", towgs84="0,0,0", ellps="WGS84")
    v36 = Proj(proj="latlong", k=0.9996012717, ellps="airy",
                    towgs84="446.448,-125.157,542.060,0.1502,0.2470,0.8421,-20.4894")
    vgrid = Proj(init="world:bng")

    return [convert_single_doc(record, v36, v84, vgrid) for record in location_data]


def run_import(data_path, db_config):
    location_data = [rec[2:-1] for rec in get_loc_data(data_path)]
    location_docs = convert_to_docs(location_data)
    print(location_docs[0])


def main():
    parser = argparse.ArgumentParser(description='Import National Rail-provided TIPLOC locations')
    parser.add_argument('reference_data_path', type=str, help='Path to the Train Planning Data file')
    args = parser.parse_args()

    conf_path = path.realpath(path.join(path.dirname(__file__), '..', 'conf.yml'))

    print('Using configuration file {}'.format(conf_path));
    db_conf = None
    with open(conf_path) as conf_yml:
        db_conf = yaml.load(conf_yml.read())['database']
    run_import(data_path=args.reference_data_path, db_config=db_conf)

if __name__ == '__main__':
    main()

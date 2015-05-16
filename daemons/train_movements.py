#-*- set fileencoding=utf-8 -*-

import rethinkdb as r
import logging

from toolz.dicttoolz import merge

TRAIN_MOVEMENTS = 'com.filipwieland.rail_delay.train_movements'
MOVEMENT_TYPES = {
    '0001': 'activation',
    '0002': 'cancellation',
    '0003': 'movement',
    '0005': 'reinstatement',
    '0006': 'change-of-origin',
    '0007': 'change-of-identity'
}

logger = logging.getLogger('TrainMovements')

def get_geo(stanox, name, conn):
    geo = {}
    try:
        stanox_entry = next(r.table('stanox_lookup').filter({'stanox': stanox}).run(conn))
        geo[name + '_name'] = stanox_entry['name']
        try:
            naptan_entry = next(r.table('naptan_stops').filter({'TiplocCode': stanox_entry['tiploc']}).run(conn))
            geo[name + '_name'] = naptan_entry['StationName']
            geo[name + '_geo'] = naptan_entry['Location']
        except Exception:
            logger.info('Stanox code {} has name {} but no location'.format(stanox, stanox_entry['name']))
    except Exception:
        logger.info('Stanox code {} not present in the database'.format(stanox))
    return geo

def clean_movement_message(msg, msg_type, conn):
    extras = {'type': msg_type}
    body = msg['body']

    for key in body.keys():
        if key.endswith('_stanox'):
            logger.debug('Train {}: Lookup stanox {} for field {}'.format(body['train_id'], body[key], key))
            extras = merge(extras, get_geo(body[key], key[:-len('_stanox')], conn))

        if key.endswith('_timestamp'):
            try:
                logger.debug('Converting timestamp for field {}'.format(key))
                intval = int(body[key])
                extras[key] = r.epoch_time(intval / 1000.0)
            except:
                pass

        if body[key] == 'true' or body[key] == 'false':
            extras[key] = bool(body[key] == 'true')

    return merge(body, extras)

def process_message(msg, conn):
    cleaned = clean_movement_message(msg, MOVEMENT_TYPES[msg['header']['msg_type']], conn)
    r.table('train_movements').insert(cleaned).run(conn)

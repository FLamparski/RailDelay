import rethinkdb as r
from toolz.dicttoolz import merge

TRAIN_MOVEMENTS = 'com.filipwieland.rail_delay.subs.train_movements'
TRAIN_MOVEMENT_TYPES = {
    '0001': 'activation',
    '0002': 'cancellation',
    '0003': 'movement',
    '0005': 'reinstatement',
    '0006': 'changeoforigin',
    '0007': 'changeofidentity'
}

conn = None


def process_train_activation(doc):
    pass


def process_train_cancellation(doc):
    pass


def process_train_movement(doc, conn):
    body = doc['body']
    extras = {}

    try:
        stanox_entry = next(r.table('stanox_lookup')
                             .filter({'stanox': body['loc_stanox']}).run(conn))
        try:
            naptan_entry = next(r.table('naptan_stops')
                                 .filter({'TiplocCode': stanox_entry['tiploc']})
                                 .run(conn))
            extras['location_name'] = naptan_entry['StationName']
            extras['location_geo'] = naptan_entry['Location']
        except r.net.DefaultCursorEmpty:
            extras['location_name'] = stanox_entry['name']
            extras['location_geo'] = None
    except r.net.DefaultCursorEmpty:
        print(' ! Train with ID {train_id}: {event_type} at unknown STANOX {loc_stanox}'.format(**body))
        extras['location_name'] = None
        extras['location_geo'] = None

    return merge(body, extras)


def process_train_reinstatement(doc):
    pass


def process_train_change_of_origin(doc):
    pass


def process_train_change_of_identity(doc):
    pass


movement_handlers = {
    'movement': process_train_movement
}


def process_train_movement_msg(doc, conn):
    mtype = TRAIN_MOVEMENT_TYPES[doc['header']['msg_type']]
    try:
        new_doc = movement_handlers[mtype](doc, conn)
        r.table('train_movements').insert(new_doc).run(conn)
    except KeyError as e:
        print('Movement handler not found? {}'.format(repr(e)))


def process_message(doc, conn):
    if doc['type'] == TRAIN_MOVEMENTS:
        process_train_movement_msg(doc, conn)
    else:
        raise ValueError('Currently only train movements are supported')

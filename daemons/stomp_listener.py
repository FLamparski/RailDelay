import sys
import json
import logging
import yaml
import stomp
import rethinkdb as r

from time import sleep
from os import path
from toolz.dicttoolz import assoc

import train_movements as tm

conf_path = path.realpath(path.join(path.dirname(__file__), '..', 'conf.yml'))
print('Using configuration file {}'.format(conf_path))

HOSTS = [
    ('datafeeds.networkrail.co.uk', 61618)
]


class RailListener:
    def __init__(self, mq):
        self._mq = mq
        self._logger = logging.getLogger('RailListener')

    def on_error(self, headers, message):
        self._logger.error('Stomp error:\n{}\n{}'.format(headers, message))
        mq.disconnect()

    def on_heartbeat_timeout(self):
        self._logger.warn('Heartbeat timed out.');
        sleep(1)

    def on_message(self, headers, message):
        self._logger.info(headers)
        decoded_messages = json.loads(message)
        self._logger.info('Received a total of {} message(s)'
                          .format(len(decoded_messages)))
        for decoded_message in decoded_messages:
            doc = assoc(decoded_message, 'type', headers['subscription'])
            r.table('raw_messages').insert(doc).run(conn)
            tm.process_message(doc, conn)
        self._mq.ack(id=headers['message-id'],
                     subscription=headers['subscription'])


def setup_logging(config):
    num_loglevel = getattr(logging, config['logging']['level'].upper(), None)
    if not isinstance(num_loglevel, int):
        raise ValueError('Invalid log level in logging.level: {}'
                         .format(config['logging']['level']))
    logging.basicConfig(filename='stomp_listener.log', level=num_loglevel)


def setup_mq(config):
    mq = stomp.Connection(host_and_ports=HOSTS,
                          keepalive=True,
                          vhost='datafeeds.networkrail.co.uk',
                          heartbeats=(10000, 5000))
    mq.set_listener(None, RailListener(mq))
    mq.start()
    logging.getLogger('setup_mq').info('Connecting to the data feeds')
    mq.connect(wait=True, **config['network_rail']['connection'])
    return mq


def on_startup():
    global conn
    config = None
    with open(conf_path) as conf_yml:
        config = yaml.load(conf_yml.read())

    setup_logging(config)
    logger = logging.getLogger('main')

    conn = r.connect(**config['database'])

    mq = setup_mq(config)
    logger.info('Subscribing to the data feeds')
    mq.subscribe('/topic/TRAIN_MVT_ALL_TOC',
                 tm.TRAIN_MOVEMENTS,
                 ack='client-individual')
    return mq


def main():
    mq = on_startup()
    while mq.is_connected():
        sleep(0.1)
    conn.close()

if __name__ == '__main__':
    main()

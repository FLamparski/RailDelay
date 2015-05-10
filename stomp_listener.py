import sys
import json
import logging
import yaml
import stomp
import rethinkdb as r

from time import sleep


class RailListener:
    def __init__(self, mq, r_conn):
        self._mq = mq
        self._logger = logging.getLogger('RailListener')

    def on_error(self, headers, message):
        self._logger.error('Stomp error:\n{}\n{}'.format(headers, message))

    def on_message(self, headers, message):
        self._logger.info(headers)
        decoded_messages = json.loads(message)
        self._logger.info('Received a total of {} message(s)'
                          .format(len(decoded_messages)))
        for decoded_message in decoded_messages:
            r.table('raw_messages').insert(decoded_message).run(r_conn)
        self._mq.ack(id=headers['message-id'],
                     subscription=headers['subscription'])

if __name__ == '__main__':
    config = None
    with open('conf.yml') as conf_yml:
        config = yaml.load(conf_yml.read())

    num_loglevel = getattr(logging, config['logging']['level'].upper(), None)
    if not isinstance(num_loglevel, int):
        raise ValueError('Invalid log level in logging.level: {}'
                         .format(config['logging']['level']))
    logging.basicConfig(filename='stomp_listener.log', level=num_loglevel)
    logger = logging.getLogger('main')

    r_conn = r.connect(**config['database'])

    HOSTS = [
        ('datafeeds.networkrail.co.uk', 61618)
    ]
    mq = stomp.Connection(host_and_ports=HOSTS,
                          keepalive=True,
                          vhost='datafeeds.networkrail.co.uk',
                          heartbeats=(10000, 5000))
    mq.set_listener(None, RailListener(mq, r_conn))
    mq.start()
    logger.info('Connecting to the data feeds')
    mq.connect(wait=True, **config['network_rail']['connection'])
    logger.info('Subscribing to the data feeds')
    mq.subscribe('/topic/TRAIN_MVT_ALL_TOC',
                 config['network_rail']['id'],
                 ack='client-individual')

    while mq.is_connected():
        sleep(0.1)

# RailDelay Server

This project aims to create an API (with a realtime component) to track
UK train delays. There will also be a client app which will consume this API
and display the result on a map.

## Getting started

1. `cp conf.example.yml conf.yml`
2. Change conf.yml to include your credentials
3. `python db_setup.py`
4. `cd utils && python import_stanox_lookup.py`

This should set you up an environment in which you can run the RailDelay
server.

## Architecture

There are two daemons. The first is `stomp_listener.py`, which listens for
train movement data and spits it into the database. The second is the main
application server, which still needs to be written. It will provide an API
for the train data, including a realtime websocket endpoint hooked up to
Rethink's change feeds.

## Stuff needed to hack

* Python 3.4
* RethinkDB 2.0
* And the following Python packages:
  ```
  beautifulsoup4==4.3.2
  Flask==0.10.1
  gevent==1.0.1
  greenlet==0.4.6
  itsdangerous==0.24
  Jinja2==2.7.3
  MarkupSafe==0.23
  PyYAML==3.11
  requests==2.7.0
  rethinkdb==2.0.0.post1
  stomp.py==4.0.16
  Werkzeug==0.10.4
  ```

You should probably run this in a venv.

## Legal

For now let's call it MIT licensed (but subject to change).
No warranties expressed or implied of this thing working at all, much less
being fit for purpose.

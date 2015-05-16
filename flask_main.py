import time
import yaml
import json
import rethinkdb as r

from os import path
from flask import Flask, request, render_template, g
from toolz.dicttoolz import merge

from utils import json_formats
from trains import get_train_info

# Load the configuration file
conf_path = path.realpath(path.join(path.dirname(__file__), 'conf.yml'))
print(' > Using config file {}'.format(conf_path))
my_config = None
with open(conf_path) as conf_yml:
    my_config = yaml.load(conf_yml)

# Create the app and load the configuration into Flask
app = Flask('RailDelay')
app.config.update(**my_config)  # That's what I get for using yaml


@app.before_request
def before_request():
    g.db_conn = r.connect(**app.config['database'])
    g.start_time = time.time()


@app.teardown_request
def after_request(exception):
    conn = getattr(g, 'db_conn', None)
    if conn is not None:
        conn.close()

    if exception is not None:
        print('Exception happened: {}'.format(repr(exception)))

    time_now = time.time()
    time_then = getattr(g, 'start_time')
    print('Request {} took {}s'.format(request.url, time_now - time_then))


@app.route('/api/movements/', defaults={'page': 0})
@app.route('/api/movements/<int:page>')
def list_movements(page):
    conn = getattr(g, 'db_conn')
    base_query = r.table('train_movements').order_by(r.desc('actual_timestamp'))
    max_count = 50
    skip_count = page * max_count
    filter_by_type = request.args.get('type', '')
    if filter_by_type:
        base_query = base_query.filter({'type': filter_by_type})
    query = base_query.skip(skip_count).limit(max_count)
    mvs = list(query.run(conn))
    return json.dumps(mvs, default=json_formats.date_handler)


@app.route('/api/train/<string:train_id>')
def get_train(train_id):
    conn = getattr(g, 'db_conn')
    query = r.table('train_movements').filter(r.row['train_id'] == train_id).order_by(r.desc('actual_timestamp'))
    mvs = list(query.run(conn))
    info = get_train_info(mvs[0])
    train = merge(info, {'movements': mvs})
    return json.dumps(train, default=json_formats.date_handler)

@app.route('/')
def get_home():
    return render_template('index.j2')

if __name__ == '__main__':
    app.run()

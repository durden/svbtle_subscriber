"""
Little wrapper to kick off web interface
"""

from __future__ import with_statement

from contextlib import closing
import os
import urlparse

import psycopg2

from flask import Flask, request, render_template, g

import svbtle_subscriber as subscriber

app = Flask(__name__)
app.debug = True


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    g.db.close()


def allowed_file(filename):
    """Return True if file has allowed extension (xml only)"""

    return '.' in filename and  filename.rsplit('.', 1)[1] in set(['xml'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    return psycopg2.connect(database=url.path[1:],
                            user=url.username, password=url.password,
                            host=url.hostname, port=url.port).cursor()


def run_web(host, port):
    """Run web interface"""

    app.run(host=host, port=port)

def get_db_writers():
    cur = g.db.execute("""select name, homepage_url, feed_url
                          from svbtle_authors""")
    writers = []

    for row in cur.fetchall():
        writers.append(dict(name=row[0], homepage=row[1], rss=row[2]))

    return writers


@app.route('/')
def home():
    """homepage"""

    return render_template('index.html')


@app.route('/all')
def available():
    """Show all available writers on svbtle.com"""

    writers = get_db_writers()
    return render_template('subscriptions.html', writers=writers)


@app.route('/update')
def update_authors():
    writers = subscriber.get_writers(False)

    for writer in writers:
        cur = g.db.execute('select name from svbtle_authors where name = %s'
                            [writer['name']])

        if len(cur.fetchall()):
            g.db.execute("""
                    update svbtle_authors set homepage_url = %s, feed_url = %s
                    where name = %s""",
                    [writer['homepage'], writer['rss'], writer['name']])
            g.db.commit()
            continue

        g.db.execute("""
                    insert into svbtle_authors (name, homepage_url, feed_url)
                    values (%s, %s, %s)""",
                    [writer['name'], writer['homepage'], writer['rss']])
        g.db.commit()

    return 'Updated!'


@app.route('/missing_subscriptions', methods=['POST'])
def missing():
    """Show missing author subscriptions based on uploaded file"""

    missing_authors = []
    file_obj = request.files['reader_xml']

    if file_obj and allowed_file(file_obj.filename):
        writers = get_db_writers()

        greader_feed_urls = subscriber.get_greader_subscription_urls(
                                                                file_obj)
        if greader_feed_urls:
            missing_authors = subscriber.diff_subscriptions(
                                                        greader_feed_urls,
                                                        writers)

    return render_template('subscriptions.html', writers=missing_authors,
                            heading='Missing Svbtle Authors')


if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    run_web(host='0.0.0.0', port=port)

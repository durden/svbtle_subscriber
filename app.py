#!/usr/bin/env python

"""
Little wrapper to kick off web interface
"""

from __future__ import with_statement

import os
import urlparse

from flask import Flask, request, render_template, g, redirect, url_for

import svbtle_subscriber as subscriber

app = Flask(__name__)
app.debug = True


@app.before_request
def before_request():
    g.db_conn = connect_db()
    g.db_cursor = g.db_conn.cursor()


@app.teardown_request
def teardown_request(exception):
    g.db_cursor.close()
    g.db_conn.close()


def allowed_file(filename):
    """Return True if file has allowed extension (xml only)"""

    return '.' in filename and  filename.rsplit('.', 1)[1] in set(['xml'])


def drop_db():
    db = connect_db()
    db.cursor().execute("drop table svbtle_authors;")
    db.commit()
    db.cursor().close()
    db.close()


def init_db():
    db = connect_db()
    db.cursor().execute("""
        create table svbtle_authors (
            id serial,
            name varchar,
            homepage_url varchar,
            feed_url varchar,
            twitter_username varchar
        );""")
    db.commit()
    db.cursor().close()
    db.close()


def connect_db():
    import psycopg2

    url = urlparse.urlparse(os.environ['DATABASE_URL'])
    return psycopg2.connect(database=url.path[1:],
                            user=url.username, password=url.password,
                            host=url.hostname, port=url.port)


def run_web(host, port):
    """Run web interface"""

    app.run(host=host, port=port)


def get_db_writers():
    g.db_cursor.execute("""select name, homepage_url, feed_url,
                            twitter_username
                          from svbtle_authors""")
    writers = []

    for row in g.db_cursor.fetchall():
        twitter_url = 'http://twitter.com/%s' % (row[3])
        writers.append(dict(name=row[0], homepage=row[1], rss=row[2],
                            twitter_url=twitter_url, twitter_username=row[3]))

    return writers


def update_db(db_conn=None, verbose=True):
    if db_conn is None:
        db_conn = connect_db()
        db_cursor = db_conn.cursor()

    for writer in subscriber.get_writers(False):
        db_cursor.execute("""
                            select name from svbtle_authors where name = %s""",
                            [writer['name']])

        if len(db_cursor.fetchall()):
            db_cursor.execute("""
                    update svbtle_authors set homepage_url = %s, feed_url = %s,
                    twitter_username = %s
                    where name = %s""",
                    [writer['homepage'], writer['rss'], writer['twitter'],
                     writer['name']])
            db_conn.commit()

            if verbose:
                subscriber._dump_results([writer])

            continue

        db_cursor.execute("""
                    insert into svbtle_authors (name, homepage_url, feed_url,
                                                twitter_username)
                    values (%s, %s, %s, %s)""",
                    [writer['name'], writer['homepage'], writer['rss'],
                     writer['twitter']])
        db_conn.commit()

        if verbose:
            subscriber._dump_results([writer])


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
    return redirect(url_for('available'))


@app.route('/missing_subscriptions', methods=['POST', 'GET'])
def missing():
    """Show missing author subscriptions based on uploaded file"""

    missing_authors = []
    greader_feed_urls = []

    writers = get_db_writers()

    if not request.files or request.method == 'GET':
        url = 'http://www.google.com/reader/api/0/subscription/list'
        greader_feed_urls = subscriber.get_greader_subscription_urls(url=url)
    else:
        file_obj = request.files['reader_xml']
        if file_obj and allowed_file(file_obj.filename):
            greader_feed_urls = subscriber.get_greader_subscription_urls(
                                                                xml=file_obj)
    if len(greader_feed_urls):
        missing_authors = subscriber.diff_subscriptions(
                                                    greader_feed_urls,
                                                    writers)

    return render_template('subscriptions.html', writers=missing_authors,
                            heading='Missing Svbtle Authors')


if __name__ == '__main__':
    import sys

    if "--update" in sys.argv:
        update_db()
    elif "--init" in sys.argv:
        init_db()
    elif "--drop" in sys.argv:
        drop_db()
    else:
        port = int(os.environ.get('PORT', 5000))
        run_web(host='0.0.0.0', port=port)

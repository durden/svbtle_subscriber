#!/usr/bin/env python

"""
Module to scrape svbtle.com for all authors and get the address to their RSS
feed.
"""

import re

import requests
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup


def _get_writers_and_homepage():
    """Get a list of dicts containing writer name and homepage addresses"""

    html = requests.get('http://svbtle.com/')
    soup = BeautifulSoup(html.content)

    writer_soup = soup.findAll('li',
                               {'class': re.compile(r'.*post clearfix.*')})

    writers = []
    for writer in writer_soup:
        try:
            name = writer.find('p', {'class': 'title'}).text
        except AttributeError:
            name = 'n/a'

        homepage = re.search(r'.*href="(.*)" ', str(writer))
        try:
            homepage = homepage.group(1)
        except AttributeError:
            homepage = 'n/a'

        writers.append({'name': name, 'homepage': homepage})

    return writers


def _get_writer_rss_address(url, verbose=True):
    """Scrape given url for a feed address and return it"""

    if verbose:
        print 'Fetching rss url from: %s\r' % (url)

    html = requests.get(url)
    soup = BeautifulSoup(html.content)

    try:
        rss = soup.find('link', {'title': 'RSS'})['href']
    except (KeyError, TypeError):
        rss = ''

    return rss


def _get_greader_subscription_urls(xml=None):
    """
    Get a list of feed urls from your greader account

    xml can be an xml file object or string of xml data
    """

    if isinstance(xml, str):
        soup = BeautifulStoneSoup(xml)
    elif isinstance(xml, file):
        soup = BeautifulStoneSoup(open(xml).read())
    else:
        raise TypeError('xml must be string or file object')

    feeds = []
    xml_soup = soup.findAll('string', {'name': 'id'})

    for feed in xml_soup:
        # text starts with feed/ for some reason
        url = re.sub(r'^feed/', '', feed.text)

        if re.search(r'^http://', url):
            feeds.append(url)

    return feeds


def _diff_subscriptions(existing_feed_urls, svbtle_authors):
    """
    Diff two feed lists and return what feeds from svbtle_authors that aren't
    already in existing_feed_urls

    svbtle_authors is a list of dictionaries containing 'homepage', 'rss', and
    'name' keys.
    """

    missing_authors = []

    for author in svbtle_authors:

        feed = author['rss']

        # Feeds might have .rss or not in them, so check for both (we could use
        # set operations if it wasn't for this weirdness)
        possible_urls = [feed]
        if re.search(r'\.rss$', feed):
            possible_urls.append(feed.split('.rss')[0])
        else:
            possible_urls.append('%s.rss' % (feed))

        found = False
        for url in possible_urls:
            if url in existing_feed_urls:
                found = True
                break

        if not found:
            missing_authors.append(author)

    return missing_authors


def _dump_results(writers):
    """Dump list of writer tuples to stdout"""

    for writer in writers:
        print '%s, %s, %s' % (writer['name'], writer['homepage'],
                              writer['rss'])


def _get_writer_rss_addresses(writers, verbose):
    """
    Fill in rss urls for given writers

    More specifically fill in the 'rss' key for each writer dict in list of
    writers
    """

    for writer in writers:

        # FIXME: Could cache/db the list of authors and only do this request if
        # we have added one.  This will reduce all most all the work.
        writer['rss'] = _get_writer_rss_address(writer['homepage'], verbose)

    return writers


def _get_writers(verbose):
    """
    Get all available writers with their info

    Returns list of dictionaries with keys: 'name', 'homepage', 'rss'
    """

    writers = _get_writers_and_homepage()
    return writers
    #return _get_writer_rss_addresses(writers, verbose)


def _parse_args():
    """Parse arguments and return tuple of parsed contents"""

    import argparse

    desc = 'See what writers on svbtle.com you aren\'t subscribed to'
    parser = argparse.ArgumentParser(prog='svbtle_subscriber.py',
                                     description=desc)

    parser.add_argument('-v', '--verbose', action='store_true', required=False,
                        default=False, help='Verbose output')

    parser.add_argument('-x', '--greader_xml', action='store', required=False,
                        default=None,
                        help='XML file of Google reader subscriptions')

    parser.add_argument('-w', '--web', action='store_true', required=False,
                        default=False, help='Run web interface')

    args = parser.parse_args()
    return (args.verbose, args.greader_xml, args.web)


def run_web():
    """Run web interface"""

    import os
    from flask import Flask, request, render_template
    from werkzeug import secure_filename

    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

    def allowed_file(filename):
        return '.' in filename and  filename.rsplit('.', 1)[1] in set(['xml'])

    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/all_available')
    def available():
        writers = _get_writers(False)
        return render_template('subscriptions.html', writers=writers)

    @app.route('/missing_subscriptions', methods=['POST'])
    def missing():
        missing_authors = []
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            xml = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            writers = _get_writers(False)

            greader_feed_urls = _get_greader_subscription_urls(xml)
            if greader_feed_urls:
                missing_authors = _diff_subscriptions(greader_feed_urls,
                                                      writers)

        return render_template('subscriptions.html', writers=missing_authors)

    app.run()


def main():
    """Start"""

    import os

    verbose, reader_xml, web = _parse_args()

    if web:
        run_web()
        return

    writers = _get_writers(verbose)
    _dump_results(writers)

    if reader_xml and os.path.isfile(reader_xml):
        missing_authors = []

        greader_feed_urls = _get_greader_subscription_urls(xml_file=reader_xml)
        if greader_feed_urls:
            missing_authors = _diff_subscriptions(greader_feed_urls, writers)

        print '--- Missing authors ---'
        _dump_results(missing_authors)

if __name__ == "__main__":
    main()

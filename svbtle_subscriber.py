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


def _dump_results(writers):
    """Dump list of writer tuples to stdout"""

    for writer in writers:
        print '%s, %s, %s' % (writer['name'], writer['homepage'],
                              writer['rss'])


def _get_greader_subscription_feed_urls():
    """Get a list of feed urls from your greader account"""

    # This is the url for the web, but just for testing we are using a xml file
    # locally since authentication is a pain.  Once in a browser it will be
    # completely separate from this app for simplicity.

    #http://www.google.com/reader/api/0/subscription/list
    soup = BeautifulStoneSoup(open('sample_subscriptions.xml').read())

    feeds = []
    xml_soup = soup.findAll('string', {'name': 'id'})

    for feed in xml_soup:
        feeds.append(re.sub(r'^feed', '', feed.text))

    return feeds


def main():
    import sys

    writers = _get_writers_and_homepage()

    verbose = '-v' in sys.argv

    for writer in writers:
        writer['rss'] = _get_writer_rss_address(writer['homepage'], verbose)

    _dump_results(writers)


if __name__ == "__main__":
    main()

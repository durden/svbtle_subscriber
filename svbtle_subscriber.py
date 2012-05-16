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
        # text starts with feed/ for some reason
        url = re.sub(r'^feed/', '', feed.text)

        if re.search(r'^http://', url):
            feeds.append(url)

    return feeds


def _diff_subscriptions(existing_feed_urls, new_feed_urls):
    """
    Diff two feed lists and return what feeds from new_feed_urls that aren't
    already in existing_feed_urls
    """

    missing_feeds = []

    import pdb;pdb.set_trace()
    for feed in new_feed_urls:
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
            missing_feeds.append(feed)

    return missing_feeds


def main():
    import sys

    writers = _get_writers_and_homepage()

    verbose = '-v' in sys.argv

    svbtle_feed_urls = []
    for writer in writers:
        writer['rss'] = _get_writer_rss_address(writer['homepage'], verbose)
        svbtle_feed_urls.append(writer['rss'])

    greader_feed_urls = _get_greader_subscription_feed_urls()

    print _diff_subscriptions(greader_feed_urls, svbtle_feed_urls)

    #_dump_results(writers)


if __name__ == "__main__":
    main()

#!/usr/bin/env python

"""
Module to scrape svbtle.com for all authors and get the address to their RSS
feed.
"""

import re

import requests
from BeautifulSoup import BeautifulSoup


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


def main():
    import sys

    writers = _get_writers_and_homepage()

    verbose = '-v' in sys.argv

    for writer in writers:
        writer['rss'] = _get_writer_rss_address(writer['homepage'], verbose)

    _dump_results(writers)


if __name__ == "__main__":
    main()

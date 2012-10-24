# -*- coding: utf-8 -*-
# __author__ = 'peter'

from application import scrapemark
import logging
import cgi
import urllib, urllib2
import urlparse
import cookielib
from BeautifulSoup import BeautifulSoup
import time

def fetch_beautified_html(url, get=None, post=None, headers=None, cookie_jar=None):
    verbose=scrapemark.verbose
    user_agent=scrapemark.user_agent
    if get:
        if type(get) == str:
            get = cgi.parse_qs(get)
        l = list(urlparse.urlparse(url))
        g = cgi.parse_qs(l[4])
        g.update(get)
        l[4] = urllib.urlencode(g)
        url = urlparse.urlunparse(l)
    if post and type(post) != str:
        post = urllib.urlencode(post)
    if cookie_jar == None:
        cookie_jar = cookielib.CookieJar()
    if not headers:
        headers = {'User-Agent': user_agent}
    else:
        if 'User-Agent' not in headers:
            headers['User-Agent'] = user_agent
    if verbose:
        print 'fetching', url, '...'
    request = urllib2.Request(url, post, headers)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
    res = opener.open(request).read()
    if verbose:
        print 'DONE fetching.'
    bs=BeautifulSoup(res).prettify()
    return bs

scrapemark.fetch_html=fetch_beautified_html

pattern = scrapemark.compile("""
    {*
    <td valign="top" width="140"><img src="{{ [fishes].image }}" /></td><td>{{ [fishes].data }}</td>
    *}
    """)

def scrape():
    for fish in pattern.scrape(url='http://www.tcfishery.com/price/default.asp', post={'page':7})['fishes']:
        yield fish

if __name__ == "__main__":
    for fish in scrape():
        data=fish['data'].split(' ')
        fish['name']=data[1]
        fish['price']=float(data[5])
        fish['date']=data[8]
        del fish['data']
        logging.error(fish)


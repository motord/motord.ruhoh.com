# -*- coding: utf-8 -*-
# __author__ = 'peter'

from flask import Blueprint, current_app, request
from application import scrapemark
import logging
import cgi
import urllib, urllib2
import urlparse
import cookielib
from application.BeautifulSoup import BeautifulSoup
from google.appengine.ext import deferred, db
from flask import jsonify, json
import time, datetime
from decorators import admin_required, invalidate_cache, cached, cache
from application.datastore import JsonProperty

class Quotes(db.Model):
    fish = db.StringProperty(required=True)
    prices = JsonProperty(required=True)
    image = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

    def jsonify(self):
        return jsonify(id = self.key().id(), name = self.fish, price=self.price)

seafood = Blueprint('seafood', __name__)

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

def all_pages():
    for page in range(1,206):
        yield page

def today_pages():
    for page in range(1,9):
        yield page

def fishes():
    for page in today_pages():
        for fish in pattern.scrape(url='http://www.tcfishery.com/price/default.asp', post={'page':page})['fishes']:
            data=fish['data'].split(' ')
            fish['name']=data[1]
            fish['price']=float(data[5])
            fish['date']=data[8]
            yield fish

def fishing():
    swarm=[]
    updates={}
    for fish in fishes():
        swarm.append({'name':fish['name'], 'price':fish['price'], 'image':fish['image'], 'date':fish['date']})
    for fish in swarm:
        cache_key = fish['name']
        try:
            v=updates[cache_key]
        except KeyError:
            v = cache.get(cache_key)
        if v is None:
            q=Quotes.gql("WHERE fish = :1", cache_key)
            v=q.get()
            if v is None:
                v=Quotes(fish=fish['name'], prices={}, image=fish['image'])
        v.prices[fish['date']]=fish['price']
        updates[cache_key]=v
    for v in updates.values():
        v.put()
        cache.set(v.fish, v)

@admin_required
@invalidate_cache(key='/aqua/market.json')
@seafood.route('/aqua/scrape')
def scrape():
    deferred.defer(fishing)
    return 'Fishing'

@cached(key='/aqua/trend.json')
@seafood.route('/aqua/trend.json')
def market():
    q=Quotes.all()
    quotes=[]
    for quote in q:
        quotes.append({'fish' : quote.fish, 'prices' : quote.prices})
    return current_app.response_class(json.dumps(quotes, indent=None if request.is_xhr else 2), mimetype='application/json')

@cached(key='/aqua/market.json')
@seafood.route('/aqua/market.json')
def market():
    q=Quotes.all()
    quotes=[]
    for quote in q:
        p=quote.prices[sorted(quote.prices.iterkeys())[0]]
        d=sorted(quote.prices.iterkeys())[0]
        quotes.append({'fish' : quote.fish, 'price' : {d:p}, 'image' : quote.image})
    return current_app.response_class(json.dumps(quotes, indent=None if request.is_xhr else 2), mimetype='application/json')
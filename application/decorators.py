"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from google.appengine.api import users
from flask import redirect, request, jsonify
from models import Authorization
from google.appengine.ext import db

from werkzeug.contrib.cache import GAEMemcachedCache
cache = GAEMemcachedCache()

def login_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.get_current_user():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view


def admin_required(func):
    """Requires App Engine admin credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.is_current_user_admin():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view

def referrer_required(func):
    """Requires standard login credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not request.referrer:
            try:
                referrer=request.json['referrer']
            except KeyError:
                return jsonify(error='referrer missing')
        else:
            referrer=request.referrer
        return func(referrer, *args, **kwargs)
    return decorated_view

def cached(timeout=720 * 3600, key='{0}'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.referrer:
                try:
                    referrer=request.json['referrer']
                except (KeyError, TypeError):
                    referrer=None
            else:
                referrer=request.referrer
            cache_key = key.format(referrer)
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def invalidate_cache(key='{0}'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.referrer:
                try:
                    referrer=request.json['referrer']
                except (KeyError, TypeError):
                    referrer=None
            else:
                referrer=request.referrer
            cache_key = key.format(referrer)
            rv = f(*args, **kwargs)
            cache.delete(cache_key)
            return rv
        return decorated_function
    return decorator

def authorization_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not request.referrer:
            try:
                referrer=request.json['referrer']
            except KeyError:
                return jsonify(error='referrer missing')
        else:
            referrer=request.referrer
        cache_key='{0}/approved'.format(referrer)
        auth=cache.get(cache_key)
        email=db.Email(users.get_current_user().email())
        if users.is_current_user_admin():
            if auth is None:
                auth=Authorization.get_by_key_name(referrer)
                if auth is None:
                    auth=Authorization(key_name=referrer)
                    auth.put()
            try:
                i=auth.approved.index(email)
            except ValueError:
                i=-1
            if i==-1:
                auth.approved.append(email)
                auth.put()
            cache.set(cache_key, auth)
            return func(*args, **kwargs)
        if auth is None:
            auth=Authorization.get_by_key_name(referrer)
            if auth is not None:
                cache.set(cache_key, auth)
        try:
            i=auth.approved.index(email)
        except ValueError:
            i=-1
        if i <> -1:
            return func(*args, **kwargs)
        return jsonify(error='not authorized')
    return decorated_view

"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from google.appengine.api import users
from flask import redirect, request

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
            return func('http://none.com', *args, **kwargs)
        return func(request.referrer, *args, **kwargs)
    return decorated_view

def cached(timeout=720 * 3600, key='%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.referrer
            rv = cache.get(cache_key)
            if rv is not None:
                return rv
            rv = f(*args, **kwargs)
            cache.set(cache_key, rv, timeout=timeout)
            return rv
        return decorated_function
    return decorator

def invalidate_cache(key='%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.referrer
            rv = f(*args, **kwargs)
            cache.delete(cache_key)
            return rv
        return decorated_function
    return decorator

"""
decorators.py

Decorators for URL handlers

"""

from functools import wraps
from google.appengine.api import users
from flask import redirect, request

from werkzeug.contrib.cache import GAEMemcachedCache
cache = GAEMemcachedCache()

def admin_required(func):
    """Requires App Engine admin credentials"""
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not users.is_current_user_admin():
            return redirect(users.create_login_url(request.url))
        return func(*args, **kwargs)
    return decorated_view

def cached(timeout=720 * 3600, key='{0}'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key
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
            cache_key = key
            rv = f(*args, **kwargs)
            cache.delete(cache_key)
            return rv
        return decorated_function
    return decorator


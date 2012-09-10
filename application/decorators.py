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
            return redirect(users.create_login_url(request.url))
        return func(request.referrer, *args, **kwargs)
    return decorated_view

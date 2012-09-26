"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""


from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError
from google.appengine.ext import db

from flask import render_template, flash, url_for, redirect, request,jsonify, current_app, json

from models import Task, Authorization, AuthRequest
from decorators import login_required, admin_required, authorization_required, referrer_required, cached, invalidate_cache, cache


def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
#    return 'Hello %s' % username
    return jsonify(test=request.referrer)

@referrer_required
@cached(key='%s')
def read(referrer):
    """List all tasks"""
    q=Task.gql("WHERE referrer = :1 ORDER BY created", referrer)
    tasks = []
    for task in q:
        tasks.append({'id' : task.key().id(), 'todo' : task.todo, 'accomplished' : task.accomplished})
    return current_app.response_class(json.dumps(tasks, indent=None if request.is_xhr else 2), mimetype='application/json')

@referrer_required
@authorization_required
@invalidate_cache()
def create(referrer):
    task=Task.construct_from_json(request.json, referrer)
    task.put()
    return task.jsonify()

@referrer_required
@authorization_required
@invalidate_cache()
def update(referrer, id):
    task=Task.get_by_id(id)
    task.update_with_json(request.json)
    return task.jsonify()

@referrer_required
@authorization_required
@invalidate_cache()
def delete(referrer, id):
    task=Task.get_by_id(id)
    task.delete()
    return 'DELETED'

@referrer_required
def authorize(referrer):
    if not users.get_current_user():
        return not_authenticated(referrer)
    else:
        cache_key='%s/emails' % request.referrer
        auth=cache.get(cache_key)
        email=db.Email(users.get_current_user().email())
        if auth is None:
            auth=Authorization.get_by_key_name(request.referrer)
            if auth is not None:
                cache.set(cache_key, auth)
        try:
            i=auth.emails.index(email)
        except ValueError:
            i=-1
        if i <> -1:
            return authorized(referrer)
        else:
            return authenticated_but_not_authorized(referrer)

@cached(key='%s/not_authorized')
def authenticated_but_not_authorized(referrer):
    return jsonify(authenticated=True, authorized=False, uri=users.create_logout_url(referrer))

@cached(key='%s/authorized')
def authorized(referrer):
    return jsonify(authenticated=True, authorized=True, uri=users.create_logout_url(referrer))

@cached(key='%s/not_authenticated')
def not_authenticated(referrer):
    return jsonify(authenticated=False, authorized=False, uri=users.create_login_url(referrer))

@referrer_required
@login_required
def authorization_request(referrer):
    if not users.get_current_user():
        return not_authenticated(referrer)
    else:
        ar=AuthRequest(referrer=referrer, email=db.Email(users.get_current_user().email()))
        ar.put()
        return authenticated_but_not_authorized(referrer)

@admin_required
def approve_authorization_request():
    pass

@admin_required
def delete_authorization_request():
    pass

@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''


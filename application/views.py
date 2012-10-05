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

from models import Task, Authorization, AuthRequest, BookKeeping
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
    bk=BookKeeping(referrer=task.referrer,
        action='delete',
        before=task.todo,
        accomplished_before=task.accomplished)
    bk.put()
    task.delete()
    return 'DELETED'

@referrer_required
def authorize(referrer):
    if not users.get_current_user():
        return login(referrer)
    else:
        cache_key='%s/authorizations' % request.referrer
        auth=cache.get(cache_key)
        email=db.Email(users.get_current_user().email())
        if auth is None:
            auth=Authorization.get_by_key_name(request.referrer)
            if auth is not None:
                cache.set(cache_key, auth)
        try:
            a=auth.approved.index(email)
        except ValueError:
            a=-1
        if a <> -1:
            return logout(referrer)
        else:
            try:
                p=auth.pending.index(email)
            except ValueError:
                p=-1
            if p <> -1:
                return pending_logout(referrer)
            else:
                try:
                    r=auth.rejected.index(email)
                except ValueError:
                    r=-1
                if r <> -1:
                    return rejected_logout(referrer)
            return authorize_logout(referrer)

@cached(key='%s/authorize-logout')
def authorize_logout(referrer):
    return jsonify(authorized=False, template='#auth-template-authorize-logout', uri=users.create_logout_url(referrer))

@cached(key='%s/pending-logout')
def pending_logout(referrer):
    return jsonify(authorized=False, template='#auth-template-pending-logout', uri=users.create_logout_url(referrer))

@cached(key='%s/rejected-logout')
def rejected_logout(referrer):
    return jsonify(authorized=False, template='#auth-template-rejected-logout', uri=users.create_logout_url(referrer))

@cached(key='%s/logout')
def logout(referrer):
    return jsonify(authorized=True, template='#auth-template-logout', uri=users.create_logout_url(referrer))

@cached(key='%s/login')
def login(referrer):
    return jsonify(authorized=False, template='#auth-template-login', uri=users.create_login_url(referrer))

@referrer_required
@login_required
def authorization_request(referrer):
    if not users.get_current_user():
        return login(referrer)
    else:
        email=db.Email(users.get_current_user().email())
        ar=AuthRequest(referrer=referrer, email=email)
        ar.put()
        auth=Authorization.get_by_key_name(request.referrer)
        auth.pending.append(email)
        auth.put()
        return pending_logout(referrer)

@admin_required
def approve_ticket(referrer, email):
    auth=Authorization.get_by_key_name(referrer)
    auth.pending.remove(email)
    auth.approved.append(email)
    auth.put()
    cache_key='%s/authorizations' % referrer
    cache.set(cache_key, auth)

@admin_required
def reject_ticket(referrer, email):
    auth=Authorization.get_by_key_name(referrer)
    auth.pending.remove(email)
    auth.rejected.append(email)
    auth.put()
    cache_key='%s/authorizations' % referrer
    cache.set(cache_key, auth)

@admin_required
def read_tickets():
    pending=[]
    i=0
    q=Authorization.gql("WHERE pending != Null")
    for a in q:
        i += 1
        for p in a.pending:
            pending.append({'id' : i, 'referrer' : a.key().name(), 'email' : p})
    return current_app.response_class(json.dumps(pending, indent=None if request.is_xhr else 2), mimetype='application/json')

@admin_required
def update_tickets(id):
    referrer=request.json['referrer']
    email=db.Email(request.json['email'])
    action=request.json['action']
    if action == 'approve':
        approve_ticket(referrer, email)
        return jsonify(status='approved')
    elif action == 'reject':
        reject_ticket(referrer, email)
        return jsonify(status='rejected')

def read_tasks():
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
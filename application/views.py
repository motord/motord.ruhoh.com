"""
views.py

URL route handlers

Note that any handler params must match the URL route params.
For example the *say_hello* handler, handling the URL route '/hello/<username>',
  must be passed *username* as the argument.

"""


from google.appengine.api import users
from google.appengine.runtime.apiproxy_errors import CapabilityDisabledError

from flask import render_template, flash, url_for, redirect, request,jsonify, current_app, json

from models import Task
from decorators import login_required, admin_required, referrer_required


def say_hello(username):
    """Contrived example to demonstrate Flask's url routing capabilities"""
#    return 'Hello %s' % username
    return jsonify(test=request.referrer)

@referrer_required
def read(referrer, id):
    """List all tasks"""
    q=Task.gql("WHERE referrer = :1", referrer)
    tasks = []
    for task in q:
        tasks.append({'id' : task.key().id(), 'todo' : task.todo, 'accomplished' : task.accomplished})
    return current_app.response_class(json.dumps(tasks, indent=None if request.is_xhr else 2), mimetype='application/json')

@login_required
@referrer_required
def create(referrer):
    task=Task.construct_from_json(request.json, referrer)
    task.put()
    return task.jsonify()

@login_required
@referrer_required
def update(referrer, id):
    task=Task.get_by_id(id)
    task.update_with_json(request.json)
    return task.jsonify()

@login_required
@referrer_required
def delete(referrer, id):
    task=Task.get_by_id(id)
    task.delete()


@admin_required
def admin_only():
    """This view requires an admin account"""
    return 'Super-seekrit admin page.'


def warmup():
    """App Engine warmup handler
    See http://code.google.com/appengine/docs/python/config/appconfig.html#Warming_Requests

    """
    return ''


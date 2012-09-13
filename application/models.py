"""
models.py

App Engine datastore models

"""


from google.appengine.ext import db
from flask import jsonify
from google.appengine.api import users

class Task(db.Model):
    todo = db.StringProperty(required=True)
    referrer = db.URLProperty(required=True)
    author = db.UserProperty()
    accomplished = db.BooleanProperty(required=True, default=False)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    def jsonify(self):
        return jsonify(id = self.key().id(), todo = self.todo, accomplished = self.accomplished)

    @classmethod
    def construct_from_json(cls, json, referrer):
        return Task(todo = json['todo'], referrer=referrer, author=users.get_current_user(), accomplished = json['accomplished'])

    def update_with_json(self, json):
        self.todo=json['todo']
        self.accomplished=json['accomplished']
        self.put()
        return self
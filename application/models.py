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
    author = db.UserProperty(auto_current_user_add=True)
    editor = db.UserProperty(auto_current_user=True)
    accomplished = db.BooleanProperty(required=True, default=False)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

    def jsonify(self):
        return jsonify(id = self.key().id(), todo = self.todo, accomplished = self.accomplished)

    @classmethod
    def construct_from_json(cls, json, referrer):
        return Task(todo = json['todo'], referrer=referrer, accomplished = json['accomplished'])

    def update_with_json(self, json):
        self.todo=json['todo']
        self.accomplished=json['accomplished']
        self.put()
        return self

class Authorization(db.Model):
    emails=db.ListProperty(db.Email)

class AuthRequest(db.Model):
    referrer = db.URLProperty(required=True)
    email = db.EmailProperty(required=True)
    approved = db.BooleanProperty(default=False, required=True)
    rejected = db.BooleanProperty(default=False, required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    modified = db.DateTimeProperty(auto_now=True)

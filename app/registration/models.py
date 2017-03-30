from app.db import db
from app.user.models import User
from flask import Blueprint, abort

class Registration(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.Text(), unique = True)
    blob = db.Column(db.Text())
    priority = db.Column(db.Integer())
    confirmed = db.Column(db.Boolean())
    uni_id = db.Column(db.Integer(), db.ForeignKey('uni.id'))
    uni = db.relationship('Uni', backref=db.backref('Registrations', lazy='dynamic', cascade="all, delete-orphan"))

    priority_constraint = db.UniqueConstraint('uni_id', 'priority', name='uni_priority_unique')

    @property
    def user(self):
        return User.get(self.username)

class Uni(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    token = db.Column(db.String(256), unique = True)
    name = db.Column(db.Text(), unique = True)

    def __init__(self, name, token):
        self.name = name
        self.token = token

    def __repr__(self):
        return "<Uni: {}>".format(self.name)

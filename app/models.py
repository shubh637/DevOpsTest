from . import db
from flask_login import UserMixin
from datetime import datetime

#User class to store the user information.
#UserMixin used to give User class some certain methods need for operation example:authentication ,manage sessions.
class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(100))
    name=db.Column(db.String(100))

    workouts=db.relationship('Workout',backref='author',lazy=True)#can use backref='user' also its just name refference.

#store the information about the workouts 
class Workout(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    pushups=db.Column(db.Integer,nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    comment=db.Column(db.Text,nullable=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)

 
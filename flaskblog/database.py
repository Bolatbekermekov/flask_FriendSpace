from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flaskblog import db, login_manager, app

#Initiialize The Database


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
#Create Model
class Users(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True,unique=True)
    username = db.Column(db.String(200),nullable=False)
    name = db.Column(db.String(200),nullable=False)
    email = db.Column(db.String(120),nullable=False,unique=True)
    about_author = db.Column(db.Text(500),nullable=True)
    date_added = db.Column(db.DateTime,default=datetime.utcnow)
    profile_pic = db.Column(db.String(200),nullable=True )
    password_hash = db.Column(db.String(130),nullable=False)
    posts = db.relationship('Posts',backref='poster')


    @property
    def password(self):
        raise AttributeError('password is not a readable attribute!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Create String
    def __repr__(self):
        return "<Name %r>" % self.name


# Create a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    date_posted = db.Column(db.DateTime,default=datetime.utcnow)
    slug = db.Column(db.String(256))
    #Foreign Key To Link Users (refer to primary key of thr user)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))
from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime ,timedelta
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)#
    username = db.Column(db.String(32), unique=True, nullable=False)#
    passhash = db.Column(db.String(256), nullable=False)#
    name = db.Column(db.String(64), nullable=False)#
    is_librarian = db.Column(db.Boolean, nullable=False, default=False)#

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)#
    name = db.Column(db.String(32), unique=True)#
    date_created = db.Column(db.Date,default=datetime.utcnow)#
    description = db.Column(db.Text)#
    books = db.relationship('Book', backref='section', lazy=True,cascade='all, delete-orphan')

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)#
    name = db.Column(db.String(64), nullable=False)#
    content = db.Column(db.Text)#
    authors = db.Column(db.String(255))#
    book_upload_date = db.Column(db.Date,default=datetime.utcnow)#
    book_rating = db.Column(db.Float) 
    
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)#
    bookrequest = db.relationship('BookRequest', backref='book', lazy=True, cascade='all, delete-orphan')#
    feedback_records = db.relationship('Feedback', backref='', lazy=True, cascade='all, delete-orphan')


class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)#
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)#
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)#
    request_date = db.Column(db.DateTime,default=datetime.utcnow)#
    requested_day=db.Column(db.Integer)#
    status=db.Column(db.String(30),default='Pending')#
    issued_date = db.Column(db.DateTime) 
    return_date = db.Column(db.DateTime) # no need
    access_expiry = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='bookrequest', lazy=True)


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer,CheckConstraint('rating >= 0 AND rating <= 5'))
    feedback = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('feedback', lazy=True))
    book = db.relationship('Book', backref=db.backref('feedback', lazy=True))
    

with app.app_context():
    db.create_all()




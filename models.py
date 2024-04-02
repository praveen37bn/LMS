from app import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint
from datetime import datetime 
from werkzeug.security import generate_password_hash

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    passhash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(64), nullable=True)
    is_librarian = db.Column(db.Boolean, nullable=False, default=False)

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), unique=True)
    date_created = db.Column(db.Date,default=datetime.utcnow)
    description = db.Column(db.Text)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text)
    authors = db.Column(db.String(255))
    
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('book', lazy=True))


class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.DateTime,default=datetime.utcnow)
    requested_day=db.Column(db.Integer)
    status=db.Column(db.String(30),default='Pending')
    issued_date = db.Column(db.DateTime) 
    return_date = db.Column(db.DateTime)
    
    user = db.relationship('User', backref=db.backref('bookrequest', lazy=True))
    book = db.relationship('Book', backref=db.backref('bookrequest', lazy=True))
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer,CheckConstraint('rating >= 0 AND rating <= 5'))
    feedback = db.Column(db.Text)

    user = db.relationship('User', backref=db.backref('feedback', lazy=True))
    book = db.relationship('Book', backref=db.backref('feedback', lazy=True))
class AccessLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    access_date = db.Column(db.Date, default=datetime.now, nullable=False)
    revoked = db.Column(db.Boolean, default=False)

    user = db.relationship('User', backref=db.backref('accesslog', lazy=True))
    book = db.relationship('Book', backref=db.backref('accesslog', lazy=True))

with app.app_context():
    db.create_all()




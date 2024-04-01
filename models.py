from app import app
from flask_sqlalchemy import SQLAlchemy
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
    date_created = db.Column(db.Date, default=datetime.now, nullable=False)
    description = db.Column(db.Text)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text)
    authors = db.Column(db.String(255))
    date_issued = db.Column(db.DateTime)
    return_date = db.Column(db.DateTime)

    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    section = db.relationship('Section', backref=db.backref('book', lazy=True))

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    request_date = db.Column(db.Date, default=datetime.now, nullable=False)
    return_date = db.Column(db.DateTime)

    user = db.relationship('User', backref=db.backref('bookrequest', lazy=True))
    book = db.relationship('Book', backref=db.backref('bookrequest', lazy=True))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)

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




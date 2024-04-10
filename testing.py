from flask import flash, redirect, render_template, url_for
from app import app, db
from models import User, BookRequest
from datetime import datetime, timedelta

@app.route('/mybook')
@auth_required
def mybook():
    user = User.query.get(session['user_id'])
    mybooks = BookRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('mybook.html', mybooks=mybooks, user=user)


@app.route('/read_book/<int:book_request_id>', methods=['POST'])
@auth_required  
def mybook_read(book_request_id):
    user = User.query.get(session['user_id'])
    book_request = BookRequest.query.get(book_request_id)

    if book_request:
        if book_request.requested_day and not book_request.access_expiry:
            book_request.access_expiry = book_request.issued_date + timedelta(days=book_request.requested_day)

        if book_request.access_expiry and book_request.access_expiry < datetime.utcnow():
            book_request.status = "Expired"

        if book_request.status == 'Rejected' or book_request.status == 'Expired':
            db.session.delete(book_request)

        # Commit all changes at once
        db.session.commit()

        if book_request.status == 'Granted':
            book = book_request.book
            return render_template('book/show.html', book=book, user=user)

    flash('Access denied or book request not found.')
    return redirect(url_for('mybook'))

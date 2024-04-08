from flask import request, redirect, url_for, flash
from app import app, db
from models import BookRequest
from datetime import datetime, timedelta
from functools import wraps

# Custom decorator for librarian authentication
def librarian_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Implement your logic for librarian authentication here
        # Example: Check if user is a librarian based on session or user role
        # if not user.is_librarian:
        #     flash('You do not have permission to access this page.')
        #     return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/process_request/<int:request_id>/<action>', methods=['POST'])
@librarian_required
def process_request(request_id, action):
    book_request = BookRequest.query.get(request_id)

    if not book_request:
        flash('Book request not found.')
        return redirect(url_for('see_requests'))

    if action == 'grant':
        # Update request status to 'Granted' and set issued date
        book_request.status = 'Granted'
        book_request.issued_date = datetime.utcnow()

        # Calculate access expiry based on requested days
        if book_request.requested_day:
            book_request.access_expiry = book_request.issued_date + timedelta(days=book_request.requested_day)

        # Check if access expiry has passed and update status accordingly
        if book_request.access_expiry and book_request.access_expiry < datetime.utcnow():
            book_request.status = 'Expired'
            book_request.return_date = book_request.access_expiry

    elif action == 'reject':
        # Update request status to 'Rejected' and clear issued date and access expiry
        book_request.status = 'Rejected'
        book_request.issued_date = None
        book_request.access_expiry = None

    # Delete the request from database if status is 'Rejected'
    if book_request.status == 'Rejected':
        db.session.delete(book_request)

    # Commit changes to the database
    db.session.commit()

    flash('Request processed successfully.')
    return redirect(url_for('see_requests'))

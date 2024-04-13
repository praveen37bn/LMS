@app.route('/myfeedback/<int:book_id>', methods=['POST'])
@auth_required
def myfeedback_post(book_id):
    book_request = BookRequest.query.get(book_id)

    if not book_request:
        flash('Book request not found')
        return redirect(url_for('mybook'))

    # Check if user has already submitted feedback for this book request
    existing_feedback = Feedback.query.filter_by(user_id=session['user_id'], book_id=book_request.book_id).first()
    if existing_feedback:
        flash('You have already submitted feedback for this book request')
        return redirect(url_for('mybook'))

    # Retrieve form data
    rating = request.form.get('rating')
    feedback_text = request.form.get('feedback')

    # Create new Feedback record
    feedback = Feedback(user_id=session['user_id'], book_id=book_request.book_id, rating=rating, feedback=feedback_text)
    
    # Add and commit to database
    db.session.add(feedback)
    db.session.commit()

    flash('Feedback sent successfully.')
    return redirect(url_for('mybook'))

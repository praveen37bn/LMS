@app.route('/process_request/<int:request_id>/<action>', methods=['POST'])
@librarian_required
def process_request(request_id, action):
    book_request = BookRequest.query.get(request_id)

    if not book_request:
        flash('Book request not found.')  
        return redirect(url_for('see_requests'))
    if action == 'grant':
        book_request.issued_date = datetime.utcnow()
        book_request.status = 'Granted'
       
    elif action == 'reject':
        book_request.status = 'Rejected'
        book_request.issued_date = None
        book_request.access_expiry = None


    if book_request.requested_day:
            book_request.access_expiry = book_request.issued_date + timedelta(days=book_request.requested_day)

    if book_request.access_expiry < datetime.utcnow() :
        book_request.status = "Expired"
        db.session.commit()  
    
    if book_request.status == 'Rejected' or book_request.status=='Expired':
        db.session.delete(book_request)  

    db.session.commit()
    flash('Request processed successfully')
    return redirect(url_for('see_requests'))
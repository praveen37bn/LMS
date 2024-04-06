@app.route('/read_book/<int:book_request_id>', methods=['POST'])
@auth_required  # Ensure the user is authenticated to access this route
def read_book(book_request_id):
    # Retrieve the BookRequest based on the book_request_id
    book_request = BookRequest.query.get(book_request_id)

    if book_request and book_request.status == 'Granted':
        # Retrieve the Book associated with the BookRequest
        book = book_request.book

        # Display the book content or perform further actions (e.g., render a template)
        return render_template('book_content.html', book=book)

    # Handle other cases (e.g., invalid request or unauthorized access)
    flash('Access denied. Book request not granted.')
    return redirect(url_for('mybook'))  # Redirect to a suitable route (e.g., mybook)

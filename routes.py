from flask import Flask,render_template,redirect,url_for,flash,request,session
from app import app
from functools import wraps
from models import db, User,Book,BookRequest,Feedback,AccessLog,Section
from werkzeug.security import generate_password_hash ,check_password_hash
from datetime import datetime ,timedelta



@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods= ['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    is_librarian = int(request.form.get('userType'))

    if not username or not password or not confirm_password:
        flash('Please fill out all fields')
        return redirect(url_for('register'))

    if password != confirm_password:
        flash('Passwords do not match')
        return redirect(url_for('register'))
    
    user = User.query.filter_by(username=username).first()
    if user:
        flash('Username already exists')
        return redirect(url_for('register'))

    password_hash = generate_password_hash(password)

    new_user = User(username = username, passhash = password_hash, name = name ,is_librarian = is_librarian)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('login'))
##################################################
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login',methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Please fill out all fields')
        return redirect(url_for('login'))

    user = User.query.filter_by(username = username).first()

    if not user:
        flash('Username does not exist')
        return redirect(url_for('login'))
    
    if not check_password_hash(user.passhash , password):
        flash('Incorrect password')
        return redirect(url_for('login'))
    
    session['user_id'] = user.id
    flash('Login successful')
    return redirect(url_for('index'))

############################################

def auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('Please login to continue')
            return redirect(url_for('login'))
    return inner

def librarian_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_librarian:
            flash('You are not authorized to access this page')
            return redirect(url_for('index'))
        return func(*args, **kwargs)
    return inner

############################################




@app.route('/profile')
@auth_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)
    

@app.route('/profile',methods=['POST'])
@auth_required
def profile_post():
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    name = request.form.get('name')

    if not username or not cpassword or not password or not name:
        flash('Please fill out all the required fields')
        return redirect(url_for('profile'))

    user = User.query.get(session['user_id'])
    if not check_password_hash(user.passhash, cpassword):
        flash('incorrect Password')
        return redirect(url_for('profile'))
    if username != user.username:
        new_username = User.query.filter_by(username = username).first()
        if new_username :
            flash('Username already exists')
            return redirect(url_for('profile'))
        
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.passhash = new_password_hash
    user.name = name 
    db.session.commit()
    flash('Profile update successfully')
    return redirect(url_for('profile'))

@app.route('/logout')
@auth_required
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))
################################################
@app.route('/librarian')
@librarian_required
def librarian():
    user = User.query.get(session['user_id'])
    sections = Section.query.all()
    section_names = [section.name for section in sections]
    return render_template('librarian.html', sections=sections, section_names=section_names,user= user )
#########################

@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_librarian:
        return redirect(url_for('librarian'))
    
    sections = Section.query.all()
    for section in sections:
        for book in section.books:
            ratings= Feedback.query.filter_by(book_id=book.id).all()
            if ratings:
                valid_ratings = [rating.rating for rating in ratings if rating.rating is not None]
                avg_rating = sum(valid_ratings)/len(valid_ratings)
                book.book_rating = avg_rating


    sname = request.args.get('sname') or ''
    bname = request.args.get('bname') or ''
    aname = request.args.get('aname')

    if sname:
        sections = Section.query.filter(Section.name.ilike(f'%{sname}%')).all()


    db.session.commit()
    return render_template('index.html',user = user, sections=sections, bname=bname, aname=aname, sname= sname)

################################

@app.route('/section/add')
@librarian_required
def add_section():
    user = User.query.get(session['user_id'])
    return render_template('section/add.html',user=user)


@app.route('/section/add', methods=['POST'])
@librarian_required
def add_section_post():
    name = request.form.get('name')
    description = request.form.get('description')

    if not name:
        flash('Please fill out all fields')
        return redirect(url_for('add_section'))
    
    section = Section(name=name,description=description,)
    db.session.add(section)
    db.session.commit()

    flash('Section added successfully')
    return redirect(url_for('librarian'))
    

@app.route('/section/<int:id>/edit')
@librarian_required
def edit_section(id):
    user = User.query.get(session['user_id'])
    section = Section.query.get(id)
    return render_template('section/edit.html', section=section,user=user)


@app.route('/section/<int:id>/edit', methods=['POST'])
@librarian_required
def edit_section_post(id):
    section = Section.query.get(id)

    name = request.form.get('name')
    description= request.form.get('description')

    section.name = name
    section.description = description
    db.session.commit()
    flash('Section updated successfully')
    return redirect(url_for('librarian'))

@app.route('/section/<int:id>')
@librarian_required
def show_section(id):
    user = User.query.get(session['user_id'])
    section = Section.query.get(id)
    books = Book.query.filter_by(section_id=id).all()
    return render_template('section/show.html',books=books,section = section,user=user)


@app.route('/section/<int:id>/delete')
@librarian_required
def delete_section(id):
    user = User.query.get(session['user_id'])
    section = Section.query.get(id)
    return render_template('section/delete.html', section=section,user=user)

@app.route('/section/<int:id>/delete', methods=['POST'])
@librarian_required
def delete_section_post(id):
    section = Section.query.get(id)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted successfully')
    return redirect(url_for('librarian'))

#######################################################

@app.route('/book/add/<int:section_id>')
@librarian_required
def add_book(section_id):
    user = User.query.get(session['user_id'])
    sections = Section.query.all()
    section = Section.query.get(section_id)
    return render_template('book/add.html', section=section, sections=sections,user=user)


@app.route('/book/add/', methods=['POST'])
@librarian_required
def add_book_post():
    name = request.form.get('name')
    authors = request.form.get('authors')
    content = request.form.get('content')
    section_id = request.form.get('section_id')
    section = Section.query.get(section_id)

    book = Book(name=name, authors=authors, section=section, content=content,section_id=section_id)
    db.session.add(book)
    db.session.commit()
    flash('Product added successfully')
    return redirect(url_for('show_section', id=section_id))


@app.route('/book/<int:id>/show')
@librarian_required
def show_book(id):
    user = User.query.get(session['user_id'])
    book = Book.query.get(id)
    return render_template('book/show.html',book= book,user=user)




@app.route('/book/<int:id>/edit')
@librarian_required
def edit_book(id):
    user = User.query.get(session['user_id'])
    sections = Section.query.all()
    book = Book.query.get(id)
    return render_template('book/edit.html', sections=sections, book=book,user=user)

@app.route('/book/<int:id>/edit', methods=['POST'])
@librarian_required
def edit_book_post(id):
    name = request.form.get('name')
    section_id = request.form.get('section_id')
    content = request.form.get('content')
    authors = request.form.get('authors')

    section = Section.query.get(section_id)

    book = Book.query.get(id)
    book.name = name
    book.content = content
    book.section = section
    book.authors = authors
    db.session.commit()

    flash('Product edited successfully')
    return redirect(url_for('show_section', id=section_id))


@app.route('/book/<int:id>/delete')
@librarian_required
def delete_book(id):
    user = User.query.get(session['user_id'])
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('librarian'))
    return render_template('book/delete.html', book=book,user=user)

@app.route('/book/<int:id>/delete', methods=['POST'])
@librarian_required
def delete_book_post(id):
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('librarian'))
    section_id = book.section.id
    db.session.delete(book)
    db.session.commit()

    flash('Book deleted successfully')
    return redirect(url_for('show_section', id=section_id))

###########################

@app.route('/mybook')
@auth_required
def mybook():
    user = User.query.get(session['user_id'])
    mybooks = BookRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('mybook.html', mybooks=mybooks,user=user)

@app.route('/read_book/<int:book_request_id>', methods=['POST'])
@auth_required  
def mybook_read(book_request_id):
    user = User.query.get(session['user_id'])
    book_request = BookRequest.query.get(book_request_id)
    if book_request and book_request.status == 'Granted':
        book = book_request.book
        return render_template('book/show.html', book=book,user=user)
    flash('Access denied Book request not granted.')
    return redirect(url_for('mybook'),user=user)  


@app.route('/return_request/<int:book_request_id>', methods=['POST'])
@auth_required 
def myrequest_return(book_request_id):
    mybook_request = BookRequest.query.get(book_request_id)
    if mybook_request and mybook_request.status == 'Pending':
        mybook_request.status = 'Rejected'
        if mybook_request.status== 'Rejected':
            db.session.delete(mybook_request)
        db.session.commit()
        flash(' Book request return ')
    else:
        flash('Invalid book return request')
    return redirect(url_for('mybook'))  


@app.route('/mybook_return/<int:book_id>',methods=['POST'])
@auth_required
def myreqeust_return(book_id):
    book = BookRequest.query.get(book_id)
    book.return_date = datetime.utcnow()
    book.status = 'Complete'
    db.session.commit()
    flash('book Returnd successfully')
    return redirect(url_for('mybook'))






@app.route('/book_request')
@auth_required
def book_request():
    user = User.query.get(session['user_id'])
    request = BookRequest.query.filter_by(user_id=session['user_id']).all()
    
    return render_template('requests/send_req.html',request= request,user=user)


@app.route('/book_request,<int:book_id>', methods=['POST'])
@auth_required
def book_request_post(book_id):
    days =  int(request.form.get('requested_day'))
    user_id = session['user_id']
    
    if days > 20 and days < 0 :
        flash('You can request max 20 days')
        return redirect(url_for('index'))

    check_exist = BookRequest.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    if check_exist:
        flash('You have already requested for this book')
        return redirect(url_for('index'))

    num_of_requests = BookRequest.query.filter_by(user_id=user_id, status='Pending').count()

    if  num_of_requests >= 5:
        flash('You have reached the maximum limit of 5 requests')
        return redirect(url_for('index'))
        
   

    
    new_request = BookRequest(user_id=user_id, book_id=book_id, requested_day=days)
    db.session.add(new_request)
    db.session.commit()

    flash('Book request sent successfully')
    return redirect(url_for('index'))

@app.route('/see_requests')
@librarian_required
def see_requests():
    requests = BookRequest.query.all()
    user_id = session.get('user_id')
    user = User.query.get(user_id)

    return render_template('see_req.html', requests=requests ,user = user)

#################################

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
        if book_request.requested_day:
            book_request.access_expiry = book_request.issued_date + timedelta(days=book_request.requested_day)
    elif action == 'reject':
        book_request.status = 'Rejected'
        book_request.issued_date = None
        book_request.access_expiry = None

    if book_request.access_expiry and book_request.access_expiry < datetime.utcnow():        
        book_request.status = 'Expired'
        book_request.return_date = book_request.access_expiry

    

    if book_request.status == 'Rejected':
        db.session.delete(book_request)  

    db.session.commit()
    flash('Request processed successfully')
    return redirect(url_for('see_requests'))


################################################################


@app.route('/myfeedback/<int:book_id>')
@auth_required
def myfeedback(book_id):
    user = User.query.get(session['user_id'])
    book_request = BookRequest.query.get(book_id)
    return render_template('feedback.html', book_request=book_request,user=user)


@app.route('/myfeedback/<int:book_id>', methods=['POST'])
@auth_required
def myfeedback_post(book_id):
    book_request = BookRequest.query.get(book_id)

    if not book_request:
        flash('Book request not found')
        return redirect(url_for('mybook'))

    if request.method == 'POST':
        rating = request.form.get('rating')
        feedback_text = request.form.get('feedback')

        feedback = Feedback(user_id=session['user_id'],book_id=book_request.book_id,rating=rating,feedback=feedback_text)
        db.session.add(feedback)
        db.session.commit()

        flash('Feedback sent successfully.')
        return redirect(url_for('mybook'))

    return render_template('feedback.html', book_request=book_request)



#######################################################








@app.route('/book_detail/<int:book_id>')
@auth_required
def book_detail(book_id):
    user = User.query.get(session['user_id'])
    book = Book.query.get_or_404(book_id)
    ratings = Feedback.query.filter_by(book_id=book.id).all()
    valid_ratings = [rating.rating for rating in ratings if rating.rating is not None]
    avg_rating = sum(valid_ratings) / len(valid_ratings) if valid_ratings else 0

    return render_template('book_detail.html', user=user , book=book, avg_rating=avg_rating, ratings=ratings)




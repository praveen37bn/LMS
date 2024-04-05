from flask import Flask,render_template,redirect,url_for,flash,request,session
from app import app
from functools import wraps
from models import db, User,Book,BookRequest,Feedback,AccessLog,Section
from werkzeug.security import generate_password_hash ,check_password_hash



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
    sections = Section.query.all()
    section_names = [section.name for section in sections]
    return render_template('librarian.html', sections=sections, section_names=section_names )

######################

#########################

@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_librarian:
        return redirect(url_for('librarian'))
    
    sections = Section.query.all()
    
    sname = request.args.get('sname')
    bname = request.args.get('bname')
    dname = request.args.get('dname')

    if sname:
        pass
    
    return render_template('index.html',user = user.is_librarian, sections=sections, bname=bname, dname=dname, sname= sname)


################################

@app.route('/section/add')
@librarian_required
def add_section():
    return render_template('section/add.html')


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
    section = Section.query.get(id)
    return render_template('section/edit.html', section=section)


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
    section = Section.query.get(id)
    books = Book.query.filter_by(section_id=id).all()
    return render_template('section/show.html',books=books,section = section)


@app.route('/section/<int:id>/delete')
@librarian_required
def delete_section(id):
    section = Section.query.get(id)
    return render_template('section/delete.html', section=section)

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
    sections = Section.query.all()
    section = Section.query.get(section_id)
    return render_template('book/add.html', section=section, sections=sections)


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
    book = Book.query.get(id)
    return render_template('book/show.html',book= book)




@app.route('/book/<int:id>/edit')
@librarian_required
def edit_book(id):
    sections = Section.query.all()
    book = Book.query.get(id)
    return render_template('book/edit.html', sections=sections, book=book)

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
    
    book = Book.query.get(id)
    if not book:
        flash('Book does not exist')
        return redirect(url_for('librarian'))
    return render_template('book/delete.html', book=book)

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
    mybooks = BookRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('mybook.html', mybooks=mybooks)


@app.route('/book_request')
@auth_required
def book_request():
    request = BookRequest.query.filter_by(user_id=session['user_id']).all()
    return render_template('requests/send_req.html',request= request)

###################
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

        
    new_request = BookRequest(user_id=user_id, book_id=book_id, requested_day=days)
    db.session.add(new_request)
    db.session.commit()

    flash('Book request sent successfully')
    return redirect(url_for('index'))


@app.route('/see_requests')
@librarian_required
def see_requests():
    requests = BookRequest.query.all()
    return render_template('requests/see_req.html', requests=requests)
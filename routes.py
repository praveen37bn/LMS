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

# @app.route('/librarian')
# @librarian_required
# def librarian():
#     return render_template('librarian.html')

#########################

@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_librarian:
        return redirect(url_for('librarian'))
    
    sections = Section.query.all()
    return render_template('index.html', sections=sections )
################################

###########################


@app.route('/profile')
@auth_requried
def profile():
    user =User.query.get(session['user_id'])
    return render_template('profile.html',user = user)

@app.route('/profile',methods=['POST'])
@auth_requried
def profile_post():
    username = request.form.get('username')
    cpassword = request.form.get('cpassword')
    password = request.form.get('password')
    name = request.form.get('name')

    if not username or not cpassword or not password:
        flash('Please fill out all the required fields')
        return redirect(url_for('profile'))
    user = User.query.get(session['user_id'])
    if not check_password_hash(user.password, cpassword):
        flash('incorrect Password')
        return redirect(url_for('profile'))
    if username != user.username:
        new_username = User.query.filter_by(username = username).first()
        if new_username :
            flash('Username already exists')
            return redirect(url_for('profile'))
    new_password_hash = generate_password_hash(password)
    user.username = username
    user.password = password
    user.name = name 
    db.session.commit()
    flash('Profile update successfully')
    return redirect(url_for('profile'))

@app.route('/logout')
@auth_requried
def logout():
    session.pop('user_id')
    return redirect(url_for('login'))

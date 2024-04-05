
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@auth_required
def add_to_cart(product_id):
    product = Product.query.get(product_id)
    if not product:
        flash('Product does not exist')
        return redirect(url_for('index'))
    quantity = request.form.get('quantity')
    try:
        quantity = int(quantity)
    except ValueError:
        flash('Invalid quantity')
        return redirect(url_for('index'))
    if quantity <= 0 or quantity > product.quantity:
        flash(f'Invalid quantity, should be between 1 and {product.quantity}')
        return redirect(url_for('index'))

    cart = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()

    if cart:
        if quantity + cart.quantity > product.quantity:
            flash(f'Invalid quantity, should be between 1 and {product.quantity}')
            return redirect(url_for('index'))
        cart.quantity += quantity
    else:
        cart = Cart(user_id=session['user_id'], product_id=product_id, quantity=quantity)
        db.session.add(cart)

    db.session.commit()

    flash('Product added to cart successfully')
    return redirect(url_for('index'))


@app.route('/cart')
@auth_required
def cart():
    carts = Cart.query.filter_by(user_id=session['user_id']).all()
    total = sum([cart.product.price * cart.quantity for cart in carts])
    return render_template('cart.html', carts=carts, total=total)

@app.route('/cart/<int:id>/delete', methods=['POST'])
@auth_required
def delete_cart(id):
    cart = Cart.query.get(id)
    if not cart:
        flash('Cart does not exist')
        return redirect(url_for('cart'))
    if cart.user_id != session['user_id']:
        flash('You are not authorized to access this page')
        return redirect(url_for('cart'))
    db.session.delete(cart)
    db.session.commit()
    flash('Cart deleted successfully')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@auth_required
def checkout():
    carts = Cart.query.filter_by(user_id=session['user_id']).all()
    if not carts:
        flash('Cart is empty')
        return redirect(url_for('cart'))

    transaction = Transaction(user_id=session['user_id'], datetime=datetime.now())
    for cart in carts:
        order = Order(transaction=transaction, product=cart.product, quantity=cart.quantity, price=cart.product.price)
        if cart.product.quantity < cart.quantity:
            flash(f'Product {cart.product.name} is out of stock')
            return redirect(url_for('delete_cart', id=cart.id))
        cart.product.quantity -= cart.quantity
        db.session.add(order)
        db.session.delete(cart)
    db.session.add(transaction)
    db.session.commit()

    flash('Order placed successfully')
    return redirect(url_for('orders'))

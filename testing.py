
@app.route('/product/<int:id>/delete')
@admin_required
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        flash('Product does not exist')
        return redirect(url_for('admin'))
    return render_template('product/delete.html', product=product)

@app.route('/product/<int:id>/delete', methods=['POST'])
@admin_required
def delete_product_post(id):
    product = Product.query.get(id)
    if not product:
        flash('Product does not exist')
        return redirect(url_for('admin'))
    category_id = product.category.id
    db.session.delete(product)
    db.session.commit()

    flash('Product deleted successfully')
    return redirect(url_for('show_category', id=category_id))



@app.route('/category/<int:id>/delete')
@admin_required
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin'))
    return render_template('category/delete.html', category=category)

@app.route('/category/<int:id>/delete', methods=['POST'])
@admin_required
def delete_category_post(id):
    category = Category.query.get(id)
    if not category:
        flash('Category does not exist')
        return redirect(url_for('admin'))
    db.session.delete(category)
    db.session.commit()

    flash('Category deleted successfully')
    return redirect(url_for('admin'))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
from flask import render_template, request, redirect, url_for, flash, session, Response, abort
from models import db, User, Crop, Inventory, Sale, Supplier, CropInventory, Alert, save_alert
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///crop_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        db.session.add_all([
            User(name="Admin One", role="admin", email="admin@example.com", password=generate_password_hash("admin")),
            User(name="Farmer John", role="farmer", email="farmer@example.com", password=generate_password_hash("farmer")),
            User(name="Expert Alice", role="expert", email="expert@example.com", password=generate_password_hash("expert"))
        ])
        db.session.commit()

@app.route('/')
def home():
    if 'user_id' in session and 'role' in session:
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/crops')
def crops():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    role = session.get('role')
    search = request.args.get('search', '').strip()
    query = Crop.query
    if role == 'farmer':
        query = query.filter_by(user_id=user_id)
    if search:
        query = query.filter(Crop.name.ilike(f"%{search}%"))
    user_crops = query.all()
    return render_template('crops.html', crops=user_crops, search=search)

@app.route('/crops/add', methods=['GET', 'POST'])
def add_crop():
    if request.method == 'POST':
        name = request.form['name']
        planting_date = datetime.strptime(request.form['planting_date'], "%Y-%m-%d").date()
        harvest_date = datetime.strptime(request.form['harvest_date'], "%Y-%m-%d").date()
        yield_quantity_str = request.form.get('yield_quantity', '').strip()
        yield_quantity = int(yield_quantity_str) if yield_quantity_str else None
        user_id = session.get('user_id')
        if not user_id:
            flash('You must be logged in to add a crop.')
            return redirect(url_for('login'))
        new_crop = Crop(name=name, planting_date=planting_date, harvest_date=harvest_date, user_id=user_id)
        if hasattr(new_crop, 'yield_quantity'):
            new_crop.yield_quantity = yield_quantity
        db.session.add(new_crop)
        db.session.commit()
        return redirect(url_for('crops'))
    return render_template('crop_form.html', crop=None)

@app.route('/crops/edit/<int:id>', methods=['GET', 'POST'])
def edit_crop(id):
    crop = Crop.query.get_or_404(id)
    if request.method == 'POST':
        crop.name = request.form['name']
        crop.planting_date = datetime.strptime(request.form['planting_date'], "%Y-%m-%d").date()
        crop.harvest_date = datetime.strptime(request.form['harvest_date'], "%Y-%m-%d").date()
        yield_quantity_str = request.form.get('yield_quantity', '').strip()
        yield_quantity = int(yield_quantity_str) if yield_quantity_str else None
        if hasattr(crop, 'yield_quantity'):
            crop.yield_quantity = yield_quantity
        db.session.commit()
        flash('Crop updated successfully!')
        return redirect(url_for('crops'))
    users = User.query.all()
    return render_template('crop_form.html', users=users, crop=crop)

@app.route('/crops/delete/<int:id>', methods=['POST'])
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    db.session.delete(crop)
    db.session.commit()
    flash('Crop deleted successfully!')
    return redirect(url_for('crops'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            session['username'] = user.name
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password!')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    role = session['role']
    user_id = session['user_id']
    search_alert_id = request.args.get('search_alert_id', '').strip()
    crops = []
    alerts = []
    # Filter alerts by alert ID if provided
    if search_alert_id and search_alert_id.isdigit():
        user_alerts = Alert.query.filter_by(user_id=user_id, id=int(search_alert_id)).order_by(Alert.created_date.desc()).all()
    else:
        user_alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.created_date.desc()).all()
    if role == 'admin':
        crops = Crop.query.all()
        # Low stock alerts for all inventory
        low_stock_items = Inventory.query.filter(Inventory.quantity < 20).all()
        for item in low_stock_items:
            alerts.append(f"Low stock: {item.name} (Quantity: {item.quantity})")
    elif role == 'farmer':
        crops = Crop.query.filter_by(user_id=user_id).all()
        today = date.today()
        for crop in crops:
            if crop.harvest_date < today:
                msg = f"Overdue harvest: {crop.name} (was due {crop.harvest_date})"
                alerts.append(msg)
                save_alert(user_id, 'harvest_overdue', msg, db, Alert)
            elif (crop.harvest_date - today).days <= 7:
                msg = f"Upcoming harvest: {crop.name} (due {crop.harvest_date})"
                alerts.append(msg)
                save_alert(user_id, 'harvest_due', msg, db, Alert)
        # Low stock alerts for this farmer's inventory
        low_stock_items = Inventory.query.filter_by(user_id=user_id).filter(Inventory.quantity < 20).all()
        for item in low_stock_items:
            msg = f"Low stock: {item.name} (Quantity: {item.quantity})"
            alerts.append(msg)
            save_alert(user_id, 'low_stock', msg, db, Alert)
    elif role == 'expert':
        crops = Crop.query.all()
    else:
        flash('Unknown role!')
        return redirect(url_for('login'))
    return render_template('dashboard.html', crops=crops, role=role, alerts=alerts, user_alerts=user_alerts, search_alert_id=search_alert_id)

@app.route('/inventory')
def inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    role = session.get('role')
    search_name = request.args.get('search_name', '').strip()
    if role == 'admin':
        query = Inventory.query
    else:
        query = Inventory.query.filter_by(user_id=user_id)
    if search_name:
        query = query.filter(Inventory.name.ilike(f"%{search_name}%"))
    items = query.all()
    return render_template('inventory.html', items=items, search_name=search_name)

@app.route('/inventory/add', methods=['GET', 'POST'])
def add_inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    suppliers = Supplier.query.all()
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        expiry_date_str = request.form.get('expiry_date')
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                expiry_date = None
        user_id = session['user_id']
        supplier_id = request.form.get('supplier_id')
        item = Inventory(name=name, quantity=quantity, user_id=user_id, supplier_id=supplier_id, expiry_date=expiry_date)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('inventory'))
    return render_template('inventory_form.html', item=None, suppliers=suppliers)

@app.route('/inventory/edit/<int:id>', methods=['GET', 'POST'])
def edit_inventory(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    suppliers = Supplier.query.all()
    item = Inventory.query.get_or_404(id)
    if request.method == 'POST':
        item.name = request.form['name']
        item.quantity = int(request.form['quantity'])
        expiry_date_str = request.form.get('expiry_date')
        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                expiry_date = None
        item.expiry_date = expiry_date
        supplier_id = request.form.get('supplier_id')
        item.supplier_id = supplier_id
        db.session.commit()
        flash('Inventory item updated!')
        return redirect(url_for('inventory'))
    return render_template('inventory_form.html', item=item, suppliers=suppliers)

@app.route('/inventory/delete/<int:id>', methods=['POST'])
def delete_inventory(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    item = Inventory.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Inventory item deleted!')
    return redirect(url_for('inventory'))

@app.route('/crops/<int:crop_id>/assign-inventory', methods=['GET', 'POST'])
def assign_inventory(crop_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    crop = Crop.query.get_or_404(crop_id)
    user_id = session['user_id']
    inventory_items = Inventory.query.filter_by(user_id=user_id).all()
    if request.method == 'POST':
        # Remove previous assignments for this crop
        CropInventory.query.filter_by(crop_id=crop_id).delete()
        for item in inventory_items:
            qty_str = request.form.get(f'quantity_used_{item.id}')
            if qty_str:
                try:
                    qty = int(qty_str)
                except ValueError:
                    qty = 0
                if qty > 0:
                    assignment = CropInventory(crop_id=crop_id, inventory_id=item.id, quantity_used=qty)
                    db.session.add(assignment)
        db.session.commit()
        flash('Inventory assigned to crop!')
        return redirect(url_for('assign_inventory', crop_id=crop_id))
    # Get current assignments
    assignments = {ci.inventory_id: ci.quantity_used for ci in CropInventory.query.filter_by(crop_id=crop_id).all()}
    return render_template('assign_inventory.html', crop=crop, inventory_items=inventory_items, assignments=assignments)

@app.route('/reports')
def reports():
    if 'user_id' not in session or 'role' not in session:
        return redirect(url_for('login'))
    role = session['role']
    user_id = session['user_id']
    today = date.today()
    # Crops with harvests due soon or overdue
    if role == 'admin':
        crops = Crop.query.all()
        inventory_items = Inventory.query.all()
    else:
        crops = Crop.query.filter_by(user_id=user_id).all()
        inventory_items = Inventory.query.filter_by(user_id=user_id).all()
    due_crops = []
    for crop in crops:
        if crop.harvest_date < today:
            due_crops.append({'crop': crop, 'status': 'Overdue'})
        elif (crop.harvest_date - today).days <= 7:
            due_crops.append({'crop': crop, 'status': 'Due Soon'})
    # Inventory items with low stock
    low_stock = [item for item in inventory_items if item.quantity < 20]
    # Inventory used per crop
    crop_inventory_usage = []
    for crop in crops:
        usage = []
        for ci in CropInventory.query.filter_by(crop_id=crop.id).all():
            inv = Inventory.query.get(ci.inventory_id)
            if inv:
                usage.append({'item': inv, 'quantity_used': ci.quantity_used})
        if usage:
            crop_inventory_usage.append({'crop': crop, 'usage': usage})
    return render_template('reports.html', due_crops=due_crops, low_stock=low_stock, crop_inventory_usage=crop_inventory_usage)

@app.route('/export/crops')
def export_crops():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    crops = Crop.query.filter_by(user_id=user_id).all()
    # Prepare CSV
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Crop Name', 'Quantity', 'Type', 'Planting Date', 'Harvest Date'])
    for crop in crops:
        # Use getattr to avoid AttributeError if fields are missing
        name = crop.name
        quantity = getattr(crop, 'yield_quantity', '')
        crop_type = getattr(crop, 'type', '')
        planting_date = crop.planting_date
        harvest_date = crop.harvest_date
        writer.writerow([name, quantity, crop_type, planting_date, harvest_date])
    output = si.getvalue()
    si.close()
    return Response(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=crops.csv'
        }
    )

@app.route('/export/inventory')
def export_inventory():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    inventory_items = Inventory.query.filter_by(user_id=user_id).all()
    import csv
    from io import StringIO
    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Name', 'Quantity', 'Unit'])
    for item in inventory_items:
        # Unit is not in the model, so leave blank or set as 'N/A'
        writer.writerow([item.name, item.quantity, ''])
    output = si.getvalue()
    si.close()
    return Response(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=inventory.csv'
        }
    )

@app.route('/crops/<int:crop_id>')
def crop_detail(crop_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    crop = Crop.query.get_or_404(crop_id)
    # Assigned inventory
    assigned_inventory = []
    for ci in CropInventory.query.filter_by(crop_id=crop_id).all():
        inv = Inventory.query.get(ci.inventory_id)
        if inv:
            assigned_inventory.append({'item': inv, 'quantity_used': ci.quantity_used})
    return render_template('crop_detail.html', crop=crop, assigned_inventory=assigned_inventory)

@app.route('/set-password/<email>/<raw_password>')
def set_password(email, raw_password):
    user = User.query.filter_by(email=email).first()
    if not user:
        return f"User with email {email} not found.", 404
    user.password = generate_password_hash(raw_password)
    db.session.commit()
    return f"Password updated for {email}."

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/users/add', methods=['GET', 'POST'])
def admin_add_user():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash('Email already exists!')
            return redirect(url_for('admin_add_user'))
        user = User(name=name, email=email, role=role, password=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('User added!')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', user=None)

@app.route('/admin/users/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_user(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        user.role = request.form['role']
        password = request.form['password']
        if password:
            user.password = generate_password_hash(password)
        db.session.commit()
        flash('User updated!')
        return redirect(url_for('admin_users'))
    return render_template('admin_user_form.html', user=user)

@app.route('/admin/users/delete/<int:id>', methods=['POST'])
def admin_delete_user(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted!')
    return redirect(url_for('admin_users'))

@app.route('/sales/add', methods=['GET', 'POST'])
def add_sale():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    crops = Crop.query.all()
    if request.method == 'POST':
        crop_id = int(request.form['crop_id'])
        quantity_sold = int(request.form['quantity_sold'])
        price = float(request.form['price'])
        sale_date = datetime.strptime(request.form['sale_date'], "%Y-%m-%d").date()
        sale = Sale(crop_id=crop_id, quantity_sold=quantity_sold, price=price, sale_date=sale_date)
        db.session.add(sale)
        db.session.commit()
        flash('Sale entry added!')
        return redirect(url_for('dashboard'))
    return render_template('add_sale.html', crops=crops)

@app.route('/sales')
def sales():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    search_id = request.args.get('search_id', '').strip()
    query = Sale.query
    if search_id:
        if search_id.isdigit():
            query = query.filter_by(id=int(search_id))
        else:
            flash('Please enter a valid numeric Sale ID.')
            return render_template('sales_list.html', sales=[], role=session.get('role'), search_id=search_id)
    sales = query.all()
    sales_data = []
    for sale in sales:
        crop_name = sale.crop.name if sale.crop else 'Unknown'
        sales_data.append({
            'id': sale.id,
            'crop_name': crop_name,
            'quantity_sold': sale.quantity_sold,
            'price': sale.price,
            'sale_date': sale.sale_date
        })
    role = session.get('role')
    return render_template('sales_list.html', sales=sales_data, role=role, search_id=search_id)

@app.route('/admin/suppliers')
def admin_suppliers():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    suppliers = Supplier.query.all()
    return render_template('admin_suppliers.html', suppliers=suppliers)

@app.route('/admin/suppliers/add', methods=['GET', 'POST'])
def admin_add_supplier():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        address = request.form['address']
        supplier = Supplier(name=name, contact=contact, address=address)
        db.session.add(supplier)
        db.session.commit()
        flash('Supplier added!')
        return redirect(url_for('admin_suppliers'))
    return render_template('admin_supplier_form.html', supplier=None)

@app.route('/admin/suppliers/edit/<int:id>', methods=['GET', 'POST'])
def admin_edit_supplier(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    supplier = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier.name = request.form['name']
        supplier.contact = request.form['contact']
        supplier.address = request.form['address']
        db.session.commit()
        flash('Supplier updated!')
        return redirect(url_for('admin_suppliers'))
    return render_template('admin_supplier_form.html', supplier=supplier)

@app.route('/admin/suppliers/delete/<int:id>', methods=['POST'])
def admin_delete_supplier(id):
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)
    supplier = Supplier.query.get_or_404(id)
    db.session.delete(supplier)
    db.session.commit()
    flash('Supplier deleted!')
    return redirect(url_for('admin_suppliers'))

@app.route('/test-alert')
def test_alert():
    if 'user_id' not in session:
        flash('You must be logged in to test alerts.')
        return redirect(url_for('login'))
    user_id = session['user_id']
    msg = f"Test alert for user {user_id} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    save_alert(user_id, 'test', msg, db, Alert)
    user_alerts = Alert.query.filter_by(user_id=user_id).order_by(Alert.created_date.desc()).all()
    return render_template('dashboard.html', users=[], crops=[], role=session.get('role'), alerts=[], user_alerts=user_alerts)

if __name__ == '__main__':
    app.run(debug=True)

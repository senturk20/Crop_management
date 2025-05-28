from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    # Relationships
    crops = db.relationship('Crop', backref='user', lazy=True)
    alerts = db.relationship('Alert', backref='user', lazy=True)

class Supplier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    address = db.Column(db.String(200))
    # No explicit inventory relationship needed; handled by Inventory

class Crop(db.Model):
    __tablename__ = 'crop'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    planting_date = db.Column(db.Date, nullable=False)
    harvest_date = db.Column(db.Date, nullable=False)
    yield_quantity = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Only define the relationship ONCE, and only on one side
    crop_inventories = db.relationship('CropInventory', backref='crop', cascade='all, delete-orphan')
    sales = db.relationship('Sale', backref='crop', cascade='all, delete-orphan')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'))
    expiry_date = db.Column(db.Date)
    supplier = db.relationship('Supplier', backref=db.backref('inventory', lazy=True))

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    quantity_sold = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.Date, nullable=False)
    # Do NOT define crop relationship here (handled by Crop)

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)
    alert_message = db.Column(db.String(255), nullable=False)
    created_date = db.Column(db.DateTime, nullable=False)
    # No explicit user relationship needed

class CropInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    crop_id = db.Column(db.Integer, db.ForeignKey('crop.id'), nullable=False)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    quantity_used = db.Column(db.Integer, nullable=False)
    # Only define inventory relationship here
    inventory = db.relationship('Inventory', backref=db.backref('crop_inventories', cascade='all, delete-orphan'))
    # Do NOT define crop relationship here (handled by Crop)

def save_alert(user_id, alert_type, alert_message, db, AlertModel, created_date=None):
    """
    Helper to save an alert to the DB, avoiding duplicates (same user, type, message, and date).
    Usage: save_alert(user_id, 'low_stock', 'Low stock: Item X', db, Alert)
    """
    from datetime import datetime
    if created_date is None:
        created_date = datetime.utcnow()
    # Check for duplicate (same user, type, message, and date)
    existing = AlertModel.query.filter_by(
        user_id=user_id,
        alert_type=alert_type,
        alert_message=alert_message
    ).filter(AlertModel.created_date >= created_date.replace(hour=0, minute=0, second=0, microsecond=0),
             AlertModel.created_date <= created_date.replace(hour=23, minute=59, second=59, microsecond=999999)).first()
    if not existing:
        alert = AlertModel(user_id=user_id, alert_type=alert_type, alert_message=alert_message, created_date=created_date)
        db.session.add(alert)
        db.session.commit()
        return alert
    return existing

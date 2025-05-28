from app import app, db, User, Crop, Inventory, Supplier

with app.app_context():
    print('User count:', User.query.count())
    print('Crop count:', Crop.query.count())
    print('Inventory count:', Inventory.query.count())
    print('Supplier count:', Supplier.query.count())

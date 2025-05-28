BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS alert (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    alert_type TEXT,
    alert_message TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);
CREATE TABLE IF NOT EXISTS "crop" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(100) NOT NULL,
	"planting_date"	DATE NOT NULL,
	"harvest_date"	DATE NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"yield_quantity"	INTEGER,
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS crop_inventory (
	id INTEGER NOT NULL, 
	crop_id INTEGER NOT NULL, 
	inventory_id INTEGER NOT NULL, 
	quantity_used INTEGER NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(crop_id) REFERENCES crop (id), 
	FOREIGN KEY(inventory_id) REFERENCES inventory (id)
);
CREATE TABLE IF NOT EXISTS "inventory" (
	"id"	INTEGER NOT NULL,
	"name"	VARCHAR(100) NOT NULL,
	"quantity"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"expiry_date"	INTEGER, supplier_id INTEGER REFERENCES supplier(id),
	PRIMARY KEY("id"),
	FOREIGN KEY("user_id") REFERENCES "user"("id")
);
CREATE TABLE IF NOT EXISTS "sale" (
	"id"	INTEGER,
	"crop_id"	INTEGER NOT NULL,
	"quantity_sold"	INTEGER,
	"price"	REAL,
	"sale_date"	DATE,
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("crop_id") REFERENCES "crop"("id")
);
CREATE TABLE IF NOT EXISTS supplier (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    address TEXT
);
CREATE TABLE IF NOT EXISTS user (
	id INTEGER NOT NULL, 
	name VARCHAR(100) NOT NULL, 
	role VARCHAR(20) NOT NULL, 
	email VARCHAR(100) NOT NULL, password TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (email)
);
COMMIT;

-- USERS table
CREATE TABLE USERS (
    User_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Role ENUM('Farmer', 'Expert', 'Supplier', 'Admin') NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE
);

-- SUPPLIERS table
CREATE TABLE SUPPLIERS (
    Supplier_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Address VARCHAR(255)
);

-- CROPS table
CREATE TABLE CROPS (
    Crop_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(50),
    Planting_Date DATE,
    Harvest_Date DATE,
    Yield_Quantity DECIMAL(10,2),
    User_ID INT,
    FOREIGN KEY (User_ID) REFERENCES USERS(User_ID)
);

-- INVENTORY table
CREATE TABLE INVENTORY (
    Item_ID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Type VARCHAR(50),
    Quantity INT,
    Expiry_Date DATE,
    Supplier_ID INT,
    FOREIGN KEY (Supplier_ID) REFERENCES SUPPLIERS(Supplier_ID)
);

-- SALES table
CREATE TABLE SALES (
    Sale_ID INT PRIMARY KEY AUTO_INCREMENT,
    Crop_ID INT,
    Quantity_Sold INT,
    Price DECIMAL(10,2),
    Sale_Date DATE,
    FOREIGN KEY (Crop_ID) REFERENCES CROPS(Crop_ID)
);

-- CROP_INVENTORY junction table
CREATE TABLE CROP_INVENTORY (
    Crop_ID INT,
    Item_ID INT,
    PRIMARY KEY (Crop_ID, Item_ID),
    FOREIGN KEY (Crop_ID) REFERENCES CROPS(Crop_ID),
    FOREIGN KEY (Item_ID) REFERENCES INVENTORY(Item_ID)
);

-- ALERTS table
CREATE TABLE ALERTS (
    Alert_ID INT PRIMARY KEY AUTO_INCREMENT,
    User_ID INT,
    Alert_Type VARCHAR(50),
    Alert_Message VARCHAR(255),
    Created_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (User_ID) REFERENCES USERS(User_ID)
);

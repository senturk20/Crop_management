-- Migration script to add expiry_date column to Inventory table
ALTER TABLE inventory ADD COLUMN expiry_date DATE;

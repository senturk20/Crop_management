# Crop Management Flask App

This project is a Flask web application with MySQL integration. It supports user login and role-based dashboard routing for admin, farmer, and expert roles. The app uses Flask-MySQLdb for database access and Flask session management for authentication and authorization.

## Features
- User registration and login
- Role-based dashboards (admin, farmer, expert)
- MySQL database integration

## Setup
1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
2. Install dependencies:
   ```powershell
   pip install Flask Flask-MySQLdb
   ```
3. Configure your MySQL database in `app.py`.
4. Run the app:
   ```powershell
   python app.py
   ```

## Folder Structure
- `app.py` - Main Flask application
- `.github/copilot-instructions.md` - Copilot custom instructions

## Notes
- Ensure MySQL is running and accessible.
- Update database credentials in the code as needed.

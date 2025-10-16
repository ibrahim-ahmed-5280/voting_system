from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.admin.admin_model import AdminModel, AdminDatabase, check_admin_model_connection
from flask_bcrypt import Bcrypt, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
import pandas as pd
import re

bcrypt = Bcrypt(app)

# Helper function for session management
def get_session_data():
    """Retrieve session data."""
    return session.get('email')

# Routes
# Admin login page
@app.route('/')
def login_page():
    return render_template("admin/admin_login.html")

# Admin registration page
@app.route('/register_admin')
def registration_admin_page():
    return render_template("admin/register_admin.html")

# Dashboard admin page
@app.route('/dashboard_admin')
def dashboard_admin():
    email = get_session_data()
    print(email)
    if not email:
        return login_page()
    return render_template("admin/dashboard.html")

# Students register page
@app.route('/register_students')
def register_students():
    return render_template("admin/register_students.html")

# Students view page
@app.route('/view_students')
def view_students():
    return render_template("admin/view_students.html")

# teachers register page
@app.route('/register_teacher')
def register_teacher():
    return render_template("admin/register_teacher.html")

# teachers view page
@app.route('/view_teacher')
def view_teacher():
    return render_template("admin/view_teacher.html")

@app.route('/view_excel', methods=['POST'])
def view_excel():
    # Check if the file is included in the request
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part in the request!'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file!'})

    try:
        filename = file.filename.lower()

        # Auto-detect file type by extension
        if filename.endswith('.csv'):
            excel_data = pd.read_csv(file)
        elif filename.endswith('.xls'):
            print('123hellow')
            excel_data = pd.read_excel(file, engine='xlrd')
        elif filename.endswith(('.xlsx', '.xls')):
            excel_data = pd.read_excel(file, engine='openpyxl')
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported file type! Please upload CSV or Excel.'})

        print("Excel/CSV data preview:")
        print(excel_data[['ID clear','Student clear']])

        # Return preview (first 5 rows)
        preview = excel_data.head(5).to_dict(orient='records')
        return jsonify({'status': 'success', 'data': preview})

    except Exception as e:
        print("Error reading file:", e)
        return jsonify({'status': 'error', 'message': f'Failed to read file: {str(e)}'})


#====================================================
# these routes make inserting or delete from database
#====================================================

# register admin
@app.route('/add_admin', methods=['POST'])
def add_admin():
    data = request.get_json()
    print(data)
    # Extract fields
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # --- NAME VALIDATION ---
    name_parts = [part for part in name.split(' ') if part]
    if len(name_parts) < 3 or len(name_parts) > 4:
        return jsonify({
            "success": False,
            "error": "invalid_name",
            "message": "Full name must contain 3 or 4 parts (first, middle, last)."
        })

    if not all(re.match(r'^[A-Za-z]{3,15}$', part) for part in name_parts):
        return jsonify({
            "success": False,
            "error": "invalid_name",
            "message": "Each name part must be 3–15 alphabetic characters."
        })

    if len(name) < 9 or len(name) > 60:
        return jsonify({
            "success": False,
            "error": "invalid_name",
            "message": "Full name must be between 9 and 60 characters long."
        })

    # --- EMAIL VALIDATION ---
    email_pattern = re.compile(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
    if not email_pattern.match(email):
        return jsonify({
            "success": False,
            "error": "invalid_email",
            "message": "Please enter a valid email address."
        })

    # --- PASSWORD VALIDATION ---
    if len(password) < 6 or len(password) > 20:
        return jsonify({
            "success": False,
            "error": "invalid_password",
            "message": "Password must be 6 to 20 chars"
        })

    # ✅ All validations passed
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    password_hashed = bcrypt.generate_password_hash(data.get('password')).decode('utf-8')
    flag = admin_model.register_admin(data.get('name'),data.get('email'), password_hashed)
    if flag:
        return jsonify({
            "success": True,
            "message": "Admin added successfully."
        })
    return jsonify({
        "success": False,
        "message": "Data not registered successfully."
    })

@app.route('/login_admin', methods=['POST'])
def login_admin():
    data = request.get_json()
    print(data)
    # Extract fields
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    # ✅ All validations passed
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, result = admin_model.check_login(data.get('email'))
    if flag:
        if check_password_hash(result[0].get('password'), password):
            print(result)
            session['email'] = result[0].get('username')
            return jsonify({
                "success": True,
                "message": "Admin added successfully."
            })
        else:
            return jsonify({
                "success": False,
                "error": "invalid_pass",
                "message": "Password is incorrect."
            })

    return jsonify({
        "success": False,
        "error": "invalid_email",
        "message": "Data not registered successfully."
    })


@app.route('/logout')
def logout_admin():
    session.clear()
    return login_page()

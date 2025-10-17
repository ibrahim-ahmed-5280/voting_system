from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.student.student_model import UserModel, UserDatabase, check_user_model_connection, bcrypt
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
from flask_bcrypt import Bcrypt, check_password_hash

# Helper function for session management
def get_session_data():
    """Retrieve session data."""
    return session.get('email')

# Routes
# Admin login page
@app.route('/user_login')
def user_login():
    return render_template("student/student and teacher login.html")

# Dashboard admin page
@app.route('/dashboard_user')
def dashboard_user():
    if 'user_id' not in session:
        return redirect('/user_login')  # Redirect to login if not logged in

    # Pass the name and role from session
    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()  # Capitalize first letter
    user_id = session.get('id', 'id')

    return render_template("student/user_dashboard.html", user_name=user_name, user_role=user_role,user_id=user_id)


from flask import request, jsonify, session
from werkzeug.security import check_password_hash

from flask import request, jsonify, session
from werkzeug.security import check_password_hash
from app import app
# from app.user_model_connection import check_user_model_connection  # adjust to your real path
@app.route('/student_or_teacher_login', methods=['POST'])
def student_or_teacher_login():
    data = request.get_json()
    print("Login request:", data)

    # Step 1: Extract and validate input
    user_id = str(data.get('id', '')).strip()
    password = data.get('password', '').strip()
    role = data.get('role', '').strip().lower()

    if not user_id or not password or not role:
        return jsonify({
            "success": False,
            "error": "missing_fields",
            "message": "Please fill all fields."
        }), 400

    if role not in ['student', 'teacher']:
        return jsonify({
            "success": False,
            "error": "invalid_role",
            "message": "Invalid role selected."
        }), 400

    # Step 2: Database connection
    connection_status, user_model = check_user_model_connection()
    if not connection_status:
        return jsonify({
            "success": False,
            "error": "db_failed",
            "message": "Database connection failed."
        }), 500

    # Step 3: Fetch user record
    found, result = user_model.check_login(user_id, role)
    if not found or not result:
        return jsonify({
            "success": False,
            "error": "invalid_id",
            "message": "No account found with that ID."
        }), 404

    user = result[0]
    db_password = user.get('password', '')

    # Step 4: Password verification (plain or bcrypt)
    password_match = False
    try:
        if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
            # bcrypt hashed password
            password_match = bcrypt.check_password_hash(db_password, password)
        else:
            # plain password
            password_match = password == db_password
    except Exception as e:
        print("⚠️ Password check error:", e)
        password_match = False

    if not password_match:
        return jsonify({
            "success": False,
            "error": "invalid_pass",
            "message": "Password is incorrect."
        }), 401

    # Step 5: Create session
    session.clear()
    session['user_id'] = user.get('id')
    session['name'] = user.get('name')
    session['role'] = role

    print(f"✅ Login successful — ID: {session['user_id']}, Name: {session['name']}, Role: {session['role']}")

    # Step 6: Success response
    return jsonify({
        "success": True,
        "message": f"{role.capitalize()} login successful.",
        "redirect": f"/{role}_dashboard"
    }), 200

@app.route('/password_change', methods=['POST'])
def password_change():
    print("\n🟢 [ROUTE] /password_change called")

    # ✅ Check JSON request
    if not request.is_json:
        print("🔴 Request is not JSON")
        return jsonify({'success': False, 'message': 'Invalid request format'}), 400

    # ✅ Get session data
    user_id = session.get('user_id')
    role = session.get('role')
    print(f"🟡 Session Data -> user_id: {user_id}, role: {role}")

    if not user_id or not role:
        print("🔴 Missing session data. User not logged in.")
        return jsonify({'success': False, 'message': 'You must be logged in to change your password'}), 401

    # ✅ Extract request data
    data = request.get_json()
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    print(f"🟢 Received JSON data -> {data}")

    # ✅ Validation
    if not old_password or not new_password or not confirm_password:
        print("🔴 Validation failed: missing fields")
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    if len(new_password) < 4:
        print("🔴 Validation failed: password too short")
        return jsonify({'success': False, 'message': 'New password must be at least 4 characters'}), 400
    if new_password != confirm_password:
        print("🔴 Validation failed: passwords do not match")
        return jsonify({'success': False, 'message': 'Passwords do not match'}), 400

    # ✅ Database connection
    print("🟡 Connecting to database...")
    connection_status, model = check_user_model_connection()
    print(f"🟢 Connection status: {connection_status}")
    if not connection_status:
        print("🔴 Database connection failed")
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        # ✅ Fetch user by role using correct `id`
        print(f"🟢 Fetching user data for {role} -> ID: {user_id}")
        success, user_data = model.check_user(user_id, role)
        print(f"🟢 User fetch result: {success}, Data: {user_data}")

        if not success or not user_data:
            print("🔴 User not found")
            return jsonify({'success': False, 'message': f'{role.capitalize()} not found'}), 404

        user = user_data[0]
        stored_password = user['password']
        print(f"🟡 Stored password: {stored_password}")

        # ✅ Verify password (plain or hashed)
        if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
            valid = bcrypt.check_password_hash(stored_password, old_password)
        else:
            valid = old_password == stored_password

        print(f"🟢 Password verification result: {valid}")
        if not valid:
            print("🔴 Current password incorrect")
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401

        # ✅ Hash new password
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        print(f"🟢 New hashed password: {new_hash}")

        # ✅ Prepare update query (use `id` for both roles)
        if role == 'student':
            update_query = "UPDATE students SET password = %s WHERE id = %s"
        else:
            update_query = "UPDATE teachers SET password = %s WHERE id = %s"

        # ✅ Execute update
        print(f"🟢 Executing update query for {role}...")
        model.cursor.execute(update_query, (new_hash, user_id))
        model.connection.commit()
        print("✅ Password successfully updated")

        return jsonify({'success': True, 'message': 'Password changed successfully!'}), 200

    except Exception as e:
        print(f"🔥 Exception caught: {str(e)}")
        app.logger.error(f"Password change error: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

from flask import redirect, url_for

@app.route('/logoutUser', methods=['GET'])
def logoutUser():
    print("🟢 [ROUTE] /logout called")
    user_id = session.get('user_id')
    role = session.get('role')
    print(f"🟡 Logging out user -> ID: {user_id}, Role: {role}")

    # Clear the session for the current user
    session.clear()
    print("✅ Session cleared")

    # Redirect to login page
    return redirect(url_for('user_login'))


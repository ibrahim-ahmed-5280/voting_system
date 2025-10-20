from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for, flash
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

@app.route('/dashboard_data', methods=['GET'])
def dashboard_data():
    # Step 0: check login
    if 'user_id' not in session or 'role' not in session:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    user_id = session['user_id']
    role = session['role']  # 'student' or 'teacher'

    try:
        # Step 1: connect to DB
        status, user_model, conn = check_user_model_connection()
        if not status:
            return jsonify({"success": False, "message": "Database connection failed"}), 500

        cursor = conn.cursor(dictionary=True)

        # Step 2: total elections
        cursor.execute("SELECT COUNT(*) AS total_elections FROM election")
        total_elections = cursor.fetchone()['total_elections']

        # Step 3: elections by status
        cursor.execute("""
            SELECT 
                SUM(status='ongoing') AS ongoing,
                SUM(status='upcoming') AS upcoming,
                SUM(status='completed') AS completed
            FROM election
        """)
        status_counts = cursor.fetchone()

        # Step 4: elections the user participated in
        cursor.execute("""
            SELECT COUNT(DISTINCT election_id) AS participated
            FROM votes
            WHERE voter_type = %s AND voter_id = %s
        """, (role, user_id))
        participated = cursor.fetchone()['participated']

        # Step 5: close cursor and connection
        cursor.close()
        conn.close()

        # Step 6: return JSON
        return jsonify({
            "success": True,
            "data": {
                "total_elections": total_elections,
                "ongoing": status_counts['ongoing'],
                "upcoming": status_counts['upcoming'],
                "completed": status_counts['completed'],
                "participated": participated
            }
        })

    except Exception as e:
        print("Dashboard error:", e)
        return jsonify({"success": False, "message": str(e)}), 500
    
    
@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('id', 'id')

    elections = []
    try:
        success, user_model, connection = check_user_model_connection()
        if success:
            # Query to get elections with candidate count
            query = """
            SELECT e.*, COUNT(c.id) as candidate_count 
            FROM election e 
            LEFT JOIN candidates c ON e.id = c.election_id 
            GROUP BY e.id 
            ORDER BY e.start_date DESC
            """
            user_model.cursor.execute(query)
            elections = user_model.cursor.fetchall()
            
            print("\n" + "="*50)
            print("ELECTION DATA DEBUG INFORMATION")
            print("="*50)
            print(f"Total elections retrieved: {len(elections)}")
            
            if not elections:
                print("No elections found in database!")
            else:
                for i, election in enumerate(elections):
                    print(f"\n--- Election {i+1} ---")
                    print(f"ID: {election.get('id')}")
                    print(f"Name: {election.get('election_name')}")
                    print(f"Description: {election.get('description')[:50]}...")  # First 50 chars
                    print(f"Status: {election.get('status')}")
                    print(f"Start Date: {election.get('start_date')}")
                    print(f"End Date: {election.get('end_date')}")
                    print(f"Candidate Count: {election.get('candidate_count')}")
                    
                    # Image path analysis
                    photo_path = election.get('photo_path')
                    print(f"Photo Path: {photo_path}")
                    print(f"Photo Path is None: {photo_path is None}")
                    print(f"Photo Path is empty string: {photo_path == ''}")
                    if photo_path:
                        print(f"Photo Path length: {len(photo_path)}")
                        print(f"Expected static URL: {url_for('static', filename='uploads/' + photo_path)}")
            
            # For each election, get candidate details to check for winners
            print("\n" + "="*50)
            print("CANDIDATE DATA FOR EACH ELECTION")
            print("="*50)
            
            for election in elections:
                candidate_query = """
                SELECT id, name, status 
                FROM candidates 
                WHERE election_id = %s
                """
                user_model.cursor.execute(candidate_query, (election['id'],))
                election['candidates'] = user_model.cursor.fetchall()
                
                print(f"\nElection '{election['election_name']}' has {len(election['candidates'])} candidates:")
                for candidate in election['candidates']:
                    print(f"  - {candidate['name']} (Status: {candidate['status']})")
            
            print("\n" + "="*50)
            print("END DEBUG INFORMATION")
            print("="*50 + "\n")
            
            if connection:
                connection.close()
    except Exception as e:
        print(f"❌ ERROR fetching elections: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        elections = []

    return render_template("student/events.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         elections=elections)

# Voting page with election ID - CHANGED ENDPOINT NAME
@app.route('/voting/<int:election_id>')
def voting_with_id(election_id):  # Changed function name
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('id', 'id')

    # Fetch election and candidates data
    election = None
    candidates = []
    
    try:
        success, user_model, connection = check_user_model_connection()
        if success:
            # Get election details
            election_query = "SELECT * FROM election WHERE id = %s"
            user_model.cursor.execute(election_query, (election_id,))
            election = user_model.cursor.fetchone()

            # Get candidates for this election
            candidates_query = """
            SELECT * FROM candidates 
            WHERE election_id = %s AND status = 'approved'
            ORDER BY name
            """
            user_model.cursor.execute(candidates_query, (election_id,))
            candidates = user_model.cursor.fetchall()
            
            if connection:
                connection.close()
                
    except Exception as e:
        print(f"Error fetching election data: {e}")
        flash('Error loading election data', 'error')

    if not election:
        flash('Election not found', 'error')
        return redirect('/events')

    return render_template("student/voting.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         election=election,
                         candidates=candidates)

# Keep your original voting route if needed, or remove it
# Keep your original voting route
@app.route('/voting')
def voting():
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('id', 'id')

    return render_template("student/voting.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         election=None,  # Pass election as None
                         candidates=None)  # Pass candidates as None

@app.route('/api/vote', methods=['POST'])
def submit_vote():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    data = request.get_json()
    candidate_id = data.get('candidate_id')
    election_id = data.get('election_id')
    user_id = session.get('user_id')
    
    try:
        success, user_model, connection = check_user_model_connection()
        if success:
            # Check if user already voted in this election
            check_vote_query = "SELECT * FROM votes WHERE voter_id = %s AND election_id = %s"
            user_model.cursor.execute(check_vote_query, (user_id, election_id))
            existing_vote = user_model.cursor.fetchone()
            
            if existing_vote:
                return jsonify({'success': False, 'message': 'You have already voted in this election'})
            
            # Insert new vote
            insert_vote_query = "INSERT INTO votes (voter_id, candidate_id, election_id) VALUES (%s, %s, %s)"
            user_model.cursor.execute(insert_vote_query, (user_id, candidate_id, election_id))
            connection.commit()
            
            if connection:
                connection.close()
                
            return jsonify({'success': True, 'message': 'Vote submitted successfully'})
            
    except Exception as e:
        print(f"Error submitting vote: {e}")
        return jsonify({'success': False, 'message': 'Error submitting vote'})

from flask import session, jsonify
from app import app




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

    # Step 2: Get DB connection & user model
    connection_status, user_model, connection = check_user_model_connection()
    if not connection_status:
        return jsonify({
            "success": False,
            "error": "db_failed",
            "message": "Database connection failed."
        }), 500

    # Step 3: Fetch user record
    found, result = user_model.check_login(user_id, role)
    if not found or not result:
        connection.close()  # ✅ Close DB here to prevent leak
        return jsonify({
            "success": False,
            "error": "invalid_id",
            "message": "No account found with that ID."
        }), 404

    user = result[0]
    db_password = user.get('password', '')

    # Step 4: Password Verification (bcrypt or plain)
    try:
        if db_password.startswith("$2b$") or db_password.startswith("$2a$"):
            password_match = bcrypt.check_password_hash(db_password, password)
        else:
            password_match = password == db_password
    except:
        password_match = False

    if not password_match:
        connection.close()
        return jsonify({
            "success": False,
            "error": "invalid_pass",
            "message": "Password is incorrect."
        }), 401

    # ✅ Step 5: Create Session (correct field based on role)
    session.clear()
    if role == 'student':
        session['user_id'] = user.get('school_id')
    else:
        session['user_id'] = user.get('teacher_id')

    session['name'] = user.get('name')
    session['role'] = role

    print(f"✅ Login successful — ID: {session['user_id']}, Name: {session['name']}, Role: {session['role']}")

    # ✅ Step 6: Close DB after success
    connection.close()

    # Step 7: Success response
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


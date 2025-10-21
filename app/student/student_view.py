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
@app.route('/')
def user_login():
    return render_template("student/student and teacher login.html")

# Dashboard admin page
@app.route('/dashboard_user')
def dashboard_user():
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('user_id')
    
    print(f"🟢 Loading dashboard for user_id: {user_id}, role: {user_role}")

    # Initialize dashboard data with defaults
    dashboard_data = {
        'total_elections': 0,
        'ongoing_elections': 0,
        'participated_elections': 0,
        'upcoming_elections': 0,
        'completed_elections': 0,
        'recent_activities': [],  # This will hold our activity feed
        'chart_data': {
            'participation_trend': [],
            'voting_distribution': [],
            'user_participation': [],
            'active_elections': []
        }
    }

    try:
        connection_status, model, db_connection = check_user_model_connection()
        
        if connection_status:
            print("✅ Database connection successful for dashboard")
            
            # Get dashboard statistics
            success, stats = model.get_dashboard_stats(user_id, user_role.lower())
            if success:
                dashboard_data.update(stats)
                print(f"✅ Dashboard stats loaded: {stats}")
            
            # Get recent activity feed
            success, activities = model.get_recent_activity_feed(user_id)
            if success:
                dashboard_data['recent_activities'] = activities
                print(f"✅ Recent activities loaded: {len(activities)} items")
            else:
                print(f"🔴 Failed to load activities: {activities}")
            
            # Get chart data (existing chart methods)
            success, trend_data = model.get_participation_trend_data('monthly')
            if success:
                dashboard_data['chart_data']['participation_trend'] = trend_data
            
            success, distribution_data = model.get_voting_distribution_data()
            if success:
                dashboard_data['chart_data']['voting_distribution'] = distribution_data
            
            # Close database connection
            try:
                if db_connection:
                    db_connection.close()
                    print("✅ Database connection closed")
            except Exception as e:
                print(f"🟡 Warning: Could not close database connection: {e}")
                
        else:
            print("🔴 Database connection failed for dashboard")
            
    except Exception as e:
        print(f"🔥 Exception in dashboard_user: {str(e)}")
        import traceback
        print(f"🔥 Stack trace: {traceback.format_exc()}")

    return render_template(
        "student/user_dashboard.html", 
        user_name=user_name, 
        user_role=user_role,
        user_id=user_id,
        dashboard_data=dashboard_data
    )

# Test endpoints to see each data type separately
@app.route('/debug/activities/voting')
def debug_voting_activities():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    connection_status, model, db_connection = check_user_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    success, data = model.get_user_voting_activities(session['user_id'])
    
    try:
        if db_connection:
            db_connection.close()
    except:
        pass
    
    return jsonify({'success': success, 'data': data})

@app.route('/debug/activities/election-changes')
def debug_election_changes():
    connection_status, model, db_connection = check_user_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    success, data = model.get_recent_election_status_changes()
    
    try:
        if db_connection:
            db_connection.close()
    except:
        pass
    
    return jsonify({'success': success, 'data': data})

@app.route('/debug/activities/upcoming')
def debug_upcoming_elections():
    connection_status, model, db_connection = check_user_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    
    success, data = model.get_upcoming_elections_soon()
    
    try:
        if db_connection:
            db_connection.close()
    except:
        pass
    
    return jsonify({'success': success, 'data': data})

# API endpoint for dashboard data (for AJAX updates)
@app.route('/dashboard_data')
def dashboard_data():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    user_id = session.get('user_id')
    user_role = session.get('role', 'student')
    
    try:
        connection_status, model, db_connection = check_user_model_connection()
        
        if not connection_status:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        success, stats = model.get_dashboard_stats(user_id, user_role)
        
        # Close connection
        try:
            if db_connection:
                db_connection.close()
        except:
            pass
            
        if success:
            return jsonify({'success': True, 'data': stats})
        else:
            return jsonify({'success': False, 'message': stats}), 500
            
    except Exception as e:
        print(f"Error in dashboard_data API: {e}")
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

@app.route('/events')
def events():
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('user_id')  # Changed to user_id for consistency

    elections = []
    try:
        connection_status, model, connection = check_user_model_connection()
        if connection_status:
            # Enhanced query with better data
            query = """
            SELECT 
                e.*, 
                COUNT(c.id) as candidate_count,
                (SELECT COUNT(*) FROM votes v WHERE v.election_id = e.id) as total_votes,
                (SELECT COUNT(*) FROM votes v WHERE v.election_id = e.id AND v.voter_id = %s) as user_voted
            FROM election e 
            LEFT JOIN candidates c ON e.id = c.election_id 
            GROUP BY e.id 
            ORDER BY 
                CASE 
                    WHEN e.status = 'ongoing' THEN 1
                    WHEN e.status = 'upcoming' THEN 2
                    ELSE 3
                END,
                e.start_date DESC
            """
            model.cursor.execute(query, (user_id,))
            elections = model.cursor.fetchall()
            
            print(f"✅ Loaded {len(elections)} elections for user {user_id}")
            
            if connection:
                connection.close()
                
    except Exception as e:
        print(f"❌ ERROR fetching elections: {e}")
        elections = []

    return render_template("student/events.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         elections=elections)

@app.route('/voting/<int:election_id>')
def voting_with_id(election_id):
    if 'user_id' not in session:
        print("🔴 User not logged in, redirecting to login")
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('user_id')

    print(f"\n" + "="*60)
    print(f"🟢 VOTING PAGE ACCESS - Election ID: {election_id}")
    print(f"🟢 User: {user_name} (ID: {user_id}, Role: {user_role})")
    print("="*60)

    election = None
    candidates = []
    user_has_voted = False
    election_results = {}
    
    try:
        connection_status, model, connection = check_user_model_connection()
        if connection_status:
            print("✅ Database connection successful")
            
            # Get election details
            election_query = "SELECT * FROM election WHERE id = %s"
            model.cursor.execute(election_query, (election_id,))
            election = model.cursor.fetchone()

            if election:
                print(f"✅ Election found: {election['election_name']} (Status: {election['status']})")
                print(f"📅 Election dates: {election['start_date']} to {election['end_date']}")
                
                # Check if user has already voted in this election
                vote_check_query = "SELECT id FROM votes WHERE voter_id = %s AND election_id = %s"
                model.cursor.execute(vote_check_query, (user_id, election_id))
                existing_vote = model.cursor.fetchone()
                user_has_voted = existing_vote is not None
                
                if user_has_voted:
                    print(f"✅ User HAS ALREADY VOTED in this election (Vote ID: {existing_vote['id']})")
                else:
                    print("✅ User has NOT voted yet in this election")

                # Get candidates for this election
                candidates_query = """
                SELECT * FROM candidates 
                WHERE election_id = %s AND status IN ('approved', 'elected', 'lost')
                ORDER BY name
                """
                model.cursor.execute(candidates_query, (election_id,))
                candidates = model.cursor.fetchall()
                print(f"✅ Found {len(candidates)} candidates for this election")

                # Log all candidates
                for i, candidate in enumerate(candidates):
                    print(f"   {i+1}. {candidate['name']} (Status: {candidate.get('status', 'approved')})")

                # If election is completed or user has voted, get results with vote counts
                if election['status'] == 'completed' or user_has_voted:
                    print(f"🔄 Getting detailed results (Election completed: {election['status'] == 'completed'}, User voted: {user_has_voted})")
                    
                    results_query = """
                    SELECT 
                        c.id,
                        c.name,
                        c.photo,
                        c.statement,
                        COUNT(v.id) as vote_count,
                        c.status as candidate_status
                    FROM candidates c
                    LEFT JOIN votes v ON c.id = v.candidate_id
                    WHERE c.election_id = %s AND c.status IN ('approved', 'elected', 'lost')
                    GROUP BY c.id, c.name, c.photo, c.statement, c.status
                    ORDER BY 
                        CASE 
                            WHEN c.status = 'elected' THEN 1
                            WHEN c.status = 'approved' THEN 2
                            ELSE 3
                        END,
                        vote_count DESC
                    """
                    model.cursor.execute(results_query, (election_id,))
                    election_results = model.cursor.fetchall()

                    print(f"📊 ELECTION RESULTS ANALYSIS:")
                    print(f"   Total candidates with results: {len(election_results)}")
                    
                    # Enhanced winner logic: Use status='elected' OR highest votes if no status
                    if election_results:
                        # First, check for explicit 'elected' status
                        elected_candidates = [c for c in election_results if c['candidate_status'] == 'elected']
                        lost_candidates = [c for c in election_results if c['candidate_status'] == 'lost']
                        
                        print(f"   Explicitly elected candidates: {len(elected_candidates)}")
                        print(f"   Explicitly lost candidates: {len(lost_candidates)}")
                        
                        if elected_candidates:
                            print("🎯 USING EXPLICIT WINNER DESIGNATION FROM DATABASE")
                            # Use the database's explicit winner designation
                            for candidate in election_results:
                                candidate['is_winner'] = (candidate['candidate_status'] == 'elected')
                                
                            # Log winners
                            winners = [c for c in election_results if c['is_winner']]
                            print(f"   🏆 WINNERS ({len(winners)}):")
                            for winner in winners:
                                print(f"      - {winner['name']} (Votes: {winner['vote_count']})")
                                
                            # Log losers
                            losers = [c for c in election_results if not c['is_winner']]
                            if losers:
                                print(f"   ❌ LOSERS ({len(losers)}):")
                                for loser in losers:
                                    print(f"      - {loser['name']} (Votes: {loser['vote_count']}, Status: {loser['candidate_status']})")
                            
                        else:
                            print("🎯 USING VOTE COUNT TO DETERMINE WINNER (No explicit status)")
                            # Fallback to vote count if no explicit winner
                            max_votes = max(candidate['vote_count'] for candidate in election_results)
                            print(f"   Maximum votes: {max_votes}")
                            
                            for candidate in election_results:
                                candidate['is_winner'] = (candidate['vote_count'] == max_votes and max_votes > 0)
                            
                            # Log winners by vote count
                            winners = [c for c in election_results if c['is_winner']]
                            print(f"   🏆 WINNERS BY VOTE COUNT ({len(winners)}):")
                            for winner in winners:
                                print(f"      - {winner['name']} (Votes: {winner['vote_count']})")
                            
                            # Log losers
                            losers = [c for c in election_results if not c['is_winner']]
                            if losers:
                                print(f"   ❌ LOSERS BY VOTE COUNT ({len(losers)}):")
                                for loser in losers:
                                    print(f"      - {loser['name']} (Votes: {loser['vote_count']})")
                        
                        # Log final vote counts for all candidates
                        print(f"📈 FINAL VOTE COUNTS:")
                        for candidate in election_results:
                            winner_indicator = " 🏆" if candidate['is_winner'] else ""
                            print(f"   - {candidate['name']}: {candidate['vote_count']} votes{winner_indicator}")
                        
                        # 🚨 CRITICAL FIX: Update the original candidates list with winner info
                        for candidate in candidates:
                            # Find matching candidate in election_results
                            matching_result = next((cr for cr in election_results if cr['id'] == candidate['id']), None)
                            if matching_result:
                                candidate['is_winner'] = matching_result['is_winner']
                                candidate['vote_count'] = matching_result['vote_count']
                                candidate['candidate_status'] = matching_result['candidate_status']
                                print(f"   ✅ Updated candidate {candidate['name']} - Winner: {candidate['is_winner']}")
                    
                    else:
                        print("⚠️ No election results available")
                else:
                    print("ℹ️ Showing voting interface (election ongoing and user hasn't voted)")
            
            else:
                print("❌ Election not found in database")
            
            if connection:
                connection.close()
                print("✅ Database connection closed")
                
    except Exception as e:
        print(f"❌ ERROR in voting route: {str(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        flash('Error loading election data', 'error')

    if not election:
        print("❌ Redirecting to events - election not found")
        flash('Election not found', 'error')
        return redirect('/events')

    print(f"✅ Rendering voting page with:")
    print(f"   - Election: {election['election_name']}")
    print(f"   - Candidates: {len(candidates)}")
    print(f"   - User voted: {user_has_voted}")
    print(f"   - Election results: {len(election_results) if election_results else 0}")
    print("="*60 + "\n")

    return render_template("student/voting.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         election=election,
                         candidates=candidates,
                         user_has_voted=user_has_voted,
                         election_results=election_results)

@app.route('/voting')
def voting():
    if 'user_id' not in session:
        return redirect('/user_login')

    user_name = session.get('name', 'User')
    user_role = session.get('role', 'student').capitalize()
    user_id = session.get('user_id')

    return render_template("student/voting.html", 
                         user_name=user_name, 
                         user_role=user_role, 
                         user_id=user_id,
                         election=None,
                         candidates=None,
                         user_has_voted=False,
                         election_results=None)
@app.route('/api/vote', methods=['POST'])
def submit_vote():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401

    user_id = session.get('user_id')
    data = request.get_json()
    
    candidate_id = data.get('candidate_id')
    election_id = data.get('election_id')
    
    print(f"🟢 Vote submission attempt - User: {user_id}, Election: {election_id}, Candidate: {candidate_id}")

    try:
        connection_status, model, connection = check_user_model_connection()
        if not connection_status:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500

        # Security Check 1: Verify election exists and is ongoing
        election_query = "SELECT * FROM election WHERE id = %s AND status = 'ongoing'"
        model.cursor.execute(election_query, (election_id,))
        election = model.cursor.fetchone()
        
        if not election:
            return jsonify({'success': False, 'message': 'Election not found or not active'}), 400

        # Security Check 2: Verify candidate exists and is approved
        candidate_query = "SELECT * FROM candidates WHERE id = %s AND election_id = %s AND status = 'approved'"
        model.cursor.execute(candidate_query, (candidate_id, election_id))
        candidate = model.cursor.fetchone()
        
        if not candidate:
            return jsonify({'success': False, 'message': 'Candidate not found or not approved'}), 400

        # Security Check 3: Check if user already voted
        vote_check_query = "SELECT id FROM votes WHERE voter_id = %s AND election_id = %s"
        model.cursor.execute(vote_check_query, (user_id, election_id))
        existing_vote = model.cursor.fetchone()
        
        if existing_vote:
            return jsonify({'success': False, 'message': 'You have already voted in this election'}), 400

        # Security Check 4: Validate election dates
        from datetime import datetime
        now = datetime.now()
        if election['start_date'] > now or election['end_date'] < now:
            return jsonify({'success': False, 'message': 'Election is not currently active'}), 400

        # All checks passed - Record the vote
        insert_query = "INSERT INTO votes (voter_id, candidate_id, election_id, timestamp) VALUES (%s, %s, %s, NOW())"
        model.cursor.execute(insert_query, (user_id, candidate_id, election_id))
        connection.commit()

        print(f"✅ Vote recorded successfully - User: {user_id}, Election: {election_id}, Candidate: {candidate_id}")

        if connection:
            connection.close()

        return jsonify({
            'success': True, 
            'message': 'Vote submitted successfully!'
        }), 200

    except Exception as e:
        print(f"❌ Vote submission error: {e}")
        if connection:
            connection.rollback()
            connection.close()
        return jsonify({'success': False, 'message': 'Internal server error'}), 500

from flask import session, jsonify
from app import app




from flask import request, jsonify, session
from werkzeug.security import check_password_hash

from flask import request, jsonify, session
from werkzeug.security import check_password_hash
from app import app
import bcrypt

@app.route('/student_or_teacher_login', methods=['POST'])
def student_or_teacher_login():
    data = request.get_json()
    print("Login request:", data)

    # Step 1: Extract and validate input
    user_id = str(data.get('id', '')).strip()
    password = data.get('password', '').strip()

    if not user_id or not password:
        return jsonify({
            "success": False,
            "error": "missing_fields",
            "message": "Please fill all fields."
        }), 400

    # Step 2: Get DB connection & user model
    connection_status, user_model, connection = check_user_model_connection()
    if not connection_status:
        return jsonify({
            "success": False,
            "error": "db_failed",
            "message": "Database connection failed."
        }), 500

    # Step 3: Fetch student record
    found, result = user_model.check_login(user_id)
    if not found or not result:
        connection.close()  # Close DB here to prevent leak
        return jsonify({
            "success": False,
            "error": "invalid_id",
            "message": "No student account found with that ID."
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

    # Step 5: Create Session
    session.clear()
    session['user_id'] = user.get('school_id')
    session['name'] = user.get('name')
    session['role'] = 'student'

    print(f"✅ Login successful — ID: {session['user_id']}, Name: {session['name']}, Role: {session['role']}")

    # Step 6: Close DB after success
    connection.close()

    # Step 7: Success response
    return jsonify({
        "success": True,
        "message": "Student login successful.",
        "redirect": "/dashboard_user"
    }), 200
from flask_bcrypt import Bcrypt

# Initialize bcrypt in your app
bcrypt = Bcrypt(app)

@app.route('/password_change', methods=['POST'])
def password_change():
    print("\n🟢 [ROUTE] /password_change called")

    try:
        # ✅ Check JSON request
        if not request.is_json:
            print("🔴 Request is not JSON")
            return jsonify({'success': False, 'message': 'Invalid request format'}), 400

        # ✅ Get session data
        user_id = session.get('user_id')  # This is school_id for students
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
        print(f"🟢 Received password change request for user_id: {user_id}")

        # ✅ Enhanced Validation
        validation_errors = []
        
        if not old_password:
            validation_errors.append("Current password is required")
        if not new_password:
            validation_errors.append("New password is required")
        if not confirm_password:
            validation_errors.append("Confirm password is required")
        elif len(new_password) < 4:
            validation_errors.append("New password must be at least 4 characters")
        elif new_password != confirm_password:
            validation_errors.append("New password and confirmation do not match")
        elif old_password == new_password:
            validation_errors.append("New password must be different from current password")

        if validation_errors:
            print(f"🔴 Validation failed: {validation_errors}")
            return jsonify({'success': False, 'message': validation_errors[0]}), 400

        # ✅ Database connection
        print("🟡 Connecting to database...")
        connection_status, model, db_connection = check_user_model_connection()
        
        if not connection_status:
            print("🔴 Database connection failed")
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        print("✅ Database connection successful.")

        # ✅ FIX: Use school_id instead of id for student lookup
        print(f"🟢 Fetching user data for {role} -> ID: {user_id}")
        
        if role == 'student':
            # Use school_id for students since that's what you use for login
            query = "SELECT * FROM students WHERE school_id = %s"
            model.cursor.execute(query, (user_id,))  # FIXED: Changed self.cursor to model.cursor
            result = model.cursor.fetchall()
            success = bool(result)
            user_data = result
        else:
            # For teachers, use id (or adjust as needed)
            success, user_data = model.check_user(user_id, role)
        
        print(f"🟢 User fetch result: {success}, Data found: {bool(user_data)}")
        
        if not success or not user_data:
            print("🔴 User not found in database")
            try:
                if db_connection:
                    db_connection.close()
            except:
                pass
            return jsonify({'success': False, 'message': f'{role.capitalize()} not found'}), 404

        user = user_data[0]
        stored_password = user['password']
        
        # DEBUG: Print user details
        print(f"🟢 User details - ID: {user.get('id')}, School ID: {user.get('school_id')}, Name: {user.get('name')}")
        print(f"🟡 Password verification in progress...")

        # ✅ Enhanced password verification
        password_valid = False
        if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
            # Bcrypt hashed password - using Flask-Bcrypt
            password_valid = bcrypt.check_password_hash(stored_password, old_password)
            print(f"🟢 Bcrypt verification result: {password_valid}")
        else:
            # Plain text password (for legacy accounts)
            password_valid = (old_password == stored_password)
            print(f"🟢 Plain text verification result: {password_valid}")

        if not password_valid:
            print("🔴 Current password incorrect")
            try:
                if db_connection:
                    db_connection.close()
            except:
                pass
            return jsonify({'success': False, 'message': 'Current password is incorrect'}), 401

        # ✅ Hash new password using Flask-Bcrypt
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        print(f"🟢 New password hashed successfully")

        # ✅ FIX: Update using the correct identifier
        if role == 'student':
            # Use the database id from the fetched user data
            db_user_id = user['id']
            update_query = "UPDATE students SET password = %s WHERE id = %s"
            print(f"🟢 Updating student with database ID: {db_user_id}")
        else:
            db_user_id = user_id
            update_query = "UPDATE teachers SET password = %s WHERE id = %s"
            print(f"🟢 Updating teacher with ID: {db_user_id}")

        print(f"🟢 Executing update query for {role}...")
        
        # ✅ Execute update
        model.cursor.execute(update_query, (new_hash, db_user_id))
        affected_rows = model.cursor.rowcount
        model.connection.commit()
        
        if affected_rows == 0:
            print("🔴 No rows affected - update failed")
            try:
                if db_connection:
                    db_connection.close()
            except:
                pass
            return jsonify({'success': False, 'message': 'Failed to update password'}), 500
            
        print(f"✅ Password successfully updated. Rows affected: {affected_rows}")

        # ✅ Verify the update by reading back the password
        if role == 'student':
            verify_query = "SELECT password FROM students WHERE id = %s"
        else:
            verify_query = "SELECT password FROM teachers WHERE id = %s"
            
        model.cursor.execute(verify_query, (db_user_id,))
        updated_user = model.cursor.fetchone()
        print(f"🟢 Updated password in DB: {updated_user['password']}")

        # ✅ Close database connection
        try:
            if db_connection:
                db_connection.close()
                print("✅ Database connection closed")
        except Exception as e:
            print(f"🟡 Warning: Could not close database connection: {e}")

        print(f"🔐 Password changed for {role} ID: {user_id} (DB ID: {db_user_id})")
        
        return jsonify({
            'success': True, 
            'message': 'Password changed successfully!'
        }), 200

    except Exception as e:
        print(f"🔥 Exception in password_change: {str(e)}")
        import traceback
        print(f"🔥 Stack trace: {traceback.format_exc()}")
        
        try:
            if 'db_connection' in locals() and db_connection:
                db_connection.close()
                print("🟡 Database connection closed due to exception")
        except:
            pass
            
        app.logger.error(f"Password change error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False, 
            'message': 'Internal server error. Please try again.'
        }), 500

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


from turtledemo.penrose import start

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

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_photo(photo):
    """Handles photo upload validation and saving."""
    if not photo:
        return False, "No photo uploaded"

    if not allowed_file(photo.filename):
        return False, "Invalid file type. Only PNG, JPG, JPEG are allowed"

    filename = secure_filename(photo.filename)
    photo_path = os.path.join(UPLOAD_FOLDER, filename)
    photo.save(photo_path)
    return True,filename


# this function give all pages the basic data
@app.context_processor
def inject_admin_data():
    """Automatically inject admin data into all templates"""
    context = {
        'admin': None
    }
    email = session.get('email')
    if email:
        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            try:
                _, admin_data = admin_model.check_login(email)
                if admin_data:
                    context.update({
                        'admin': admin_data[0]
                    })
                    return context
            except Exception as e:
                app.logger.error(f"Error loading student data: {str(e)}")
    return context


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
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, data = admin_model.get_dashboard_stats()
    if flag:
        return render_template("admin/dashboard.html",
                               dashboard_data = data)
    return render_template("admin/dashboard.html")

# Students register page
@app.route('/register_students')
def register_students():
    return render_template("admin/register_students.html")

# Students view page
@app.route('/view_students')
def view_students():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, students_table = admin_model.get_all_students()
    if flag:
        return render_template("admin/view_students.html",
                               students_table = students_table)
    return render_template("admin/view_students.html")

# teachers register page
@app.route('/register_teacher')
def register_teacher():
    return render_template("admin/register_teacher.html")

# teachers view page
@app.route('/view_teacher')
def view_teacher():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, teachers_table = admin_model.get_all_teachers()
    if flag:
        return render_template("admin/view_teacher.html",
                               teachers_table = teachers_table)
    return render_template("admin/view_teacher.html")

# election register page
@app.route('/register_election')
def register_election():
    return render_template("admin/election_register.html")

# election view page
@app.route('/view_election')
def view_election():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, elections_table = admin_model.get_all_elections()
    if flag:
        return render_template("admin/view_elections.html",
                               elections_table = elections_table)
    return render_template("admin/view_elections.html")

# candidate register page
@app.route('/register_candidates')
def register_candidates():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, elections_data = admin_model.get_all_elections()
    if flag:
        return render_template("admin/candidates_register.html",
                               elections_data = elections_data)
    return render_template("admin/candidates_register.html")

# candidates view page
@app.route('/view_candidates')
def view_candidates():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({"Database connection failed."})
    flag, candidates_table = admin_model.get_all_candidates()
    if flag:
        flag, elections_table = admin_model.get_all_elections()
        return render_template("admin/view_candidates.html",
                               candidates_table = candidates_table,
                               elections_data = elections_table)
    return render_template("admin/view_candidates.html")

@app.route('/live-results')
def live_results_page():
    return render_template('admin/live_results.html')

@app.route('/view-votes')
def view_votes_page():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500
    flag,data = admin_model.get_all_votes()
    if flag:
        flag, elections_table = admin_model.get_all_elections()
        if flag:
            print(data)
            print(elections_table)
            return render_template('admin/view_votes.html',
                               votes_data = data,
                               election_data = elections_table)
        return render_template('admin/view_votes.html',
                               votes_data=data)
    return render_template('admin/view_votes.html')

@app.route('/final-results')
def final_results_page():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500
    flag, data = admin_model.get_final_results()
    if flag:
        flag, elections_table = admin_model.get_all_elections_completed()
        if flag:
            print(data)
            # print(elections_table)
            return render_template('admin/final_results.html',
                                   final_result=data,
                                   election_data = elections_table)
        return render_template('admin/final_results.html',final_result = data)
    return render_template('admin/final_results.html')
#======================
#funtions use for validate
# function for validating full name
def validate_full_name(name):
    name = name.strip()
    if not all(word.isalpha() for word in name.split()):
        return False, 'Name must contain only alphabets (no numbers or special characters)'
    if len(name) < 9:
        return False, 'Name must be at least 9 characters long'
    if len(name) > 60:
        return False, 'Name cannot exceed 60 characters'
    words = name.split()
    word_count = len(words)
    if word_count < 3 or word_count > 4:
        return False, 'Name must contain 3 or 4 words separated by spaces'
    for word in words:
        if len(word) < 3 or len(word) > 15:
            return False, f'Each name must be between 3 and 15 characters: "{word}" is invalid'
    return True, None

# function for validating email
def validate_email(email):
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))


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

    # All validations passed
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

#=================Student=======================#
# add student
@app.route('/add_student', methods=['POST'])
def add_student():
    data = request.get_json()
    print(data)

    # Extract fields
    name = data.get('name', '').strip()
    student_id = data.get('student_id', '').strip()

    # --- NAME VALIDATION ---
    valid_name, name_error = validate_full_name(name)
    if not valid_name:
        return jsonify({
            "success": False,
            "error": "invalid_name",
            "message": name_error
        })
    # --- STUDENT ID VALIDATION ---
    if not re.match(r'^(?!0$)[0-9]{1,10}$', student_id):
        return jsonify({
            "success": False,
            "error": "invalid_id",
            "message": "Student ID must be numeric (1–10 digits) and not just 0."
        })

    # All validations passed — Example Database Handling
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        })

    # check student before registration if registered al ready
    error,result = admin_model.is_student_registered(student_id,name)
    if error:
        return jsonify({
            "success": False,
            "message": "This Student already registered or student id used already!"
        })


    # Insert into database (example function)
    flag = admin_model.register_student(name, student_id)
    if flag:
        return jsonify({
            "success": True,
            "message": "Student registered successfully!"
        })

    return jsonify({
        "success": False,
        "message": "Data not registered successfully."
    })

# add student by excel based import
@app.route('/add_students_as_import', methods=['POST'])
def add_students_as_import():
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
            students_data = pd.read_csv(file)
        elif filename.endswith('.xls'):
            print('123hellow')
            students_data = pd.read_excel(file, engine='xlrd')
        elif filename.endswith(('.xlsx', '.xls')):
            students_data = pd.read_excel(file, engine='openpyxl')
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported file type! Please upload CSV or Excel.'})

        print("Excel/CSV data preview:")
        print(students_data[['student_id','name']])

        # Return preview (first 5 rows)
        preview = students_data.head(5).to_dict(orient='records')

        connection_status, admin_model = check_admin_model_connection()
        if not connection_status:
            return jsonify({
                "success": False,
                "message": "Database connection failed."
            })

        for index,student in students_data.iterrows():
            print(student)
            print(student.loc[['student_id']],student.loc[['name']])
            # check student before registration if registered al ready
            error, result = admin_model.is_student_registered(student['student_id'], student['name'])
            if error:
                return jsonify({
                    "success": False,
                    "message": f"{student['name']} with student id {student['student_id']} already registered or student id used already!"
                })

            # Insert into database (example function)
            flag = admin_model.register_student(student['name'], student['student_id'])
            if not flag:
                return jsonify({
                    "success": False,
                "message": "Data not registered successfully."
                })

        return jsonify({
                "success": True,
                "message": "Students registered successfully!"
            })

    except Exception as e:
        print("Error reading file:", e)
        return jsonify({'status': 'error', 'message': f'Failed to read file: {str(e)}'})

# update student details
@app.route('/update_student_details', methods=['POST'])
def update_student_details():
    if not request.is_json:
        return jsonify({'status': False, 'message': 'Request must be JSON'}), 400

    try:
        data = request.get_json()
        # Extract fields
        name = data.get('name', '').strip()
        student_id = data.get('student_id', '').strip()
        print(data)

        # --- NAME VALIDATION ---
        valid_name, name_error = validate_full_name(name)
        if not valid_name:
            return jsonify({
                "success": False,
                "error": "invalid_name",
                "message": name_error
            })
        # --- STUDENT ID VALIDATION ---
        if not re.match(r'^(?!0$)[0-9]{1,10}$', student_id):
            return jsonify({
                "success": False,
                "error": "invalid_id",
                "message": "Student ID must be numeric (1–10 digits) and not just 0."
            })

        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            success = admin_model.update_student_details(data)
            if success:
                return jsonify({'success': True, 'message': 'students details updated successfully'})
            return jsonify({'success': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500

# change student password
@app.route('/change_password_student', methods=['POST'])
def change_password_student():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = admin_model.change_student_password(hashed_password, data.get('id'))
    if success:
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400

#=================Teacher===================#
# add teacher
@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    data = request.get_json()
    print(data)

    # Extract fields
    name = data.get('name', '').strip()
    teacher_id = data.get('teacher_id', '').strip()

    # --- NAME VALIDATION ---
    valid_name, name_error = validate_full_name(name)
    if not valid_name:
        return jsonify({
            "success": False,
            "error": "invalid_name",
            "message": name_error
        })
    # --- TEACHER ID VALIDATION ---
    if not re.match(r'^(?!0$)[0-9]{1,10}$', teacher_id):
        return jsonify({
            "success": False,
            "error": "invalid_id",
            "message": "Teacher ID must be numeric (1–10 digits) and not just 0."
        })

    # All validations passed — Example Database Handling
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({
            "success": False,
            "message": "Database connection failed."
        })

    # check teacher before registration if registered al ready
    error,result = admin_model.is_teacher_registered(teacher_id,name)
    if error:
        return jsonify({
            "success": False,
            "message": "This teacher already registered or teacher id used already!"
        })


    # Insert into database (example function)
    flag = admin_model.register_teacher(name, teacher_id)
    if flag:
        return jsonify({
            "success": True,
            "message": "Teacher registered successfully!"
        })

    return jsonify({
        "success": False,
        "message": "Data not registered successfully."
    })

# add teacher by excel based import
@app.route('/add_teachers_as_import', methods=['POST'])
def add_teachers_as_import():
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
            teachers_data = pd.read_csv(file)
        elif filename.endswith('.xls'):
            print('123hellow')
            teachers_data = pd.read_excel(file, engine='xlrd')
        elif filename.endswith(('.xlsx', '.xls')):
            teachers_data = pd.read_excel(file, engine='openpyxl')
        else:
            return jsonify({'status': 'error', 'message': 'Unsupported file type! Please upload CSV or Excel.'})

        print("Excel/CSV data preview:")
        print(teachers_data[['teacher_id','name']])

        # Return preview (first 5 rows)
        preview = teachers_data.head(5).to_dict(orient='records')

        connection_status, admin_model = check_admin_model_connection()
        if not connection_status:
            return jsonify({
                "success": False,
                "message": "Database connection failed."
            })

        for index,teacher in teachers_data.iterrows():
            print(teacher)
            print(teacher.loc[['teacher_id']],teacher.loc[['name']])
            # check teacher before registration if registered al ready
            error, result = admin_model.is_teacher_registered(teacher['teacher_id'], teacher['name'])
            if error:
                return jsonify({
                    "success": False,
                    "message": f"{teacher['name']} with teacher id {teacher['teacher_id']} already registered or teacher id used already!"
                })

            # Insert into database (example function)
            flag = admin_model.register_teacher(teacher['name'], teacher['teacher_id'])
            if not flag:
                return jsonify({
                    "success": False,
                "message": "Data not registered successfully."
                })

        return jsonify({
                "success": True,
                "message": "Teachers registered successfully!"
            })

    except Exception as e:
        print("Error reading file:", e)
        return jsonify({'status': 'error', 'message': f'Failed to read file: {str(e)}'})

# update teacher details
@app.route('/update_teacher_details', methods=['POST'])
def update_teacher_details():
    if not request.is_json:
        return jsonify({'status': False, 'message': 'Request must be JSON'}), 400

    try:
        data = request.get_json()
        # Extract fields
        name = data.get('name', '').strip()
        teacher_id = data.get('teacher_id', '').strip()
        print(data)

        # --- NAME VALIDATION ---
        valid_name, name_error = validate_full_name(name)
        if not valid_name:
            return jsonify({
                "success": False,
                "error": "invalid_name",
                "message": name_error
            })
        # --- STUDENT ID VALIDATION ---
        if not re.match(r'^(?!0$)[0-9]{1,10}$', teacher_id):
            return jsonify({
                "success": False,
                "error": "invalid_id",
                "message": "teacher ID must be numeric (1–10 digits) and not just 0."
            })

        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            success = admin_model.update_teacher_details(data)
            if success:
                return jsonify({'success': True, 'message': 'teacher details updated successfully'})
            return jsonify({'success': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500

# change teacher password
@app.route('/change_password_teacher', methods=['POST'])
def change_password_teacher():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = admin_model.change_teacher_password(hashed_password, data.get('id'))
    if success:
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400

#=============Election =========================#
@app.route('/add_election', methods=['POST'])
def add_election():
    election_name = request.form.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    description = request.form.get('election_desc')

    # Get the uploaded photo file (if provided)
    photo = request.files.get('photo')
    print(election_name,start_date,end_date,description,photo)
    # Validation
    if not all([election_name, start_date,end_date, photo,description]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    # Save uploaded photo
    flag, photo_path = upload_photo(photo)
    if not flag:
        return jsonify({'success': False, 'message': 'Candidate photo make error!'})

    # Example DB logic
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    success = admin_model.add_election(election_name, start_date, end_date, description,photo_path)

    if success:
        return jsonify({'success': True, 'message': 'Election added successfully!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to add election.'}), 400

@app.route('/update_election_details', methods=['POST'])
def update_election_details():
    election_id = request.form.get('id')
    election_name = request.form.get('name')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    description = request.form.get('election_desc')

    # Get the uploaded photo file (if provided)
    photo = request.files.get('photo')
    print(election_id,election_name,start_date,end_date,description,photo)
    # Validation
    if not all([election_name, start_date, end_date, description]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if photo:
        # Save uploaded photo
        flag, photo_path = upload_photo(photo)
        if not flag:
            return jsonify({'success': False, 'message': 'Candidate photo make error!'})

        # Example DB logic
        connection_status, admin_model = check_admin_model_connection()
        if not connection_status:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500

        success = admin_model.update_election_details(election_id,election_name, start_date, end_date, description,photo_path)

        if success:
            return jsonify({'success': True, 'message': 'Election added successfully!'}), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to add election.'}), 400

    # Example DB logic
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    photo_path = False
    success = admin_model.update_election_details(election_id, election_name, start_date, end_date, description,photo_path)

    if success:
        return jsonify({'success': True, 'message': 'Election added successfully!'}), 200
    else:
        return jsonify({'success': False, 'message': 'Failed to add election.'}), 400

# change election status
@app.route('/change_election_status', methods=['POST'])
def change_election_status():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['status']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    allowed_status = ['upcoming','ongoing','completed']
    if len(data['status']) in allowed_status:
        return jsonify({'success': False, 'message': 'Status must be allowed status'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500
    success = admin_model.change_election_status(data.get('status'), data.get('id'))
    if success:
        return jsonify({'success': True, 'message': 'status changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400


#=============Candidates====================#
@app.route('/add_candidate', methods=['POST'])
def add_candidate():
    try:
        name = request.form.get('name')
        election_id = request.form.get('election')
        statement = request.form.get('statement')
        photo = request.files.get('photo')

        # Validation
        if not all([name, election_id, statement, photo]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400

        # Save uploaded photo
        flag,photo_path = upload_photo(photo)
        if not flag:
            return jsonify({'success': False, 'message': 'Candidate photo make error!'})
        # Insert into DB
        connection_status, admin_model = check_admin_model_connection()
        if not connection_status:
            return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

        print("Halkaan ",name,photo,statement,election_id,photo_path)
        success = admin_model.add_candidate(name,photo_path,statement,election_id)
        if success:
            return jsonify({'success': True, 'message': 'Register candidate successfully'}), 200
        return jsonify({'success': False, 'message': 'Failed to register candidate', 'field': 'general'}), 400

    except Exception as e:
        print("Error registering candidate:", e)
        return jsonify({'success': False, 'message': 'Server error: ' + str(e)}), 500

@app.route('/update_candidate_details', methods=['POST'])
def update_candidate_details():
    try:
        name = request.form.get('name')
        election_id = request.form.get('election')
        statement = request.form.get('statement')
        photo = request.files.get('photo')
        candidate_id = request.form.get('id')
        # Validation
        if not all([name, election_id, statement]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        if photo:
            # Save uploaded photo
            flag,photo_path = upload_photo(photo)
            if not flag:
                return jsonify({'success': False, 'message': 'Candidate photo make error!'})
            # Insert into DB
            connection_status, admin_model = check_admin_model_connection()
            if not connection_status:
                return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

            success = admin_model.update_candidate_details(candidate_id,name,photo_path,statement,election_id)
            if success:
                return jsonify({'success': True, 'message': 'updates candidate successfully'}), 200
            return jsonify({'success': False, 'message': 'Failed to update candidate', 'field': 'general'}), 400
        # Insert into DB
        connection_status, admin_model = check_admin_model_connection()
        if not connection_status:
            return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500
        photo_path = False
        success = admin_model.update_candidate_details(candidate_id, name, photo_path, statement,
                                                       election_id)
        if success:
            return jsonify({'success': True, 'message': 'updates candidate successfully'}), 200
        return jsonify({'success': False, 'message': 'Failed to update candidate', 'field': 'general'}), 400

    except Exception as e:
        print("Error registering candidate:", e)
        return jsonify({'success': False, 'message': 'Server error: ' + str(e)}), 500

# change candidate status
@app.route('/change_candidate_status', methods=['POST'])
def change_candidate_status():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['status']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    allowed_status = ['pending','approved','rejected','withdrawn','elected','lost']
    if len(data['status']) in allowed_status:
        return jsonify({'success': False, 'message': 'Status must be allowed status'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500
    success = admin_model.change_candidate_status(data.get('status'), data.get('id'))
    if success:
        return jsonify({'success': True, 'message': 'status changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400


#===============Votes======================================#
@app.route('/api/ongoing-elections')
def get_ongoing_elections():
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    try:
        sql = "SELECT id, election_name FROM election WHERE status = 'ongoing' ORDER BY id ASC"
        admin_model.cursor.execute(sql)
        elections = admin_model.cursor.fetchall()
        if elections:
            elections = [dict(zip([key[0] for key in admin_model.cursor.description], row)) for row in elections]
        else:
            elections = []
        return jsonify({'success': True, 'elections': elections})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/live-results-chart')
def api_live_results_chart():
    election_id = request.args.get('election_id', type=int)
    if not election_id:
        return jsonify([])

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500

    flag, data = admin_model.get_candidate_votes_summary(election_id)
    return jsonify(data if flag else [])


@app.route('/api/live-summary/<int:election_id>')
def live_summary_api(election_id):
    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed'}), 500
    data = admin_model.get_live_summary(election_id)
    if data:
        if data.get('time_remaining') is not None:
            data['time_remaining'] = str(data['time_remaining'])
        return jsonify(data)
    return jsonify({'error': 'Could not fetch data'}), 500

# checking admin login
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
            session['password'] = result[0].get('password')
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
        "message": "This user is not registered!."
    })

# profile admin
@app.route('/profile_admin')
def profile_admin():
    return render_template('admin/admin_profile.html')

# change admin password
@app.route('/change_password_admin', methods=['POST'])
def change_password_admin():

    data = request.get_json()
    print(data)
    if not all(key in data for key in ['old_password', 'new_password', 'confirm_password']):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400

    if len(data['new_password']) < 6 or len(data['new_password']) > 20:
        return jsonify({'success': False, 'message': 'Password must be at least 6 to 20 characters long'}), 400

    if data['new_password'] != data['confirm_password']:
        return jsonify({'success': False, 'message': 'New password and confirmation do not match'}), 400
    if not bcrypt.check_password_hash(session['password'], data['old_password']):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400

    connection_status, admin_model = check_admin_model_connection()
    if not connection_status:
        return jsonify({'success': False, 'message': 'Database connection failed', 'field': 'general'}), 500

    hashed_password = bcrypt.generate_password_hash(data.get('new_password')).decode('utf-8')
    success = admin_model.change_admin_password(hashed_password, data.get('admin_id'))
    if success:
        session['password'] = hashed_password
        return jsonify({'success': True, 'message': 'Password changed successfully'}), 200
    return jsonify({'success': False, 'message': 'Failed to change password', 'field': 'general'}), 400

# change admin details
@app.route('/change_admin_details', methods=['POST'])
def change_admin_details():
    if not request.is_json:
        return jsonify({'status': False, 'message': 'Request must be JSON'}), 400

    try:
        data = request.get_json()
        print(data)
        errors = {}

        if not data.get('name'):
            errors['name'] = 'Name is required'
        else:
            is_valid_name, name_error = validate_full_name(data['name'])
            if not is_valid_name:
                errors['name'] = name_error

        if not data.get('email'):
            errors['email'] = 'Email is required'
        elif not validate_email(data['email']):
            errors['email'] = 'Invalid email format'

        if errors:
            return jsonify({'status': False, 'message': 'Validation failed', 'errors': errors}), 400

        connection_status, admin_model = check_admin_model_connection()
        if connection_status:
            success = admin_model.update_admin_details(data)
            if success:
                return jsonify({'status': True, 'message': 'admin details updated successfully'})
            return jsonify({'status': False, 'message': 'Failed to update user details'})
        return jsonify({"Database connection problem."})
    except Exception as e:
        print(f'Error updating user details: {str(e)}')
        return jsonify({'status': False, 'message': 'Server error occurred while updating user details'}), 500


#logout page
@app.route('/logout_page_admin')
def logout_page_admin():
    return render_template('admin/pages_logout.html')
# Logout admin
@app.route('/logout')
def logout_admin():
    session.clear()
    return render_template('admin/pages_logout.html')

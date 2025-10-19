import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta
bcrypt = Bcrypt(app)

class AdminDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def make_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.connection.cursor()
        except Exception as e:
            print(e)

    def my_cursor(self):
        return self.cursor


class AdminModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as err:
            print('Something went wrong! Internet connection or database connection. (Admin DB)')
            print(f'Error: {err}')

    # check admin login
    def check_login(self,email):
        sql = """
                 SELECT * FROM admin
                 WHERE username = %s;"""

        try:
            self.cursor.execute(sql,(email,))
            result = self.cursor.fetchall()
            if result:
                print('Waa la helay Adeegsadaha.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Lama helin wax Adeegsade ah.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    # insert admin data
    def register_admin(self, name,email,password):
        try:
            query = """
            INSERT INTO admin (name, username,password)
            VALUES (%s, %s, %s)
                      """
            self.cursor.execute(query, (name,email,password))
            self.connection.commit()
            return True, 'Admin registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    # change admin password
    def change_admin_password(self, password,admin_id):
        sql = """
                   UPDATE admin 
                   SET password = %s 
                   WHERE id = %s;
                   """
        try:
            self.cursor.execute(sql, (password, admin_id))
            self.connection.commit()  # Commit the transaction
            print(f"success happen.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            print(f'there is an error happen.')
            return False

    # change admin details
    def update_admin_details(self, admin_data):
        """
        Update admin details in admin_login table
        """
        sql = """
        UPDATE admin SET
            name = %s,
            username = %s
        WHERE id = %s;
        """

        try:
            values = (
                admin_data.get('name'),
                admin_data.get('email'),  # address is optional
                int(admin_data.get('admin_id'))
            )

            self.cursor.execute(sql, values)
            self.connection.commit()

            if self.cursor.rowcount == 0:
                return False, 'No admin found with that ID or no changes made'

            return True, 'User details updated successfully'

        except Exception as e:
            self.connection.rollback()
            print(f"Error updating admin details: {str(e)}")

            # Handle duplicate email/phone errors
            if "Duplicate entry" in str(e) and "email" in str(e):
                return False, 'Email is already in use by another user'
            if "Duplicate entry" in str(e) and "phone" in str(e):
                return False, 'Phone number is already in use by another user'

            return False, f'Database error: {str(e)}'

    #=================================#
    #student data
    # insert student data
    def register_student(self, name, student_id):
        try:
            query = """
               INSERT INTO students (name, school_id)
               VALUES (%s, %s)
                         """
            self.cursor.execute(query, (name, student_id))
            self.connection.commit()
            return True, 'Student registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    #check student id
    def is_student_registered(self,student_id,name):
        sql = """
                 SELECT * FROM students
                 WHERE (school_id = %s and name = %s) or (school_id = %s);"""

        try:
            self.cursor.execute(sql,(student_id,name,student_id))
            result = self.cursor.fetchall()
            if result:
                print('Waa la helay ardayga.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Lama helin wax arday ah.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    #get all students data
    def get_all_students(self):
        sql = """
                 SELECT * FROM students;"""

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                print('Waa la helay ardayda.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Lama helin wax arday ah.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

    # change student details
    def update_student_details(self, student_data):
            """
            Update admin details in admin_login table
            """
            sql = """
            UPDATE students SET
                name = %s,
                school_id = %s
            WHERE id = %s;
            """

            try:
                values = (
                    student_data.get('name'),
                    student_data.get('student_id'),
                    int(student_data.get('id'))
                )

                self.cursor.execute(sql, values)
                self.connection.commit()

                if self.cursor.rowcount == 0:
                    return False, 'No admin found with that ID or no changes made'

                return True, 'User details updated successfully'

            except Exception as e:
                self.connection.rollback()
                print(f"Error updating admin details: {str(e)}")

                # Handle duplicate email/phone errors
                if "Duplicate entry" in str(e) and "email" in str(e):
                    return False, 'Email is already in use by another user'
                if "Duplicate entry" in str(e) and "phone" in str(e):
                    return False, 'Phone number is already in use by another user'

                return False, f'Database error: {str(e)}'

    # change student password
    def change_student_password(self, password, id):
        sql = """
                       UPDATE students 
                       SET password = %s 
                       WHERE id = %s;
                       """
        try:
            self.cursor.execute(sql, (password, id))
            self.connection.commit()  # Commit the transaction
            print(f"success happen.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            print(f'there is an error happen.')
            return False

    #====================Teachers====================#
    # insert teacher data
    def register_teacher(self, name, teacher_id):
            try:
                query = """
                   INSERT INTO teachers (name, teacher_id)
                   VALUES (%s, %s)
                             """
                self.cursor.execute(query, (name, teacher_id))
                self.connection.commit()
                return True, 'Teacher registered successfully.'
            except Exception as e:
                self.connection.rollback()
                print('Database insert error:', str(e))
                return False, str(e)

    # check if teacher already registered
    def is_teacher_registered(self, teacher_id, name):
            sql = """
                     SELECT * FROM teachers
                     WHERE (teacher_id = %s and name = %s) or (teacher_id = %s);"""

            try:
                self.cursor.execute(sql, (teacher_id, name, teacher_id))
                result = self.cursor.fetchall()
                if result:
                    print('Waa la helay macalinka.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Lama helin wax macalinka ah.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    # get all teachers data
    def get_all_teachers(self):
            sql = """
                     SELECT * FROM teachers;"""

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                if result:
                    print('Waa la helay macallinka.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Lama helin wax macallinka ah.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    # change teacher details
    def update_teacher_details(self, teacher_data):
            """
            Update admin details in admin_login table
            """
            sql = """
                UPDATE teachers SET
                    name = %s,
                    teacher_id = %s
                WHERE id = %s;
                """

            try:
                values = (
                    teacher_data.get('name'),
                    teacher_data.get('teacher_id'),
                    int(teacher_data.get('id'))
                )

                self.cursor.execute(sql, values)
                self.connection.commit()

                if self.cursor.rowcount == 0:
                    return False, 'No teacher found with that ID or no changes made'

                return True, 'teacher details updated successfully'

            except Exception as e:
                self.connection.rollback()
                print(f"Error updating admin details: {str(e)}")

                # Handle duplicate email/phone errors
                if "Duplicate entry" in str(e) and "email" in str(e):
                    return False, 'Email is already in use by another user'
                if "Duplicate entry" in str(e) and "phone" in str(e):
                    return False, 'Phone number is already in use by another user'

                return False, f'Database error: {str(e)}'

    # change teacher password
    def change_teacher_password(self, password, id):
            sql = """
                           UPDATE teachers 
                           SET password = %s 
                           WHERE id = %s;
                           """
            try:
                self.cursor.execute(sql, (password, id))
                self.connection.commit()  # Commit the transaction
                print(f"success happen.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False

    #================= Election ============#
    # insert election data
    def add_election(self, name, start_date, end_date, desc,photo_path):
        try:
            query = """
                       INSERT INTO election (election_name, description,start_date,end_date,photo_path)
                       VALUES (%s, %s,%s,%s,%s)
                                 """
            self.cursor.execute(query, (name, desc,start_date,end_date,photo_path))
            self.connection.commit()
            return True, 'Election registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    # get all elections data
    def get_all_elections(self):
            sql = """
                         SELECT * FROM election;"""

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                if result:
                    print('Waa la helay doorashooyinka.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Lama helin wax doorashooyin ah.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    # change election details
    def update_election_details(self, election_id,election_name, start_date, end_date, description,photo_path):
            """
            Update election details in admin_login table
            """
            try:
                # Case 1: When a new photo is uploaded
                if photo_path is not False:
                    sql = """
                            UPDATE election SET
                                election_name = %s, 
                                description = %s,
                                start_date = %s,
                                end_date = %s,
                                photo_path = %s
                            WHERE id = %s;
                            """
                    values = (election_name,description, start_date, end_date,photo_path,election_id)
                else:
                    sql = """
                        UPDATE election SET
                        election_name = %s, 
                        description = %s,
                        start_date = %s,
                        end_date = %s
                        WHERE id = %s;
                                                """
                    values = (election_name,description, start_date, end_date, election_id)
                self.cursor.execute(sql, values)
                self.connection.commit()

                if self.cursor.rowcount == 0:
                    return False, 'No election found with that ID or no changes made'

                return True, 'election details updated successfully'

            except Exception as e:
                self.connection.rollback()
                print(f"Error updating admin details: {str(e)}")

                # Handle duplicate email/phone errors
                if "Duplicate entry" in str(e) and "email" in str(e):
                    return False, 'Email is already in use by another user'
                if "Duplicate entry" in str(e) and "phone" in str(e):
                    return False, 'Phone number is already in use by another user'

                return False, f'Database error: {str(e)}'

    # change election status
    def change_election_status(self, status, id):
            sql = """
            UPDATE election 
            SET status = %s 
            WHERE id = %s;
            """
            try:
                self.cursor.execute(sql, (status, id))
                self.connection.commit()  # Commit the transaction
                print(f"success happen.")
                return True
            except Exception as e:
                print(f"Error: {e}")
                print(f'there is an error happen.')
                return False

    #==================Candidates==================#
    # insert election data
    def add_candidate(self, name,photo,statement,election_id):
        try:
            query = """
            INSERT INTO candidates (name,photo,statement,election_id)
            VALUES (%s,%s,%s,%s)
                                     """
            self.cursor.execute(query, (name,photo,statement,election_id))
            self.connection.commit()
            return True, 'Candidate registered successfully.'
        except Exception as e:
            self.connection.rollback()
            print('Database insert error:', str(e))
            return False, str(e)

    # get all candidates data
    def get_all_candidates(self):
        sql = """
                SELECT * FROM candidates;"""

        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                print('Waa la helay musharaxiinta.')
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                return True, result
            else:
                print('Lama helin wax musharaxiin ah.')
                return False, {}
        except Exception as e:
            print(f'Error: {e}')
            return False, f'Error {e}.'

        # change election details

    def update_candidate_details(self, candidate_id, name, photo, statement, election_id):
        """
        Update candidate details in the candidates table.
        If `photo` is False, the photo will not be updated.
        """
        print('come here ...123')
        try:
            # Case 1: When a new photo is uploaded
            if photo is not False:
                print('halkaan markaan 1')
                sql = """
                    UPDATE candidates
                    SET name = %s,
                        photo = %s,
                        statement = %s,
                        election_id = %s
                    WHERE id = %s;
                """
                values = (name, photo, statement, election_id, int(candidate_id))
            else:
                # Case 2: When the photo should remain unchanged
                sql = """
                    UPDATE candidates
                    SET name = %s,
                        statement = %s,
                        election_id = %s
                    WHERE id = %s;
                """
                values = (name, statement, election_id, int(candidate_id))

            # Execute SQL
            self.cursor.execute(sql, values)
            self.connection.commit()

            if self.cursor.rowcount == 0:
                return False, 'No candidate found with that ID or no changes made.'

            return True, 'Candidate details updated successfully.'

        except Exception as e:
            self.connection.rollback()
            print(f"Error updating candidate details: {str(e)}")

            # Custom duplicate key messages (if you need them)
            if "Duplicate entry" in str(e) and "email" in str(e):
                return False, 'Email is already in use by another user.'
            if "Duplicate entry" in str(e) and "phone" in str(e):
                return False, 'Phone number is already in use by another user.'

            return False, f'Database error: {str(e)}'

    def change_candidate_status(self, status, id):
        sql = """
                UPDATE candidates 
                SET status = %s 
                WHERE id = %s;
                """
        try:
            self.cursor.execute(sql, (status, id))
            self.connection.commit()  # Commit the transaction
            print(f"success happen.")
            return True
        except Exception as e:
            print(f"Error: {e}")
            print(f'there is an error happen.')
            return False

    #=======================votes=========================#
    # --- Get all votes ---
    def get_all_votes(self, election_id=None):
        sql = """
            SELECT v.id, v.voter_id, v.candidate_id, v.timestamp, v.election_id,
                   c.name AS candidate_name,
                   e.election_name,
                   s.name AS voter_name
            FROM votes v
            LEFT JOIN candidates c ON v.candidate_id = c.id
            LEFT JOIN election e ON v.election_id = e.id
            LEFT JOIN students s ON v.voter_id = s.id
        """
        try:
            if election_id:
                sql += " WHERE v.election_id = %s"
                self.cursor.execute(sql, (election_id,))
            else:
                self.cursor.execute(sql)

            result = self.cursor.fetchall()
            if result:
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]
                return True, result
            else:
                return False, []
        except Exception as e:
            return False, str(e)

    # Candidate votes summary (no position column)
    def get_candidate_votes_summary(self, election_id=None):
        """
        Returns a summary of candidates and their total votes for a given election.
        Now ignores 'position' since it was removed from the database.
        """

        sql = """
            SELECT 
                c.id,
                c.name AS candidate_name,
                c.photo,
                COUNT(v.id) AS votes
            FROM candidates c
            LEFT JOIN votes v 
                ON c.id = v.candidate_id 
                AND v.election_id = c.election_id
        """
        params = []

        if election_id:
            sql += " WHERE c.election_id = %s"
            params.append(election_id)

        sql += " GROUP BY c.id, c.name ORDER BY votes DESC"

        try:
            self.cursor.execute(sql, params)
            rows = self.cursor.fetchall()

            if rows:
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in rows]
                return True, result
            else:
                return True, []  # no candidates found but not an error
        except Exception as e:
            return False, str(e)

    # Live election summary
    def get_live_summary(self, election_id):
        """
        Returns a live summary for a given election — now simplified:
        total votes, students voted/not voted, and remaining time.
        """

        dict_cursor = self.connection.cursor(dictionary=True)

        sql = """
            SELECT 
                (SELECT COUNT(*) FROM votes WHERE election_id=%s) AS total_votes,
                (SELECT COUNT(DISTINCT voter_id) FROM votes 
                    WHERE election_id=%s ) AS total_students_voted,
                (SELECT COUNT(*) FROM students) -
                    (SELECT COUNT(DISTINCT voter_id) FROM votes 
                        WHERE election_id=%s) AS total_students_not_voted,
                TIMEDIFF(e.end_date, NOW()) AS time_remaining
            FROM election e
            WHERE e.id=%s;
        """

        num_placeholders = sql.count('%s')
        params = [election_id] * num_placeholders

        try:
            dict_cursor.execute(sql, params)
            result = dict_cursor.fetchone()

            if result and result.get('time_remaining') is not None:
                result['time_remaining'] = str(result['time_remaining'])

            return result
        except Exception as e:
            print(f"Error fetching live summary: {e}")
            return None

    # --- Get final results (vote counts) ---
    def get_final_results(self, election_id=None):
        sql = """
            SELECT 
                c.id,
                c.name AS candidate_name,
                e.id AS election_id,
                e.election_name,
                COALESCE(COUNT(v.id), 0) AS votes
            FROM candidates c
            LEFT JOIN votes v ON c.id = v.candidate_id
            LEFT JOIN election e ON c.election_id = e.id
            WHERE e.status = 'completed'
        """
        try:
            params = ()
            if election_id:
                sql += " AND c.election_id = %s"
                params = (election_id,)

            sql += " GROUP BY c.id, c.name, e.election_name ORDER BY votes DESC"
            self.cursor.execute(sql, params)

            result = self.cursor.fetchall()
            if result:
                result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]
                return True, result
            else:
                return False, []
        except Exception as e:
            return False, str(e)

    #get all election with status completed for use of final result page
    def get_all_elections_completed(self):
            sql = """
                         SELECT * FROM election WHERE status = 'completed';"""

            try:
                self.cursor.execute(sql)
                result = self.cursor.fetchall()
                if result:
                    print('Waa la helay doorashooyinka.')
                    result = [dict(zip([key[0] for key in self.cursor.description], row)) for row in result]

                    return True, result
                else:
                    print('Lama helin wax doorashooyin ah.')
                    return False, {}
            except Exception as e:
                print(f'Error: {e}')
                return False, f'Error {e}.'

    #dashboard data
    def get_dashboard_stats(self):
        """
        Fetch dashboard statistics and calculate change percentages safely.
        """
        try:
            data = {}

            # ---------------------------
            # Helper function
            # ---------------------------
            def calc_change(current, previous):
                if previous > 0:
                    change = round(((current - previous) / previous) * 100, 2)
                else:
                    change = 0
                return {
                    'count': current,
                    'change': change,
                    'direction': 'up' if change >= 0 else 'down'
                }

            # ---------------------------
            # Registered Students
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM students;")
            current_students = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM students 
                WHERE MONTH(created_at) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH)
                AND YEAR(created_at) = YEAR(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_students_row = self.cursor.fetchone()
            prev_students = prev_students_row[0] if prev_students_row else 0

            data['registered_students'] = calc_change(current_students, prev_students)

            # ---------------------------
            # Total Votes
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM votes;")
            current_votes = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM votes
                WHERE YEARWEEK(timestamp, 1) = YEARWEEK(CURRENT_DATE - INTERVAL 1 WEEK, 1);
            """)
            prev_votes_row = self.cursor.fetchone()
            prev_votes = prev_votes_row[0] if prev_votes_row else 0

            data['total_votes'] = calc_change(current_votes, prev_votes)

            # ---------------------------
            # Active Elections
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM election WHERE status = 'ongoing';")
            current_active = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM election
                WHERE status = 'ongoing'
                AND MONTH(start_date) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_active_row = self.cursor.fetchone()
            prev_active = prev_active_row[0] if prev_active_row else 0

            data['active_elections'] = calc_change(current_active, prev_active)

            # ---------------------------
            # Upcoming Elections
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM election WHERE status = 'upcoming';")
            current_upcoming = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM election
                WHERE status = 'upcoming'
                AND MONTH(start_date) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_upcoming_row = self.cursor.fetchone()
            prev_upcoming = prev_upcoming_row[0] if prev_upcoming_row else 0

            data['upcoming_elections'] = calc_change(current_upcoming, prev_upcoming)

            # ---------------------------
            # All Elections
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM election;")
            current_all_elections = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM election
                WHERE MONTH(start_date) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_all_elections_row = self.cursor.fetchone()
            prev_all_elections = prev_all_elections_row[0] if prev_all_elections_row else 0

            data['all_elections'] = calc_change(current_all_elections, prev_all_elections)

            # ---------------------------
            # Approved Candidates
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'approved';")
            current_approved = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM candidates
                WHERE status = 'approved'
                AND MONTH(id) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_approved_row = self.cursor.fetchone()
            prev_approved = prev_approved_row[0] if prev_approved_row else 0

            data['approved_candidates'] = calc_change(current_approved, prev_approved)

            # ---------------------------
            # Pending Candidates
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM candidates WHERE status = 'pending';")
            current_pending = self.cursor.fetchone()[0] or 0

            self.cursor.execute("""
                SELECT COUNT(*) FROM candidates
                WHERE status = 'pending'
                AND MONTH(id) = MONTH(CURRENT_DATE - INTERVAL 1 MONTH);
            """)
            prev_pending_row = self.cursor.fetchone()
            prev_pending = prev_pending_row[0] if prev_pending_row else 0

            data['pending_candidates'] = calc_change(current_pending, prev_pending)

            # ---------------------------
            # System Users (admins)
            # ---------------------------
            self.cursor.execute("SELECT COUNT(*) FROM admin;")
            current_admins = self.cursor.fetchone()[0] or 0

            # No previous-month data (static)
            data['system_users'] = calc_change(current_admins, current_admins)

            print("Dashboard stats fetched successfully.")
            return True, data

        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
            return False, f"Error: {e}"


admin_db_configuration = DbConfiguration()


def check_admin_model_connection():
    try:
        mysql_connect = AdminDatabase(
            host=admin_db_configuration.DB_HOSTNAME,
            port=3306,
            user=admin_db_configuration.DB_USERNAME,
            password=admin_db_configuration.DB_PASSWORD,
            database=admin_db_configuration.DB_NAME
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_admin_model = AdminModel(mysql_connect.connection)

        return True, my_admin_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'

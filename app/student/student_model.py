import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
from datetime import datetime, timedelta

bcrypt = Bcrypt(app)

class UserDatabase:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def make_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                auth_plugin='mysql_native_password'  # ensures compatibility
            )
            self.cursor = self.connection.cursor(dictionary=True)

            print("✅ Database connection successful.")
        except Error as e:
            print(f"❌ Database connection error: {e}")
            self.connection = None
            self.cursor = None

    def my_cursor(self):
        return self.cursor



class UserModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor(dictionary=True)
        except Exception as err:
            print('Something went wrong! Database connection issue.')
            print(f'Error: {err}')

    # =================================RECENT ACTIVITIES PART=======================================
    def get_user_voting_activities(self, user_id, limit=5):
        """Get user's recent voting activities"""
        try:
            self.cursor.execute("""
                SELECT 
                    v.timestamp,
                    e.election_name,
                    c.name as candidate_name,
                    TIMESTAMPDIFF(HOUR, v.timestamp, NOW()) as hours_ago
                FROM votes v
                JOIN election e ON v.election_id = e.id
                JOIN candidates c ON v.candidate_id = c.id
                WHERE v.voter_id = %s
                ORDER BY v.timestamp DESC
                LIMIT %s
            """, (user_id, limit))
            
            voting_activities = self.cursor.fetchall()
            return True, voting_activities
        except Exception as e:
            print(f"Error in get_user_voting_activities: {e}")
            return False, str(e)

    def get_recent_election_status_changes(self, limit=3):
        """Get recently started or completed elections"""
        try:
            self.cursor.execute("""
                SELECT 
                    election_name,
                    description,
                    start_date,
                    end_date,
                    status,
                    TIMESTAMPDIFF(HOUR, 
                        CASE 
                            WHEN status = 'ongoing' THEN start_date
                            WHEN status = 'completed' THEN end_date
                        END, 
                        NOW()
                    ) as hours_ago
                FROM election
                WHERE (status = 'ongoing' AND start_date >= DATE_SUB(NOW(), INTERVAL 7 DAY))
                   OR (status = 'completed' AND end_date >= DATE_SUB(NOW(), INTERVAL 7 DAY))
                ORDER BY 
                    CASE 
                        WHEN status = 'ongoing' THEN start_date
                        WHEN status = 'completed' THEN end_date
                    END DESC
                LIMIT %s
            """, (limit,))
            
            election_changes = self.cursor.fetchall()
            return True, election_changes
        except Exception as e:
            print(f"Error in get_recent_election_status_changes: {e}")
            return False, str(e)

    def get_upcoming_elections_soon(self, limit=2):
        """Get elections starting in the next 7 days"""
        try:
            self.cursor.execute("""
                SELECT 
                    election_name,
                    description,
                    start_date,
                    TIMESTAMPDIFF(DAY, NOW(), start_date) as days_until_start
                FROM election
                WHERE status = 'upcoming' 
                AND start_date BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 7 DAY)
                ORDER BY start_date ASC
                LIMIT %s
            """, (limit,))
            
            upcoming_elections = self.cursor.fetchall()
            return True, upcoming_elections
        except Exception as e:
            print(f"Error in get_upcoming_elections_soon: {e}")
            return False, str(e)

    def get_new_candidates_activities(self, limit=3):
        """Get recently added candidates"""
        try:
            self.cursor.execute("""
                SELECT 
                    c.name as candidate_name,
                    e.election_name,
                    c.status as candidate_status,
                    TIMESTAMPDIFF(DAY, e.created_at, NOW()) as days_ago
                FROM candidates c
                JOIN election e ON c.election_id = e.id
                WHERE e.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                ORDER BY e.created_at DESC
                LIMIT %s
            """, (limit,))
            
            candidate_activities = self.cursor.fetchall()
            return True, candidate_activities
        except Exception as e:
            print(f"Error in get_new_candidates_activities: {e}")
            return False, str(e)

    def get_recent_activity_feed(self, user_id, limit=10):
        """Combine all activities into a single feed"""
        try:
            activities = []
            
            # 1. Get user's voting activities
            success, voting_activities = self.get_user_voting_activities(user_id, 3)
            if success:
                for activity in voting_activities:
                    activities.append({
                        'type': 'vote',
                        'title': f'Voted in {activity["election_name"]}',
                        'description': f'You voted for {activity["candidate_name"]}',
                        'timestamp': activity['timestamp'],
                        'time_ago': self._format_time_ago(activity['hours_ago']),
                        'icon': 'vote'
                    })
            
            # 2. Get recent election status changes
            success, election_changes = self.get_recent_election_status_changes(3)
            if success:
                for election in election_changes:
                    if election['status'] == 'ongoing':
                        activities.append({
                            'type': 'election_start',
                            'title': 'New Election Started',
                            'description': f'{election["election_name"]} is now open for voting',
                            'timestamp': election['start_date'],
                            'time_ago': self._format_time_ago(election['hours_ago']),
                            'icon': 'election'
                        })
                    elif election['status'] == 'completed':
                        activities.append({
                            'type': 'election_end',
                            'title': 'Election Completed',
                            'description': f'{election["election_name"]} results are available',
                            'timestamp': election['end_date'],
                            'time_ago': self._format_time_ago(election['hours_ago']),
                            'icon': 'result'
                        })
            
            # 3. Get upcoming elections
            success, upcoming_elections = self.get_upcoming_elections_soon(2)
            if success:
                for election in upcoming_elections:
                    activities.append({
                        'type': 'election_upcoming',
                        'title': 'Election Starting Soon',
                        'description': f'{election["election_name"]} starts in {election["days_until_start"]} days',
                        'timestamp': election['start_date'],
                        'time_ago': f'in {election["days_until_start"]} days',
                        'icon': 'election'
                    })
            
            # 4. Get new candidates
            success, candidate_activities = self.get_new_candidates_activities(2)
            if success:
                for candidate in candidate_activities:
                    activities.append({
                        'type': 'new_candidate',
                        'title': 'New Candidate Added',
                        'description': f'{candidate["candidate_name"]} joined {candidate["election_name"]}',
                        'timestamp': None,  # We don't have candidate creation timestamp
                        'time_ago': f'{candidate["days_ago"]} days ago',
                        'icon': 'vote'
                    })
            
            # Sort by timestamp (most recent first) and limit
            activities.sort(key=lambda x: x['timestamp'] if x['timestamp'] else '', reverse=True)
            return True, activities[:limit]
            
        except Exception as e:
            print(f"Error in get_recent_activity_feed: {e}")
            return False, str(e)

    def _format_time_ago(self, hours_ago):
        """Convert hours to human readable time ago"""
        if hours_ago < 1:
            return 'Just now'
        elif hours_ago < 24:
            return f'{hours_ago} hours ago'
        else:
            days = hours_ago // 24
            return f'{days} days ago'
    # ========================================================================
    
    def get_dashboard_stats(self, user_id, role):
        """Get all dashboard statistics for a user"""
        try:
            stats = {}
            
            # Total Elections
            self.cursor.execute("SELECT COUNT(*) as count FROM election")
            total_elections = self.cursor.fetchone()['count']
            stats['total_elections'] = total_elections
            
            # Ongoing Elections (current date between start_date and end_date)
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM election 
                WHERE status = 'ongoing' 
                OR (start_date <= NOW() AND end_date >= NOW())
            """)
            ongoing_elections = self.cursor.fetchone()['count']
            stats['ongoing_elections'] = ongoing_elections
            
            # Upcoming Elections
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM election 
                WHERE status = 'upcoming' 
                OR start_date > NOW()
            """)
            upcoming_elections = self.cursor.fetchone()['count']
            stats['upcoming_elections'] = upcoming_elections
            
            # Completed Elections
            self.cursor.execute("""
                SELECT COUNT(*) as count FROM election 
                WHERE status = 'completed' 
                OR end_date < NOW()
            """)
            completed_elections = self.cursor.fetchone()['count']
            stats['completed_elections'] = completed_elections
            
            # Participated Elections (elections where user has voted)
            if role == 'student':
                self.cursor.execute("""
                    SELECT COUNT(DISTINCT election_id) as count FROM votes 
                    WHERE voter_id = %s
                """, (user_id,))
            else:
                # For teachers, you might have a different logic
                self.cursor.execute("""
                    SELECT COUNT(DISTINCT election_id) as count FROM votes 
                    WHERE voter_id = %s
                """, (user_id,))
            
            participated_result = self.cursor.fetchone()
            stats['participated_elections'] = participated_result['count'] if participated_result else 0
            
            return True, stats
            
        except Exception as e:
            print(f"Error in get_dashboard_stats: {e}")
            return False, str(e)

    def get_recent_elections(self, limit=5):
        """Get recent elections for the activity feed"""
        try:
            self.cursor.execute("""
                SELECT * FROM election 
                ORDER BY start_date DESC 
                LIMIT %s
            """, (limit,))
            elections = self.cursor.fetchall()
            return True, elections
        except Exception as e:
            print(f"Error in get_recent_elections: {e}")
            return False, str(e)

    def get_user_voting_activity(self, user_id, role):
        """Get user's recent voting activity"""
        try:
            if role == 'student':
                self.cursor.execute("""
                    SELECT v.*, e.election_name, c.name as candidate_name
                    FROM votes v
                    JOIN election e ON v.election_id = e.id
                    JOIN candidates c ON v.candidate_id = c.id
                    WHERE v.voter_id = %s
                    ORDER BY v.timestamp DESC
                    LIMIT 5
                """, (user_id,))
            else:
                # Similar query for teachers if needed
                self.cursor.execute("""
                    SELECT v.*, e.election_name, c.name as candidate_name
                    FROM votes v
                    JOIN election e ON v.election_id = e.id
                    JOIN candidates c ON v.candidate_id = c.id
                    WHERE v.voter_id = %s
                    ORDER BY v.timestamp DESC
                    LIMIT 5
                """, (user_id,))
            
            activity = self.cursor.fetchall()
            return True, activity
        except Exception as e:
            print(f"Error in get_user_voting_activity: {e}")
            return False, str(e)

    def check_login(self, user_id):
        """Check student login by ID."""
        try:
            query = "SELECT * FROM students WHERE school_id = %s"
            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchall()

            if result and len(result) > 0:
                return True, result
            else:
                return False, None

        except Exception as e:
            print(f"Error in check_login: {e}")
            return False, None
        

    def check_user(self, user_id, role):
        try:
            if role == 'student':
                query = "SELECT * FROM students WHERE id = %s"
            elif role == 'teacher':
                query = "SELECT * FROM teachers WHERE id = %s"
            else:
                return False, None

            self.cursor.execute(query, (user_id,))
            result = self.cursor.fetchall()

            if result and len(result) > 0:
                return True, result
            else:
                return False, None

        except Exception as e:
            print(f"Error in check_login: {e}")
            return False, None




user_db_configuration = DbConfiguration()

def check_user_model_connection():
    try:
        mysql_connect = UserDatabase(
            host=user_db_configuration.DB_HOSTNAME,
            port=3306,
            user=user_db_configuration.DB_USERNAME,
            password=user_db_configuration.DB_PASSWORD,
            database=user_db_configuration.DB_NAME
        )
        
        # Create database connection
        mysql_connect.make_connection()
        
        # Create model
        my_user_model = UserModel(mysql_connect.connection)

        # ✅ return also the connection so we can close it later
        return True, my_user_model, mysql_connect.connection

    except Exception as e:
        return False, f'Error: {e}', None

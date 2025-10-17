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

    def check_login(self, user_id, role):
        """Check user login by role and ID."""
        try:
            if role == 'student':
                query = "SELECT * FROM students WHERE school_id = %s"
            elif role == 'teacher':
                query = "SELECT * FROM teachers WHERE teacher_id = %s"
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
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_user_model = UserModel(mysql_connect.connection)

        return True, my_user_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
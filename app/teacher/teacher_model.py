import mysql.connector
from app.configuration import DbConfiguration
from mysql.connector import Error, IntegrityError
from flask_bcrypt import Bcrypt
from app import app
import datetime
from datetime import datetime, timedelta
bcrypt = Bcrypt(app)

class TeacherDatabase:
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


class TeacherModel:
    def __init__(self, connection):
        try:
            self.connection = connection
            self.cursor = connection.cursor()
        except Exception as err:
            print('Something went wrong! Internet connection or database connection. (Admin DB)')
            print(f'Error: {err}')

        # retrieving data
        #login



teacher_db_configuration = DbConfiguration()


def check_teacher_model_connection():
    try:
        mysql_connect = TeacherDatabase(
            host=teacher_db_configuration.DB_HOSTNAME,
            port=3306,
            user=teacher_db_configuration.DB_USERNAME,
            password=teacher_db_configuration.DB_PASSWORD,
            database=teacher_db_configuration.DB_NAME
        )
        # Create an instance of the Store class
        mysql_connect.make_connection()
        my_teacher_model = TeacherModel(mysql_connect.connection)

        return True, my_teacher_model
    except Exception as e:
        print(f'')
        return False, f'Error: {e}.'
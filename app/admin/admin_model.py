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

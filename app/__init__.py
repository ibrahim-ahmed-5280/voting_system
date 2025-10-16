from flask import Flask, session

app = Flask(__name__)

from app.admin import admin_model
from app.admin import admin_view

from app.student import student_view
from app.student import student_model

# set secret key
app.secret_key = '5280'
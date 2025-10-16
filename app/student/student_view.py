from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.student.student_model import UserModel, UserDatabase, check_user_model_connection
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
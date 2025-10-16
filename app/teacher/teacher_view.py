from app import app
from flask import render_template, request, make_response, jsonify, session, redirect, url_for
from app.teacher.teacher_model import TeacherModel, TeacherDatabase, check_teacher_model_connection
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date
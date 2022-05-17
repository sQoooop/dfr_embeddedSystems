from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# Create app variable, init creates a module which can be imported
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import modules for entry point
from app import views
from app import admin_views
from app import artifacts_api
from app import mockdata
#initialize db







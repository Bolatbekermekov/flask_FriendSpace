from flask import Flask
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy


# from main import app, db
# # Создайте контекст приложения
# app.app_context().push()
# # Теперь вы можете выполнять операции с базой данных
# db.create_all()
# $ pip uninstall werkzeug
# $ pip install werkzeug==2.3.0



app = Flask(__name__)

# Configure the SQLAlchemy database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gnmdflkbns'

UPLOAD_FOLDER = 'flaskblog/static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

# Initialize the db with the app

# Add CKEditor
ckeditor = CKEditor(app)



# Flask_login Stuff
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Log in to access closed sites"
login_manager.login_message_category = "error"

from flaskblog import main
from flaskblog import api

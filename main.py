import pathlib

from flask import Flask, render_template,url_for,get_flashed_messages,flash,message_flashed,request,redirect
from flask_login import UserMixin,LoginManager,login_user,logout_user,login_required,current_user
from flask_ckeditor import CKEditor
from flask_restx import Api, Resource, Namespace,fields
from google_auth_oauthlib.flow import Flow

from webforms import LoginForm,UserForm,PostForm,NamerForm,SearchForm,ForgotForm
from database import db,Posts,Users
from werkzeug.security import generate_password_hash,check_password_hash
from api import api,ns
from werkzeug.utils import secure_filename
import uuid
import os
from flask_mail import Mail, Message

import jwt
from flask_jwt_extended import create_access_token, JWTManager

from google.auth.transport import requests
from google.oauth2.id_token import verify_oauth2_token
# Import the db instance


# from main import app, db
# # Создайте контекст приложения
# app.app_context().push()
# # Теперь вы можете выполнять операции с базой данных
# db.create_all()
# $ pip uninstall werkzeug
# $ pip install werkzeug==2.3.0



app = Flask(__name__)

# Configure the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'gnmdflkbns'


UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize the db with the app
db.init_app(app)


# Add CKEditor
ckeditor = CKEditor(app)


mail = Mail()  # предположим, что mail - это экземпляр Flask Mail


# Flask_login Stuff
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Log in to access closed sites"
login_manager.login_message_category = "error"

@app.route("/")
def index():
    first_name = "John"
    stuff = "This is bold text"
    favorite_pizza = ["Pepperoni", "Cheeze", "Mushrooms", 41]
    return render_template('index.html', first_name=first_name, stuff=stuff, favorite_pizza=favorite_pizza)

# Create Api service
api.init_app(app)
api.add_namespace(ns)






@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))



#Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create a Search Function
@app.route('/search',methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    posts2 = Posts.query

    if form.validate_on_submit():
        #Get data from submitted form
        posts.searched = form.searched.data
        posts2.searched = form.searched.data

        # Query the Database
        searched_posts = Posts.query.filter(Posts.title.like(f'%{posts.searched}%')).order_by(Posts.title).all()
        searched_posts2 = Posts.query.filter(Posts.content.like(f'%{posts.searched}%')).order_by(Posts.title).all()


        return render_template('search.html',form=form,searched=posts.searched,posts=searched_posts,posts2=searched_posts2)


# Create  Login Page
@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #Check the hash
            if check_password_hash(user.password_hash,form.password.data):
                login_user(user)
                flash("Login Successfull!!!",'success')
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password - Try Again!",'error')
        else:
            flash("That User Doesn't Exist! Try Again...", 'error')
    return render_template('login.html',form=form)

# Create  Logout Page
@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash('You Have Been Logged!','success')
    return redirect(url_for('login'))
def email(recipient, subject, html_body, text_body):
    msg = Message(subject, recipients=[recipient])
    msg.html = html_body
    msg.body = text_body
    mail.send(msg)
@app.route('/forgot',methods=['GET','POST'])
def forgot():
    error = None
    message = None
    form = ForgotForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()
        if user:
            code = str(uuid.uuid4())
            user.change_configuration={
                "password_reset_code":code
            }
            db.session.add(user)  # добавляем пользователя в сессию
            db.session.commit()  #email the user
            msg = Message('Password Reset Request',
                          sender='ermek.bolatbek@bk.ru',
                          recipients=[user.email])
            msg.body = f"Your password reset code is: {code}"
            mail.send(msg)

            flash('Password reset code sent to your email!', 'success')
            return redirect(url_for('reset_password', code=code))

        flash('Email does not exist!', 'danger')
        return render_template('forgot.html', form=form)


@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']
        # name_to_update.profile_pic = request.files['profile_pic']

        # Check for profile pic
        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']

            # Grab image name
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            # Set UUID
            pic_name = str(uuid.uuid1()) + '_' + pic_filename
            # Save That Image
            saver = request.files['profile_pic']
            # Change it to a string to save to db
            name_to_update.profile_pic = pic_name

            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash('User Updated Successfully!', category='success')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
            except:
                flash('Errors! Looks like there','error')
                return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
        else:
            db.session.commit()
            flash('User Updated Successfully!', category='success')
            return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)
    return render_template('dashboard.html')


#
if __name__ == '__main__':
    app.run(debug=True)

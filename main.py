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


@app.route("/posts")
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template("posts.html",posts=posts)

@app.route("/user_posts/<int:user_id>")
def user_posts(user_id):
    posts = Posts.query.filter_by(poster_id=user_id).order_by(Posts.date_posted)
    return render_template("user_posts.html", posts=posts)

@app.route("/posts/edit/<int:id>",methods=['GET','POST'])
@login_required
def edit_post(id):
    edit_post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        edit_post.title = form.title.data
        # edit_post.author = form.author.data
        edit_post.slug = form.slug.data
        edit_post.content = form.content.data

        # Update a Database
        db.session.add(edit_post)
        db.session.commit()
        flash("Post has Been Updated!",category='success')
        return redirect(url_for('users_post',id=edit_post.id))
    if current_user.id == edit_post.poster_id or current_user.id==4:

        form.title.data = edit_post.title
        # form.author.data = edit_post.author
        form.slug.data = edit_post.slug
        form.content.data = edit_post.content
        return render_template('edit_post.html',form=form)
    else:
        flash("You Aren't Authorized To Edit That Post! ",'error')
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
@app.route("/posts/<int:id>")
def users_post(id):

    users_post = Posts.query.get_or_404(id)

    return render_template("users_post.html",users_post=users_post)
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id or id == 4:

        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            flash("Blog Post Was Deleted!",category='success')
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)

        except:
            flash("Whooops! There was a problem,try again...",'error')

            posts = Posts.query.order_by(Posts.date_posted)
            return render_template("posts.html", posts=posts)
    else:
        flash("You Aren't Authorized To Delete That Post! ",'error')

        posts = Posts.query.order_by(Posts.date_posted)
        return render_template("posts.html", posts=posts)
#Add Post page
@app.route('/add-post',methods=['GET','POST'])
def add_post():
    form = PostForm()
    post_users = Posts.query.order_by(Posts.date_posted)


    if form.validate_on_submit():
            poster = current_user.id
            post = Posts(title=form.title.data,content=form.content.data,poster_id=poster,slug=form.slug.data)
           # Clear the Form
            form.title.data = ''
            form.content.data = ''
            form.slug.data = ''

            db.session.add(post)
            db.session.commit()

            flash("Blog Post Submitted Successfully!",category="success")
    return render_template("add_post.html",form=form,post_users=post_users)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    our_users = Users.query.order_by(Users.date_added)

    try:
        db.session.delete(user_to_delete)
        if id == post_to_delete.poster_id:
                db.session.delete(post_to_delete)
                db.session.commit()
        db.session.commit()
        flash("User Deleted Successfully!!!",category='success')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    except:
        flash("Whooops! There was a problem deleting user,try again... ",category='error')
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/update/<int:id>',methods=['GET','POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        name_to_update.about_author = request.form['about_author']

        try:
            db.session.commit()
            flash('User Updated Successfully!',category='success')
            return redirect(url_for('dashboard'))
        except:
            flash('Errors! Looks like there')
            return render_template('update.html', form=form, name_to_update=name_to_update,id=id)
    else:
        return render_template('update.html',form=form,name_to_update=name_to_update,id=id)

# class PasswordForm(FlaskForm):
#     email = StringField("What is Your Email",validators=[DataRequired()])
#     password_hash = PasswordField("What is Your Password",validators=[DataRequired()])
#     submit = SubmitField('Submit')



@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()
    our_users = Users.query.order_by(Users.date_added)
    hashed_pw = None

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        about_author = form.about_author.data

        if form.password_hash.data != form.password_hash2.data:
            flash("Passwords do not match. Please try again.", category='error')
            return redirect(url_for('add_user'))
        else:
            # Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)

            user = Users.query.filter_by(email=email).first()
            if user:
                flash("User with this email already exists.", category="error")
            else:
                new_user = Users(username=username,name=name, email=email, password_hash=hashed_pw,about_author=about_author)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash("User Added Successfully!",category='success')
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error when adding to the database: {str(e)}", category="error")

    return render_template('add_user.html', form=form, name=name, our_users=our_users, password_hash=hashed_pw)


@app.route("/profile")
@login_required
def user():
    user_id = current_user.id
    posts = Posts.query.filter_by(poster_id=user_id).order_by(Posts.date_posted.desc()).all()
    return render_template('user.html', posts=posts)

# Create Custom Error pages
# Invalid URL
@app.errorhandler(404)
def page_not_founded(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Create a Name page
@app.route('/name',methods=["GET","POST"])
def name():
    name = None
    form = NamerForm()
    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully")

    return render_template("name.html",name=name,form=form)


#
if __name__ == '__main__':
    app.run(debug=True)

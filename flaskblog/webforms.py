from flask_wtf import FlaskForm,Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, EmailField,validators
from wtforms.validators import DataRequired,EqualTo,Length, Email
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField
from flaskblog.database import Users


class SearchForm(FlaskForm):
    searched = StringField("Searched",validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Name",validators=[DataRequired()])
    username = StringField("Username",validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    about_author = TextAreaField("About Author",validators=[DataRequired()])
    password_hash = PasswordField("Password",validators=[DataRequired()])
    password_hash2 = PasswordField("Confirm Password",validators=[DataRequired()])
    profile_pic = FileField("Profile Pic")
    submit = SubmitField('Submit')



class PostForm(FlaskForm):
    title = StringField("Title",validators=[DataRequired()])
    # content = StringField("Content",validators=[DataRequired()],widget=TextArea())
    content = CKEditorField("Content",validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug",validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create  LoginForm
class LoginForm(FlaskForm):
    username = StringField("Username",validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Submit")

class ForgotForm(FlaskForm):
    email = EmailField('Email address',validators=[validators.DataRequired(), validators.Email()])
    password_hash = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Reset password")


class PasswordResetForm(FlaskForm):
    current_password = PasswordField('Current Password',[validators.DataRequired()],validators.Length(min=4,max=80))

class NamerForm(FlaskForm):
    name = StringField("What is Your name",validators=[DataRequired()])
    submit = SubmitField('Submit')



class PasswordForm(FlaskForm):
    email = StringField("What is Your Email",validators=[DataRequired()])
    password_hash = PasswordField("What is Your Password",validators=[DataRequired()])
    submit = SubmitField('Submit')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
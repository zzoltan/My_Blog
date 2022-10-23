from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField



# Create login form
class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired("Please enter your username in!")])
    password = PasswordField("Password: ", validators=[DataRequired("Please enter your password in!")])
    submit = SubmitField("Log In")


# Create Post Form

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("Cannot leave this empty")])
    # content = StringField("Content", validators=[DataRequired("Cannot leave this empty")], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    # author = StringField("Author", validators=[DataRequired("Cannot leave this empty")])
    slug = StringField("Slug", validators=[DataRequired("Cannot leave this empty")])

    submit = SubmitField("Post")

# Create user form


class UserForm(FlaskForm):
    username = StringField("User name:", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email!")])
    about_author = TextAreaField("About author: ")
    password_hash = PasswordField("Password:", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords must match!")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    profile_pic = FileField("Profile Photoe")
    submit = SubmitField("Submit")

# Create PasswordForm

class PasswordForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired("Cannot leave this empty!"), Email("Has to be a valid email!")])
    password = PasswordField("Password: ", validators=[DataRequired("Cannot leave this empty!")])
    submit = SubmitField("Submit")

# We are creating a form class

class NamerForm(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create Search form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Submit")






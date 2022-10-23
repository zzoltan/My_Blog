from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length
from wtforms.widgets import TextArea
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_login import UserMixin, login_user, LoginManager,login_required, logout_user, current_user

from datetime import date
# importing werkzeug for handling passwords
from werkzeug.security import generate_password_hash,check_password_hash

# Create a Flask Instance

app = Flask(__name__)

# Add database

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///users.db"
# Secret key
app.config['SECRET_KEY'] = "ZoltanZavarkoPolcsike"


# Initialize database

db = SQLAlchemy(app)

# Setting up the ability to migrate (add new columns on the fly) to our database

migrate = Migrate(app, db)

# Flask Login Stuff
login_manager = LoginManager()
login_manager.init_app(app)
# the below we define which page to display if we are not logged in
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

# Returning JSON - we used to use jsonfy() method, but in flask if we returning a dictionary, flask will convert it to JSON

@app.route("/date")
def get_curent_date():
    favourite_pizza = {
        "John":"Pepperoni",
        "Mary": "Cheese",
        "Tim": "Mushroom"
    }
    # return {"Date":["Current date",date.today()]}
    return favourite_pizza



# Create the User Database Model


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    favourite_color=db.Column(db.String[150])
#     do some password stuff
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute!")
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

#     Create A String
    def __repr__(self):
        return "<Name %r>" % self.name

# Create a Blog Post model

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default = datetime.utcnow)
    slug = db.Column(db.String(255))

# create the database - only run once, after we have to comment it out
# db.create_all()

# Create Post Form

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired("Cannot leave this empty")])
    content = StringField("Content", validators=[DataRequired("Cannot leave this empty")], widget=TextArea())
    author = StringField("Author", validators=[DataRequired("Cannot leave this empty")])
    slug = StringField("Slug", validators=[DataRequired("Cannot leave this empty")])

    submit = SubmitField("Post")

# We are creating a form class

class NamerForm(FlaskForm):
    name = StringField("What is your name", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create user form


class UserForm(FlaskForm):
    username = StringField("User name:", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email("Please enter a valid email!")])
    favourite_color = StringField("Favourite colour: ")
    password_hash = PasswordField("Password:", validators=[DataRequired(), EqualTo("password_hash2", message="Passwords must match!")])
    password_hash2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create PasswordForm

class PasswordForm(FlaskForm):
    email = StringField("Email: ", validators=[DataRequired("Cannot leave this empty!"), Email("Has to be a valid email!")])
    password = PasswordField("Password: ", validators=[DataRequired("Cannot leave this empty!")])
    submit = SubmitField("Submit")

# Create a route decorator

# Home page
@app.route("/")
def home():
    return render_template("index.html")



# Create login form
class LoginForm(FlaskForm):
    username = StringField("Username: ", validators=[DataRequired("Please enter your username in!")])
    password = PasswordField("Password: ", validators=[DataRequired("Please enter your password in!")])
    submit = SubmitField("Log In")

# Create Login page
@app.route("/login", methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #  check the hash
            if check_password_hash(user.password_hash, form.password.data):
                # The login_user function logs in the user, creates the session all that thing
                # to keep track of our logged in user
                login_user(user)
                flash("Login successfull!!!")

                return redirect(url_for("dashboard"))
            else:
                flash("Wrong Password - Try again!!!")
        else:
            flash("The Username Is Wrong!!!")

    return render_template("login.html", form=form)

# create Logout page
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    flash("You have been loged out!!")
    return redirect(url_for("login"))
# Create Dashboard Page
@app.route("/dashboard", methods=["POST", "GET"])
# Down below the decorated function defines that we have to be logged in to get to the Dashboard page
@login_required
def dashboard():
    # name = request.args.get("name")
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favourite_color = request.form["favourite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User updated successully!")
            # return render_template("update.html", form=form, name_to_update=name_to_update)
            return redirect(url_for("dashboard"))
        except:
            flash("Error, looks like there was a problem!!")
            return render_template("dashboard.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("dashboard.html", form=form, name_to_update=name_to_update)

    # return render_template("dashboard.html")

# Add User Page
@app.route("/user/add", methods=["GET", "POST"])
def addUser():
    name = None
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email = form.email.data).first()
        if user is None:
            # hashing the password
            hash_pw = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username = form.username.data,
                        name= form.name.data,
                         email = form.email.data,
                         favourite_color = form.favourite_color.data,
                         password_hash = hash_pw)
            db.session.add(user);
            db.session.commit();

        name = form.name.data;
        form.username.data = ""
        form.name.data = ""
        form.email.data=""
        form.favourite_color.data=""
        form.password_hash.data=""
        form.password_hash2.data=""
        flash("User Added Successfully!")


    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html", form = form, name=name, our_users = our_users)
# Add Post Page

@app.route("/add-post", methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = BlogPost(
            title = form.title.data,
            content = form.content.data,
            author = form.author.data,
            slug = form.slug.data
        )
        # Clear the form
        form.title.data=""
        form.content.data=""
        form.author.data=""
        form.slug.data=""
        # Add post to the Database
        db.session.add(post)
        db.session.commit()
        # Return a Message
        flash("Blog Post Submited Successfully!")
    # Getting the post back
    #     posts = BlogPost.query.order_by(BlogPost.date_posted)
        return redirect(url_for("add_post"))
    posts = BlogPost.query.order_by(BlogPost.date_posted)
    # Redirect the Web Page
    return render_template("add_post.html", form=form, posts = posts)

# Show The Posts
@app.route("/posts")
def posts():
    posts = BlogPost.query.order_by(BlogPost.date_posted)
    return render_template("posts.html",posts=posts)

# Show the entire post
@app.route("/post/<int:id>")
def post(id):
    post = BlogPost.query.get_or_404(id)
    return render_template("show_post.html", post=post)

# Edit post
@app.route("/posts/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_post(id):
    post = BlogPost.query.get_or_404(id)
    form = PostForm(
        title=post.title,
        author=post.author,
        slug=post.slug,
        content = post.content
    )
    if form.validate_on_submit():
        post.title = form.title.data
        post.author = form.author.data
        post.slug = form.slug.data
        post.content = form.content.data
#       Update to database
#         db.session.add(post)
        db.session.commit()
        flash("Post has been updated!")
        return redirect(url_for("post", id=id))
    return render_template("edit_post.html", form=form, post=post)
# Delete the post
@app.route("/post/delete/<int:id>")
@login_required
def delete(id):
    post = BlogPost.query.get_or_404(id)
    try:
        db.session.delete(post)
        db.session.commit()
        flash("Post has been deleted!")
    except:
        flash("Opps, there was a problem deleting the post, try again....")
        return redirect(url_for("posts"))

    return redirect(url_for("posts"))


# Update Database Record

@app.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form["name"]
        name_to_update.email = request.form["email"]
        name_to_update.favourite_color= request.form["favourite_color"]
        name_to_update.username = request.form["username"]
        try:
            db.session.commit()
            flash("User updated successully!")
            # return render_template("update.html", form=form, name_to_update=name_to_update)
            return redirect(url_for("addUser"))
        except:
            flash("Error, looks like there was a problem!!")
            return render_template("update.html", form=form, name_to_update=name_to_update)
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update)
# Deleting the user
@app.route("/delete/<int:id>", methods=["GET", "POST"])
@login_required
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    db.session.delete(user_to_delete)
    db.session.commit()
    flash("User Deleted Successfully!!")
    return redirect(url_for("addUser"))
# Displaying the Name we put in - this is just a demo how to pass data
@app.route("/name/<name>")
def user(name):
    return render_template("user.html", name=name)


# Create password page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        # Clear the form
        form.email.data = ""
        form.password.data=""
        # Lookup user by email
        pw_to_check = Users.query.filter_by(email=email).first()
    #     Check hashed password
        if pw_to_check:

            passed = check_password_hash(pw_to_check.password_hash,password)
        else:
            passed = "No Such User In the Database!!"




    return render_template("test_pw.html", form=form, email=email, password=password, pw_to_check=pw_to_check, passed=passed)
# Create Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    form = NamerForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
        flash("Form Submitted Successfully!")
    return render_template("name.html", form=form, name=name)

# Creating custom error pages

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

# Internal Server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)

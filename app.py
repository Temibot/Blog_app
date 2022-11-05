from flask import Flask, render_template, url_for, request, redirect, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, login_user, logout_user, current_user, LoginManager

from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(base_dir, 'database.sqlite')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False



db = SQLAlchemy(app)

class User(db.Model):  # type: ignore
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False, unique=False)
    last_name = db.Column(db.String(255), nullable=False, unique=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=False, unique=False)
    email = db.Column(db.String(255), nullable=False, unique=False)
    password_hash = db.Column(db.Text(), nullable=False)
    # blog = db.relationship('Blog', backref='post')

    def __repr__(self):
        return f"User ('{self.username}')"



class Blog(db.Model):  # type: ignore
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, unique=False)
    content = db.Column(db.String(255), nullable=False, unique=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # blog_id = db.relationship('Blog', db.ForeignKey('user.id'))

    # def __repr__(self) -> str:
    #     return super().__repr__()

    def __repr__(self):
        return f"Blog ({self.title}, {self.date_posted})"

    


@app.route('/')
def index():
    blogs = Blog.query.all()

    context = {
        'blogs': blogs
    } 
     
    #This should be the home page where all the blog posts will show
    #If logged in or otherwise
    return render_template('index.html', **context, current_time = datetime.utcnow())
    

@app.route('/signup', methods= ['GET', 'POST'])
def register():

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        username = request.form.get('username')
        age = request.form.get('age')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        firstName = User.query.filter_by(first_name=first_name).first()
        if firstName:
            return redirect(url_for('register'))

        lastName = User.query.filter_by(last_name=last_name).first()
        if lastName:
            return redirect(url_for('register'))

        userName = User.query.filter_by(username=username).first()
        if userName:
            return redirect(url_for('register'))

        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return redirect(url_for('register'))

        #To encrypt the password written by the user
        password_hash = generate_password_hash(password)  # type: ignore

        new_user = User(first_name=first_name, last_name=last_name, username=username, age=age, email=email, password_hash=password_hash)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):  # type: ignore
        login_user(user)
        # flash('you are logged in')
        return redirect(url_for('post_blog'))

    # flash('Invalid username or password.')

    return render_template('login.html')



@app.route('/logout')
@login_required
def logout():  
    logout_user()
    return redirect(url_for('index'))

#To handle the posting of blogs
@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_blog():
    # let there be a code that will post and add blog post on home page - index
    #  and the time.. maybe using JAVASCRIPT SHA

    if request.method == 'POST':
        title = request.form.get('title')
        content  = request.form.get('content')
        date_posted = datetime.utcnow()

        title = Blog.query.filter_by(title=title).first()
        if title:
            return redirect(url_for('post_blog'))

        content = Blog.query.filter_by(content=content).first()
        if content:
            return redirect(url_for('post_blog'))

        new_blog = Blog(title=title, content=content, user=current_user)

        db.session.add(new_blog)
        db.session.commit()
        flash('Your post has been created', 'success')

        return redirect(url_for('index'))

    return render_template('write_post.html', user=current_user )

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post_update = Blog.query.get_or_404(id)
    if request.method == 'POST':
        post_update.title = request.form.get('titel')
        post_update.content = request.form.get('content')

        db.session.commit() 
        return redirect(url_for('index'))

    context = {
        'user': post_update
    }

    # return render_template("update.html",  **context)

    return render_template('write_post.html', **context)


#for the delete button
@app.route('/post/<int:post_id>/delete/', methods=['GET'])
def delete_post(id):
    post_to_delete = Blog.query.get_or_404(id)

    db.session.delete(post_to_delete)
    db.session.commit()

    return redirect(url_for('index'))
  

#Update route
# @app.route('/update/<int:id>/', methods=['GET', 'POST'])
# def update(id):
#     user_to_update = User.query.get_or_404(id) 
#     # the get_or_404 means to get an id or if its absent, send 404 error message

#     if request.method == 'POST':
#         user_to_update.username = request.form.get('username')
#         user_to_update.email = request.form.get('email')
#         user_to_update.age = request.form.get('age')
#         user_to_update.gender = request.form.get('gender')

#         db.session.commit() 
#         #we didnt do the db.session.add cos it will just create a new db-stuff instead of updating what we want

#         return redirect(url_for('index'))

#     context = {
#         'user': user_to_update
#     }

#     return render_template("update.html",  **context)
    

@app.route('/about')
def about():

    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__=='__main__':
    app.run(debug=True)
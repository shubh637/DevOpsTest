# Flask Web Development Guide

## Table of Contents
1. [Introduction to Flask](#introduction-to-flask)
2. [Setting Up Development Environment](#setting-up-development-environment)
3. [Creating Your First Flask App](#creating-your-first-flask-app)
4. [Blueprint Architecture](#blueprint-architecture)
5. [Database Setup with SQLAlchemy](#database-setup-with-sqlalchemy)
6. [User Authentication](#user-authentication)
7. [CRUD Operations](#crud-operations)
8. [Flash Messages](#flash-messages)
9. [Pagination](#pagination)
10. [RESTful APIs](#restful-apis)

---

## Introduction to Flask <a name=""introduction-to-flask""></a>

Flask is a lightweight web application framework designed for quick development with the ability to scale up to complex applications. It provides simplicity and flexibility for web development.

---

## Setting Up Development Environment <a name=""setting-up-development-environment""></a>

### Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment (Mac/Linux)
source venv/bin/activate

# Activate virtual environment (Windows)
venv\Scripts\activate
```

### Install Dependencies
```bash
# Install Flask
pip install Flask

# Install from requirements.txt
pip install -r requirements.txt
```

---

## Creating Your First Flask App <a name=""creating-your-first-flask-app""></a>

### Basic Application Structure
```python
# __init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    return app
```

### Running the Application
```bash
export FLASK_APP=app_name
flask run
```

---

## Blueprint Architecture <a name=""blueprint-architecture""></a>

Blueprints help organize your app into smaller, manageable components.

### Main Blueprint
```python
# main.py
from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return ""Hello World""

@main.route('/profile')
def profile():
    return ""Profile Page""
```

### Auth Blueprint
```python
# auth.py
from flask import Blueprint

auth = Blueprint('auth', __name__)

@auth.route('/signup')
def signup():
    return ""Signup Page""

@auth.route('/login')
def login():
    return ""Login Page""

@auth.route('/logout')
def logout():
    return ""Logout Page""
```

### Registering Blueprints
```python
# __init__.py
from flask import Flask
from main import main as main_blueprint
from auth import auth as auth_blueprint

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    
    return app
```

---

## Database Setup with SQLAlchemy <a name=""database-setup-with-sqlalchemy""></a>

### Configuration
```python
# config.py
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'dev-secret-key'  # Change during deployment
```

### Database Initialization
```python
# __init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Import models
    from app import models
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app
```

### User Model
```python
# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # Relationship with workouts
    workouts = db.relationship('Workout', backref='author', lazy=True)
```

### Workout Model
```python
# models.py
class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pushups = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

---

## User Authentication <a name=""user-authentication""></a>

### Login Setup
```python
# __init__.py
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    # ... other configurations
    
    login_manager.init_app(app)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

### User Registration
```python
# auth.py
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from app import db
from app.models import User

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exists')
            return redirect(url_for('auth.signup'))
        
        # Create new user
        new_user = User(
            name=name, 
            email=email, 
            password=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully')
        return redirect(url_for('auth.login'))
    
    return render_template('signup.html')
```

### User Login
```python
# auth.py
from flask_login import login_user
from werkzeug.security import check_password_hash

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=remember)
        return redirect(url_for('main.profile', name=user.name))
    
    return render_template('login.html')
```

### Protected Routes
```python
from flask_login import login_required

@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
```

### Logout
```python
from flask_login import logout_user, login_required

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
```

---

## CRUD Operations <a name=""crud-operations""></a>

### Create Workout
```python
# main.py
@main.route('/workout/new', methods=['GET', 'POST'])
@login_required
def new_workout():
    if request.method == 'POST':
        pushups = request.form.get('pushups')
        comment = request.form.get('comment')
        
        workout = Workout(
            pushups=pushups, 
            comment=comment, 
            author=current_user
        )
        
        db.session.add(workout)
        db.session.commit()
        
        flash('Workout created successfully')
        return redirect(url_for('main.workouts'))
    
    return render_template('create_workout.html')
```

### Read Workouts
```python
@main.route('/workouts')
@login_required
def workouts():
    user_workouts = Workout.query.filter_by(author=current_user).all()
    return render_template('workouts.html', workouts=user_workouts)
```

### Update Workout
```python
@main.route('/workout/<int:workout_id>/update', methods=['GET', 'POST'])
@login_required
def update_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    
    if workout.author != current_user:
        abort(403)
    
    if request.method == 'POST':
        workout.pushups = request.form.get('pushups')
        workout.comment = request.form.get('comment')
        
        db.session.commit()
        flash('Workout updated successfully')
        return redirect(url_for('main.workouts'))
    
    return render_template('update_workout.html', workout=workout)
```

### Delete Workout
```python
@main.route('/workout/<int:workout_id>/delete', methods=['POST'])
@login_required
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    
    if workout.author != current_user:
        abort(403)
    
    db.session.delete(workout)
    db.session.commit()
    
    flash('Workout deleted successfully')
    return redirect(url_for('main.workouts'))
```

---

## Flash Messages <a name=""flash-messages""></a>

### Displaying Flash Messages
```html
<!-- In your base template -->
{% with messages = get_flashed_messages() %}
  {% if messages %}
    {% for message in messages %}
      <p class=""flash"">{{ message }}</p>
    {% endfor %}
  {% endif %}
{% endwith %}
```

### Creating Flash Messages
```python
from flask import flash

flash('Your message here', 'category')  # Category is optional
```

---

## Pagination <a name=""pagination""></a>

### Implementing Pagination
```python
@main.route('/workouts')
@login_required
def workouts():
    page = request.args.get('page', 1, type=int)
    workouts = Workout.query.filter_by(author=current_user)\
        .order_by(Workout.date_created.desc())\
        .paginate(page=page, per_page=5)
    
    return render_template('workouts.html', workouts=workouts)
```

### Pagination in Templates
```html
{% if workouts.pages > 1 %}
  <div class=""pagination"">
    {% for page_num in workouts.iter_pages(left_edge=1, right_edge=1, left_current=1, right_current=2) %}
      {% if page_num %}
        {% if workouts.page == page_num %}
          <a class=""active"" href=""{{ url_for('main.workouts', page=page_num) }}"">{{ page_num }}</a>
        {% else %}
          <a href=""{{ url_for('main.workouts', page=page_num) }}"">{{ page_num }}</a>
        {% endif %}
      {% else %}
        <span>...</span>
      {% endif %}
    {% endfor %}
  </div>
{% endif %}
```

---

## RESTful APIs <a name=""restful-apis""></a>

### Installing Flask-RESTful
```bash
pip install flask-restful
```

### Basic API Setup
```python
# __init__.py
from flask_restful import Api

def create_app():
    app = Flask(__name__)
    api = Api(app)
    
    # Add resources
    from app.api import HelloWorld, HelloName
    api.add_resource(HelloWorld, '/api/helloworld')
    api.add_resource(HelloName, '/api/helloworld/<string:name>')
    
    return app
```

### Simple API Resources
```python
# api.py
from flask_restful import Resource

class HelloWorld(Resource):
    def get(self):
        return {'data': 'Hello World'}

class HelloName(Resource):
    def get(self, name):
        return {'data': f'Hello, {name}'}
```

### Advanced API with Request Parsing
```python
from flask_restful import reqparse, abort, fields, marshal_with

# Request parser for POST
task_post_args = reqparse.RequestParser()
task_post_args.add_argument('task', type=str, required=True, help='Task is required')
task_post_args.add_argument('summary', type=str, required=True, help='Summary is required')

# Request parser for PUT
task_put_args = reqparse.RequestParser()
task_put_args.add_argument('task', type=str)
task_put_args.add_argument('summary', type=str)

# Response fields
resource_fields = {
    'id': fields.Integer,
    'task': fields.String,
    'summary': fields.String
}

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        todo = ToDoModel.query.get(todo_id)
        if not todo:
            abort(404, message=""Task not found"")
        return todo
    
    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        
        # Check if todo exists
        todo = ToDoModel.query.get(todo_id)
        if todo:
            abort(409, message=""Task ID already exists"")
        
        # Create new todo
        new_todo = ToDoModel(
            id=todo_id, 
            task=args['task'], 
            summary=args['summary']
        )
        
        db.session.add(new_todo)
        db.session.commit()
        return new_todo, 201
    
    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        todo = ToDoModel.query.get(todo_id)
        
        if not todo:
            abort(404, message=""Task doesn't exist"")
        
        if args['task']:
            todo.task = args['task']
        if args['summary']:
            todo.summary = args['summary']
        
        db.session.commit()
        return todo
    
    def delete(self, todo_id):
        todo = ToDoModel.query.get(todo_id)
        if not todo:
            abort(404, message=""Task doesn't exist"")
        
        db.session.delete(todo)
        db.session.commit()
        return '', 204
```

---

## Conclusion

This guide covers the essential aspects of Flask web development, from basic setup to advanced features like RESTful APIs. Use this as a reference for your Flask projects, and customize the code according to your specific needs.

Remember to always:
- Use environment variables for sensitive data
- Validate user input
- Handle errors appropriately
- Test your application thoroughly

Happy coding with Flask!"  root    1    3  4  3  5  deepseek-chat  2025-09-09T17:51:48.451000+08:00  RESPONSE  "
Of course. I will convert your handwritten notes into a structured, digital PDF guide. This guide is designed to be practical, with clear code snippets you can easily copy and use.

***

# Flask Web Development Guide

**From Notes to Code**

---

## Table of Contents

1.  **Introduction & Setup**
    *   What is Flask?
    *   Virtual Environment Setup
    *   Installing Dependencies

2.  **Core Application Structure**
    *   Creating Your First App (`__init__.py`)
    *   Running the Application

3.  **Organizing with Blueprints**
    *   Main Blueprint (`main.py`)
    *   Auth Blueprint (`auth.py`)
    *   Registering Blueprints

4.  **Database Management with SQLAlchemy**
    *   Configuration (`config.py`)
    *   Initialization & Models (`models.py`)
    *   Creating Tables

5.  **User Authentication**
    *   Login Manager Setup
    *   User Registration
    *   User Login & Logout
    *   Protecting Routes

6.  **CRUD Operations**
    *   Creating Records
    *   Reading & Displaying Records
    *   Updating Records
    *   Deleting Records

7.  **User Feedback & Interface**
    *   Flash Messages
    *   Pagination

8.  **Building RESTful APIs**
    *   Flask-RESTful Setup
    *   Basic API Endpoints
    *   Request Parsing
    *   Full CRUD API with Marshalling

---

### 1. Introduction & Setup

**What is Flask?**
Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.

**Virtual Environment Setup**
A virtual environment is crucial to manage dependencies for your project separately.

```bash
# Create the virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
.\venv\Scripts\activate
```

**Installing Dependencies**
With your virtual environment activated, install Flask and other packages.

```bash
# Install Flask
pip install Flask

# Install common Flask extensions
pip install Flask-SQLAlchemy Flask-Login Flask-RESTful

# To save your dependencies to a file
pip freeze > requirements.txt

# To install from a requirements file
pip install -r requirements.txt
```

---

### 2. Core Application Structure

This is the foundation of your Flask app, typically in an `app/__init__.py` file. This ""Application Factory"" pattern keeps things clean and configurable.

**`app/__init__.py`**

```python
from flask import Flask

# Create the application factory function
def create_app():
    app = Flask(__name__)

    # Set a secret key for session management
    app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change for production!

    return app
```

**Running the Application**
Create a main entry point for your app, e.g., `run.py` in the root directory.

**`run.py`**
```python
from app import create_app

"  5  4  6  deepseek-chat  2025-09-09T17:52:34.160000+08:00  REQUEST  Pdf so I can download it  7  6  8  deepseek-chat  2025-09-09T22:42:53.855000+08:00  REQUEST  make me.py file with this  8  7    deepseek-chat  2025-09-09T22:42:53.855000+08:00  RESPONSE  "
I'll create a complete Flask application based on your notes with all the components organized into proper files.

Here's the file structure we'll create:
```
/flask-app
  /app
    /templates
    /static
    __init__.py
    models.py
    routes.py
    forms.py
    config.py
  /migrations
  run.py
  requirements.txt
```

Let me create each file:

### 1. requirements.txt
```txt
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.2
Flask-WTF==1.1.1
Flask-Migrate==4.0.5
Flask-RESTful==0.3.10
Werkzeug==2.3.7
email-validator==2.0.0
```

### 2. config.py
```python
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

### 3. app/__init__.py
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restful import Api
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
"  10  9  13  deepseek-chat  2025-09-09T22:49:14.742000+08:00  RESPONSE  "
# Flask Web Development Guide
## Complete Reference from Basic Setup to Advanced APIs

This Jupyter Notebook provides a comprehensive guide to Flask web development, from basic setup to advanced API development. You can run the code cells to see Flask in action.

## Table of Contents
1. [Introduction to Flask](#1)
2. [Environment Setup](#2)
3. [Basic Flask Application Structure](#3)
4. [Blueprint Architecture](#4)
5. [Database Setup with SQLAlchemy](#5)
6. [User Authentication System](#6)
7. [CRUD Operations Implementation](#7)
8. [Flash Messages](#8)
9. [Pagination System](#9)
10. [RESTful API Development](#10)
11. [Advanced API Features](#11)

<a id='1'></a>
## 1. Introduction to Flask

Flask is a lightweight WSGI web application framework. It is designed to make getting started quick and easy, with the ability to scale up to complex applications.

```python
# Let's start by importing Flask
from flask import Flask
```

<a id='2'></a>
## 2. Environment Setup

First, let's set up a virtual environment and install Flask. Run these commands in your terminal, not in this notebook:

```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install Flask
pip install Flask
```

For this notebook, we'll install Flask directly:

```python
# Install Flask if not already installed
!pip install flask
```

<a id='3'></a>
## 3. Basic Flask Application Structure

Let's create a minimal Flask application:

```python
from flask import Flask

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About Page'

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
```

However, in a Jupyter notebook, we need to run Flask differently:

```python
from flask import Flask
import threading
import time

# Create Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    return ""Hello, World!""

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()

# Give the server a moment to start
time.sleep(1)

print(""Flask server is running at http://localhost:5000"")
```

<a id='4'></a>
## 4. Blueprint Architecture

Blueprints help organize your application into reusable components.

```python
from flask import Blueprint, Flask

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Define routes for blueprints
@main_bp.route('/')
def index():
    return ""Main Page""

@main_bp.route('/profile')
def profile():
    return ""Profile Page""

@auth_bp.route('/login')
def login():
    return ""Login Page""

@auth_bp.route('/signup')
def signup():
    return ""Signup Page""

# Create app and register blueprints
app = Flask(__name__)
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)

# Test the routes
with app.test_client() as client:
    print(""Testing routes:"")
    print(""Main page:"", client.get('/').get_data(as_text=True))
    print(""Profile page:"", client.get('/profile').get_data(as_text=True))
    print(""Login page:"", client.get('/auth/login').get_data(as_text=True))
    print(""Signup page:"", client.get('/auth/signup').get_data(as_text=True))
```

<a id='5'></a>
## 5. Database Setup with SQLAlchemy

Let's set up a database with SQLAlchemy:

```python
!pip install flask-sqlalchemy

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Create Flask app
app = Flask(__name__)

# Configure database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'

# Define Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'

# Create tables
with app.app_context():
    db.create_all()
    
print(""Database setup complete!"")
```

<a id='6'></a>
## 6. User Authentication System

Let's implement a basic authentication system:

```python
!pip install flask-login werkzeug

from flask import Flask, render_template_string, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# HTML templates as strings
login_template = """"""
<h2>Login</h2>
<form method=""post"">
    <p>Username: <input type=""text"" name=""username""></p>
    <p>Password: <input type=""password"" name=""password""></p>
    <p><input type=""submit"" value=""Login""></p>
</form>
<p><a href=""{{ url_for('register') }}"">Register</a></p>
""""""

register_template = """"""
<h2>Register</h2>
<form method=""post"">
    <p>Username: <input type=""text"" name=""username""></p>
    <p>Email: <input type=""email"" name=""email""></p>
    <p>Password: <input type=""password"" name=""password""></p>
    <p><input type=""submit"" value=""Register""></p>
</form>
<p><a href=""{{ url_for('login') }}"">Login</a></p>
""""""

profile_template = """"""
<h2>Profile</h2>
<p>Welcome, {{ current_user.username }}!</p>
<p><a href=""{{ url_for('logout') }}"">Logout</a></p>
""""""

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('profile'))
    return render_template_string(login_template)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(register_template)

@app.route('/profile')
@login_required
def profile():
    return render_template_string(profile_template)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Test the authentication system
with app.test_client() as client:
    # Create a test user
    with app.app_context():
        test_user = User(username='testuser', email='test@example.com')
        test_user.set_password('testpassword')
        db.session.add(test_user)
        db.session.commit()
    
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    print(""Login test:"", ""Success"" if response.status_code == 200 else ""Failed"")
    
    # Test accessing protected route
    response = client.get('/profile', follow_redirects=True)
    print(""Profile access test:"", ""Success"" if response.status_code == 200 else ""Failed"")
```

<a id='7'></a>
## 7. CRUD Operations Implementation

Let's implement CRUD (Create, Read, Update, Delete) operations:

```python
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

# Create Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<Post {self.title}>'

# Create tables
with app.app_context():
    db.create_all()

# HTML templates
post_list_template = """"""
<h2>Posts</h2>
<ul>
{% for post in posts %}
    <li>
        <a href=""{{ url_for('view_post', post_id=post.id) }}"">{{ post.title }}</a>
        <a href=""{{ url_for('edit_post', post_id=post.id) }}"">Edit</a>
        <form action=""{{ url_for('delete_post', post_id=post.id) }}"" method=""post"" style=""display:inline;"">
            <button type=""submit"">Delete</button>
        </form>
    </li>
{% endfor %}
</ul>
<a href=""{{ url_for('create_post') }}"">Create New Post</a>
""""""

post_form_template = """"""
<h2>{{ action }} Post</h2>
<form method=""post"">
    <p>Title: <input type=""text"" name=""title"" value=""{{ post.title if post else '' }}""></p>
    <p>Content: <textarea name=""content"">{{ post.content if post else '' }}</textarea></p>
    <p><input type=""submit"" value=""Save""></p>
</form>
<a href=""{{ url_for('list_posts') }}"">Back to Posts</a>
""""""

post_detail_template = """"""
<h2>{{ post.title }}</h2>
<p>{{ post.content }}</p>
<a href=""{{ url_for('edit_post', post_id=post.id) }}"">Edit</a>
<form action=""{{ url_for('delete_post', post_id=post.id) }}"" method=""post"" style=""display:inline;"">
    <button type=""submit"">Delete</button>
</form>
<br>
<a href=""{{ url_for('list_posts') }}"">Back to Posts</a>
""""""

# Routes
@app.route('/')
def list_posts():
    posts = Post.query.all()
    return render_template_string(post_list_template, posts=posts)

@app.route('/post/new', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post = Post(title=title, content=content)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('list_posts'))
    return render_template_string(post_form_template, action='Create')

@app.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template_string(post_detail_template, post=post)

@app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()
        return redirect(url_for('list_posts'))
    return render_template_string(post_form_template, action='Edit', post=post)

@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('list_posts'))

# Test CRUD operations
with app.test_client() as client:
    # Create a post
    response = client.post('/post/new', data={
        'title': 'Test Post',
        'content': 'This is a test post.'
    }, follow_redirects=True)
    print(""Create post test:"", ""Success"" if response.status_code == 200 else ""Failed"")
    
    # Read posts
    response = client.get('/')
    print(""Read posts test:"", ""Success"" if response.status_code == 200 else ""Failed"")
    
    # Update a post
    response = client.post('/post/1/edit', data={
        'title': 'Updated Post',
        'content': 'This post has been updated.'
    }, follow_redirects=True)
    print(""Update post test:"", ""Success"" if response.status_code == 200 else ""Failed"")
    
    # Delete a post
    response = client.post('/post/1/delete', follow_redirects=True)
    print(""Delete post test:"", ""Success"" if response.status_code == 200 else ""Failed"")
```

<a id='8'></a>
## 8. Flash Messages

Let's implement flash messages for user feedback:

```python
from flask import Flask, render_template_string, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flash-secret-key'

# HTML template with flash messages
flash_template = """"""
<h2>Flash Messages Demo</h2>
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        <ul>
        {% for category, message in messages %}
            <li class=""{{ category }}"">{{ message }}</li>
        {% endfor %}
        </ul>
    {% endif %}
{% endwith %}
<form method=""post"">
    <p>Message: <input type=""text"" name=""message""></p>
    <p>Category: 
        <select name=""category"">
            <option value=""success"">Success</option>
            <option value=""info"">Info</option>
            <option value=""warning"">Warning</option>
            <option value=""error"">Error</option>
        </select>
    </p>
    <p><input type=""submit"" value=""Flash Message""></p>
</form>
""""""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        message = request.form['message']
        category = request.form['category']
        flash(message, category)
        return redirect(url_for('index'))
    return render_template_string(flash_template)

# Test flash messages
with app.test_client() as client:
    response = client.post('/', data={
        'message': 'This is a success message!',
        'category': 'success'
    }, follow_redirects=True)
    print(""Flash message test:"", ""Success"" if response.status_code == 200 else ""Failed"")
```

<a id='9'></a>
## 9. Pagination System

Let's implement pagination for handling large datasets:

```python
from flask import Flask, render_template_string, request
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Item model
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f'<Item {self.name}>'

# Create tables and sample data
with app.app_context():
    db.create_all()
    
    # Create sample items if none exist
    if Item.query.count() == 0:
        for i in range(50):
            name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            item = Item(name=name)
            db.session.add(item)
        db.session.commit()

# Pagination template
pagination_template = """"""
<h2>Items (Page {{ items.page }})</h2>
<ul>
{% for item in items.items %}
    <li>{{ item.name }}</li>
{% endfor %}
</ul>

<!-- Pagination controls -->
<div class=""pagination"">
    {% if items.has_prev %}
        <a href=""{{ url_for('list_items', page=items.prev_num) }}"">Previous</a>
    {% endif %}
    
    {% for page_num in items.iter_pages(left_edge=2, right_edge=2, left_current=2, right_current=2) %}
        {% if page_num %}
            {% if items.page == page_num %}
                <a href=""{{ url_for('list_items', page=page_num) }}"" class=""active"">{{ page_num }}</a>
            {% else %}
                <a href=""{{ url_for('list_items', page=page_num) }}"">{{ page_num }}</a>
            {% endif %}
        {% else %}
            <span>...</span>
        {% endif %}
    {% endfor %}
    
    {% if items.has_next %}
        <a href=""{{ url_for('list_items', page=items.next_num) }}"">Next</a>
    {% endif %}
</div>

<p>Showing {{ items.items|length }} of {{ items.total }} items</p>
""""""

@app.route('/')
def list_items():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    items = Item.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template_string(pagination_template, items=items)

# Test pagination
with app.test_client() as client:
    response = client.get('/')
    print(""Pagination test:"", ""Success"" if response.status_code == 200 else ""Failed"")
    
    response = client.get('/?page=2')
    print(""Page 2 test:"", ""Success"" if response.status_code == 200 else ""Failed"")
```

<a id='10'></a>
## 10. RESTful API Development

Let's create a RESTful API using Flask:

```python
!pip install flask-restful

from flask import Flask, request
from flask_restful import Api, Resource, abort, reqparse
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Task model
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description
        }

# Create tables
with app.app_context():
    db.create_all()

# Request parsers
task_parser = reqparse.RequestParser()
task_parser.add_argument('title', type=str, required=True, help='Title is required')
task_parser.add_argument('description', type=str)

# Task resource
class TaskResource(Resource):
    def get(self, task_id):
        task = Task.query.get_or_404(task_id)
        return task.to_dict()
    
    def put(self, task_id):
        task = Task.query.get_or_404(task_id)
        args = task_parser.parse_args()
        task.title = args['title']
        task.description = args['description']
        db.session.commit()
        return task.to_dict()
    
    def delete(self, task_id):
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        return {'message': 'Task deleted successfully'}

# Task list resource
class TaskListResource(Resource):
    def get(self):
        tasks = Task.query.all()
        return {'tasks': [task.to_dict() for task in tasks]}
    
    def post(self):
        args = task_parser.parse_args()
        task = Task(title=args['title'], description=args['description'])
        db.session.add(task)
        db.session.commit()
        return task.to_dict(), 201

# Add resources to API
api.add_resource(TaskListResource, '/api/tasks')
api.add_resource(TaskResource, '/api/tasks/<int:task_id>')

# Test the API
with app.test_client() as client:
    # Create a task
    response = client.post('/api/tasks', json={
        'title': 'Test Task',
        'description': 'This is a test task'
    })
    print(""Create task API test:"", response.status_code, response.get_json())
    
    # Get all tasks
    response = client.get('/api/tasks')
    print(""Get tasks API test:"", response.status_code, response.get_json())
    
    # Get a specific task
    response = client.get('/api/tasks/1')
    print(""Get task API test:"", response.status_code, response.get_json())
    
    # Update a task
    response = client.put('/api/tasks/1', json={
        'title': 'Updated Task',
        'description': 'This task has been updated'
    })
    print(""Update task API test:"", response.status_code, response.get_json())
    
    # Delete a task
    response = client.delete('/api/tasks/1')
    print(""Delete task API test:"", response.status_code, response.get_json())
```

<a id='11'></a>
## 11. Advanced API Features

Let's implement advanced API features like request parsing and response marshalling:

```python
from flask import Flask
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
api = Api(app)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    in_stock = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Product {self.name}>'

# Create tables
with app.app_context():
    db.create_all()

# Response marshalling
product_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'in_stock': fields.Boolean,
    'url': fields.Url('product', absolute=True)
}

# Request parsers
product_parser = reqparse.RequestParser()
product_parser.add_argument('name', type=str, required=True, help='Name is required')
product_parser.add_argument('price', type=float, required=True, help='Price is required')
product_parser.add_argument('in_stock', type=bool, default=True)

# Product resource
class ProductResource(Resource):
    @marshal_with(product_fields)
    def get(self, product_id):
        product = Product.query.get_or_404(product_id)
        return product
    
    @marshal_with(product_fields)
    def put(self, product_id):
        product = Product.query.get_or_404(product_id)
        args = product_parser.parse_args()
        product.name = args['name']
        product.price = args['price']
        product.in_stock = args['in_stock']
        db.session.commit()
        return product
    
    def delete(self, product_id):
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return {'message': 'Product deleted successfully'}

# Product list resource
class ProductListResource(Resource):
    @marshal_with(product_fields)
    def get(self):
        products = Product.query.all()
        return products
    
    @marshal_with(product_fields)
    def post(self):
        args = product_parser.parse_args()
        product = Product(
            name=args['name'],
            price=args['price'],
            in_stock=args['in_stock']
        )
        db.session.add(product)
        db.session.commit()
        return product, 201

# Add resources to API
api.add_resource(ProductListResource, '/api/products')
api.add_resource(ProductResource, '/api/products/<int:product_id>')

# Test the advanced API
with app.test_client() as client:
    # Create a product
    response = client.post('/api/products', json={
        'name': 'Test Product',
        'price': 9.99,
        'in_stock': True
    })
    print(""Create product API test:"", response.status_code, response.get_json())
    
    # Get all products
    response = client.get('/api/products')
    print(""Get products API test:"", response.status_code, response.get_json())
    
    # Get a specific product
    response = client.get('/api/products/1')
    print(""Get product API test:"", response.status_code, response.get_json())
    
    # Update a product
    response = client.put('/api/products/1', json={
        'name': 'Updated Product',
        'price': 19.99,
        'in_stock': False
    })
    print(""Update product API test:"", response.status_code, response.get_json())
    
    # Delete a product
    response = client.delete('/api/products/1')
    print(""Delete product API test:"", response.status_code, response.get_json())
```

## Conclusion

This Jupyter Notebook has demonstrated the key concepts of Flask web development, from basic setup to advanced API features. You can use this as a reference for your Flask projects.

To use this code in a real Flask application:
1. Create separate files for models, routes, and other components
2. Use proper HTML templates instead of template strings
3. Add error handling and validation
4. Implement proper authentication and authorization
5. Use environment variables for configuration

Remember to always:
- Validate user input
- Handle errors appropriately
- Use secure practices for authentication
- Test your application thoroughly

Happy coding with Flask!"                13  10  14  deepseek-chat  2025-09-09T23:40:26.805000+08:00  REQUEST  Can you make the proper GitHub readme including # and ###  14  13  15  deepseek-chat  2025-09-09T23:40:26.805000+08:00  RESPONSE  "
# Flask Web Development Guide 🚀

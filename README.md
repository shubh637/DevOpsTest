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

Happy coding with Flask!"  
    

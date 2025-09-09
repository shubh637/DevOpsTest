
from flask import Flask, abort
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_login import LoginManager
from flask_restful import Resource,Api,reqparse,fields,marshal_with

db=SQLAlchemy()

# class HelloWorld(Resource):
#     def get(self):
#         return {"data":"hello world!"}
    
# class HelloName(Resource):
#     def get(self,name):
#         return {'data':f'hello, {name}'}    
# todos = {
#     1: {"task": "write hello world program", "summary": "write the code using python"},
#     2: {"task": "build a Flask API", "summary": "create a RESTful API using Flask-RESTful"},
#     3: {"task": "test with Postman", "summary": "send requests to your API using Postman to test all CRUD operations"}
# }

task_post_args=reqparse.RequestParser()
task_post_args.add_argument('task',type=str,help='Task is required.',required=True)
task_post_args.add_argument('summary',type=str,help='Summary is required.',required=True)

task_put_args=reqparse.RequestParser()
task_put_args.add_argument('task',type=str)
task_put_args.add_argument('summary',type=str)

class ToDoModel(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    task=db.Column(db.String(200))
    summary=db.Column(db.String(500))


resource_fields={
    "id":fields.Integer,
    "task":fields.String,
    "summary":fields.String
}

class ToDo(Resource):
    @marshal_with(resource_fields)
    def get(self, todo_id):
        todo = ToDoModel.query.get(todo_id)
        if not todo:
            abort(404,"Task not found")
        return todo

    @marshal_with(resource_fields)
    def post(self, todo_id):
        args = task_post_args.parse_args()
        todo = ToDoModel.query.get(todo_id)
        if todo:
            abort(409,"Task already exists")
        
        new_todo = ToDoModel(id=todo_id, task=args['task'], summary=args['summary'])
        db.session.add(new_todo)
        db.session.commit()
        return new_todo, 201

    @marshal_with(resource_fields)
    def put(self, todo_id):
        args = task_put_args.parse_args()
        todo = ToDoModel.query.get(todo_id)
        if not todo:
            abort(404,"Task not found")

        if args['task']:
            todo.task = args['task']
        if args['summary']:
            todo.summary = args['summary']

        db.session.commit()
        return todo

    @marshal_with(resource_fields)
    def delete(self, todo_id):
        todo = ToDoModel.query.get(todo_id)
        if not todo:
            abort(404,"Task not found")
        db.session.delete(todo)
        db.session.commit()
        return '', 204
    
  
class  All_Todo(Resource):
   
    @marshal_with(resource_fields)
    def get(self):
        tasks=ToDoModel.query.all()
        todos={}
        for task in tasks:
            todos[task.id]={'task':task.task,"summary":task.summary}
        return todos    
    
def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)

    #creatign restfull api.
    api=Api(app)
  
    # api.add_resource(HelloWorld, '/helloworld')
    # api.add_resource(HelloName,'/helloworld/<string:name>')#passing the arguments.
    api.add_resource(ToDo,'/todos/<int:todo_id>')
    api.add_resource(All_Todo,"/all-todos")

    db.init_app(app)

    from . import models

    login_manager=LoginManager()
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()



    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app



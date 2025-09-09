from flask import Blueprint, flash, redirect,render_template,url_for,request
from flask_login import login_required,current_user
from .models import User, Workout
from . import db
main=Blueprint("main",__name__)

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/send-data', methods=['POST'])
def receive_data():
    data = request.get_json()
    name = data.get('name')
    age = data.get('age')

    # Pass the data to an HTML page
    return render_template('show_data.html', name=name, age=age)

@main.route("/profile")
@login_required
def profile():
    return render_template("profile.html",name=current_user.name)


@main.route('/new',methods=['GET','POST'])
@login_required
def new_workout():
    if request.method=='POST':
        pushups=request.form.get('pushups') 
        comment=request.form.get('comment')

        workout=Workout(pushups=pushups,comment=comment,author=current_user)
        db.session.add(workout)
        db.session.commit()

        flash('new workout has been added')

        return redirect(url_for('main.user_workouts'))
    else:
        return render_template('create_workout.html')

@main.route("/all")
@login_required
def user_workouts():
    user=User.query.filter_by(email=current_user.email).first_or_404()
    page=request.args.get('page',1,type=int)#taking page number form the url come from the request.
    workouts=Workout.query.filter_by(author=user).paginate(page=page,per_page=3)#per_page=3 means 3 page to show and page means page_number.
    return render_template('all_workouts.html',workouts=workouts,user=user)  #passing workout and user info.  


@main.route('/workout/<int:workout_id>/update',methods=['GET','POST'])
@login_required
def  update_workout(workout_id):
    workout=Workout.query.get_or_404(workout_id)
    if request.method=='POST':
        workout.pushups=request.form.get('pushups')
        workout.comment=request.form.get('comment')
        db.session.commit()
        flash('your workout has been updated!')

        return redirect(url_for('main.user_workouts'))
    else:
        return render_template('update_workout.html',workout=workout)

@main.route('/workout/<int:workout_id>/delete',methods=['GET','POST'])
@login_required
def delete_workout(workout_id):
    workout=Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    flash("your workout has been deleted!")
    db.session.commit()
    return redirect(url_for('main.user_workouts'))



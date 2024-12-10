from flask_migrate import Migrate
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user
from flask_mail import Mail, Message
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

app = Flask(__name__, template_folder = "static/css")
app.config['SECRET_KEY'] = 'habitflowsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 't4416706@gmail.com'
app.config['MAIL_PASSWORD'] = 'agsj lyzs phua pfzm'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
scheduler = BackgroundScheduler()


# User model

class HabitUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable = False)
    password = db.Column(db.String(150), nullable=False)

# Habit model

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    interval = db.Column(db.String(150), nullable=False)
    counter = db.Column(db.Integer, default=0) 
    alert = db.Column(db.String(50), nullable=True)
    last_notified_time = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('habit_user.id'), nullable=False)

# Create database tables

with app.app_context():
    db.create_all()

# Load user when session is active

@login_manager.user_loader
def load_user(user_id):
    return HabitUser.query.get(int(user_id))

#Home page app route
@app.route("/")
def home():
    return render_template('index.html', user=current_user)

#Signup app route

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Does user exist?

        user = HabitUser.query.filter_by(email=email).first()
        if user:
            flash('Sorry, that email address has been taken. Try another one.', 'flash-error')
            return redirect(url_for('signup'))

        # If user doesn't exist, create a new user

        new_user = HabitUser(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account successfully created. Welcome to HabitFlow!', 'flash-success')
        return redirect(url_for('login'))

    return render_template('signup.html')

#Login app route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Email?
        user = HabitUser.query.filter_by(email=email).first()

# If username (email) and password are incorrect, give error message

        if not user or user.password != password:
            flash('Login error. Please check your email and password and try again.', 'flash-error')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('tracker'))

    return render_template('login.html')

#tracker app route
@app.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    if request.method == 'POST':
        data = request.get_json(silent=True)
        habit_name = data.get('habit')
        interval = data.get('interval', 'Daily')
        alert = data.get('alert')
        new_habit = Habit(name=habit_name, interval=interval, alert=alert, user_id=current_user.id)
        db.session.add(new_habit)
        db.session.commit()
        return {"id": new_habit.id}

    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('tracker.html', user=current_user, habits=habits)

#Edit habit app route
@app.route("/edit_habit/<int:habit_id>", methods=['POST'])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    data = request.get_json()  # data includes 'name' and 'interval'

    habit.name = data.get('name', habit.name)
    habit.interval = data.get('interval', habit.interval)
    habit.alert = data.get('alert', habit.alert)
    habit.last_notified_time = False
    db.session.commit()

    flash('Habit updated successfully.', 'flash-success')
    return redirect(url_for('tracker'))

#Delete habit app route
@app.route("/delete_habit/<int:habit_id>", methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    db.session.delete(habit)
    db.session.commit()

    flash('Habit deleted successfully.', 'flash-success')
    return redirect(url_for('tracker'))

#Update habit counter app route (to the server)
@app.route("/update_habit_counter/<int:habit_id>", methods=['POST'])
@login_required
def update_habit_counter(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    data = request.get_json()
    habit.counter = data.get('count', habit.counter)
    db.session.commit()
    return {"success": True}, 200

#Update name (username) of user app route
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    new_name = request.form.get('name')
    if new_name:
        current_user.name = new_name
        db.session.commit()
        flash('Profile updated successfully!', 'flash-success')
    else:
        flash('Name cannot be empty.', 'flash-error')
    return redirect(url_for('tracker'))

# Updates email and password of the user
@app.route('/update_settings', methods=['POST'])
@login_required
def update_settings():
    data = request.json
    new_email = data.get('email')
    new_password = data.get('password')

    if new_email:
        current_user.email = new_email
    if new_password:
        current_user.password = new_password
    db.session.commit()

    return {"success": True}, 200

#Logout app route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# function that calculates alert date and time
def alert_time(interval, alert):
    time_str, days_str = interval.split(' - ')
    habit_time = datetime.strptime(time_str, '%I:%M %p').time()
    alert_map = {
        'None' : timedelta(0),
        "atTime" : timedelta(0),
        "15minbf" : timedelta(minutes=15),
        "30minbf" : timedelta(minutes=30),
        "1hrbf": timedelta(hours=1),
        "2hrbf": timedelta(hours=2),
        "1daybf": timedelta(days=1),
    }
    alert_delta = alert_map.get(alert, timedelta())
    
    day_map = {
        "Sunday": 6, "Monday": 0, "Tuesday": 1, "Wednesday": 2,
        "Thursday": 3, "Friday": 4, "Saturday": 5
    }

    # turns selected days into lists
    days = days_str.split(', ')
    selected_days = [day_map[day] for day in days]

    # get current day of the week 
    now = datetime.now()
    today = now.weekday()

    all_alerts = []
    for day in selected_days:
        count_down_days = (day - today) % 7
        habit_date = now.date() + timedelta(count_down_days)
        original_date = datetime.combine(habit_date, habit_time)
        alert_dates = original_date - alert_delta
        all_alerts.append(alert_dates)
    return all_alerts

# function that sends timed notiification
def send_notification():
    print("Running notification task...")
    with app.app_context():
        curr_time = datetime.now().replace(second=0, microsecond=0)
        habits = Habit.query.all()
        for habit in habits:
            all_alerts = alert_time(habit.interval, habit.alert)
            for alert in all_alerts:
                if abs((alert - curr_time).total_seconds()) <= 60:
                    # checks if email has already been sent
                    if not habit.last_notified_time:
                        user = HabitUser.query.get(habit.user_id)
                        if user:
                            msg = Message('Habit Tracker Reminder', sender='t4416706@gmail.com', recipients=[user.email])
                            msg.body = f'Hey {user.name}, \nThis is your friendly reminder to {habit.name} at {habit.interval}'
                            mail.send(msg)
                            print(f"Email sent to {user.email} for habit {habit.name} at {alert}")
                            habit.last_notified_time = True
                            db.session.commit()

scheduler.start()
scheduler.add_job(send_notification, trigger=IntervalTrigger(minutes=1), misfire_grace_time=60, coalesce=True)

# if __name__ == '__main__':
#     app.run(debug=True)
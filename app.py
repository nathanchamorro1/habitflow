from flask_migrate import Migrate
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, UserMixin, login_required, logout_user, current_user

app = Flask(__name__, template_folder = "static/css")
app.config['SECRET_KEY'] = 'habitflowsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)

# User model
class HabitUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable = False)
    password = db.Column(db.String(150), nullable=False)


# Habit model (just added - saves habit per user)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    interval = db.Column(db.String(150), nullable=False)
    counter = db.Column(db.Integer, default=0) 
    user_id = db.Column(db.Integer, db.ForeignKey('habit_user.id'), nullable=False)

# DATABASE
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return HabitUser.query.get(int(user_id))

@app.route("/")
def home():
    return render_template('index.html', user=current_user)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if user already exists
        user = HabitUser.query.filter_by(email=email).first()
        if user:
            flash('Sorry, that email address has been taken. Try another one.', 'flash-error')
            return redirect(url_for('signup'))

        # Create a new user and add them to the database
        new_user = HabitUser(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account successfully created. Welcome to HabitFlow!', 'flash-success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query the user by email
        user = HabitUser.query.filter_by(email=email).first()

        if not user or user.password != password:
            flash('Login error. Please check your email and password and try again.', 'flash-error')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('tracker'))

    return render_template('login.html')

@app.route('/tracker', methods=['GET', 'POST'])
@login_required
def tracker():
    if request.method == 'POST':
        data = request.get_json()
        habit_name = data.get('habit')
        interval = data.get('interval', 'Daily')
        new_habit = Habit(name=habit_name, interval=interval, user_id=current_user.id)
        db.session.add(new_habit)
        db.session.commit()
        return {"id": new_habit.id}, 201

    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return render_template('tracker.html', user=current_user, habits=habits)

@app.route("/edit_habit/<int:habit_id>", methods=['POST'])
@login_required
def edit_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    data = request.get_json()  # Handle JSON data from the frontend
    habit.name = data.get('name')
    db.session.commit()

    flash('Habit updated successfully.', 'flash-success')
    return redirect(url_for('tracker'))

@app.route("/delete_habit/<int:habit_id>", methods=['POST'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)

    db.session.delete(habit)
    db.session.commit()

    flash('Habit deleted successfully.', 'flash-success')
    return redirect(url_for('tracker'))

@app.route("/update_habit_counter/<int:habit_id>", methods=['POST'])
@login_required
def update_habit_counter(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    data = request.get_json()
    habit.counter = data.get('count', habit.counter)
    db.session.commit()
    return {"success": True}, 200

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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
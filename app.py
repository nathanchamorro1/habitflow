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

# USER MODEL
class HabitUser(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable = False)
    password = db.Column(db.String(150), nullable=False)

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
            flash('Sorry, that email address has been taken. Try another one.')
            return redirect(url_for('signup'))

        # Create a new user and add them to the database
        new_user = HabitUser(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account successfully created. Welcome to HabitFlow!')
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
            flash('Login error. Please check your email and password and try again.')
            return redirect(url_for('login'))

        login_user(user)
        return redirect(url_for('home'))

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
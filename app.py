from flask import Flask, render_template
app = Flask(__name__, template_folder = "/Users/nathanchamorro/Desktop/habitflow_git/templates")

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/signup")
def signup():
    return render_template('signup.html')

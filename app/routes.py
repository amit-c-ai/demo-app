from flask import render_template, url_for, flash, redirect
from app import app
from app.models import User, Post
from app.forms import RegisterationForm, LoginForm
from sqlalchemy.orm import backref
from enum import unique

Posts = [
    {
        'author': 'amit choudhary',
        'title': 'blog post 1',
        'content': 'This is my first blog',
        'date': '1 January'
    },
    {
        'author': 'Akshay choudhary',
        'title': 'blog post 2',
        'content': 'This is my second blog',
        'date': '2 January'
    },
    {
        'author': 'Komal choudhary',
        'title': 'blog post 3',
        'content': 'This is my third blog',
        'date': '3 January'
    }
]

@app.route("/")
@app.route("/Home")
def home():
    return render_template('home.html', Posts=Posts)

@app.route("/About")
def about():
    return render_template('about.html', title="About page")

@app.route('/Register', methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.username.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title="Registeration", form=form)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if(form.email.data == 'admin@gmail.com' and form.password.data == 'Admin@1234'):
            flash('Logged in succesfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unseccesfull. Please check email and password!', 'danger')

    return render_template('login.html', title="Login", form=form)

from flask import render_template, url_for, flash, redirect, request
from flask_login.utils import login_required
from app import app, db, bcrypt
from app.models import User, Post
from app.forms import RegisterationForm, LoginForm
from sqlalchemy.orm import backref
from enum import unique
from flask_login import login_user, current_user, logout_user, login_required

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title="Registeration", form=form)

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if( user and bcrypt.check_password_hash(user.password, form.password.data)):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Logged in successfully!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unseccesfull. Please check email and password!', 'danger')

    return render_template('login.html', title="Login", form=form)

@app.route('/Logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/Account')
@login_required
def account():
    return render_template('account.html', title="Account")

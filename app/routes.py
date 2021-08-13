import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from flask_login.utils import login_required
from app import app, db, bcrypt
from app.models import User, Post
from app.forms import RegisterationForm, LoginForm, UpdateAccountForm
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

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path + '/static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route('/Account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    if not (os.path.exists(app.root_path + '/static/profile_pics' + current_user.image_file)):
        current_user.image_file = 'default.jpg'
        db.session.commit()

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', form=form, image_file=image_file)

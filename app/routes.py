import secrets, os
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login.utils import login_required
from app import app, db, bcrypt, mail
from app.models import User, Post
from app.forms import RegisterationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm
from sqlalchemy.orm import backref
from enum import unique
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import smtplib, ssl
from email.message import EmailMessage
from email.mime.text import MIMEText

@app.route("/")
@app.route("/Home")
def home():
    page = request.args.get('page', 1, type=int)
    Posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
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
            flash('Login Unsuccessfull. Please check email and password!', 'danger')

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

@app.route('/Post/New', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your blog posted successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')

@app.route('/Post/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route('/Post/<int:post_id>/Update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Post updated!', 'success')
        return redirect(url_for('post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update post', form=form, legend='Update Post')

@app.route('/Post/<int:post_id>/Delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/User/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    Posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', Posts=Posts, user=user)

def send_reset_email(user):
    token = user.get_reset_token()
    print(token)
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    msg=MIMEText(f'''Visit the following link to reset your password:
{url_for('reset_token', token=token, _external=True)}

If you didn't make this request then simply ignore this email, no changes will be made.
''')
    sender_email = os.environ.get('MAIL_USER')
    passw = os.environ.get('MAIL_PASS')
    msg['Subject'] = "Reset Password"
    msg['From'] = sender_email
    msg['To'] = user.email
    context = ssl.create_default_context()
    print(sender_email)
    print(passw)
    print(msg)
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, passw)
        server.sendmail(sender_email, user.email, msg.as_string())

    print(msg)

"""
    msg = Message('Password reset request', sender='amitchoudhary9425@gmail.com', recipients=[user.email]) 
    msg.body = f'''Visit the following link to reset your password:
{url_for('reset_token', token=token, _external=True)}

If you didn't make this request then simply ignore this email, no changes will be made.
'''
    print("mail sent")
    print("url: ", url_for('reset_token', token=token, _external=True))
    print(os.environ.get('MAIL_USER'))
    print(os.environ.get('MAIL_PASS'))
    mail.send(msg)
    print("send command done")
    return 'Sent'
"""

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        print("flashed")
        flash('An email has been sent to the registered email!', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    user = User.verify_reset_token(token)
    if user is None:
        flash('Invalid or expired token!', 'warning')
        return redirect(url_for('reset_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(f'Password reset successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)
    

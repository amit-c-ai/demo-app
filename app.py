from flask import Flask, render_template, url_for, flash, redirect
from forms import RegisterationForm, LoginForm
app = Flask(__name__)

app.config['SECRET_KEY'] = 'fba86f33d6533b176f68252e817c2958'

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

if __name__== '__main__':
    app.run(debug=True)
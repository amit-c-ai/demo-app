from flask import Flask, render_template, url_for

app = Flask(__name__)

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
def hello():
    return render_template('home.html', Posts=Posts)

@app.route("/About")
def about():
    return render_template('about.html', title="About page")

if __name__== '__main__':
    app.run(debug=True)
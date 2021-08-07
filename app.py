from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route("/")
@app.route("/Home")
def hello():
    return "<h1>Hello World!<\h1>"

@app.route("/About")
def about():
    return "<h1>About<\h2>"

if __name__== '__main__':
    app.run()

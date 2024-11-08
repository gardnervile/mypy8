from flask import Flask


def hello_world():
    return "Hello, World!"

app = Flask(__name__)
app.add_url_rule('/', 'hello', hello_world)
app.run('0.0.0.0')
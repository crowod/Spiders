from flask import Flask
app = Flask(__name__)


@app.route('/')
def hello_flask():
    return "<h1>hello, Flask!</h1>"


if __name__ == '__main__':
    app.debug = True
    app.run(host='127.0.0.1', port=5000)

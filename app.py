# a very simple Flask Hello World app for testing purposes
from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hello, World!'

#add a route to return the current time
from datetime import datetime

@app.route('/time')
def get_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
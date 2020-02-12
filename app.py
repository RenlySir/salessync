from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def ping():
    return 'pong'


@app.route('/test', methods=['get', 'post'])
def test():
    return request.data


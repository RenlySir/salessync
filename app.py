from flask import Flask, request

app = Flask(__name__)


@app.route('/')
def ping():
    return 'pong'


@app.route('/test', methods=['get', 'post'])
def test():
    print(request.data)
    return request.data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000)

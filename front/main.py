import requests
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/submit', methods=['GET', 'OPTIONS'])
def submit():
    action = request.args.get('action')
    response = jsonify(requests.get('http://user-service:5001', verify=False, params={'action': action}).json())
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

import requests
from flask import Flask
from flask import jsonify
from flask import request


app = Flask(__name__)


@app.route('/', methods=['GET', 'OPTIONS'])
def submit():
    action = request.args.get('action')
    if action not in ('Rock', 'Paper', 'Scissor'):
        return jsonify({'error': 'unknown action'})
    response = jsonify(requests.get('http://back-service:5002', verify=False, params={'action': action}).json())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

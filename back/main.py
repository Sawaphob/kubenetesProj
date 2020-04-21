from flask import Flask
from flask import request
from flask import jsonify
import requests


app = Flask(__name__)


def compare(user, bot):
    if user == bot:
        return 'draw'

    if any([user == 'Rock' and bot == 'Scissor',
            user == 'Scissor' and bot == 'Paper',
            user == 'Paper' and bot == 'Rock']):
        return 'win'

    return 'lose'


@app.route('/', methods=['GET'])
def evaluate():
    user_action = request.args.get('action')
    bot_action = requests.get('http://bot-service:5003', verify=False).json()['action']

    return jsonify({'user': user_action, 'bot': bot_action,
                    'result': compare(user_action, bot_action)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

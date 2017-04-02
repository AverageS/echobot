# -*- coding: utf-8 -*-
import time
import requests
import json
from threading import Thread
from flask import request, Flask

FLASK = Flask(__name__)
APP_ID = 'INSERT YOURS'
PASSWORD = 'INSERT YOURS' # секрет от бота
context =('fullchain.pem', 'privkey.pem') # относительные или абсолютные пути к файлам, которые сгенерировал cert_bot
TOKEN = {}


def get_token():
    global TOKEN
    payload = {'grant_type': 'client_credentials',
               'client_id': APP_ID,
               'client_secret': PASSWORD,
               'scope': 'https://api.botframework.com/.default',
              }
    token = requests.post('https://login.microsoftonline.com/botframework.com/oauth2/v2.0/token', data=payload).content
    TOKEN = json.loads(str(token)[2:-1])
    return json.loads(str(token)[2:-1])


def send_token_to_connector(token):
    url = 'https://groupme.botframework.com/v3/conversations'
    headers = {'Authorization': 'Bearer ' + token}
    r = requests.post(url, headers=headers)
    return r


def get_and_verify_token():
    global TOKEN
    while True:
        get_token()
        send_token_to_connector(TOKEN['access_token'])
        time.sleep(TOKEN['expires_in']*0.9)


@FLASK.route('/', methods=['GET', 'POST'])
def handle():
    data = request.get_json()
    talk_id = data['conversation']['id']
    msg = {
        "type": "message",
        "from": {
                "id": APP_ID,
                "name": "habraechobot"
            },
        "conversation": {
            "id": talk_id,
        },
        "text": data['text'],
    }
    url = data['serviceUrl'] + '/v3/conversations/{}/activities/'.format(data['conversation']['id'])
    headers = {'Authorization': 'Bearer ' + TOKEN['access_token'],
               'content-type': 'application/json; charset=utf8'}
    r = requests.post(url, headers=headers, data=json.dumps(msg))
    return 'success'




if __name__ == '__main__':
    thread = Thread( target=get_and_verify_token )
    thread.start()
    FLASK.run(host='0.0.0.0', port=8080, ssl_context=context)





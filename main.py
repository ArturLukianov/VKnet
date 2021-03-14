from flask import Flask, jsonify, render_template
import json
import requests
from config import ACCESS_TOKEN
import time


def users_get(user_id):
    response = requests.get("https://api.vk.com/method/users.get", params={
        "v": "5.52",
        "user_ids": user_id,
        "fields": "photo_50",
        "access_token": ACCESS_TOKEN
        })
    return json.loads(response.text)

def friends_get(user_id):
    response = requests.get("https://api.vk.com/method/friends.get", params={
        "v": "5.52",
        "user_id": user_id,
        "access_token": ACCESS_TOKEN
        })
    return json.loads(response.text)

def utils_resolvescreenname(screen_name):
    response = requests.get("https://api.vk.com/method/utils.resolveScreenName", params={
        "v": "5.103",
        "screen_name": screen_name,
        "access_token": ACCESS_TOKEN
        })
    return json.loads(response.text)

nodes = dict()


def analyse(user_id, depth):
    global nodes
    trying = True
    while trying:
        info = users_get(user_id)
        if 'error' in info:
            if info['error']['error_code'] == 6:
#                print('Too many requests')
                time.sleep(1)
            else:
                print(info['error'])
                return
        else:
            trying = False

    info = info['response'][0]

    friends = friends_get(user_id)
    if 'response' in friends:
        friends = friends['response']['items']
    else:
        friends = []

#    print('User analysed')

    nodes[user_id] = {
            'first_name': info['first_name'], 
            'last_name': info['last_name'], 
            'photo': info['photo_50'], 
            'friends': friends
            }

    for friend in friends:
        if friend in nodes:
            continue
        if depth > 0:
            analyse(friend, depth - 1)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/analyse/<string:user_id>/<int:depth>')
def analyse_request(user_id, depth):
    global nodes
    if depth > 2:
        return jsonify({'error': 'too big depth'})
    is_shortname = False
    for i in user_id:
        if i.isalpha():
            is_shortname = True
            break
    if is_shortname:
        user_id = utils_resolvescreenname(user_id)['response']['object_id']
    else:
        user_id = int(user_id)
    nodes = dict()
    analyse(user_id, depth)
    return jsonify(nodes)



app.run(host='0.0.0.0', port=8000)

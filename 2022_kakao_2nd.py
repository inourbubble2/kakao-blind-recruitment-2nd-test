import requests
import json

x_auth_token = '0bfbd7688e42f6c7d8037a6cb181978a'
auth_key = ''
header = {}
base = 'https://huqeyhi95c.execute-api.ap-northeast-2.amazonaws.com/prod'


def start():
    global auth_key, header
    header = {'X-Auth-Token': x_auth_token}
    param = {'problem': problem}
    r = requests.post(base + '/start', headers=header, params=param).json()
    auth_key = r['auth_key']
    header = {'Authorization': auth_key}


def waiting_line():
    r = requests.get(base + '/waiting_line', headers=header).json()
    if 'waiting_line' in r:
        return r['waiting_line']


def game_result():
    r = requests.get(base + '/game_result', headers=header).json()
    if 'game_result' in r:
        return r['game_result']


def user_info():
    r = requests.get(base + '/user_info', headers=header).json()
    if 'user_info' in r:
        return r['user_info']


def _change_grade(game_result):
    for game in game_result:
        win = game['win']
        lose = game['lose']
        taken = game['taken']
        if problem == 1:
            diff = ((1500 - taken * 35) / 5) * (float(grade[win - 1]['grade']) / float(grade[lose - 1]['grade']))
        else:
            diff = ((1500 - taken * 35) / 5)
        grade[win - 1]['grade'] += diff
        grade[lose - 1]['grade'] -= diff
    return grade


def change_grade(game_result):
    data = {'commands': _change_grade(game_result)}
    r = requests.put(base + '/change_grade', headers=header, data=json.dumps(data)).json()
    return r


def _match(waiting_line, user_info):
    if len(waiting_line) == 0:
        return []
    people = []
    for wait in waiting_line:
        s = user_info[wait['id'] - 1]['grade']
        people.append(([wait['id'], s]))
    people = sorted(people, key=lambda x: x[1])

    pairs = []
    for i in range(0, len(people)-1, 2):
        if abs(people[i][1] - people[i+1][1]) >= 1000:
            continue
        pairs.append([people[i][0], people[i+1][0]])
    return pairs


def match(waiting_line, user_info):
    pairs = _match(waiting_line, user_info)
    data = {'pairs': pairs}
    r = requests.put(base + '/match', headers=header, data=json.dumps(data)).json()
    return r


def score():
    r = requests.get(base + '/score', headers=header).json()
    return r


def p1_simulator():
    start()
    status = 'ready'
    print(auth_key)
    while status == 'ready':
        _game_result = game_result()
        _user_info = user_info()
        change_grade(_game_result)
        _waiting_line = waiting_line()
        r = match(_waiting_line, _user_info)
        status = r['status']
        print(r)


# problem = 1
problem = 2
n = 30 if problem == 1 else 900

grade = []
for i in range(1, n+1):
    grade.append({'id': i, 'grade': 5000})
p1_simulator()

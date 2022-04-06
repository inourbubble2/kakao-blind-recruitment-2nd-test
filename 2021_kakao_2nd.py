import requests
import json

x_auth_token = '90a01ab6c5b59048bc5849e5109d350d'
auth_key = ''
auth_key = ''
problem = 1
time = 0
d = {'up': 1, 'right': 2, 'down': 3, 'left': 4, 'pick': 5, 'put': 6}
service_map = []
if problem == 1:
    n = 5
else:
    n = 60
for i in range(n-1, -1, -1):
    i_list = []
    for j in range(i, i + n * (n-1) + 1, n):
        i_list.append(j)
    service_map.append(i_list)
print(service_map)


def req(method, path, params=None, data=None, json=None, headers=None):
    base = 'https://kox947ka1a.execute-api.ap-northeast-2.amazonaws.com/prod/users'
    if not headers:
        global auth_key
        headers = {'Authorization': auth_key, 'Content-Type': 'application/json',}
    if method == 'GET':
        r = requests.get(base + path, params=params, headers=headers, data=data, json=json)
    elif method == 'POST':
        r = requests.post(base + path, params=params, headers=headers, data=data, json=json)
    elif method == 'PUT':
        r = requests.put(base + path, params=params, headers=headers, data=data, json=json)
    elif method == 'DELETE':
        r = requests.delete(base + path, params=params, headers=headers, data=data, json=json)
    return r


def start():
    global auth_key, problem, time
    r = req('POST', '/start', headers={'X-Auth-Token': x_auth_token}, params={'problem': problem})
    data = r.json()
    for key, value in data.items():
        if key == 'auth_key':
            auth_key = value
        elif key == 'problem':
            problem = value
        elif key == 'time':
            time = value
        print(key, value)


def print_data(data):
    for key, value in data.items():
        print(key, end=':\n')
        print(value)
        if hasattr(value, '__iter__') and not isinstance(value, str):
            for v in value:
                print(v)


def get_bikes(data):
    bikes = {}
    for key, value in data.items():
        for v in value:
            bikes[v['id']] = v['located_bikes_count']
    return bikes


def get_trucks(data):
    trucks = {}
    for key, value in data.items():
        for v in value:
            truck = {'location_id': v['location_id'], 'loaded_bikes_count': v['loaded_bikes_count']}
            trucks[v['id']] = truck
    return trucks


# (x1, y1) 에서 (x2, y2)로 가는 길의 커맨드를 제공한다
def make_command(fr, to):
    fr_i, fr_j, to_i, to_j = 0, 0, 0, 0
    command = []
    for i in range(n):
        if fr in service_map[i]:
            for j in range(n):
                if fr == service_map[i][j]:
                    fr_i, fr_j = i, j
        if to in service_map[i]:
            for j in range(5):
                if to == service_map[i][j]:
                    to_i, to_j = i, j
    while fr_i != to_i:
        if fr_i < to_i:
            # print('down', end=' ')
            command.append(d['down'])
            fr_i += 1
        elif fr_i > to_i:
            # print('up', end=' ')
            command.append(d['up'])
            fr_i -= 1
    while fr_j != to_j:
        if fr_j < to_j:
            # print('right', end=' ')
            command.append(d['right'])
            fr_j += 1
        elif fr_j > to_j:
            # print('left', end=' ')
            command.append(d['left'])
            fr_j -= 1
    return command


def is_range(near):
    if problem == 1:
        return 0 <= near < 25
    elif problem == 2:
        return 0 <= near < 60*60


# 인접한 칸들 중 바이크가 가장 많은 대여소로 이동 후 자전거를 수거하고
# 다시 인접한 칸들 중에서 바이크가 가장 적은 대여소로 이동해 자전거를 내려놓는다
def move_truck(bikes, prev_location_id):
    command = []
    nears = [prev_location_id - 5,
             prev_location_id + 5,
             prev_location_id - 1,
             prev_location_id + 1,
             prev_location_id - 4,
             prev_location_id + 4,
             prev_location_id - 6,
             prev_location_id + 6]
    diff = []
    for near in nears:
        if is_range(near) and bikes[near] > bikes[prev_location_id]:
            diff.append((near, abs(bikes[prev_location_id] - bikes[near])))
    if diff:
        near = sorted(diff, key=lambda x: x[1], reverse=True)[0][0]
        way = make_command(prev_location_id, near)
        if way:
            prev_location_id = near
            command = way

    nears = [prev_location_id - 5,
             prev_location_id + 5,
             prev_location_id - 1,
             prev_location_id + 1,
             prev_location_id - 4,
             prev_location_id + 4,
             prev_location_id - 6,
             prev_location_id + 6]
    for near in nears:
        if is_range(near) and bikes[near] < bikes[prev_location_id]:
            diff.append((near, abs(bikes[prev_location_id] - bikes[near])))
    if diff:
        near = sorted(diff, key=lambda x: x[1], reverse=True)[0][0]
        way = make_command(prev_location_id, near)
        if way:
            command += [d['pick']] + way + [d['put']]
    print(command)
    if 6 in command:
        bikes[prev_location_id] -= 1
        bikes[near] += 1
    return command


# random 하게 목표 위치를 정해서
# 이전에 있던 대여소의 자전거 개수보다 적으면 자전거를 내려놓기
def simulate(bikes, trucks):
    commands = []
    for i in range(len(trucks)):
        truck = trucks[i]
        prev_location_id = truck['location_id']
        command = move_truck(bikes, prev_location_id)
        # print(command)
        obj = {"truck_id": i, "command": command}
        commands.append(obj)
    data = {"commands": commands}
    r = req('PUT', '/simulate', data=json.dumps(data))
    print_data(r.json())


def score():
    method = 'GET'
    path = '/score'
    r = req(method, path)
    print_data(r.json())
    # return r.json()


def kakao_2nd():
    start()

    for i in range(720):
        r = req('GET', '/locations', params={'problem': problem})
        bikes = get_bikes(r.json())

        r = req('GET', '/trucks')
        trucks = get_trucks(r.json())

        simulate(bikes, trucks)
    score()


# print(service_map)
# print(make_command(22, 1))
kakao_2nd()
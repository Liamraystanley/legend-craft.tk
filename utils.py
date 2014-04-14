#!/usr/bin/python

import flask
from dateutil.relativedelta import relativedelta
import json
import hashlib
import functools
import requests


attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
date = lambda delta: ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and \
  attr or attr[:-1]) for attr in attrs if getattr(delta, attr)] # Super messy but it works!

# Time convert usage
# date(relativedelta(seconds=1207509))


def getServers():
    try:
        with open('servers.db', 'r') as file:
            servers = json.loads(file.read())['list']
            return servers
    except:
        with open('servers.db', 'w') as file:
            file.write(json.dumps({'list': []}, indent=4))
            return []


def saveServers(data):
    with open('servers.db', 'w') as file:
        file.write(json.dumps({'list': data}, indent=4))


def getServerIds():
    servers = getServers()
    ids = []
    for server in servers:
        ids.append(server['id'])
    return ids


def editServer(id, ping, pcount):
    # First, find the server with that ID...
    servers = getServers()
    tmp = []
    for server in servers:
        tmp.append(server)
        if id == server['id']:
            tmp[-1]['last_ping'] = ping
            tmp[-1]['pcount'] = pcount

    saveServers(tmp)


def api():
    release_uri = 'https://api.github.com/repos/LegendCraft/LegendCraft/releases'
    try:
        data = {
            'releases': json.loads(requests.get(release_uri).text)
        }
        with open('data.db', 'w') as file:
            file.write(json.dumps(data, indent=4))
        return data
    except Exception, e:
        with open('data.db', 'r') as file:
            data = json.loads(file.read())
        print 'Failed to get data from Github (%s) Using backups.' % str(e)
        return data


def isauthed(username, passwd):
    admins = ['me@liamstanley.io', 'aceofblades51@gmail.com']
    uri = 'https://authserver.mojang.com/%s'
    data = json.dumps({
        "agent": {"name": "Minecraft", "version": 1},
        "username": username, "password": passwd
    })
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(uri % 'authenticate', data=data, headers=headers)
        r = r.json()
    except:
        return False
    if 'error' in r or 'accessToken' not in r:
        return False
    # If we wanted to get premium profiles... r['availableProfiles']
    if username.lower() in admins:
        return 1
    else:
        return 2


def login(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
        if 'username' in flask.session:
            return method(*args, **kwargs)
        else:
            # error = 'You must be logged in to use that!'
            # return flask.render_template('login.html',error=error)
            return flask.render_template('login.html', url=flask.request.path)
    return wrapper


def hash(data):
    data = hashlib.md5(data).hexdigest()
    return data


def getRequests():
    try:
        with open('request.db', 'r') as file:
            data = json.loads(file.read())['list']
    except IOError:
        genNewDB('request.db', {'list': []})
        data = []
    return data


def remRequest(index):
    data = getRequests()
    try:
        del data[int(index)]
        with open('request.db', 'w') as file:
            file.write(json.dumps({'list': data}, indent=4))
        return True
    except:
        return False


def getRequestIds():
    requests = getRequests()
    ids = []
    for request in requests:
        ids.append(request['id'])
    return ids


def addRequest(item):
    with open('request.db', 'r') as file:
        data = json.loads(file.read())['list']
    data.append(item)
    with open('request.db', 'w') as file:
        file.write(json.dumps({'list': data}, indent=4))
    return data


def genNewDB(dbname, data):
    with open(str(dbname), 'w') as file:
        file.write(json.dumps(data, indent=4))

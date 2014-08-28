#!/usr/bin/python

import flask
from dateutil.relativedelta import relativedelta
import json
import hashlib
import functools
import requests
import redis
import re
from pprint import pprint


attrs = ['years', 'months', 'days', 'hours', 'minutes', 'seconds']
date = lambda delta: ['%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and \
  attr or attr[:-1]) for attr in attrs if getattr(delta, attr)] # Super messy but it works!

# Time convert usage
# date(relativedelta(seconds=1207509))


# def getServers():
#     try:
#         with open('servers.db', 'r') as file:
#             servers = json.loads(file.read())['list']
#             return servers
#     except:
#         with open('servers.db', 'w') as file:
#             file.write(json.dumps({'list': []}, indent=4))
#             return []


# def saveServers(data):
#     with open('servers.db', 'w') as file:
#         file.write(json.dumps({'list': data}, indent=4))


# def getServerIds():
#     servers = getServers()
#     ids = []
#     for server in servers:
#         ids.append(server['id'])
#     return ids


# def editServer(id, ping, pcount):
#     # First, find the server with that ID...
#     servers = getServers()
#     tmp = []
#     for server in servers:
#         tmp.append(server)
#         if id == server['id']:
#             tmp[-1]['last_ping'] = ping
#             tmp[-1]['pcount'] = pcount

#     saveServers(tmp)


def isauthed(username, passwd):
    admins = ['me@liamstanley.io', 'aceofblades51@gmail.com']
    r = mc_auth(username, passwd)
    if 'error' in r or 'accessToken' not in r:
        return False
    # If we wanted to get premium profiles... r['availableProfiles']
    if username.lower() in admins:
        return 1
    else:
        return 2


def mc_auth(username, passwd):
    uri = 'https://authserver.mojang.com/%s'
    data = json.dumps({
        "agent": {"name": "Minecraft", "version": 1},
        "username": username, "password": passwd
    })
    headers = {'content-type': 'application/json'}
    try:
        r = requests.post(uri % 'authenticate', data=data, headers=headers)
        r = r.json()
        return r
    except:
        return False

def cc_auth(username, passwd):
    uri = 'http://www.classicube.net/acc/login'

    try:
        # First we need to get the CSRF token before we send a POST...
        data = requests.get(uri).text
        csrf_re = re.compile(r'id="csrf_token" name="csrf_token" type="hidden" value="(.*?)"')
        csrf = csrf_re.findall(data)[0]
        
        # Now, we need to send the user/pass/csrf token to the website
        payload = {
            'csrf_token': csrf,
            'username': username,
            'password': passwd
        }
        pprint(payload)
        response = requests.post(uri, data=json.dumps(payload))
        print response
        print response.history
    except:
        return False


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


# def getRequests():
#     try:
#         with open('request.db', 'r') as file:
#             data = json.loads(file.read())['list']
#     except IOError:
#         genNewDB('request.db', {'list': []})
#         data = []
#     return data


# def remRequest(index):
#     data = getRequests()
#     try:
#         del data[int(index)]
#         with open('request.db', 'w') as file:
#             file.write(json.dumps({'list': data}, indent=4))
#         return True
#     except:
#         return False


# def getRequestIds():
#     requests = getRequests()
#     ids = []
#     for request in requests:
#         ids.append(request['id'])
#     return ids


# def addRequest(item):
#     with open('request.db', 'r') as file:
#         data = json.loads(file.read())['list']
#     data.append(item)
#     with open('request.db', 'w') as file:
#         file.write(json.dumps({'list': data}, indent=4))
#     return data


# def genNewDB(dbname, data):
#     with open(str(dbname), 'w') as file:
#         file.write(json.dumps(data, indent=4))

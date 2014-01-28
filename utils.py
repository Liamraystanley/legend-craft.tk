#!/usr/bin/python

import flask
from dateutil.relativedelta import relativedelta
import urllib, urllib2, json, hashlib
import io, functools


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
                'releases': json.loads(urllib2.urlopen(release_uri).read())
        }
        with open('data.db', 'w') as file:
            file.write(json.dumps(data, indent=4))
        return data
    except Exception,e:
        with open('data.db', 'r') as file:
            data = json.loads(file.read())
        print 'Failed to get data from Github (%s) Using backups.' % str(e)
        return data


def isauthed(username, passwd):
    try:
        # This is a legacy method of logging into Mineraft.net. By using this, we can ONLY
        #   tell that the user is an account, and the name they used to login. So all we're
        #   doing is checking their account name (successful login), with the admin list
        #   that is based on emails. All because I'm lazy and don't want to do full auth
        #   with the new format of Mojang authentication xD
        data = urllib2.urlopen('http://login.minecraft.net/?user=%s&password=%s&version=12' % (urllib.quote(username), urllib.quote(passwd))).read()
    except:
        return False
    if 'not premium' in data or 'deprecated' in data:
        # User is logginable
        # Here, make an admin email list. Also make sure that they are LOWER case!
        admins = ['me@liamstanley.net', 'aceofblades51@gmail.com']
        if not username.lower() in admins:
            return 2
        return 1
    else:
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


def getRequests():
    try:
        with open('request.db', 'r') as file:
            data = json.loads(file.read())['list']
    except IOError as e:
        genNewDB('request.db', {'list': []})
        data = []
    return data


def remRequest(index):
    data = getRequests()
    try:
        del data[int(index)]
        with open('request.db','w') as file:
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

# def get_quotes():
#     if not os.path.isfile('quotes.db'):
#         return False
#     with open('quotes.db', 'r') as file:
#         data = json.loads(file.read())['list']
#     return data
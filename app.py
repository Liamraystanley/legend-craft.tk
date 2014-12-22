#!/usr/bin/python
import flask
import flask.views
import time
import os
from flask import jsonify
from threading import Thread
from hashlib import md5
from utils import *
import settings
import thread
import requests as web


app = flask.Flask(__name__)
database = redis.StrictRedis(host='localhost', port=6379, db=0)
app.debug = True
app.secret_key = settings.key


@app.route('/')
@app.route('/<page>')
def main(page="index"):
    if page == 'logout':
        flask.session.pop('username', None)
        return flask.render_template('index.html', success="Successfully logged out!")
    if os.path.isfile('templates/%s.html' % page):
        return flask.render_template(page + '.html')
    return flask.abort(404)


@app.route('/download')
@app.route('/download/<version>')
@app.route('/download/<version>/<other>')
def download(version=None, other=None):
    source_uri = 'https://api.github.com/repos/LeChosenOne/LegendCraft/zipball/%s'
    download_uri = 'https://github.com/LeChosenOne/LegendCraft/releases/download/%s/%s'
    git_uri = 'https://github.com/LeChosenOne/LegendCraft/releases/%s'
    if not github:
        return flask.abort(404)

    latest_tag = github[0]['tag_name']
    latest_file = github[0]['assets'][0]['name']
    src_aliases = ['src', 'source', 'fork', 'git']
    view_aliases = ['view', 'read', 'html', 'github', 'read']
    if not version:  # Assume that they want to list all current downloads
        return flask.render_template('download.html', data=github)
    elif version.lower() == 'latest':
        if other:
            if other.lower() in src_aliases:
                return flask.redirect(source_uri % github[0]['tag_name'])
            elif other.lower() == 'update':
                return str(latest_tag)
            else:
                return flask.abort(404)
        else:
            return flask.redirect(download_uri % (latest_tag, latest_file))
    else:
        try:
            tag, filename = None, None
            for release in github:
                if version == release['tag_name']:
                    tag, filename = release['tag_name'], release['assets'][0]['name']
                    break
            if not tag or not filename:
                return flask.abort(404)
        except:
            return flask.abort(404)
        if other:
            if other.lower() in src_aliases:
                return flask.redirect(source_uri % tag)
            elif other.lower() in view_aliases:
                return flask.redirect(git_uri % tag)
            else:
                return flask.abort(404)
        else:
            return flask.redirect(download_uri % (tag, filename))


@app.route('/license')
def license():
    return flask.redirect('https://raw.github.com/LeChosenOne/LegendCraft/master/License.txt')


@app.route('/wiki')
def wiki():
    return flask.redirect('http://minecraft.gamepedia.com/Custom_servers/legendcraft')


def server_daemon():
    while True:
        time.sleep(120)
        # get the servers, check for inactive servers, remove old servers, and save servers
        #print '[DAEMON] Checking for inactive servers!'
        if not servers:
            #print '[DAEMON] No servers to check for!'
            pass
        tmp = []
        for server in servers:  # "server" being a index #
            difference = int(time.time()) - int(server['last_ping'])
            if difference > 480:
                print '[DAEMON] Removed stale server'
            else:
                tmp.append(server)
        save('servers', tmp)


@app.route('/heartbeat', methods=['GET'])
def server_heartbeat():
    # Collect the current POSIX time, so if the server is valid we get a good
    # start-process time to work with
    uptime = str(int(time.time()))
    required = ['name', 'players', 'max', 'version', 'url']
    args = flask.request.args
    print args

    # Lets see if we're missing the required GET variables...
    for requirement in required:
        if not requirement in args:
            return 'Bad request'

    # Make the dictionary of data to insert into the database of servers
    server = {}
    server['name'] = args['name']
    server['version'] = args['version']
    server['id'] = md5(server['name'] + server['version']).hexdigest()
    server['pcount'] = str(args['players'])
    server['pmax'] = str(args['max'])
    server['url'] = args['url']

    if len(server['version'].split('.')) != 3:
        server['version'] = 'Custom'

    # Still not finished vars: "last_ping", and "uptime". Those are sorted now..
    # First we need to tell if the server is new or not. By looping through and finding ID's!
    # This is ugly, but we're not using a huge database for this so this is the best we get
    ids = []
    for server in servers:
        ids.append(server['id'])

    if server['id'] in ids:
        # It is already in the list... Lets update "last_ping"
        # This does the actual updating...
        tmp = []
        for server in servers:
            tmp.append(server)
            if server['id'] == server['id']:
                tmp[-1]['last_ping'] = str(uptime)
                tmp[-1]['pcount'] = server['pcount']

        save('servers', tmp)
        return 'Updated'
    else:
        # It's a new server, so we're going to append it to the serverlist
        server['last_ping'], server['uptime'] = uptime, uptime
        servers.append(server)
        save('servers', servers)
        print('Server "%s" has been added.' % server['name'])
        return 'Added'


@app.route('/servers')
def server_list():
    # "servers" should be populated, or empty..
    if not servers:
        return flask.render_template('servers.html')

    # Assume "servers" is a list() of dict()'s with server data
    # So, lets return the data to the user, sorted by uptime!
    tmp = servers
    tmp = sorted(tmp, key=lambda k: k['uptime'])

    # Take the time, convert their ugly POSIX time to humanly-readable-time
    for server in tmp:
        print server
        # At a later time, we'll find the difference between the stored INITIAL heartbeat,
        # And the current time, giving us the seconds for the HR uptime
        difference = int(time.time()) - int(server['uptime'])
        try:
            server['uptime_nice'] = date(relativedelta(seconds=difference))[0]
        except:
            pass

    return flask.render_template('servers.html', servers=tmp)


class Login(flask.views.MethodView):
    def get(self):
        if 'username' in flask.session:
            return flask.redirect(flask.url_for('index'))
        if 'url' in flask.request.args:
            return flask.render_template('login.html', url=flask.request.args['url'])
        return flask.render_template('login.html')

    def post(self):
        if 'username' in flask.session:
            return flask.redirect('/')
        form = flask.request.form
        required = ['username', 'passwd']
        if not required[0] in form or not required[1] in form:
            return flask.render_template('login.html')
        errors = {
            'blank': 'You must have both a username and password.',
            'incorrect': 'Incorrect username or password.',
            'notadmin': 'Authentication successful but user not admin.'
        }
        for r in required:
            if r not in form:
                return flask.render_template('login.html', error=errors['blank'])
            if form[r].strip() == '':
                return flask.render_template('login.html', error=errors['blank'])
        username = form[required[0]]
        passwd = form[required[1]]
        accountStatus = isauthed(username, passwd)
        if accountStatus == 1:
            flask.session[required[0]] = username
            print('User %s successfully authenticated!' % username)
        elif accountStatus == 2:
            return flask.render_template('login.html', error=errors['notadmin'])
        else:
            return flask.render_template('login.html', error=errors['incorrect'])
        if 'url' in form:
            return flask.redirect(form['url'])
        return flask.redirect('/')


class Request(flask.views.MethodView):
    @login
    def get(self):
        global requests
        args = flask.request.args
        if 'delete' in args:
            del requests[int(args['delete'])]
            save('requests', requests)
            return flask.redirect(flask.url_for('request'))

        count = str(len(requests))

        # Assume "servers" is a list() of dict()'s with server requests
        # So, lets return the requests to the user, sorted by uptime!
        count = 0
        for request in requests:
            difference = int(time.time()) - int(request['date'])
            request['time'] = date(relativedelta(seconds=difference))[0]
            request['num'] = str(count)
            count += 1

        requests = sorted(requests, key=lambda k: k['date'])[::-1]

        return flask.render_template('request.html', requests=requests, count=count)

    def post(self):
        form = flask.request.form
        required = ['email', 'type', 'message']
        optional = ['os', 'runtime', 'version']
        types = ['Bug', 'Feature']
        for requirement in required:
            if not requirement in form:
                error = 'An email, a submission type, and a message are all required!'
                return flask.render_template('index.html', error=error)

        # Yoo. Don't you love this ugly set of if's
        if not form['type'] in types or len(form['message']) < 15 or len(form['email']) < 5 or \
          ' ' in form['email'] or not '@' in form['email'] or not '.' in form['email']:
            error = 'Invalid submission!'
            return flask.render_template('index.html', error=error)

        item = {
            'date': str(int(time.time())),
            'type': form['type'].lower(),
            'message': form['message'],
            'id': str(md5(form['message']).hexdigest()),
            'author': form['email'],
            'ip': flask.request.remote_addr
        }

        # Make sure message isn't mass spam..
        while '\r\n\r\n\r\n' in item['message']:
            item['message'] = item['message'].replace('\r\n\r\n\r\n', '\r\n\r\n')

        # Add some optional things that we might get, from a servers winform
        for setting in optional:
            if setting in form:
                item[setting] = form[setting]

        if 'runtime' in form:
            item['runtime'] = form['runtime']
        if 'os' in form:
            item['os'] = form['os']

        # Before we add it, see if we match another server...
        ids = []
        for request in requests:
            ids.append(request['id'])
        if item['id'] in ids:
            return flask.render_template('index.html', error='Duplicate submission!')
        requests.append(item)
        save('requests', requests)
        print('Added %s\'s request (%s)' % (item['author'], item['type']))
        return flask.render_template('index.html', success='Request has been received. Thank you!')


@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('404.html'), 404


app.add_url_rule('/login', view_func=Login.as_view('login'), methods=['GET', 'POST'])
app.add_url_rule('/request', view_func=Request.as_view('request'), methods=['GET', 'POST'])


@app.template_filter()
def nl2br(value):
    return value.replace('\n', '\n<br>')


def github_retrieve():
    while True:
        try:
            github = web.get('https://api.github.com/repos/LeChosenOne/LegendCraft/releases',
               auth=(settings.github_user, settings.github_password)).json()
            save('github', github)
        except:
            pass
        time.sleep(120)


def save(id, data):
    global servers
    global github
    global requests
    if id == 'servers':
        servers = data
    elif id == 'github':
        github = data
    elif id == 'requests':
        requests = data
    if isinstance(data, list):
        data = json.dumps({'list': data})
    elif isinstance(data, (int, long, float, complex)):
        data = str(data)
    elif isinstance(data, dict):
        data = json.dumps(data)
    else:
        return
    database.set('legend-craft.tk/%s' % id, data)


def get(id):
    data = database.get('legend-craft.tk/%s' % id)
    if not data:
        return False
    if data.startswith('{'):
        data = json.loads(data)
        if 'list' in data:
            data = data['list']

    return data


def init():
    global servers
    global github
    global requests
    # servers, github, requests
    servers = get('servers')
    if not servers:
        save('servers', [])
        servers = []
    thread.start_new_thread(server_daemon, ())

    github = get('github')
    if not github:
        save('github', [])
        github = []
    thread.start_new_thread(github_retrieve, ())

    requests = get('requests')
    if not requests:
        save('requests', [])
        requests = []


init()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

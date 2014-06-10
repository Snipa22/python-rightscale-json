#!/usr/bin/python
from flask import Flask, request, abort
import simplejson as json
from rsapi.rsapi_working import rsapi_working as working
app = Flask(__name__)

repo_map_dev={}
repo_map_prod={}

@app.route("/dev", methods=['POST'])
def dev():
    if request.headers.get('X-GitHub-Event') == "ping":
        return json.dumps({'msg': 'Hi!'})
    if request.headers.get('X-GitHub-Event') != "push":
        return json.dumps({'msg': "Wrong event type"})
    payload = json.loads(request.form['payload'])
    if "Merge pull request" in payload['head_commit']['message']:
        rsapi = working()
        rsapi.refetch_repository(repo_map_dev[payload['repository']['name']], payload['head_commit']['id'])
    return json.dumps({'msg': "Hi!"})

@app.route("/prod", methods=['POST'])
def prod():
    if request.headers.get('X-GitHub-Event') == "ping":
        return json.dumps({'msg': 'Hi!'})
    if request.headers.get('X-GitHub-Event') != "push":
        return json.dumps({'msg': "Wrong event type"})
    payload = json.loads(request.form['payload'])
    if "Merge pull request" in payload['head_commit']['message']:
        rsapi = working(api_type="prod")
        rsapi.refetch_repository(repo_map_dev[payload['repository']['name']], payload['head_commit']['id'])
    return json.dumps({'msg': "Hi!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

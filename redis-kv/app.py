from flask import Flask, render_template, request, jsonify, json
import requests
import redis
app = Flask(__name__)

""" 
PART ONE OF FINAL PROJECT WEEK 1
---------------------------------
Change the previous 'database' system that was being used (2 dictionaries) to a redis database.

USEFUL RESOURCE FOR THIS PROJECT AND FUTURE SWE ASPIRATIONS:
https://realpython.com/python-redis/#ten-or-so-minutes-to-redis

"""

"""
Data Strucure:

{key : 
    {
         1 : value
         2 : value
         3 : value
        ...
    }
}
"""

r = redis.Redis(host='localhost', port=6379, db=0) # Creates Redis database 0 

@app.route('/<key>', methods=["PUT"])
def put(key):
    value = request.data.decode("utf-8") # value is a string
    # check if key currently exists in the database
    if (r.exists(key) == 0):
        # add key to database as version 0
        r.hset(key, key = 1, value = value)
    else:
        # add latest value to database
        new_version = r.hlen(key) + 1
        r.hset(key, key = new_version, value = value)  # 1st arg is name of highest level datastr in redis

    return 'success', 200

@app.route('/<key>', methods=["GET"])
def get(key):

    if(r.exists(key) == 0):
        return "The key does not exist", 404
    
    version_latest = r.hlen(key)
    value = r.hget(key, version_latest)
    value = value.decode("utf-8")

    tr = {'value' : value, 'version' : version_latest}
    json_tr = json.dumps(tr)

    print(r.hgetall("neil"))
    return json_tr, 200

@app.route('/<key>/<version>', methods = ["GET"])
def get_specific(key, version):
    
    try:
        version = int(version)
    except ValueError:
        'invalid input', 404

    if(r.exists(key) == 0):
        return "The key does not exist", 404

    version_latest = r.hlen(key)

    if version > version_latest:
        return "Version too high", 404
    
    value = r.hget(key, version) 
    value = value.decode("utf-8")

    tr = {'value' : value, 'version' : version}
    json_tr = json.dumps(tr)

    return json_tr, 200


@app.route('/<key>', methods=["DELETE"])
def delete(key):
    if(r.exists(key) == 0):
        return "No need for deletion, key already does not exist.", 404
    
    r.delete(key)

    return "Done", 200
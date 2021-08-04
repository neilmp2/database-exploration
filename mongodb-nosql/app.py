from flask import Flask, render_template, request, jsonify, json
import requests
app = Flask(__name__)
from pymongo import MongoClient


""" 
PART TWO OF FINAL PROJECT WEEK 1
---------------------------------
Change the previous 'database' system that was being used (2 dictionaries) to a MongoDB database.

"""

mongo = client = MongoClient('localhost', 27017)
db = mongo["state-server"]

data = db.data # intialize collection called 'data.' It will not be created until first doc insert

""" 
EXAMPLE STRUCTURE OF DOCUMENTS
{ "name" : name of key
  "max_version" : current maximum version 
  "1"   : value for version 1
  "2"  : value for version 2
}
"""
@app.route('/<key>', methods=["PUT"])
def put(key):
  value = request.data.decode("utf-8") # value is a string
  # key does not already exist
  if (data.find_one({"name" : key}) == None):
      insert = {
        "name" : key, 
        "max_version" : 1,
        "1" : value
      }
      data.insert_one(insert)
  else:
    # key already exists
    document = data.find_one({"name" : key})
    curr_max_version = document["max_version"]

    data.update_one(
      {"name" : key}, 
      [ {"$set" : {"max_version" : curr_max_version + 1}},
        {"$set" : {str(curr_max_version + 1) : value}},
      ]
    )
  return "Success", 200

@app.route('/<key>', methods=["GET"])
def get(key):
  document  = data.find_one({"name" : key})
  if (document == None):
    return "Key does not exist", 404
  
  curr_max_version = document["max_version"]
  value = document[str(curr_max_version)]

  tr = {"value" : value, "version" : curr_max_version}
  tr_json = json.dumps(tr)
  return tr_json, 200


@app.route('/<key>/<version>', methods = ["GET"])
def get_specific(key, version):
  # version is a string => which is desired in this case
  document  = data.find_one({"name" : key})
  if (document == None):
    return "Key does not exist", 404
  
  value = document[version]
  tr = {"value" : value, "version" : version}
  tr_json = json.dumps(tr)
  return tr_json, 200
  

@app.route('/<key>', methods=["DELETE"])
def delete(key):
  document  = data.find_one({"name" : key})
  if (document == None):
    return "Key does not exist", 404
  
  data.delete_one(document)
  return "Deleted", 200
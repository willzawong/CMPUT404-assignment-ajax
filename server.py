#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


from http import HTTPStatus
from flask import Flask, Response, request, redirect, jsonify
import json
import sys
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()          

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

def parsePUT(responseString):
    responseString = responseString[2:]
    stack = []
    builder = ""
    for char in responseString:
        if char == ':' or char == ',' or char == '}':
            stack.append(builder)
            builder = ""
        else:
            builder += char
    alt = 1
    builder = "{"
    for string in stack:
        if(alt):
            builder += '"' + string + '":'
            alt = 0
        else:
            alt = 1
            builder += string + ","
            
    builder = builder[:-1]+"}"
    print(builder, file=sys.stdout)
    return json.loads(builder)  

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    # https://stackoverflow.com/a/14343957
    return redirect("/static/index.html", code=302)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    # https://stackoverflow.com/a/51932419
    returner = {"status":200,"mimetype":'application/json'}
    if(request.method == 'PUT'):
        requestJSON = flask_post_json()
        for key in requestJSON:
            myWorld.update(entity, key, requestJSON[key])
            returner[key] = requestJSON[key]
    elif(request.method == 'POST'):
        # not sure what to do
        requestJSON = flask_post_json()
        for key in requestJSON:
            print(key)
            myWorld.update(entity, key, requestJSON[key])
    else:
        return None
    return returner

@app.route("/world", methods=['POST','GET'])    
def world():
    '''you should probably return the world here'''
    return myWorld.world()

@app.route("/entity/<entity>")    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''

    return myWorld.get(entity)

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return myWorld.world()

if __name__ == "__main__":
    app.run()

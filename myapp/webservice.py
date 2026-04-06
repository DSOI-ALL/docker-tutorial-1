#!/usr/bin/python
from bottle import route, run, debug, default_app, response
import os
import random
from pymongo import MongoClient

# Configure DB params
db_name = 'slsdb'

# MONGO_HOST is set via --env on docker run, or via the 'environment' key in docker-compose.yml.
# When containers share a Docker network, the container name is resolvable as a hostname.
# Default to 'mongo' so it works out-of-the-box with docker-compose without extra config.
default_host = 'mongo'
db_host = os.environ.get('MONGO_HOST', default_host)

@route('/')
def index():
    """
    Default landing page.  We'll initialize some mongo test data here.
    """
    client = MongoClient(db_host)
    db = client[db_name]
    r = lambda: random.randint(0,255)
    color = ('#%02X%02X%02X' % (r(),r(),r()))
    db.colors.insert_one({"color":color})
    return """
    <p>Hello. Creating some default data every time the page is visited.</p>
    <a href="http://localhost:8000/hello">See the data!</a>
    """

@route('/hello')
def hello_world():
    """
    Return the contents of the collection we created at index.
    """

    client = MongoClient(db_host)
    db = client[db_name]

    blocks = ''
    colors = [doc['color'] for doc in db.colors.find()]

    for color in colors:
        blocks += '<div style="width:75px; height:75px; border:1px solid;'
        blocks += 'float: left; margin: 1px; background-color:' + color
        blocks += '">' + color + '</div>'

    # Add a back link
    blocks += '<div style="clear:both"><a href="http://localhost:8000">Go back.</a></div>'
    return blocks


app = default_app()

debug(True)
run(host='0.0.0.0', port=8000, reloader=True)

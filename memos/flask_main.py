"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates: 
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will 
   - User input/output is in local (to the server) time.  
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for

import json
import logging

import sys
# To make id
import uuid

# Date handling 
import arrow   
from dateutil import tz  # For interpreting local times

# Mongo database
from pymongo import MongoClient

import config
if __name__ == "__main__":
   CONFIG = config.configuration()
else: 
   CONFIG = config.configuration(proxied=True)


MONGO_CLIENT_URL = "mongodb://{}:{}@{}:{}/{}".format(
    CONFIG.DB_USER,
    CONFIG.DB_USER_PW,
    CONFIG.DB_HOST, 
    CONFIG.DB_PORT, 
    CONFIG.DB)


print("Using URL '{}'".format(MONGO_CLIENT_URL))


###
# Globals
###

app = flask.Flask(__name__)
app.secret_key = CONFIG.SECRET_KEY

####
# Database connection per server process
###

try: 
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, CONFIG.DB)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)


###
# Pages
###

@app.route("/", methods=['GET', 'POST'])
@app.route("/index", methods=['GET', 'POST'])
def index():
  app.logger.debug("Main page entry")
  g.memos = get_memos()
  for memo in g.memos: 
    app.logger.debug("Memo: " + str(memo))

  return flask.render_template('index.html')


@app.route("/create")
def create():
    app.logger.debug("Create")
    return flask.render_template('create.html')


@app.route("/send", methods=['POST'])
def send():
  app.logger.debug("send")
  memo_text = request.form['memo_text']
  date = request.form['datepicker']
  app.logger.debug(date)
  memo_id = uuid.uuid4()
  app.logger.debug(memo_id)
  
  record = { "type": "dated_memo",
        "text": str(memo_text),
        "date": date,
        "memo_id": str(memo_id)
      }

  app.logger.debug(record)
  collection.insert(record)
  record2 = {"type": "dated", "text": "moo"}
  collection.insert(record2)
  app.logger.debug(get_memos())
  g.memos = get_memos()

  return flask.render_template('index.html')


@app.route("/delete", methods=['POST'])
def delete():
  memo_id = request.form["memo_id"]
  app.logger.debug(memo_id)
  collection.remove({"memo_id": memo_id}, 1)
  # Refresh memos dict
  app.logger.debug(db.Memos)
  g.memos = get_memos()
  app.logger.debug(get_memos())

  return flask.render_template('delete.html')
   

@app.errorhandler(404)
def page_not_found(error):
    app.logger.debug("Page not found")
    #return flask.render_template('create.html')
    #if request.method == 'GET':
    #app.logger.debug("GET request")
    # Access form
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404

#################
#
# Functions used within the templates
#
#################


@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    """
    Date is internal UTC ISO format string.
    Output should be "today", "yesterday", "in 5 days", etc.
    Arrow will try to humanize down to the minute, so we
    need to catch 'today' as a special case. 
    """
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        diff = now - then
        hours,remainder = divmod(diff.seconds,3600) # courtesy of OShadmon, StackOverflow
        if diff.days == 0 and hours < now.hours:
            human = "Today"
        if then.date() == now.date():
            human = "Today"
        else: 
            human = then.humanize(now)
            if human == "in a day":
                human = "Tomorrow"
    except: 
        human = date
    return human


#############
#
# Functions available to the page code above
#
##############
def get_memos():
    """
    Returns all memos in the database, in a form that
    can be inserted directly in the 'session' object.
    """
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ):

        del record['_id']
        record['date'] = arrow.get(record['date']).isoformat()
        records.append(record)

    return records 



if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0", debug=True)

    

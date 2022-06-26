# App name: heroku-app-status-api
# Version: 1.0.1
# Author: hamid0740
# License: MIT
# Github: https://github.com/hamid0740/heroku-app-status-api
#
# Modules & Libraries
import os
from flask import Flask, request

# Defining & configuring Flask app
app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# Root with no format error
@app.route("/")
def index():
  answer = {
    "OK": False,
    "message": "No format",
    "help": "Good format: %sAPI_KEY/APP_NAME" % request.url_root
  }
  return answer

# Bad format error
@app.errorhandler(404)
def not_found(e):
  answer = {
    "OK": False,
    "message": "Bad format",
    "help": "Good format: %sAPI_KEY/APP_NAME" % request.url_root
  }
  return answer

# Unknown error
@app.errorhandler(Exception)
def global_error(e):
  answer = {
    "OK": False,
    "message": "Unknown error",
    "code": e.code,
    "help": "Report issue: https://github.com/hamid0740/heroku-app-status"
  }
  return answer

# JSON API creation
@app.route("/<api_key>/<app_name>")
def api(api_key, app_name):
  try:
    output = (os.popen("HEROKU_API_KEY='%s' heroku ps -a %s" % (api_key, app_name.lower()))).read()
    if output:
      lines = [l for l in output.split("\n") if l]
      if not lines[0].startswith("=== "):
        lines = (lines[:2] + lines[4:])
        if lines[2].startswith("No dynos on "):
          answer = {
            "OK": True,
            "message": "No dynos",
            "access_level": "owner",
            "remaining": lines[0].split(": ")[-1],
            "used": lines[1].split(": ")[-1],
            "dynos": []
          }
        else:
          dynos = []
          for i in range(2, len(lines), 2):
            dynos += [{
              "command": " ".join(lines[i].split(": ")[1].split(" ")[:-1]),
              "name": lines[i+1].split(": ")[0],
              "type": lines[i+1].split(": ")[0].split(".")[0],
              "state": lines[i+1].split(": ")[1].split(" ")[0],
              "full_time": " ".join(lines[i+1].split(": ")[1].split(" ")[1:])
            }]
          answer = {
            "OK": True,
            "message": "Found dynos",
            "access_level": "owner",
            "remaining": lines[0].split(": ")[-1],
            "used": lines[1].split(": ")[-1],
            "dynos": dynos
          }
      else:
        if lines[0].startswith("No dynos on "):
          answer = {
            "OK": True,
            "message": "No dynos",
            "access_level": "collaborator",
            "dynos": []
          }
        else:
          dynos = []
          for i in range(0, len(lines), 2):
            dynos += [{
              "command": " ".join(lines[i].split(": ")[1].split(" ")[:-1]),
              "name": lines[i+1].split(": ")[0],
              "type": lines[i+1].split(": ")[0].split(".")[0],
              "state": lines[i+1].split(": ")[1].split(" ")[0],
              "full_time": " ".join(lines[i+1].split(": ")[1].split(" ")[1:])
            }]
          answer = {
            "OK": True,
            "message": "Found dynos",
            "access_level": "collaborator",
            "dynos": dynos
          }
    else:
      answer = {
        "OK": True,
        "message": "No Access",
        "access_level": "no_access"
      }
  except:
    answer = {
      "OK": False,
      "message": "Unknown error",
      "help": "Report issue: https://github.com/hamid0740/heroku-app-status"
    }
  return answer

# Flask app run
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8443")))

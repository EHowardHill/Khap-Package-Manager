from flask import Flask, request
from json import loads

with open("config.json", "r") as f:
    config = loads(''.join(f.readlines()))

app = Flask(__name__)

@app.route("/", methods=["GET"])
def primary():

    action = request.args.get('action')

    if action == "install":
        package = request.args.get('package')
        info = request.args.get('info')
        return config[package]["binaries"][info]["link"]
    
    elif action == "search":
        package = request.args.get('package')
        info = request.args.get('info')

        packages = [
            p + '\t' + config[p]["binaries"][info]["version"] for p in config.keys() if info in config[p]["binaries"].keys() and (package in p or p in package)
        ]

        return '\n'.join(packages)
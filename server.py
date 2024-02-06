import json
from pathlib import Path

import flask
import numpy as np
from flask import Flask

app = Flask(__name__)

@app.route("/event/<event_id>")
def event(event_id):
    event_dir = Path("events") / event_id
    with open(event_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
    return flask.render_template("index.html", client_config=metadata)

@app.route("/xy/<event_id>/<channel>")
def xy(event_id, channel):
    event_dir = Path("events") / event_id
    # Assume file has correct dtype!
    XY = np.load(event_dir / f"{channel}.npy")
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response

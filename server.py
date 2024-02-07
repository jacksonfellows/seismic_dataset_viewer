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

@app.route("/")
def index():
    event_info = {}
    for event_dir in Path("events").iterdir():
        event_id = event_dir.name
        with open(event_dir / "metadata.json", "r") as f:
            event_m = json.load(f)
            event_info[event_id] = {
                "reference_channel": event_m["reference_channel"],
                "trace_start_time": event_m["trace_start_time"]
            }
    # Sort by trace_start_time.
    event_info_render = list(sorted(
        [dict(event_id=k, reference_channel=v["reference_channel"], trace_start_time=v["trace_start_time"]) for k,v in event_info.items()],
        key=lambda x: x["trace_start_time"]
    ))
    return flask.render_template("home.html", event_info=event_info_render)

@app.route("/save_picks/<event_id>", methods=["POST"])
def save_picks(event_id):
    save_info = flask.request.json
    print(f"{save_info=}")
    return {}                   # Need to return a non-None response.

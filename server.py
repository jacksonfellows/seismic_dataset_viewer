import json
import sqlite3
from pathlib import Path

import flask
import numpy as np
from flask import Flask

app = Flask(__name__)


# DB functions:


def get_picks(event_id):
    with sqlite3.connect("picks.db") as cur:
        res = cur.execute(
            "SELECT channel_id, pick_sample, MAX(created_time) FROM picks WHERE event_id = ? GROUP BY channel_id;",
            (event_id,),
        )
        return {row[0]: row[1] for row in res}


def get_num_picks(event_id):
    with sqlite3.connect("picks.db") as cur:
        # This count could be off if we have null picks (i.e. a pick was overwritten w/ a null pick).
        res = cur.execute(
            "SELECT COUNT() FROM (SELECT * from picks WHERE event_id = ? GROUP BY channel_id);",
            (event_id,),
        )
        return res.fetchone()[0]


def do_save_picks(event_id, trace_start_time, picks):
    current_picks = get_picks(event_id)
    new_picks = {
        channel_id: pick_sample
        for channel_id, pick_sample in picks.items()
        if current_picks.get(channel_id) != pick_sample
    }
    rows = [
        (event_id, channel_id, trace_start_time, pick_sample)
        for channel_id, pick_sample in new_picks.items()
    ]
    with sqlite3.connect("picks.db") as cur:
        cur.executemany(
            "INSERT INTO picks (event_id, channel_id, trace_start_time, pick_sample) VALUES (?, ?, ?, ?);",
            rows,
        )


# Routes:


@app.route("/event/<event_id>")
def event(event_id):
    event_dir = Path("events") / event_id
    with open(event_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
    metadata["picks"] = get_picks(event_id)
    return flask.render_template("index.html", client_config=metadata)


@app.route("/xy/<event_id>/<channel>")
def xy(event_id, channel):
    event_dir = Path("events") / event_id
    # Assume file has correct dtype!
    Y = np.load(event_dir / f"{channel}.npy")
    X = np.linspace(0, 120, len(Y), dtype=Y.dtype)
    XY = np.concatenate((X, Y), axis=None)
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response


@app.route("/")
def index():
    event_info_render = []
    for event_dir in Path("events").iterdir():
        event_id = event_dir.name
        with open(event_dir / "metadata.json", "r") as f:
            event_m = json.load(f)
            event_info_render.append(
                dict(
                    event_id=event_id,
                    reference_channel=event_m["reference_channel"],
                    trace_start_time=event_m["trace_start_time"],
                    n_reference_picks=len(event_m["reference_picks"]),
                    n_picks=get_num_picks(event_id),
                )
            )
    return flask.render_template("home.html", event_info=event_info_render)


@app.route("/save_picks/<event_id>", methods=["POST"])
def save_picks(event_id):
    event_dir = Path("events") / event_id
    with open(event_dir / "metadata.json", "r") as f:
        metadata = json.load(f)
    trace_start_time = metadata["trace_start_time"]
    picks = flask.request.json["picks"]
    do_save_picks(event_id, trace_start_time, picks)
    return {}  # Need to return a non-None response.

import json
from pathlib import Path

import flask
import numpy as np
import seisbench.data
from flask import Flask

app = Flask(__name__)


dataset = seisbench.data.PNWExotic()

# Routes:


@app.route("/trace/<trace_name>")
def event(trace_name):
    return flask.render_template("trace.html", trace_name=trace_name)


@app.route("/xy/<trace_name>")
def xy(trace_name):
    SAMPLING_RATE = 100
    i = dataset.metadata[dataset.metadata["trace_name"] == trace_name].iloc[0]["index"]
    Y = dataset.get_waveforms(i).astype("<f")[0]
    X = np.linspace(0, Y.shape[-1] / SAMPLING_RATE, Y.shape[-1]).astype("<f")
    XY = np.concatenate((X, Y), axis=None)
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response


@app.route("/")
def index():
    head = dataset.metadata.head(100)
    table_html = head.to_html(index=False, table_id="t")
    return flask.render_template("home.html", table_html=table_html)

import flask
import numpy as np
import pandas as pd
import seisbench.data
from flask import Flask

app = Flask(__name__)


# dataset = seisbench.data.WaveformDataset(
#     "/Users/jackson/seismoslide/pnw_all", component_order="Z"
# )
dataset = seisbench.data.WaveformDataset(
    "/Users/jackson/seismoslide/inference_test", component_order="Z"
)
SAMPLING_RATE = 100


def get_trace_metadata(trace_name):
    return dataset.metadata[dataset.metadata["trace_name"] == trace_name].iloc[0]


# Routes:


@app.route("/trace/<trace_name>")
def event(trace_name):
    m = get_trace_metadata(trace_name)
    P_s = m.trace_P_arrival_sample / SAMPLING_RATE
    S_s = m.get("trace_S_arrival_sample")
    if S_s:
        S_s /= SAMPLING_RATE
    CC = dict(
        trace_name=trace_name,
        picks=[dict(pick_s=P_s, color="red"), dict(pick_s=S_s, color="blue")],
        components=list(dataset.component_order),
    )
    metadata_html = m.to_frame().to_html(header=False)
    return flask.render_template("trace.html", CC=CC, metadata_html=metadata_html)


@app.route("/xy/<trace_name>/<component>")
def xy(trace_name, component):
    component_i = dataset.component_order.index(component)
    i = get_trace_metadata(trace_name)["index"]
    Y = dataset.get_waveforms(i, sampling_rate=SAMPLING_RATE).astype("<f")[component_i]
    X = np.linspace(0, Y.shape[-1] / SAMPLING_RATE, Y.shape[-1]).astype("<f")
    XY = np.concatenate((X, Y), axis=None)
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response


def make_link(trace_name):
    return f"<a href='/trace/{trace_name}'>{trace_name}</a>"


@app.route("/")
def index():
    head: pd.DataFrame = dataset.metadata.head(1000)
    table_html = head.to_html(
        index=False, table_id="t", formatters=dict(trace_name=make_link), escape=False
    )
    return flask.render_template("home.html", table_html=table_html)

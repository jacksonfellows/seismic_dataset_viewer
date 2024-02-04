import flask
import numpy as np
from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/xy/<i>")
def testxy(i):
    XY = np.load(f"XY_{i}.npy")
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response

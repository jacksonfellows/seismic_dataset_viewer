import flask
import numpy as np
from flask import Flask

app = Flask(__name__)

XY = np.load("XY_test.npy")

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/testxy")
def testx():
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response

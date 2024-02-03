import flask
import numpy as np
from flask import Flask

app = Flask(__name__)

X = np.linspace(0,10,50,dtype="float32")
Y = np.sin(X)
XY = np.concatenate((X, Y), axis=None)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/testxy")
def testx():
    response = flask.make_response(XY.tobytes())
    response.headers.set("Content-Type", "application/octet-stream")
    return response

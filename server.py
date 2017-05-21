#!/usr/bin/env python

'''
server.py
Flask server for recommender.py API
'''

from flask import Flask  # type: ignore
from flask_cors import CORS  # type: ignore
from flask import Response
from recommender import Recommender
from decorator import decorator
import json
import brotli

rec = Recommender()

app = Flask(__name__)
CORS(app)


@decorator
def brotlify(f, *args, **kwargs):
    """Brotli Flask Response Decorator"""

    data = f(*args, **kwargs)

    if isinstance(data, Response):
        content = data.data
    else:
        content = data

    deflated_data = brotli.compress(content)

    if isinstance(data, Response):
        data.data = deflated_data
        data.headers['Content-Encoding'] = 'br'
        data.headers['Content-Length'] = str(len(data.data))

        return data

    return deflated_data


@app.route("/movies")
@brotlify
def movies() -> Response:
    return Response(
        json.dumps(rec.get_movies()),
        mimetype='application/json'
    )


@app.route("/recommend/<string:title>")
@brotlify
def recommend(title: str) -> Response:
    return Response(
        json.dumps(rec.recommend(title)),
        mimetype='application/json'
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=5000)

#!/usr/bin/env python

import ast
import io
from typing import Dict

import flask

from predictor import inference

app = flask.Flask(__name__)


@app.route("/ping", methods=["GET"])
def ping() -> flask.Response:
    """Determine if the container is working and healthy."""
    # You can insert a functional health check here
    # For example: try to load a saved model and return True
    # if no errors occurred.
    health = True
    status = 200 if health else 404
    mt = "application/json"
    return flask.Response(response="\n", status=status, mimetype=mt)


@app.route("/invocations", methods=["POST"])
def process_request() -> flask.Response:
    """
    Get JSON of input information (metadata) and return an inference.
    """
    data = None

    if flask.request.data is None:
        return flask.Response(
            response="Data is empty", status=420, mimetype="text/plain"
        )
    if flask.request.content_type == "text/json":
        data = flask.request.data.decode("utf-8")
        data = ast.literal_eval(data)
    elif flask.request.content_type == "application/json":
        data = flask.request.get_json(force=True)
    else:
        return flask.Response(
            response="This predictor only supports JSON data",
            status=415,
            mimetype="text/plain",
        )

    return handle_request(data)


def handle_request(data: Dict) -> flask.Response:
    """
    Handles the payload dictionary `data`
    """
    keys = data.keys()
    if "config" in keys and "params" in keys:
        params = data["params"]
        # support for missing names
        names = [f"item {i}" for i in range(20, 0, -1)]
        _config = data["config"]
        # filter out blank column names, replace them with generic "item X"
        _data = {}
        for item in params:
            key = item["name"] if item["name"] != "" else names.pop()
            _data[key] = item

        # DO SOMETHING WITH DATA HERE:
        output_df = inference(_config, _data)

        out = io.StringIO()
        output_df.to_csv(out, header=True, index=False)
        result_str = out.getvalue()
        status = 200
        mt = "text/csv"
        return flask.Response(response=result_str, status=status, mimetype=mt)

    return flask.Response(
        response="Invalid request format. Try again?",
        status=404,
        mimetype="text/plain",
    )

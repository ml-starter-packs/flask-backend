# flask-backend

sagemaker-compatible flask API

This example API attempts to estimate the amount of payroll costs ($) and
number of shifts that would need to be scheduled for analysts to process
documents in some queue of work.

# Instructions

We are going to rely on docker to serve this (there are some Linux assumptions in `serve.py`):

Start the server locally:

```bash
make local
```

Start the server with docker:

```bash
make serve
```

Then to test the API in a separate shell (or `Ctrl-Z`, `bg` and use the same shell):

```bash
make tests
```

Extra fun: upload the resulting `test.csv` to [hiplot](https://facebookresearch.github.io/hiplot/_static/hiplot_upload.html) to visualize the result of the calculation that was just performed.

# Debugging / Developing

This can be helpful for making edits while keeping `flask` running.
Flask will look for `app.py` and run it when `flask run` is called.

```bash
pip install -r requirements.txt
cd model
flask run --host 0.0.0.0 --port 1337
```

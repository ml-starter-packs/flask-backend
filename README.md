# flask-backend
sagemaker-compatible flask API

# Instructions

We are going to rely on docker to serve this (there are some Linux assumptions in `serve.py`):

```bash
make
```


# Debugging / Developing
This can be helpful for making edits while keeping `flask` running.
Flask will look for `app.py` and run it when `flask run` is called.

```bash
pip install -r requirements.txt
cd model
flask run --host 0.0.0.0 --port 1337
```

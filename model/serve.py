#!/usr/bin/env python

# This file implements the API shell.
# You don't necessarily need to modify it for various algorithms.
# It starts nginx and gunicorn with the correct configurations and
# then waits until gunicorn exits.
#
# The flask server is specified to be the app object in wsgi.py
#
# We set the following parameters:
#
# Parameter             Environment Variable     Default Value
# ---------             --------------------     -------------
# number of workers     MODEL_SERVER_WORKERS     the number of CPU cores
# timeout               MODEL_SERVER_TIMEOUT     60 seconds

from __future__ import print_function
import multiprocessing
import os
import signal
import subprocess
import sys

cpu_count = multiprocessing.cpu_count()

model_server_timeout = os.environ.get("MODEL_SERVER_TIMEOUT", 60)
model_server_workers = int(os.environ.get("MODEL_SERVER_WORKERS", cpu_count))


def sigterm_handler(nginx_pid, gunicorn_pid):
    try:
        os.kill(nginx_pid, signal.SIGQUIT)
    except OSError:
        pass
    try:
        os.kill(gunicorn_pid, signal.SIGTERM)
    except OSError:
        pass

    sys.exit(0)


def start_server():
    print(f"Starting server with {model_server_workers} workers.")

    # link the log streams to stdout/err so that
    # they will be logged to the container logs
    subprocess.check_call(["ln", "-sf", "/dev/stdout", "/var/log/nginx/access.log"])
    subprocess.check_call(["ln", "-sf", "/dev/stderr", "/var/log/nginx/error.log"])

    nginx = subprocess.Popen(["nginx", "-c", "/opt/program/nginx.conf"])
    gunicorn = subprocess.Popen(
        [
            "gunicorn",
            "--timeout",
            str(model_server_timeout),
            "-k",
            "gevent",
            "-b",
            "unix:/tmp/gunicorn.sock",
            "-w",
            str(model_server_workers),
            "wsgi:app",
        ]
    )

    # sets handler (second argument) for the signal SIGTERM (first argument).
    # The handler should be a callable which takes two arguments (hence `a`, `b`),
    # and it is called with two arguments: the signal number and current stack frame.
    # Neither of these are relevant to us, so we define a dummy handler which kills
    # the two processes we have started (nginx and gunicorn) regardless of `a`/`b`.
    # Basically, we are hard-coding "kill these two processes if you get a SIGTERM"
    def handler(a, b):
        return sigterm_handler(nginx.pid, gunicorn.pid)

    signal.signal(signal.SIGTERM, handler)

    # If either subprocess exits, so do we.
    pids = set([nginx.pid, gunicorn.pid])
    while True:
        pid, _ = os.wait()
        if pid in pids:
            break

    sigterm_handler(nginx.pid, gunicorn.pid)
    print("API server exiting")


# The main routine just invokes the start function.
if __name__ == "__main__":
    start_server()

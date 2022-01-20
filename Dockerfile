# Build an image that can do inference in AWS SageMaker
# This is a Python 3 image that uses the nginx, gunicorn, flask stack
# for serving inferences in a stable way.
FROM debian:bullseye-slim
WORKDIR /opt/program
# Set some environment variables. PYTHONUNBUFFERED keeps Python from buffering our standard
# output stream, which means that logs can be delivered to the user quickly. PYTHONDONTWRITEBYTECODE
# keeps Python from writing the .pyc files which are unnecessary in this case. We also update
# PATH so that the  serve program is found when the container is invoked.
ENV PYTHONUNBUFFERED=TRUE
ENV PYTHONDONTWRITEBYTECODE=TRUE
ENV PATH="/opt/program:${PATH}"

# Get basic dependencies
RUN apt-get -y update && apt-get install -y --no-install-recommends \
         build-essential \
         python3-pip \
         python3-dev \
         nginx \
         ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# overwrite the link to system python and upgrade pip
RUN ln -s /usr/bin/python3 /usr/bin/python \
    && pip3 install --upgrade pip

COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt && \
        rm -rf /root/.cache


# Set up the program in the image
COPY model/ /opt/program

EXPOSE 1337
CMD ./serve.py

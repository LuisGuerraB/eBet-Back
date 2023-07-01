# This is a slim Debian image with Python
FROM python:3.9-slim-buster

# Copy and install requirements
WORKDIR /root/lguerra

COPY requirements.txt /root/lguerra

RUN echo "export PYTHONPATH=$PYTHONPATH:/root/lguerra" > /root/.bashrc

RUN export PYTHONPATH=. && \
    python -m pip install --upgrade pip && \
    pip install "gunicorn==20.0.*" && \
    pip install -r requirements.txt -U

COPY . /root/lguerra

CMD gunicorn --bind 0.0.0.0:30888 --workers=1 --threads 8 --timeout 0 app:app

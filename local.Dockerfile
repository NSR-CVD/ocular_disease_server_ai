FROM python:3.10.10

WORKDIR /flask-docker

RUN pip install --no-cache --upgrade pip setuptools

RUN apt-get update

RUN apt-get install libgl1 -y

RUN apt-get install ffmpeg libsm6 libxext6 -y

ENV TZ=Asia/Bangkok

COPY requirement.txt requirement.txt

RUN pip install -r requirement.txt

RUN pip install --upgrade pip 

RUN pip install --upgrade tensorflow

COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development
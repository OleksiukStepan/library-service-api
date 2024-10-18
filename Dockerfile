FROM python:3.12.7-alpine3.20

LABEL maintainer="vladislav.tsybuliak@gmail.com"

ENV PYTHONBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

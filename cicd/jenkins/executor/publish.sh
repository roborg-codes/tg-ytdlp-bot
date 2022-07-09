#!/bin/env bash

TAG=roborgcodes/jenkins-executor-python:latest
TARGET=.
# TARGET=https://github.com/roborg-codes/tg-ytdlp-bot#main:cicd/jenkins/executor/

docker build -t "$TAG" "$TARGET" && \
    docker push "$TAG"

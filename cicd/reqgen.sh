#!/bin/env sh

set -xe

# Install the packages if needed
# $ pip install pipreqs pip-tools

pipreqs --savepath=requirements.in && \
    pip-compile && \
    rm ./requirements.in

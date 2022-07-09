FROM python:3.9 AS gt-ytdlp-bot

ENV PIP_DEFAULT_TIMEOUT=100
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PIP_NO_CACHE_DIR=off
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONHASHSEED=random
ENV PYTHONUNBUFFERED=1

ENV BOT_USERNAME="bot"
ENV BOT_HOME="/home/${BOT_USERNAME}"
ENV PATH="${BOT_HOME}/.local/bin:$PATH"

USER root
RUN apt-get update \
    && apt-get install -y python3 python3-pip python-dev build-essential python3-venv \
    && useradd -rms /bin/bash -u 1001 $BOT_USERNAME
ADD . $BOT_HOME
RUN chown -R $BOT_USERNAME:$BOT_USERNAME $BOT_HOME

USER $BOT_USERNAME
WORKDIR $BOT_HOME
RUN pip3 install -r requirements.txt && chmod +x ./main.py
CMD ["python3", "./main.py"];

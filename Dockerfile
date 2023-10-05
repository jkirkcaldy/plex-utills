FROM python:3.11.5-slim-bullseye



LABEL maintainer="JKirkcaldy"
LABEL support = "https://github.com/jkirkcaldy/plex-utills"
LABEL discord = "https://discord.gg/z3FYhHwHMw"

SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt upgrade -y && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    wget \
    nginx \
    nano \
    git \
    python3-dev \
    python3-venv \
    gcc \
    supervisor
WORKDIR /
RUN wget https://mediaarea.net/repo/deb/repo-mediaarea_1.0-21_all.deb
RUN dpkg -i repo-mediaarea_1.0-21_all.deb 
RUN apt install -y  mediainfo redis  \
	&& rm -rf /var/lib/apt/lists/* && apt autoremove && apt clean
RUN rm repo-mediaarea_1.0-21_all.deb


WORKDIR /plex-utils

ENV VIRTUAL_ENV=/plex-utils
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ENV CELERY_APP='plex_utils'

ENV ENABLE_REDIS='no'

RUN python3 -m venv $VIRTUAL_ENV

RUN pip install --upgrade pip
RUN pip install --upgrade setuptools
RUN pip install --upgrade wheel
RUN pip install --upgrade twine

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt 

COPY --chown=www-data:root . .

RUN chmod 777 -R /plex-utils/static
RUN chmod 777 -R /plex-utils/templates

RUN chmod +x entrypoint.sh
RUN chmod +x start.sh
RUN chmod +x prestart.sh



ARG TZ=Europe/London
ENV TZ="${TZ}"
EXPOSE 80 5000
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]

ENTRYPOINT ["/plex-utils/entrypoint.sh"]
CMD ["/plex-utils/start.sh"]

FROM python:3.9-bullseye

LABEL maintainer="JKirkcaldy"
LABEL support = "https://github.com/jkirkcaldy/plex-utills"
LABEL discord = "https://discord.gg/z3FYhHwHMw"

WORKDIR /app
COPY ./start.sh .
RUN chmod +x start.sh
COPY supervisord-debian.conf /etc/supervisor/conf.d/supervisord.conf
COPY app/static/dockerfiles/default /etc/nginx/sites-enabled/default


ARG TZ=Europe/London
ARG UID=1000
ARG GID=1000

ENV UID="${UID}"
ENV GID="${GID}"

RUN groupadd -g "${GID}" python \
  && useradd --create-home --no-log-init -u "${UID}" -g "${GID}" python
USER python

COPY ./app ./app
COPY ./main.py .
COPY ./requirements.txt .
COPY ./start.sh .
COPY ./version .
COPY . /app/

# Install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -Ur requirements.txt
RUN pip install git+https://github.com/AnthonyBloomer/tmdbv3api.git




RUN wget https://mediaarea.net/repo/deb/repo-mediaarea_1.0-21_all.deb
RUN dpkg -i repo-mediaarea_1.0-21_all.deb
RUN apt update && apt upgrade -y && apt install -y supervisor mediainfo nginx ffmpeg libsm6 libxext6 nano \
&& rm -rf /var/lib/apt/lists/*


ENV TZ="${TZ}"
EXPOSE 80 5000
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]

CMD ["/app/start.sh"]

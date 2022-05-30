FROM python:3.9-bullseye

LABEL maintainer="JKirkcaldy"
LABEL support = "https://github.com/jkirkcaldy/plex-utills"
LABEL discord = "https://discord.gg/z3FYhHwHMw"

WORKDIR /app
COPY ./app ./app
COPY ./main.py .
COPY ./requirements.txt .
COPY ./start.sh .
COPY ./version .


# Install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
EXPOSE 5000
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
RUN wget https://mediaarea.net/repo/deb/repo-mediaarea_1.0-19_all.deb
RUN dpkg -i repo-mediaarea_1.0-19_all.deb
RUN apt-get update && apt-get install -y supervisor mediainfo nginx ffmpeg libsm6 libxext6 nano \
&& rm -rf /var/lib/apt/lists/*
COPY supervisord-debian.conf /etc/supervisor/conf.d/supervisord.conf
COPY app/static/dockerfiles/default /etc/nginx/sites-enabled/default

ENV NGINX_MAX_UPLOAD 0
ENV NGINX_WORKER_PROCESSES 1
ENV LISTEN_PORT 80


RUN chmod +x start.sh

ENV TZ=Europe/London

CMD ["/app/start.sh"]

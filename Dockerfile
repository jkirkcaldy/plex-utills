FROM python:3.9.16-slim-bullseye

LABEL maintainer="JKirkcaldy"
LABEL support = "https://github.com/jkirkcaldy/plex-utills"
LABEL discord = "https://discord.gg/z3FYhHwHMw"


COPY app/static/dockerfiles/default /etc/nginx/sites-enabled/default
RUN apt update && apt upgrade -y && apt install -y wget git
RUN wget https://mediaarea.net/repo/deb/repo-mediaarea_1.0-21_all.deb
RUN dpkg -i repo-mediaarea_1.0-21_all.deb
RUN apt install -y  mediainfo nginx ffmpeg libsm6 libxext6 nano \
&& rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./start.sh .
RUN chmod +x start.sh











COPY ./app ./app
COPY ./main.py .
COPY ./requirements.txt .
COPY ./version .
# Install requirements
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -Ur requirements.txt
RUN pip install git+https://github.com/AnthonyBloomer/tmdbv3api.git





ARG TZ=Europe/London
ENV TZ="${TZ}"
EXPOSE 80 5000
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]

CMD ["/app/start.sh"]

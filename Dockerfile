FROM debian/stretch-slim:latest
LABEL author="Jkirkcaldy"

RUN apt update && apt install python3 python3-venv python3-pip supervisor nginx mediainfo nano -y
RUN useradd -s /bin/bash plex-utills
USER plex-utills
WORKDIR /app
COPY . .
RUN python3 -m venv venv
RUN source venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
EXPOSE 80

RUN exec 'start.sh'

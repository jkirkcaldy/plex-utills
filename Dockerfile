FROM debian:bullseye-slim
LABEL author="Jkirkcaldy"

RUN apt update && apt install python3 python3-venv python3-pip supervisor nginx mediainfo nano -y
RUN useradd -s /bin/bash plex-utills
#USER plex-utills
WORKDIR /app
COPY . .
#RUN chown plex-utills:plex-utills /app -R
RUN python3 -m venv venv
RUN venv/bin/pip install -r requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt

VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
EXPOSE 80
RUN cp /app/app/static/dockerfiles/default /etc/nginx/sites-enabled/default 
RUN cp /app/app/static/dockerfiles/plex-utills.conf /etc/supervisor/conf.d/plex-utills.conf 
RUN chmod +x ./start.sh
RUN chown -R plex-utills:plex-utills ./
USER plex-utills

ENTRYPOINT [ "./start.sh"]



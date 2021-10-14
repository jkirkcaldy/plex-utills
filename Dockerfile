FROM python:3.9.6-slim-bullseye
LABEL author="Jkirkcaldy"

RUN apt update && apt install mediainfo nano -y
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
EXPOSE 5000

ENTRYPOINT ["/bin/bash", "/app/init.sh"]

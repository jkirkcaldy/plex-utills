FROM tiangolo/uwsgi-nginx-flask:python3.9
LABEL author="Jkirkcaldy"

RUN apt update && apt install mediainfo nano -y
WORKDIR /app

ENV STATIC_PATH /app/app/static
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
EXPOSE 5000



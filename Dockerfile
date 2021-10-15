FROM tiangolo/uwsgi-nginx-flask:python3.9
LABEL author="Jkirkcaldy"

RUN apt update 
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata mediainfo nano
WORKDIR /app
ENV TZ=Europe/London
ENV STATIC_PATH /app/app/static
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
VOLUME [ "/logs" ]
EXPOSE 5000



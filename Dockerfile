FROM python:3.9.6-slim
LABEL author="Jkirkcaldy"

RUN apt update && apt install ffmpeg -y
RUN apt install tzdata -y
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
#workdir /config
CMD /bin/bash ./init.sh
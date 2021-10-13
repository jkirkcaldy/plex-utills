FROM python:3.9.6-slim
LABEL author="Jkirkcaldy"

RUN apt update && apt install ffmpeg -y
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
EXPOSE 5000
#workdir /config
CMD /bin/bash ./init.sh

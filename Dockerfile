FROM python:3.9.6-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
VOLUME [ "/films" ]
VOLUME [ "/config" ]
#workdir /config
CMD /bin/bash ./init.sh

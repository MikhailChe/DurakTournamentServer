FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt update && apt install -y git python3.7 python3-pip libpython3.7-dev vim && python3.7 -m pip install --upgrade pip virtualenv && rm -rf /var/lib/apt/lists/*
COPY . /app
WORKDIR /app/gameserver
RUN virtualenv -p python3.7 --clear /app/env
RUN /app/env/bin/pip install --upgrade -r requirements.txt && /app/env/bin/python manage.py migrate
VOLUME /db
CMD ["/app/env/bin/python", "manage.py", "runserver", "0.0.0.0:80"]
EXPOSE 80
FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt-get update && \
    apt-get install -y python3.7 python3-pip libpython3.7-dev vim && \
    python3.7 -m pip install --upgrade pip virtualenv && rm -rf /var/lib/apt/lists/* && mkdir /app && mkdir -p /db
WORKDIR /app/gameserver
RUN virtualenv -p python3.7 --clear /app/env
ENV DATABASE_SQLITE_PATH=/db/db.sqlite3
COPY . /app
RUN /app/env/bin/pip install --upgrade -r ../requirements.txt
VOLUME /db

CMD ["/app/env/bin/python", "manage.py", "runserver", "0.0.0.0:80"]
EXPOSE 80
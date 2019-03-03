FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt-get update && apt-get install -y git python3.7 python3-pip libpython3.7-dev vim && python3.7 -m pip install --upgrade pip virtualenv && mkdir -p /srv
WORKDIR /srv
RUN virtualenv -p python3.7 --clear env
ADD requirements.txt requirements.txt
RUN /srv/env/bin/pip install --upgrade -r requirements.txt

ADD gameserver /srv/gameserver
WORKDIR /srv/gameserver
RUN /srv/env/bin/python manage.py migrate

CMD ["/srv/env/bin/python", "manage.py", "runserver", "0.0.0.0:80"]
EXPOSE 80
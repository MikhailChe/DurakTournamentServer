FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt-get update && apt-get -y upgrade && apt-get install -y git python3.7 python3-pip python3-dev libc6-dev libv8-dev libpython3-dev libpython3.7-dev && python3.7 -m pip install --upgrade pip
RUN mkdir -p /srv && cd /srv && git clone https://github.com/MikhailChe/DurakTournamentServer.git
WORKDIR /srv/DurakTournamentServer
RUN pip install --upgrade virtualenv
RUN virtualenv -p python3.7 --clear env
RUN /srv/DurakTournamentServer/env/bin/pip install --upgrade -r requirements.txt
WORKDIR /srv/DurakTournamentServer/gameserver
RUN /srv/DurakTournamentServer/env/bin/python manage.py migrate

ENTRYPOINT /srv/DurakTournamentServer/env/bin/python manage.py runserver 0:80
EXPOSE 80
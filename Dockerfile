FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt-get update && apt-get -y upgrade && apt-get install -y git python3.7 && python3.7 -m pip install --upgrade pip && python3.7 -m pip install --upgrade virtualenv
RUN mkdir /srv && cd /srv && git clone https://github.com/MikhailChe/DurakTournamentServer.git
WORKDIR /srv/DurakTournamentServer
RUN python3 -m venv --clear env && source ./env/bin/activate && pip install --upgrade -r requirements.txt && pushd gameapi && python manage.py migrate && python manage.py createsuperuser && popd
WORKDIR /srv/DurakTournamentServer/gameapi
ENTRYPOINT source ./env/bin/activate && pushd gameapi && python manage.py runserver 0:80
EXPOSE 80
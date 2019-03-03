FROM ubuntu:18.04
MAINTAINER Mikhail Chernoskutov <mikhail.chernoskutov@gmail.com>
RUN apt update && apt install -y git python3.7 python3-pip libpython3.7-dev vim && python3.7 -m pip install --upgrade pip virtualenv && mkdir -p /srv
ADD . /srv
WORKDIR /srv/gameserver
RUN virtualenv -p python3.7 --clear /srv/env
RUN /srv/env/bin/pip install --upgrade -r requirements.txt && /srv/env/bin/python manage.py migrate

CMD ["/srv/env/bin/python", "manage.py", "runserver", "0.0.0.0:80"]
EXPOSE 80
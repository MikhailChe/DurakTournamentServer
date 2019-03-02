#!/usr/bin/env bash
virtualenv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pushd gameserver
python manage.py migrate
popd
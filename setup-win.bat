py -3 -m venv --clear env
env\Scripts\python.exe -m pip install -r requirements.txt
env\Scripts\python.exe -m pip install -r requirements.txt
pushd gameserver
..\env\Scripts\python.exe manage.py migrate
..\env\Scripts\python.exe manage.py createsuperuser
popd
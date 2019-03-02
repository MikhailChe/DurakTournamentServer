virtualenv -p python3.7 --clear env
./env/Scripts/activate.bat
pip install --upgrade pip
pip install -r requirements.txt
pushd gameserver
python manage.py migrate
popd

setlocal enabledelayedexpansion
if %errorlevel% neq 0 exit /b %errorlevel%
python3 -m venv --clear env
if %errorlevel% neq 0 exit /b %errorlevel%
./env/Scripts/activate.bat
if %errorlevel% neq 0 exit /b %errorlevel%
pip install --upgrade pip
if %errorlevel% neq 0 exit /b %errorlevel%
pip install -r requirements.txt
if %errorlevel% neq 0 exit /b %errorlevel%
pushd gameserver
if %errorlevel% neq 0 exit /b %errorlevel%
python manage.py migrate
if %errorlevel% neq 0 exit /b %errorlevel%
popd
if %errorlevel% neq 0 exit /b %errorlevel%

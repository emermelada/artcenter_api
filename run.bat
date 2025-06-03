@echo off
echo Activando entorno virtual...
call venv\Scripts\activate.bat

echo Lanzando servidor Flask...
set FLASK_APP=app.py
set FLASK_ENV=development
flask run

pause

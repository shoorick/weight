server: app.py
	env FLASK_APP=app.py flask run --debugger

prepare:
	pip install -r requirements.txt

server: app.py
	export FLASK_APP=app.py
	env FLASK_ENV=development flask run

prepare:
	pip install -r requirements.txt

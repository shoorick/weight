server: app.py
	export FLASK_APP=app.py
	flask run --debug

prepare:
	pip install -r requirements.txt

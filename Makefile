server:
	flask --debug run

prepare:
	pip install -r requirements.txt

test:
	pytest -v

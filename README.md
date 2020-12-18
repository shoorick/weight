Weight
======

Record digital data (weight for example), store it, ~~and then draw graphs~~ (_not yet implemented_).

Purpose
-------

There is a just [Flask](https://flask.palletsprojects.com/) example, nothing more :-)

Requirements
------------

* Python 3
* pip
* flask

How to run
----------

### Initialize database

```bash
cd db
python init.py
```

### Run application in development mode

```bash
# Choose application and set mode
export FLASK_APP=app
export FLASK_ENV=development

# Run development server
flask run
```
Hit `Ctrl+C` to stop the server.

See also
--------

[How To Make a Web Application Using Flask in Python 3](https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3) by Abdelhadi Dyouri


Author
------

Alexander Sapozhnikov
http://shoorick.ru
<shoorick@cpan.org>

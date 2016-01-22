# simple-blog

##step 1

bulid and run virtual environments

$ virtualenv venv

* Linux：

$ source venv/bin/activate

* Windows：

$ venv\Scripts\activate

##step 2

run requirements file

(venv) $ pip install -r requirements.txt

##step 3

open config.py to set envirment variables

* line 9  FLASKY_MAIL_SENDER
* line 10 FLASKY_ADMIN
* line 21 MAIL_SERVER
* line 22 MAIL_PORT
* line 23 MAIL_USE_LTS
* line 24 MAIL_USERNAME
* line 25 MAIL_PASSWORD

##step 4

* launch application in shell to create database tables

(venv) $ python manage.py shell

>>> from manage import db

>>> db.create_all()

* insert roles

>>> Role.insert_roles()

* launch application on localhost

(venv) $ python manage.py runserver --host localhost

##step 5

navigate to  http://localhost:5000/

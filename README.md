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

set envirment variables

* Linux:

export MAIL_SERVER='smtp.emailserver.com' 

export MAIL_PORT=xx

export FLASKY_MAIL_SENDER='example@mail.com'

export FLASKY_ADMIN='example@mail.com'

export MAIL_SENDER='example@mail.com'

export MAIL_PASSWORD='emailpassword'

* Windows:

set MAIL_SERVER='smtp.mail.com'

set MAIL_PORT=xx

set FLASKY_MAIL_SENDER='example@mail.com'

set FLASKY_ADMIN='example@mail.com'

set MAIL_SENDER='example@mail.com'

set MAIL_PASSWORD='emailpassword'

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

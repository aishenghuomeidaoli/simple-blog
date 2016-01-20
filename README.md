# simple-blog

##step 1

bulid virtual environments

$ virtualenv venv

##step 2

run requirements file

(venv) $ pip install -r requirements.txt

##step 3

set envirment variables

* Linux:

explore MAIL_SERVER='smtp.mail.com' 

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

launch application on localhost

(venv) $ python hello.py runserver --host localhost

##step 5

navigate to  http://localhost:5000/

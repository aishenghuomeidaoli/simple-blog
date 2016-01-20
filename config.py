import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
	FLASKY_MAIL_SENDER='aishenghuomeidaoli@163.com' or \
	'Flasky Admin'+'<'+os.environ.get('FLASKY_MAIL_SENDER')+'>' 
	FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN') or 'aishenghuomeidaoli@163.com'
	FLASKY_POSTS_PER_PAGE = 20
	FLASKY_FOLLOWERS_PER_PAGE = 50
	FLASK_COMMENTS_PER_AGE=10
	
	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG=True
	MAIL_SERVER='smtp.163.com' or os.environ.get('MAIL_SERVER')
	MAIL_PORT=25 or os.environ.get('MAIL_PORT')
	MAIL_USE_LTS=True
	MAIL_USERNAME=os.environ.get('MAIL_USERNAME') or 'aishenghuomeidaoli@163.com'
	MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD') or 'zhujiawei'
	SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
	TESTING=True
	SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
	WTF_CSRF_ENABLED=False

class  ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
	'sqlite:///' + os.path.join(basedir, 'data.sqlite')

config={
	'development':DevelopmentConfig,
	'testing':TestingConfig,
	'production':ProductionConfig,
	
	'default':DevelopmentConfig
}
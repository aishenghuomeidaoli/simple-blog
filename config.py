#-*- coding:UTF-8 -*-
import os
basedir=os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	FLASKY_MAIL_SUBJECT_PREFIX='爱生活-blog'
	FLASKY_MAIL_SENDER='爱生活-blog 管理员'+'<aishenghuomeidaoli@163.com>' 
	FLASKY_ADMIN='aishenghuomeidaoli@163.com'#os.environ.get('FLASKY_ADMIN')
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
	MAIL_USERNAME='aishenghuomeidaoli@163.com'#os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD='zhujiawei1234567'#os.environ.get('MAIL_PASSWORD')
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

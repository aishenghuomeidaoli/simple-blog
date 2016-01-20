import unittest
import json
import re
from base64 import b64encode
from flask import url_for
from app import create_app, db
from app.models import User, Role, Post, Comment

class APITestCase(unittest.TeestCase):
	def get_api_headers(self,username,password):
		return {
		'Authorization':'Basic' + b64encode((username+':'+password).encode('utf-8')).decode('utf-8'),
		'Accept':'application/json',
		'Content-Type':'application/json'
		}

	def test_no_auth(self):
		response=self.client.get(url_for('api.get_posts'),content_type='application/json')
		self.assertTrue(response.status_code==401)

	def test_posts(self):
		#添加一个用户
		r=Role.query.filter_by(name='User').first()
		self.assertIsNotNone(r)
		u=User(email='1435806541@qq.com',password='cat',confirmed=True,role=r)
		db.session.add(u)
		db.session.commit()

		#写一篇文章
		response=self.client.post(
			url_for('api.new_post'),
			headers=self.get_auth_header('1435806541@qq.com','zhujiawei'),
			data=json.dumps({'body':'body of the *blog* post'}))
		self.assertTrue(response.status_code==201)
		url=response.headers.get('Location')
		self.assertIsNotNone(url)
		
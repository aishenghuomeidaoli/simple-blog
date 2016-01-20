import unittest
from app import create_app, db
from app.models import User, Role

class FlaskClientTestCase(unittest.TestCase):
	def setUp(self):
		self.app=create_app('testing')
		self.app_context=self.app.app_context()
		self.app_context.push()
		db.create_all()
		Role.insert_roles()
		self.client=self.app.test_client(user_cookies=True)

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.app_context.pop()

	def test_home_page(self):
		response=self.client.get(url_for('main.index'))
		self.assertTrue('Stranger' in response.get_data(as_text=True))

	def test_register_and_login(self):

		#注册新账户
		response=self.client.post(url_for('auth.register'),data={
			'email':'1435806541@qq.com',
			'username':'1435806541',
			'password':'zhujiawei',
			'password2':'zhujiawei'
			})
		self.assertTrue(response.status_code==302)

		#使用注册账户登录
		response=self.client.post(url_for('auth.login'),data={
			'email':'1435806541@qq.com',
			'password':'zhujiawei'
			},
			follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertTrue(re.search('Helllo,\s+1435806541',data))
		self.assertTrue('该账户尚未认证' in data)

		#发送确认令牌
		user=User.query.filter_by(email='1435806541@qq.com').first()
		token=user.generate_confirmation_token()
		response=self.client.get(url_for('auth.confirm',token=token),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertTrue('账户已认证'in data)

		#退出
		response=self.client.get(url_for('auth.logout'),follow_redirects=True)
		data=response.get_data(as_text=True)
		self.assertTrue('成功退出'in data)
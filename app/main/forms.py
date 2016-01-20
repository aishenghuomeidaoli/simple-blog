#-*- coding:UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, PasswordField
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from flask.ext.pagedown.fields import PageDownField
from ..models import Role, User
from app.exceptions import ValidationError

class EditProfileForm(Form):
    name = StringField('真实名字', validators=[Length(0, 64)])
    location = StringField('地点', validators=[Length(0, 64)])
    about_me = TextAreaField('简介')
    submit = SubmitField('提交')

class EditProfileAdminForm(Form):
	email=StringField('邮箱', validators=[Required(), Length(1,64), Email() ])
	username = StringField('用户名', validators=[Required(), Length(1,64), 
		Regexp('^[A-Za-z0-9_.]*$',0,'Usernames must have only letters, ''numbers, dots or underscores')])
	confirmed=BooleanField('认证状态')
	role=SelectField('角色', coerce=int)
	name=StringField('真实名字', validators=[Length(0,64)])
	location=StringField('地点',validators=[Length(0,64)])
	about_me=TextAreaField('简介')
	submit = SubmitField('提交')

	def __init__(self, user, *args, **kwargs):
		super(EditProfileAdminForm, self).__init__(*args, **kwargs)
		self.role.choices=[(role.id,role.name) for role in Role.query.order_by(Role.name).all()]
		self.user=user

	def validate_email(self, field):
		if field.data != self.user.email and \
		User.query.filter_by(email=field.data).first():
			raise ValidationError('该邮箱已被注册')

	def validate_username(self, field):
		if field.data != self.username and \
		User.query.filter_by(username=field.data).first():
			raise ValidationError('该用户名已被使用')

class PostForm(Form):
	body=PageDownField("发表文章?", validators=[Required()])
	submit=SubmitField('提交')

class NameForm(Form):
	name=StringField('你叫什么名字？', validators=[Required()])
	submit=SubmitField('提交')

class ForgetpasswordForm(Form):
	email=StringField('邮箱',validators=[Required(),Email()])
	submit=SubmitField('确定')

class ResetpasswordForm(Form):
	password=PasswordField('密码', validators=[Required(),EqualTo('password2',message='两次输入不一致')])
	password2 = PasswordField('密码再次确认', validators=[Required()])
	submit=SubmitField('确定')

class CommentForm(Form):
	body=StringField('',validators=[Required()])
	submit=SubmitField('提交')
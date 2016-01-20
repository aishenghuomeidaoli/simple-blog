#-*- coding:UTF-8 -*-
from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from  ..models import User
from app.exceptions import ValidationError

class LoginForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('密码', validators=[Required()])
    remember_me=BooleanField('记住我')
    submit=SubmitField('登录')

class RegistrationForm(Form):
    email = StringField('邮箱', validators=[Required(), Length(1,64), Email()])
    username=StringField('用户名', validators=[Required(), Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$',0,'Usernames must have only letters,'
                                                                                 'numbers, dots or underscores')])
    password = PasswordField('密码', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('密码确认', validators=[Required()])
    submit=SubmitField('注册')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已被使用')

class ChangepasswordForm(Form):
    oldpassword = PasswordField('旧密码', validators=[Required()])
    newpassword = PasswordField('新密码', validators=[Required(),EqualTo('newpassword2',message='两次输入不一致')])
    newpassword2 = PasswordField('新密码再次确认', validators=[Required()])
    submit=SubmitField('确定')

class ChangeemailForm(Form):
    email=StringField('输入新邮箱',validators=[Required(),Length(1,64),Email(),EqualTo('email2',message='两次输入不一致')])
    email2=StringField('邮箱再次确认',validators=[Required(),Length(1,64),Email()])
    submit=SubmitField('确定')
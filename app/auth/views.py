#-*- coding:UTF-8 -*-
from flask import render_template, redirect, request, url_for, flash
from . import auth
from flask.ext.login import login_required, login_user, current_user, logout_user
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangepasswordForm, ChangeemailForm
from ..email import send_email
from .. import db
import sys, hashlib

reload(sys)
sys.setdefaultencoding('utf8')

@auth.route('/login', methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('邮箱或密码不可用')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已登出')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET','POST'])#       发送确认邮件
def register():
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()#        确认令牌需要用到id，所以要提交数据库赋予id，且不能延后
        token=user.generate_confirmation_token()#加载加密令牌
        send_email(user.email,'账户认证','auth/email/confirm',user=user,token=token)
        flash('认证邮件已发送至您的邮箱，请查收。')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)

@auth.route('/secret')
@login_required
def secret():
    return '仅登录用户可用，请登录。'

#避免邮件丢失，定义重新发送确认邮件的路由
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token=current_user.generate_confirmation_token()
    send_email(current_user.email,'账户认证','auth/email/confirm',user=current_user,token=token)
    flash('一封新的认证邮件已发送至您的邮箱，请查收。')
    return redirect(url_for('main.index'))

@auth.route('/confirm/<token>')#        确认用户账户
@login_required#        此修饰器用来保护此路由，要求用户登陆后才能执行视图函数
def confirm(token):
    if current_user.confirmed:#     检查用户是否确认过
        return redirect(url_for('main.index'))#     若确认过，重定向至首页
    if current_user.confirm(token):
        flash('您的账户已认证。')
    else:
        flash('认证连接不可用。')
    return redirect(url_for('main.index'))

@auth.before_app_request#       此修饰器用来使蓝笨中before_request钩子对程序全局使用
def before_request():#      flask提供的before_request钩子，在用户确认之前，完成某些操作。
    #满足一下条件时before_app_request拦截权限的获取
    if current_user.is_authenticated :#        用户已登录
        current_user.ping()#每次用户登录都调用ping方法，用于更新last_seen值
        if not current_user.confirmed \
        and request.endpoint[:5] != 'auth.'\
        and request.endpoint != 'static':#      用户为确认，且请求的端点不在认证蓝本中
            return redirect(url_for('auth.unconfirmed'))#       重定向至/auth/unconfirmed路由

@auth.route('/unconfirmed')#        用来显示账户确认的相关信息
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')

@auth.route('/change-password', methods=['GET','POST'])#更改用户密码,前提：用户登录且已确认；方法：输入旧密码、新密码。
@login_required
def change_password():
    form = ChangepasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.oldpassword.data):
            current_user.passsword=form.newpassword.data
            db.session.add(current_user)
            flash('更改密码成功！')
            return redirect(url_for('main.index'))
        else:
            flash('旧密码输入错误')
    return render_template('auth/changepassword.html',form=form)

@auth.route('/change-email',methods=['GET','POST'])
@login_required
def change_email():
    form=ChangeemailForm()
    if form.validate_on_submit():
        if form.email.data==current_user.email:
            flash('输入的邮箱与当前邮箱一致，请输入新邮箱')
        else:
            current_user.email=form.email.data
            current_user.confirmed=False
            current_user.avatar_hash=hashlib.md5(current_user.email.encode('utf-8')).hexdigest()
            db.session.add(current_user)
            flash('更改邮箱成功！')
            return redirect(url_for('main.index'))
    return render_template('auth/changeemail.html',form=form)
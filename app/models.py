#-*- coding:UTF-8 -*-
from werkzeug.security import generate_password_hash,check_password_hash
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer#生成带有过期时间的JSON web签名
from flask import current_app, request, url_for
import hashlib, bleach
from datetime import datetime
from markdown import markdown
from app.exceptions import ValidationError

class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    users=db.relationship('User',backref='role',lazy='dynamic')
    default=db.Column(db.Boolean,default=False,index=True)
    permissions=db.Column(db.Integer)

    @staticmethod
    def insert_roles():
        roles={
        'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
        'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|Permission.MODERATE_COMMENTS,False),
        'Administrator':(0xff,False)
        }#定义角色
        for r in roles:
            role=Role.query.filter_by(name=r).first()#查找角色
            if role is None:#如无角色则创建
                role=Role(name=r)
            role.permissions=roles[r][0]#为permission属性赋值
            role.default=roles[r][1]#为default属性赋值
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>'%self.name
        
class Follow(db.Model):
    __tablename__='follows'
    follower_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    followed_id=db.Column(db.Integer,db.ForeignKey('users.id'),primary_key=True)
    timestamp=db.Column(db.DateTime,default=datetime.utcnow)

class User(UserMixin,db.Model):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(64),unique=True,index=True)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    password_hash=db.Column(db.String(128))
    email=db.Column(db.String(64),unique=True,index=True)
    confirmed=db.Column(db.Boolean,default=False)
    avatar_hash = db.Column(db.String(32))
    posts=db.relationship('Post', backref='author', lazy='dynamic')

    #用户信息字段
    name=db.Column(db.String(64))
    location=db.Column(db.String(64))
    about_me=db.Column(db.Text())#      db.Text()不需指定最大长度
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)#      注册时间默认为当前时间，default可以调用函数，不必写成utcnow()
    last_seen=db.Column(db.DateTime(),default=datetime.utcnow)#     初始值为当前时间，每次访问后都被刷新，在User模型中用ping方法实现

    followed=db.relationship('Follow',foreign_keys=[Follow.follower_id],
        backref=db.backref('follower',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')
    followers=db.relationship('Follow',foreign_keys=[Follow.followed_id],
        backref=db.backref('followed',lazy='joined'),lazy='dynamic',cascade='all,delete-orphan')
    comments=db.relationship('Comment',backref='author',lazy='dynamic')

    def follow(self,user):
        if not self.is_following(user):
            f=Follow(follower=self,followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self,user):
        f=self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self,user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self,user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
        
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            u=User(email=forgery_py.internet.email_address(),
                username=forgery_py.internet.user_name(True),
                password=forgery_py.lorem_ipsum.word(),
                confirmed=True,
                name=forgery_py.name.full_name(),
                location=forgery_py.address.city(),
                about_me=forgery_py.lorem_ipsum.sentence(),
                member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except  IntegrityError:
                db.session.rollback()

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email==current_app.config['FLASKY_ADMIN']:#若邮箱地址与FLASK_ADMIN中保存的一致，则被设置为管理员
                self.role=Role.query.filter_by(permissions=0xff).first()
            if self.role is None:#否则默认为User角色
                self.role=Role.query.filter_by(default=True).first()
        if  self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        self.follow(self)

    #若角色中包含请求的所有权限位，返回True
    def can(self, permissions):
                return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):#        检查管理员权限
        return self.can(Permission.ADMINISTER)

    def ping(self):#创建ping方法，用于更新last_seen值
        self.last_seen=datetime.utcnow()
        db.session.add(self)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @property
    def followed_posts(self):
        return Post.query.join(Follow,Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)
    

    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)

    def generate_confirmation_token(self,expiration=3600):#     生成加密令牌，默认过期时间为3600秒
        s=Serializer(current_app.config['SECRET_KEY'],expiration)#      参数为密钥，过期时间
        return s.dumps({'confirm':self.id})#dumps先为s生成加密签名，然后在再对self.di和签名进行序列化，最后生成令牌字符串

    def generate_auth_token(self,expiration):
        s=Serializer(current_app.config['SECRET_KEY'],expires_in=expiration)
        return s.dumps({'id':self.id})

    @staticmethod
    def verify_auth_token(token):
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)
        except:
            return None
        return User.query.get(data['id'])
        
    def confirm(self,token):#       检验令牌，及令牌中id是否与已登录用户匹配
        s=Serializer(current_app.config['SECRET_KEY'])
        try:
            data=s.loads(token)#        token为令牌字符串，loads()检验签名和过期时间，若通过，返回原始数据即token，未通过抛出异常
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed=True
        db.session.add(self)
        return True

    def __repr__(self):
        return '<User %r>' %self.username

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url='https://secure.gavatar.com/avatar'
        else:
            url='http://www.gravatar.com/avatar'
        hash=self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash} ?s={size} $d={default} &r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)
    def to_json(self):
        json_user={
        'url':url_for('api.get_post',id=self.id,_external=True),
        'username':self.username,
        'member_since':self.member_since,
        'last_seen':self.last_seen,
        'posts':url_for('api.get_user_posts',id=self.id,_external=True),
        'followed_posts':url_for('api.get_user_followed_posts',id=self.id,_external=True),
        'post_count':self.posts.count()
        }
        return json_user


@login_manager.user_loader#加载用户的回调函数
def load_user(user_id):
    return User.query.get(int(user_id))


class Permission:
    FOLLOW=0x01
    COMMENT=0x02
    WRITE_ARTICLES=0x04
    MODERATE_COMMENTS=0x08
    ADMINISTER=0x80


#继承自Flask-Login中的AnonymousUserMixin类，将其设置为未登录用户的current_user的值
#这样不用检查用户是否登陆，即可调用current_user.can()、current_user.is_administrator()方法
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user=AnonymousUser


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html=db.Column(db.Text)
    comments=db.relationship('Comment',backref='post',lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','blockquote','code','em','i','li','ol','pre','strong','ul','h1','h2',
        'h3','p']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),tags=allowed_tags,strip=True))
    
    @staticmethod
    def from_json(json_post):
        body=json_post.get('body')
        if body is None or body=='':
            raise ValidationError('文章没有内容')
        return Post(body=body)
        
    def to_json(self):
        json_post={
        'url':url_for('api.get_post',id=self.id,_external=True),
        'body':self.body,
        'body_html':self.body_html,
        'timestamp':self.timestamp,
        'author':url_for('api.get_user',id=self.author_id,_external=True),
        'comments':url_for('api.get_post_comments',id=self.id,_external=True),
        'comment_count':self.comments.count()
        }
        return json_post

db.event.listen(Post.body,'set',Post.on_change_body)

class Comment(db.Model):
    __tablename__='comments'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text)
    body_html=db.Column(db.Text)
    timestamp=db.Column(db.DateTime,index=True,default=datetime.utcnow)
    disabled=db.Column(db.Boolean)
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    post_id=db.Column(db.Integer,db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','code','em','i','strong']
        target.body_html=bleach.linkify(bleach.clean(markdown(value,output_format='html'),
            tags=allowed_tags,strip=True))
db.event.listen(Comment.body,'set',Comment.on_changed_body)
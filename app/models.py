from app import db,config
from werkzeug.security import generate_password_hash,check_password_hash
from . import  login_manager
from flask import current_app
from flask_login import UserMixin,current_user,AnonymousUserMixin
from datetime import datetime
from markdown import markdown
import bleach

class Permission:
    #权限常量（位标志，通过位计算组合权限），暂时有5个权限
    FOLLOW=0x01   #关注用户
    COMMENT=0x02   #在他人的文章中发表评论
    WRITE_ARTICLES=0x04  #写文章
    MODERATE_COMMENTS=0x08  #管理他人发表的评论
    ADMINSTER=0x80        #管理员权限


class Role(db.Model):
    __tablename__='roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(64),unique=True)
    default=db.Column(db.Boolean,default=False,index=True)
    permissons=db.Column(db.Integer)

    user_list=db.relationship('User',backref='role',lazy='dynamic')

    @staticmethod
    def insert_roles():
        #对角色表导入角色

        roles={
            'User':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES,True),
            'Moderator':(Permission.FOLLOW|Permission.COMMENT|Permission.WRITE_ARTICLES|
                         Permission.MODERATE_COMMENTS,False),
            'Adminstrator':(0xff,False)
        }
        # 需要导入的角色（包含了permission和default)
        for r in roles:
            role=Role.query.filter_by(name=r).first()
            if role is None:
                role=Role(name=r)
            role.permissons=roles[r][0]
            role.default=roles[r][1]
            db.session.add(role)
        db.session.commit()


    def __repr__(self):
        return '<Role %r>' % self.name

class Follow(db.Model):
    __tablename__ = "follows"

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    byfollowed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class User(db.Model,UserMixin):
    #继承UserMixin多了四个方法：is_authenticated、is_active、is_anonymos、get_id
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(64),unique=True,index=True)
    username=db.Column(db.String(64),unique=True,index=True)
    password_hash=db.Column(db.String(128))
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'))
    name=db.Column(db.String(64))
    location=db.Column(db.String(64))
    about_me=db.Column(db.Text())
    member_since=db.Column(db.DateTime(),default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    head_portrait=db.Column(db.String(128))



    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role=Role.query.filter_by(permissons=0xff).first()
            else:
                self.role=Role.query.filter_by(default=True).first()


    #用户关注相关属性和方法

    post_list = db.relationship('Post', backref='user', lazy='dynamic')
    follower_list = db.relationship('Follow', foreign_keys=[Follow.byfollowed_id],
                                            backref=db.backref('byfollowed', lazy='joined'),
                                            lazy='dynamic',
                                            cascade='all,delete-orphan'
                                            )
    byfollowed_list = db.relationship('Follow', foreign_keys=[Follow.follower_id],
                                              backref=db.backref('follower', lazy='joined'),
                                              lazy='dynamic',
                                              cascade='all,delete-orphan'
                                              )

    @property
    def byfollowed_posts(self):
            return Post.query.join(Follow,Follow.byfollowed_id==Post.author_id)\
                .filter(Follow.follower_id==self.id)

    # 2.关注的辅助方法

    def follow(self,user):
        #点击关注
        if not self.is_following(user):
            f=Follow(follower=self,byfollowed=user)
            db.session.add(f)
            db.session.commit()
    def unfollow(self,user):
        #取消关注
        f=self.byfollowed_list.filter_by(byfollowed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self,user):
        return self.byfollowed_list.filter_by(byfollowed_id=user.id).first() is not None

    def is_follow_by(self,user):
        return self.follower_list.filter_by(follower_id=user.id).first() is not None




    #密码字段和密码检测
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    @password.setter
    def password(self,password):
        self.password_hash=generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash,password)



    #权限验证相关
    def can(self,permissions):
        return self.role is not None and (self.role.permissons & permissions) ==permissions

    def is_adminstrator(self):
        return self.can(Permission.ADMINSTER)


    #刷新用户最后访问时间
    def ping(self):
        self.last_seen=datetime.utcnow()
        db.session.add(self)

     #头像文件名拼接图片链接

    def head_img(self):
        relative_url='/static/img/head_portrait/'+str(self.head_portrait)
        return relative_url


    def __repr__(self):
        return '<User %r>' % self.username


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u=User(email=forgery_py.internet.email_address(),
                   username=forgery_py.internet.user_name(),
                   password=forgery_py.lorem_ipsum.word(),
                   name=forgery_py.name.full_name(),
                   location=forgery_py.address.city(),
                   about_me=forgery_py.lorem_ipsum.sentence(),
                   member_since=forgery_py.date.date()
                   )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()










#匿名用户类
class AnonymousUser(AnonymousUserMixin):
    def can(self,permissions):
        return False
    def is_adminstrator(self):
        return False

login_manager.anonymous_user=AnonymousUser    #设置匿名用户



#加载用户的回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))








class Post(db.Model):
    __tablename__='posts'
    id=db.Column(db.Integer,primary_key=True)
    body=db.Column(db.Text())
    author_id=db.Column(db.Integer,db.ForeignKey('users.id'))
    timestamp=db.Column(db.DateTime(),default=datetime.utcnow)
    body_html=db.Column(db.Text())
    title=db.Column(db.Text())
    digest=db.Column(db.Text())

    def get_author(self):
        user=User.query.filter_by(id=self.author_id).first()
        return user



    @staticmethod
    def on_change_body(target,value,oldvalue,initiator):
        allowed_tags=['a','abbr','acronym','b','blockquote','code',
                      'em','i','li','ol','pre','strong','ul','h1',
                      'h2','h3','p']
        target.body_html=bleach.linkify(bleach.clean(
            markdown(value,output_format='html'),tags=allowed_tags,strip=True))

    @staticmethod
    def generate_fake(count=100):
        from random import  seed ,randint
        import forgery_py

        seed()
        user_count=User.query.count()
        for i in range(count):
            u=User.query.offset(randint(0,user_count-1)).first()
            p=Post(body=forgery_py.lorem_ipsum.sentences(randint(1,3)),
                    timestamp=forgery_py.date.date(True),
                    author_id=u.id)
            db.session.add(p)
            db.session.commit()

db.event.listen(Post.body,'set',Post.on_change_body)
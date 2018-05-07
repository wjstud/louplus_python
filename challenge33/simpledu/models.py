from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for

db = SQLAlchemy()

class Base(db.Model):
   # 不创建数据库，不要将此类当作 Model 类
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(),
                                        onupdate=datetime.utcnow())

class User(Base, UserMixin):
# 继承 UserMixin 主要是为了使用它提供的 is_authenticated property 方法判断用户是否是登录状态
    __tablename__ = 'user'
    """ 用数值表示角色, 方便判断是否有权限, 比如说有个操作要角色为员工
        及以上的用户才可以做, 那么只要判断 user.role >= ROLE_STAFF 就可
        以了, 数值之间设置了 10 的间隔是方便以后加入其他角色 """

    ROLE_USER = 10
    ROLE_STAFF = 20
    ROLE_ADMIN = 30

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    # 默认, sqlalchemy 会以字段名来定义列名, 但这里是 _password 所以需指定数据库表列名为 password
    _password = db.Column('password', db.String(256), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    job = db.Column(db.String(64))
    publish_courses = db.relationship('Course')

    def __repr__(self):
        return '<User: {}>'.format(self.username)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, orig_password):
        self._password = generate_password_hash(orig_password)

    def check_password(self, password):
        return check_password_hash(self._password, password)

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role == self.ROLE_STAFF
    
class Course(Base):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True, nullable=False)
    description = db.Column(db.String(256))
    image_url = db.Column(db.String(256))
    # ondelete='CASCADE' 表示如果用户被删除了，他的课程也删除
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL')) # 多对一关系
    author = db.relationship('User', uselist=False) # uselist=False 表示通过 relationship 引用时创建为对象而不是列表
    chapters = db.relationship('Chapter')

    def __repr__(self):
        return '<Course: {}>'.format(self.name)

    @property
    def url(self):
        return url_for('course.detail', course_id=self.id)

class Chapter(Base):
    __tablename__ = 'chapter'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True, nullable=False)
    description = db.Column(db.String(256))
    video_url = db.Column(db.String(256))
    video_duration = db.Column(db.String(24))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id', ondelete='CASCADE'))
    course = db.relationship('Course', uselist=False)

    def __repr__(self):
        return '<Chapter: {}>'.format(self.name)

    @property
    def url(self):
        return url_for('course.chapter', course_id=self.course.id, chapter_id=self.id)

class Live(Base):
    __tablename__ = 'live'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True)
    url = db.Column(db.String(256)) # 保存直播流地址
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'))
    user = db.relationship('User', uselist=False)
    
    def __repr__(self):
        return '<Live: {}>'.format(self.name)

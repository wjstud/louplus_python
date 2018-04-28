from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class Base(db.Model):
   # 不创建数据库，不要将此类当作 Model 类
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(),
                                        onupdate=datetime.utcnow())

class User(Base, UserMixin):
# 继承 UserMixin 可以使用 is_authenticated property 方法判断用户是否登录
    __tablename__ = 'user'

    # 利用数值表示角色 方便判断 和以后添加角色
    ROLE_USER = 10
    ROLE_STAFF = 20
    ROLE_ADMIN = 30

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    email = db.Column(db.String(64), unique=True, index=True, nullable=False)
    _password = db.Column('password', db.String(256), nullable=False)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    job = db.Column(db.String(64))
    publish_courses = db.relationship('Course')

    def __repr__(self):
        return '<User:{}>'.format(self.username)

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
    # ondelete='CASCADE' 表示如果用户被删除了，他的课程也删除
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # 多对一关系
    author = db.relationship('User', uselist=False) # uselist=False 表示通过 relationship 引用时创建为对象而不是列表

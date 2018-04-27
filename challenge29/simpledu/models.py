from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Base(db.Model):
   # 不创建数据库，不要将此类当作 Model 类
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(db.DateTime, default=datetime.utcnow(),
                                        onupdate=datetime.utcnow())

class User(Base):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), unique=True, index=True, nullable=False)
    publish_courses = db.relationship('Course')
    
class Course(Base):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True, nullable=False)
    # ondelete='CASCADE' 表示如果用户被删除了，他的课程也删除
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE')) # 多对一关系
    author = db.relationship('User', uselist=False) # uselist=False 表示通过 relationship 引用时创建为对象而不是列表

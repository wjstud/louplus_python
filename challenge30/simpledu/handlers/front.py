from flask import Blueprint, render_template, redirect, url_for, flash
from simpledu.models import Course, User
from simpledu.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user, login_required

front = Blueprint('front', __name__)

@front.route('/')
def index():
    courses = Course.query.all()
    return render_template('index.html', courses=courses)

@front.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        form.create_user()
        flash('注册成功, 请登陆! ', 'success')
        return redirect(url_for('.login')) # front.login 简写, 在同一个 Blueprint 下
    return render_template('register.html', form=form)

@front.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # 使用 flask-login 提供的 login_user 函数。它的使用也很简单，第一个参数是 User 对象，第二个参数是个布尔值，告诉 flask-login 是否需要记住该用户。
        login_user(user, form.remember_me.data)
        return redirect(url_for('.index'))
    return render_template('login.html', form=form)

@front.route('/logout')
@login_required # 退出登录功能只应该在用户登录的状态下使用，所以这里用 login_required 装饰器保护了这个路由
def logout():
    logout_user()
    flash('您已经退出登陆', 'success')
    return redirect(url_for('.index'))

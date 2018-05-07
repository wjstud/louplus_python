from flask import Blueprint, render_template
from simpledu.models import User

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/<username>')
def index(username):
    user = User.query.filter_by(username=username).first_or_404()
    #user = User.query.get_or_404(user_id) # get_or_404() 只支持主键, 所以不能放入 username
    return render_template('user.html', user=user)

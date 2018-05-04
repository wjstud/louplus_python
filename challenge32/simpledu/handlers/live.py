from flask import Blueprint, render_template, request, current_app
from simpledu.models import Live

live = Blueprint('live', __name__, url_prefix='/live')

@live.route('/')
def index():
    # 获取参数中传过来的页数
    page = request.args.get('page', default=1, type=int)
    """ 生成分页对象: 该对象的方法
    has_next: 如果还有下一页返回 True
    has_prev: 如果还有上一页返回 True
    items: 当页页面的所有 items，以课程页来说就是当页页面的课程列表
    iter_pages(): 迭代分页中的所有页数
    page: 当前页数
    pages: 总的页数
    prev_num: 上一页的页数
    next_num: 下一页的页数
    """
    pagination = Live.query.paginate(
            page=page,
            per_page=current_app.config['INDEX_PER_PAGE'], # 注意
            error_out=False # 如果设置为 True，那么发生错误时会引发 404
            )
    return render_template('live/index.html', pagination=pagination)

@live.route('/<int:live_id>')
def detail(live_id):
    live = Live.query.get_or_404(live_id)
    return render_template('live/detail.html', live=live)

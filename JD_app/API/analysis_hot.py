from model import *

analysis_hot = Blueprint('analysis_hot', __name__)


# 热点分析第1块，包括注册、登录、兑换、任务4个模块
@analysis_hot.route('/hot_spot_1', methods=['GET', 'POST'])
def hot_spot_1():
    sql_hot_all()
    res = sql_hot_spot_1()
    return res


# 热点分析第2块，阅读量和收藏量折线图
@analysis_hot.route('/hot_spot_2', methods=['GET', 'POST'])
def hot_spot_2():
    types = request.form.get('type')
    res = sql_hot_spot_2(types)
    return res


# 热点分析第3块，线上热门搜索和折线图
@analysis_hot.route('/hot_spot_3', methods=['GET', 'POST'])
def hot_spot_3():
    res = sql_hot_spot_3()
    return res


# 热点分析第4块，搜索排名
@analysis_hot.route('/hot_spot_4', methods=['GET', 'POST'])
def hot_spot_4():
    pn = request.form.get('pn')
    size = request.form.get('size')
    res = sql_hot_spot_4(pn, size)
    return res


# 热点分析第5块，文章阅读排名和文章收藏排名
@analysis_hot.route('/hot_spot_5', methods=['GET', 'POST'])
def hot_spot_5():
    types = request.form.get('type')
    res = sql_hot_spot_5(types)
    return res


# 热点分析第6块，阅读资讯占比
@analysis_hot.route('/hot_spot_6', methods=['GET', 'POST'])
def hot_spot_6():
    res = sql_hot_spot_6()
    return res


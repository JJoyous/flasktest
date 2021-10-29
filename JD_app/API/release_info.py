from model import *

release_info = Blueprint('release_info', __name__)


# 咨讯查询
@release_info.route('/info', methods=['POST'])
def info_inquire():
    art_title = request.form.get('art_title')  # 文章标题
    name = request.form.get('name')  # 操作人
    art_type = request.form.get('art_type')  # 文章类型
    time_s = request.form.get('time_s')  # 开始时间
    time_e = request.form.get('time_e')  # 结束时间
    pn = request.form.get('page_num')  # 页码
    size = request.form.get('page_size')  # 条数
    res = sql_info_sear(art_title, name, art_type, time_s, time_e, pn, size)
    return res


# 点击编辑资讯
@release_info.route('/info_edit', methods=['POST'])
def info_edit():
    info_id = request.form.get('id')
    res = sql_info_id(info_id)
    return res


# 编辑、新建保存文章
@release_info.route('/info_update', methods=['POST'])
def info_new():
    name = request.form.get('name')
    art_title = request.form.get('art_title')
    art_type = request.form.get('art_type')
    art_cont = request.form.get('art_cont')
    info_id = request.form.get('id')
    res = sql_info_update(info_id, name, art_title, art_type, art_cont)
    return res


# 发布文章
@release_info.route('/info_zt', methods=['POST'])
def info_zt():
    info_id = request.form.get('id')
    name = request.form.get('name')
    col = request.form.get('col')
    res = sql_info_status(info_id, name, col)
    return res


# 删除文章
@release_info.route('/info_del', methods=['POST'])
def info_del():
    info_id = request.form.get('id')
    res = sql_info_del(info_id)
    return res


# 上传图片
@release_info.route('/get_picture_new', methods=['POST'])
def get_picture_new():
    filepath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/imgs/'
    f = request.files['img_file']
    img = f.filename
    f.save(filepath + img)
    # path = "http://192.168.0.46:8089/imgs/" + "1" + '.jpg'
    path = "http://192.168.0.46:8089/imgs/" + img
    res = stand({"url": path})
    return res


# 视频上传分片处理
@release_info.route('/chunk', methods=['GET', 'POST'])
def index():  # 一个分片上传后被调用
    upload_file = request.files['file']
    task = request.form.get('task_md5')  # 获取文件唯一标识符
    chunk = request.form.get('cur_chunk')  # 获取该分片在所有分片中的序号
    filepath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/upload/'
    filename = '{0}{1}'.format(task, chunk)  # 构成该分片唯一标识符
    upload_file.save(filepath + '{0}'.format(filename))  # 保存分片到本地
    res = stand([])
    return res


# 切片视频整合
@release_info.route('/chunk_suc', methods=['GET', 'POST'])
def upload_suc():  # 所有分片均上传完后被调用
    filepath = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + '/upload/'
    chunks = request.form.get('chunks')  # 分片总数，判断文件是否分片
    target_filename = str_md5(request.form.get('file_name'))  # 获取上传文件的文件名
    task = request.form.get('task_md5')  # 获取文件的唯一标识符
    chunk = 1   # 分片序号
    if chunks == '1':
        upload_file = request.files['file']
        upload_file.save(filepath + '{0}.mp4'.format(target_filename))
    else:
        with open(filepath + '{0}.mp4'.format(target_filename), 'wb') as target_file:  # 创建新文件
            while True:
                try:
                    filename = filepath + '{0}{1}'.format(task, chunk)
                    source_file = open(filename, 'rb')  # 按序打开每个分片
                    target_file.write(source_file.read())  # 读取分片内容写入新文件
                    source_file.close()
                except IOError:
                    break
                chunk += 1
                os.remove(filename)  # 删除该分片，节约空间
    path = "http://192.168.0.46:8089/upload/" + target_filename + '.mp4'
    res = stand({"url": path})
    return res

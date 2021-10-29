import pymongo
import pymysql


# 连接database
def con_mysql():
    conn = pymysql.connect(host='74.6.7.123', user='yisa_oe', password='3B3488D10C4E2BA203852568B785FF51', database='',
                           charset='utf8')
    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor()
    # 定义要执行的SQL语句
    # 获取涉私/涉毒/吸毒的标签id
    sql = '''select '''
    # 执行SQL语句
    cursor.execute(sql)
    # 关闭光标对象
    cursor.close()
    # 关闭数据库连接
    conn.close()

# 遍历人员库,查询近三个月以来的涉私/涉毒/吸毒人员的身份证号码


# 遍历车主信息,mongo,根据上面的身份证号码查询相关的车主信息
def save_base_info():
    try:
        batch = 1000
        vehicle_data = {}

        myclient = pymongo.MongoClient("mongodb://74.6.7.124:27017")  # 连接MongoDB
        db = myclient['yisa_oe']  # 选择数据库
        collection = db['GAJT_VEHICLE_37']  # 选择表

        total = collection.estimated_document_count()  # 数据总条数
        print(total)
        iter_number = total // batch  # 总页数
        print(iter_number)

        for i in range(iter_number + 1):
            small_part = collection.find({}).limit(batch).skip(i * batch)
            for item in small_part:
                pass

    except:
        pass

# 对车主信息进行标签分类,入库
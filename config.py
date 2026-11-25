import os
from urllib.parse import quote_plus


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    """项目基础配置，数据库采用 MySQL。"""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'campus-books-dev-secret-key')

    # MySQL 连接参数，可通过环境变量覆盖，也可直接在下方修改默认值
    DB_USER = os.environ.get('MYSQL_USER', 'root')
    DB_PASSWORD = os.environ.get('MYSQL_PASSWORD', '123456')
    DB_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    DB_PORT = os.environ.get('MYSQL_PORT', '3306')
    DB_NAME = os.environ.get('MYSQL_DATABASE', 'campus_books')

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8mb4' % (
        DB_USER, quote_plus(DB_PASSWORD), DB_HOST, DB_PORT, DB_NAME
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,   # 断线重连，避免 MySQL 8 小时超时断链
        'pool_recycle': 3600,
        'pool_size': 5,
        'max_overflow': 10,
    }

    # 图书封面存放目录
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 单个文件不超过 5MB
    PER_PAGE = 12

    # 业务字典
    CATEGORIES = ['教材教辅', '文学小说', '计算机技术', '外语学习', '考研考证', '经济管理', '其他']
    CONDITIONS = ['全新', '九成新', '八成新', '七成新', '有笔记']
    BOOK_STATUS = {
        'on_sale': '在售',
        'reserved': '已预订',
        'sold': '已售出',
        'off_shelf': '已下架',
    }
    ORDER_STATUS = {
        'pending': '待确认',
        'completed': '已完成',
        'cancelled': '已取消',
    }

"""pytest 公共夹具：临时数据库、测试客户端与演示数据。

本文件只依赖项目自身的 app/config，不读取本机 MySQL 配置，
数据库固定使用临时目录下的 SQLite 文件，保证任何机器上都能直接跑。
"""

import os
import sys

import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app            # noqa: E402
from app.extensions import db         # noqa: E402
from app.models import Book, User     # noqa: E402
from config import Config             # noqa: E402


def _seed():
    """写入两个演示账号与三本在售图书。"""
    seller = User(username='seller01', nickname='卖书的小林',
                  student_id='202426000001', campus='瑶湖校区')
    seller.set_password('123456')
    buyer = User(username='buyer01', nickname='找书的阿哲',
                 student_id='202426000002', campus='瑶湖校区')
    buyer.set_password('123456')
    db.session.add_all([seller, buyer])
    db.session.flush()

    db.session.add_all([
        Book(title='数据结构（C 语言版）', author='严蔚敏', category='计算机技术',
             condition='九成新', price=22.0, original_price=45.0,
             description='书内干净', seller_id=seller.id),
        Book(title='高等数学（上册）', author='同济大学数学系', category='教材教辅',
             condition='八成新', price=18.0, original_price=49.8,
             description='有铅笔笔记', seller_id=seller.id),
        Book(title='活着', author='余华', category='文学小说',
             condition='全新', price=15.0, original_price=28.0,
             description='全新未拆封', seller_id=seller.id),
    ])
    db.session.commit()


@pytest.fixture
def app(tmp_path):
    class TestConfig(Config):
        TESTING = True
        SECRET_KEY = 'test-secret'
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(tmp_path / 'test.db')
        SQLALCHEMY_ENGINE_OPTIONS = {}
        UPLOAD_FOLDER = str(tmp_path / 'uploads')

    app = create_app(TestConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        _seed()

    yield app

    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    """返回一个登录函数，默认用 seller01 登录。"""
    def _login(username='seller01', password='123456'):
        return client.post('/login', data={'username': username, 'password': password},
                           follow_redirects=True)
    return _login

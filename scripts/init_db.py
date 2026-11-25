"""初始化 MySQL 数据库：建库、建表、写入演示数据。

用法（在项目根目录 E:\\xm 下执行）：
    python scripts/init_db.py

执行前请确认 MySQL 已启动，且 config.py 或环境变量中的账号密码正确。
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, BASE_DIR)

from sqlalchemy import create_engine, text  # noqa: E402

from config import Config  # noqa: E402


def create_database():
    """连接 MySQL 服务器（不指定库），创建数据库。"""
    server_uri = 'mysql+pymysql://%s:%s@%s:%s?charset=utf8mb4' % (
        Config.DB_USER, Config.DB_PASSWORD, Config.DB_HOST, Config.DB_PORT
    )
    engine = create_engine(server_uri, isolation_level='AUTOCOMMIT')
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE DATABASE IF NOT EXISTS `%s` "
            "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci" % Config.DB_NAME
        ))
    engine.dispose()
    print('[1/3] 数据库 %s 已就绪' % Config.DB_NAME)


def create_tables():
    from app import create_app
    from app.extensions import db

    app = create_app()
    with app.app_context():
        db.create_all()
    print('[2/3] 数据表已创建（users / books / orders）')


def seed_data():
    """写入演示数据，已存在数据时跳过。"""
    from app import create_app
    from app.extensions import db
    from app.models import User, Book

    app = create_app()
    with app.app_context():
        if User.query.count() > 0:
            print('[3/3] 已存在数据，跳过演示数据写入')
            return

        seller = User(username='seller01', nickname='卖书的小林', student_id='202426204001', campus='瑶湖校区')
        seller.set_password('123456')
        buyer = User(username='buyer01', nickname='找书的阿哲', student_id='202426204002', campus='瑶湖校区')
        buyer.set_password('123456')
        db.session.add_all([seller, buyer])
        db.session.flush()

        books = [
            Book(title='高等数学（上册）第七版', author='同济大学数学系', category='教材教辅',
                 condition='八成新', price=18.0, original_price=49.8,
                 description='重点章节有铅笔笔记，封面边角轻微磨损，不影响阅读。', seller_id=seller.id),
            Book(title='数据结构（C 语言版）', author='严蔚敏', category='计算机技术',
                 condition='九成新', price=22.0, original_price=45.0,
                 description='考研常用教材，书内干净，附赠手写知识点提纲。', seller_id=seller.id),
            Book(title='C Primer Plus（第 6 版）中文版', author='Stephen Prata', category='计算机技术',
                 condition='九成新', price=45.0, original_price=89.0,
                 description='自学 C 语言经典教材，仅翻阅过前四章。', seller_id=seller.id),
            Book(title='活着', author='余华', category='文学小说',
                 condition='全新', price=15.0, original_price=28.0,
                 description='买重了一本，全新未拆封。', seller_id=seller.id),
            Book(title='新视野大学英语 读写教程 2', author='郑树棠', category='外语学习',
                 condition='有笔记', price=12.0, original_price=42.0,
                 description='课文内有翻译笔记，配套听力材料已丢失。', seller_id=seller.id),
            Book(title='考研政治核心考案', author='徐涛', category='考研考证',
                 condition='七成新', price=10.0, original_price=59.0,
                 description='做过选择题，答案页有标记。', seller_id=seller.id),
            Book(title='西方经济学（微观部分）', author='高鸿业', category='经济管理',
                 condition='八成新', price=16.0, original_price=45.0,
                 description='课程用书，笔记集中在每章末尾。', seller_id=seller.id),
            Book(title='Python 编程：从入门到实践', author='Eric Matthes', category='计算机技术',
                 condition='九成新', price=35.0, original_price=89.0,
                 description='含项目实战部分，代码可正常运行，无笔记。', seller_id=seller.id),
        ]
        db.session.add_all(books)
        db.session.commit()
        print('[3/3] 演示数据写入完成：2 个用户、%d 本图书' % len(books))
        print('     演示账号：seller01 / buyer01，密码均为 123456')


if __name__ == '__main__':
    create_database()
    create_tables()
    seed_data()
    print('数据库初始化完成，可执行 python run.py 启动项目')

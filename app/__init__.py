import os

from flask import Flask, render_template

from app.extensions import db
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_class)

    # 上传目录需要存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)

    # 导入模型，保证建表时元数据已加载
    from app import models  # noqa: F401

    from app.routes.auth import auth_bp
    from app.routes.books import books_bp
    from app.routes.orders import orders_bp
    from app.routes.users import users_bp
    from app.routes.favorites import favorites_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(favorites_bp)

    # 模板全局变量与过滤器
    @app.context_processor
    def inject_globals():
        return {
            'CATEGORIES': app.config['CATEGORIES'],
            'CONDITIONS': app.config['CONDITIONS'],
            'SITE_NAME': '校园二手书交易平台',
        }

    @app.template_filter('money')
    def money_filter(value):
        try:
            return '%.2f' % float(value)
        except (TypeError, ValueError):
            return '0.00'

    @app.template_filter('short_time')
    def short_time_filter(value):
        if not value:
            return ''
        return value.strftime('%Y-%m-%d %H:%M')

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('error.html', code=404, message='页面不存在或已被移除'), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return render_template('error.html', code=413, message='上传的图片超过 5MB，请压缩后重试'), 413

    with app.app_context():
        # 数据表不存在时自动创建；数据库本身需先由 scripts/init_db.py 创建
        db.create_all()

    return app

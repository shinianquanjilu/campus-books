"""数据模型定义。

以 users / books / orders 三张表支撑“发布—浏览—下单—成交”主流程。
"""

from datetime import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(40), nullable=False)
    student_id = db.Column(db.String(20), unique=True, nullable=True)
    campus = db.Column(db.String(40), nullable=True)
    contact = db.Column(db.String(60), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    books = db.relationship('Book', back_populates='seller', lazy='dynamic')

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def __repr__(self):
        return '<User %s>' % self.username


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, index=True)
    author = db.Column(db.String(60), nullable=True)
    category = db.Column(db.String(20), nullable=False, index=True)
    condition = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Numeric(8, 2), nullable=False)
    original_price = db.Column(db.Numeric(8, 2), nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), default='on_sale', nullable=False, index=True)
    views = db.Column(db.Integer, default=0)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)

    seller = db.relationship('User', back_populates='books')
    orders = db.relationship('Order', back_populates='book', lazy='dynamic')

    @property
    def status_text(self):
        from flask import current_app
        return current_app.config['BOOK_STATUS'].get(self.status, self.status)

    @property
    def discount_text(self):
        if not self.original_price or self.original_price <= 0:
            return ''
        ratio = self.price / self.original_price * 10
        return '%.1f 折' % ratio


class Favorite(db.Model):
    """用户对图书的收藏记录。"""

    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref=db.backref('favorites', lazy='dynamic'))
    book = db.relationship('Book', backref=db.backref('favorites', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'book_id', name='uk_favorite_user_book'),
    )


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    order_no = db.Column(db.String(32), unique=True, nullable=False, index=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False, index=True)
    remark = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    book = db.relationship('Book', back_populates='orders')
    buyer = db.relationship('User', foreign_keys=[buyer_id])
    seller = db.relationship('User', foreign_keys=[seller_id])

    @property
    def status_text(self):
        from flask import current_app
        return current_app.config['ORDER_STATUS'].get(self.status, self.status)

"""FR-06 下单预订与订单流转的验收用例。"""

import pytest

from app.extensions import db
from app.models import Book, Order, User


def _book_id(title='数据结构（C 语言版）'):
    return Book.query.filter_by(title=title).first().id


def _create_order(client, book_id, remark='周三下午图书馆门口交易'):
    return client.post('/order/create/%d' % book_id, data={'remark': remark})


def _add_user(username, nickname):
    user = User(username=username, nickname=nickname)
    user.set_password('123456')
    db.session.add(user)
    db.session.commit()


def test_cannot_buy_own_book(client, login, app):
    login()  # seller01
    with app.app_context():
        book_id = _book_id()

    resp = _create_order(client, book_id)
    assert resp.status_code == 302
    text = client.get(resp.headers['Location']).get_data(as_text=True)
    assert '不能购买自己发布的图书' in text
    with app.app_context():
        assert Order.query.count() == 0


def test_create_order_reserves_book(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()

    resp = _create_order(client, book_id)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/orders/bought')

    with app.app_context():
        order = Order.query.one()
        assert order.status == 'pending'
        assert order.buyer_id != order.seller_id
        assert float(order.amount) == pytest.approx(22.0)
        assert Book.query.get(book_id).status == 'reserved'


def test_second_order_blocked_by_status(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)

    with app.app_context():
        _add_user('buyer02', '另一位买家')

    login('buyer02')
    resp = client.post('/order/create/%d' % book_id, follow_redirects=True)
    assert '该图书当前不可购买' in resp.get_data(as_text=True)
    with app.app_context():
        assert Order.query.count() == 1


def test_confirm_by_seller_completes_order(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)
    with app.app_context():
        order_id = Order.query.one().id

    login('seller01')
    resp = client.post('/order/%d/confirm' % order_id)
    assert resp.status_code == 302

    with app.app_context():
        assert Order.query.get(order_id).status == 'completed'
        assert Book.query.get(book_id).status == 'sold'


def test_confirm_by_buyer_forbidden(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)
    with app.app_context():
        order_id = Order.query.one().id

    resp = client.post('/order/%d/confirm' % order_id, follow_redirects=True)
    assert '只有卖家可以确认成交' in resp.get_data(as_text=True)
    with app.app_context():
        assert Order.query.get(order_id).status == 'pending'


def test_cancel_by_buyer_restores_book(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)
    with app.app_context():
        order_id = Order.query.one().id

    resp = client.post('/order/%d/cancel' % order_id)
    assert resp.status_code == 302

    with app.app_context():
        assert Order.query.get(order_id).status == 'cancelled'
        assert Book.query.get(book_id).status == 'on_sale'


def test_cancel_completed_order_forbidden(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)
    with app.app_context():
        order_id = Order.query.one().id

    login('seller01')
    client.post('/order/%d/confirm' % order_id)

    login('buyer01')
    resp = client.post('/order/%d/cancel' % order_id, follow_redirects=True)
    assert '该订单当前状态不支持取消' in resp.get_data(as_text=True)
    with app.app_context():
        assert Order.query.get(order_id).status == 'completed'


def test_third_party_cannot_cancel(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id()
    _create_order(client, book_id)
    with app.app_context():
        order_id = Order.query.one().id
        _add_user('other01', '无关的用户')

    login('other01')
    resp = client.post('/order/%d/cancel' % order_id, follow_redirects=True)
    assert '无权操作该订单' in resp.get_data(as_text=True)
    with app.app_context():
        assert Order.query.get(order_id).status == 'pending'

"""FR-03 发布、FR-04 检索、FR-05 详情、FR-07 我的书架的验收用例。"""

from app.extensions import db
from app.models import Book


def _book_id(title):
    return Book.query.filter_by(title=title).first().id


def _new_book_form(**kwargs):
    data = {
        'title': 'Python 编程：从入门到实践', 'author': 'Eric Matthes',
        'category': '计算机技术', 'condition': '九成新',
        'price': '35', 'original_price': '89', 'description': '无笔记',
    }
    data.update(kwargs)
    return data


def test_index_shows_only_on_sale(client, app):
    with app.app_context():
        book = Book.query.filter_by(title='活着').first()
        book.status = 'off_shelf'
        db.session.commit()

    text = client.get('/').get_data(as_text=True)
    assert '数据结构（C 语言版）' in text
    assert '活着' not in text


def test_index_filter_keyword_and_category(client):
    text = client.get('/?q=数据结构&category=计算机技术').get_data(as_text=True)
    assert '数据结构（C 语言版）' in text
    assert '高等数学（上册）' not in text


def test_index_filter_price_range(client):
    text = client.get('/?min_price=16&max_price=20').get_data(as_text=True)
    assert '高等数学（上册）' in text
    assert '数据结构（C 语言版）' not in text


def test_index_sort_price_asc(client):
    text = client.get('/?sort=price_asc').get_data(as_text=True)
    assert text.index('活着') < text.index('数据结构（C 语言版）')


def test_detail_views_increment(client, app):
    with app.app_context():
        book_id = _book_id('活着')

    client.get('/book/%d' % book_id)
    client.get('/book/%d' % book_id)

    with app.app_context():
        assert Book.query.get(book_id).views == 2


def test_detail_seller_sees_manage_notice(client, login, app):
    login()  # seller01
    with app.app_context():
        book_id = _book_id('活着')

    text = client.get('/book/%d' % book_id).get_data(as_text=True)
    assert '这是你发布的图书' in text
    assert '立即预订' not in text


def test_publish_requires_login(client):
    resp = client.post('/books/new', data=_new_book_form())
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']


def test_publish_invalid_price_rejected(client, login, app):
    login()
    resp = client.post('/books/new', data=_new_book_form(price='0'),
                       follow_redirects=True)
    assert '售价必须为大于 0 的数字' in resp.get_data(as_text=True)
    with app.app_context():
        assert Book.query.count() == 3


def test_publish_invalid_category_rejected(client, login, app):
    login()
    resp = client.post('/books/new', data=_new_book_form(category='不存在的分类'),
                       follow_redirects=True)
    assert '请选择有效的图书分类' in resp.get_data(as_text=True)
    with app.app_context():
        assert Book.query.count() == 3


def test_publish_success(client, login, app):
    login()
    resp = client.post('/books/new', data=_new_book_form())
    assert resp.status_code == 302
    assert '/book/' in resp.headers['Location']
    with app.app_context():
        book = Book.query.filter_by(title='Python 编程：从入门到实践').first()
        assert book is not None
        assert book.status == 'on_sale'


def test_toggle_own_book(client, login, app):
    login()
    with app.app_context():
        book_id = _book_id('活着')

    client.post('/book/%d/toggle' % book_id)
    with app.app_context():
        assert Book.query.get(book_id).status == 'off_shelf'

    client.post('/book/%d/toggle' % book_id)
    with app.app_context():
        assert Book.query.get(book_id).status == 'on_sale'


def test_toggle_others_book_forbidden(client, login, app):
    login('buyer01')
    with app.app_context():
        book_id = _book_id('活着')

    resp = client.post('/book/%d/toggle' % book_id, follow_redirects=True)
    assert '无权操作他人发布的图书' in resp.get_data(as_text=True)
    with app.app_context():
        assert Book.query.get(book_id).status == 'on_sale'


def test_delete_reserved_book_forbidden(client, login, app):
    login()
    with app.app_context():
        book = Book.query.filter_by(title='活着').first()
        book.status = 'reserved'
        db.session.commit()
        book_id = book.id

    resp = client.post('/book/%d/delete' % book_id, follow_redirects=True)
    assert '无法删除' in resp.get_data(as_text=True)
    with app.app_context():
        assert Book.query.get(book_id) is not None

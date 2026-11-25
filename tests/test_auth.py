"""FR-01 注册、FR-02 登录与退出的验收用例。"""

from app.models import User


def test_register_success(client, app):
    resp = client.post('/register', data={
        'username': 'newbie01', 'nickname': '新同学',
        'student_id': '202426000099', 'campus': '瑶湖校区',
        'password': 'abc123', 'confirm': 'abc123',
    })
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/login')
    with app.app_context():
        user = User.query.filter_by(username='newbie01').first()
        assert user is not None
        assert user.password_hash != 'abc123'


def test_register_duplicate_username(client):
    resp = client.post('/register', data={
        'username': 'seller01', 'nickname': '重复', 'password': '123456',
        'confirm': '123456',
    }, follow_redirects=True)
    assert '该用户名已被注册' in resp.get_data(as_text=True)


def test_register_password_mismatch(client):
    resp = client.post('/register', data={
        'username': 'newbie02', 'nickname': '新同学', 'password': '123456',
        'confirm': '654321',
    }, follow_redirects=True)
    text = resp.get_data(as_text=True)
    assert '两次输入的密码不一致' in text


def test_register_short_password(client):
    resp = client.post('/register', data={
        'username': 'newbie03', 'nickname': '新同学', 'password': '123',
        'confirm': '123',
    }, follow_redirects=True)
    assert '密码长度不少于 6 位' in resp.get_data(as_text=True)


def test_register_duplicate_student_id(client):
    resp = client.post('/register', data={
        'username': 'newbie04', 'nickname': '新同学',
        'student_id': '202426000001', 'password': '123456', 'confirm': '123456',
    }, follow_redirects=True)
    assert '该学号已被注册' in resp.get_data(as_text=True)


def test_login_success(client):
    resp = client.post('/login', data={'username': 'buyer01', 'password': '123456'})
    assert resp.status_code == 302
    with client.session_transaction() as session:
        assert session['user_id'] is not None


def test_login_wrong_password(client):
    resp = client.post('/login', data={'username': 'buyer01', 'password': 'wrong'},
                       follow_redirects=True)
    assert '用户名或密码不正确' in resp.get_data(as_text=True)


def test_login_next_must_be_internal(client):
    """next 指向站外地址时应回到首页，避免开放重定向。"""
    resp = client.post('/login?next=https://example.com/evil',
                       data={'username': 'buyer01', 'password': '123456'})
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/')


def test_logout_clears_session(client, login):
    login()
    resp = client.get('/logout')
    assert resp.status_code == 302
    with client.session_transaction() as session:
        assert 'user_id' not in session


def test_login_required_redirect(client):
    resp = client.get('/books/mine')
    assert resp.status_code == 302
    assert '/login' in resp.headers['Location']

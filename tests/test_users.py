"""FR-08 个人中心：资料修改与密码修改的验收用例。"""

from app.models import User


def test_update_profile_nickname(client, login, app):
    login('buyer01')
    resp = client.post('/profile', data={'nickname': '阿哲同学', 'campus': '瑶湖校区',
                                         'contact': '微信 azhe2026'},
                       follow_redirects=True)
    assert resp.status_code == 200
    with app.app_context():
        user = User.query.filter_by(username='buyer01').first()
        assert user.nickname == '阿哲同学'
        assert user.contact == '微信 azhe2026'


def test_change_password_success(client, login, app):
    login('buyer01')
    client.post('/profile/password', data={'old_password': '123456',
                                           'new_password': 'newpass1',
                                           'confirm_password': 'newpass1'},
                follow_redirects=True)
    client.get('/logout')
    resp = client.post('/login', data={'username': 'buyer01', 'password': 'newpass1'})
    assert resp.status_code == 302


def test_change_password_wrong_old(client, login, app):
    login('buyer01')
    resp = client.post('/profile/password', data={'old_password': 'wrongpwd',
                                                  'new_password': 'newpass1',
                                                  'confirm_password': 'newpass1'},
                       follow_redirects=True)
    assert '原密码不正确' in resp.get_data(as_text=True)
    with app.app_context():
        user = User.query.filter_by(username='buyer01').first()
        assert user.check_password('123456')

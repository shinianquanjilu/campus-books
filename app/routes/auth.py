"""认证模块：注册、登录、退出。"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.extensions import db
from app.models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        nickname = (request.form.get('nickname') or '').strip()
        student_id = (request.form.get('student_id') or '').strip() or None
        campus = (request.form.get('campus') or '').strip() or None
        password = request.form.get('password') or ''
        confirm = request.form.get('confirm') or ''

        errors = []
        if len(username) < 3 or len(username) > 20:
            errors.append('用户名长度需在 3 至 20 个字符之间')
        if not nickname:
            errors.append('请填写昵称')
        if len(password) < 6:
            errors.append('密码长度不少于 6 位')
        if password != confirm:
            errors.append('两次输入的密码不一致')
        if User.query.filter_by(username=username).first():
            errors.append('该用户名已被注册')
        if student_id and User.query.filter_by(student_id=student_id).first():
            errors.append('该学号已被注册')

        if errors:
            for item in errors:
                flash(item, 'error')
            return render_template('register.html', form=request.form)

        user = User(username=username, nickname=nickname, student_id=student_id, campus=campus)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash('注册成功，请登录', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form={})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = (request.form.get('username') or '').strip()
        password = request.form.get('password') or ''
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash('用户名或密码不正确', 'error')
            return render_template('login.html', form=request.form)

        session['user_id'] = user.id
        session['nickname'] = user.nickname
        flash('欢迎回来，%s' % user.nickname, 'success')

        next_url = request.args.get('next') or url_for('books.index')
        # 仅允许站内跳转，避免开放重定向
        if not next_url.startswith('/'):
            next_url = url_for('books.index')
        return redirect(next_url)

    return render_template('login.html', form={})


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('已退出登录', 'success')
    return redirect(url_for('books.index'))

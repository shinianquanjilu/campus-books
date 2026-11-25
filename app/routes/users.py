"""个人中心：查看与修改资料、修改密码。"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from app.extensions import db
from app.models import User, Book, Order
from app.utils import login_required, current_user_id

users_bp = Blueprint('users', __name__)


@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get_or_404(current_user_id())

    if request.method == 'POST':
        nickname = (request.form.get('nickname') or '').strip()
        campus = (request.form.get('campus') or '').strip() or None
        contact = (request.form.get('contact') or '').strip() or None

        if not nickname:
            flash('昵称不能为空', 'error')
            return render_template('profile.html', user=user, counts=_counts(user))

        user.nickname = nickname
        user.campus = campus
        user.contact = contact
        db.session.commit()
        flash('资料已更新', 'success')
        return redirect(url_for('users.profile'))

    return render_template('profile.html', user=user, counts=_counts(user))


@users_bp.route('/profile/password', methods=['POST'])
@login_required
def change_password():
    user = User.query.get_or_404(current_user_id())
    old = request.form.get('old_password') or ''
    new = request.form.get('new_password') or ''
    confirm = request.form.get('confirm_password') or ''

    if not user.check_password(old):
        flash('原密码不正确', 'error')
    elif len(new) < 6:
        flash('新密码长度不少于 6 位', 'error')
    elif new != confirm:
        flash('两次输入的新密码不一致', 'error')
    else:
        user.set_password(new)
        db.session.commit()
        flash('密码修改成功', 'success')

    return redirect(url_for('users.profile'))


def _counts(user):
    return {
        'published': Book.query.filter_by(seller_id=user.id).count(),
        'bought': Order.query.filter_by(buyer_id=user.id).count(),
        'sold': Order.query.filter_by(seller_id=user.id, status='completed').count(),
    }

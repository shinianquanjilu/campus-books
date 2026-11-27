"""收藏模块：收藏 / 取消收藏、我的收藏列表。"""

from flask import Blueprint, render_template, redirect, url_for, flash, session

from app.extensions import db
from app.models import Book, Favorite
from app.utils import login_required, current_user_id

favorites_bp = Blueprint('favorites', __name__)


@favorites_bp.route('/favorite/<int:book_id>/toggle', methods=['POST'])
@login_required
def toggle(book_id):
    """在收藏与取消收藏之间切换，重复提交保持幂等。"""
    book = Book.query.get_or_404(book_id)
    user_id = current_user_id()

    record = Favorite.query.filter_by(user_id=user_id, book_id=book_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        flash('已取消收藏', 'success')
    else:
        favorite = Favorite(user_id=user_id, book_id=book_id)
        db.session.add(favorite)
        db.session.commit()
        flash('已加入收藏', 'success')

    referrer = session.get('_referrer') or url_for('books.index')
    return redirect(referrer)


@favorites_bp.route('/favorites')
@login_required
def mine():
    """当前用户的收藏图书，按收藏时间倒序。"""
    records = (Favorite.query.filter_by(user_id=current_user_id())
               .order_by(Favorite.created_at.desc()).all())
    books = [record.book for record in records if record.book]
    return render_template('my_favorites.html', books=books)

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Post, Comment, User, Category
from slugify import slugify

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('posts.index'))
        return f(*args, **kwargs)
    return decorated

@admin_bp.route('/admin')
@login_required
@admin_required
def dashboard():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    users = User.query.all()
    comments = Comment.query.order_by(Comment.created_at.desc()).all()
    return render_template('admin/dashboard.html', posts=posts, users=users, comments=comments)

@admin_bp.route('/admin/post/<int:post_id>/approve')
@login_required
@admin_required
def approve_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_approved = True
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/post/<int:post_id>/unapprove')
@login_required
@admin_required
def unapprove_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.is_approved = False
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/comment/<int:comment_id>/delete')
@login_required
@admin_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/admin/category/add/<name>')
@login_required
@admin_required
def add_category(name):
    cat = Category(name=name, slug=name.lower().replace(' ', '-'))
    db.session.add(cat)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Post, Category, Notification, Like
from datetime import datetime
import re

posts_bp = Blueprint('posts', __name__)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[\s]+', '-', text)
    text = re.sub(r'[^\w-]', '', text)
    return text

@posts_bp.route('/')
def index():
    posts = Post.query.filter_by(status='published', is_approved=True).order_by(Post.published_at.desc()).all()
    categories = Category.query.all()
    return render_template('posts/index.html', posts=posts, categories=categories)

@posts_bp.route('/post/<slug>')
def view_post(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('posts/view.html', post=post)

@posts_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    categories = Category.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        status = request.form.get('status')
        scheduled_at = request.form.get('scheduled_at')
        category_ids = request.form.getlist('categories')
        slug = slugify(title)
        post = Post(
            title=title, content=content, slug=slug,
            status=status, user_id=current_user.id,
            published_at=datetime.utcnow() if status == 'published' else None,
            scheduled_at=datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M') if scheduled_at and status == 'scheduled' else None
        )
        for cid in category_ids:
            cat = Category.query.get(int(cid))
            if cat:
                post.categories.append(cat)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!')
        return redirect(url_for('posts.index'))
    return render_template('posts/new.html', categories=categories)

@posts_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('Not authorized.')
        return redirect(url_for('posts.index'))
    categories = Category.query.all()
    if request.method == 'POST':
        post.title = request.form.get('title')
        post.content = request.form.get('content')
        post.status = request.form.get('status')
        scheduled_at = request.form.get('scheduled_at')
        post.scheduled_at = datetime.strptime(scheduled_at, '%Y-%m-%dT%H:%M') if scheduled_at and post.status == 'scheduled' else None
        post.published_at = datetime.utcnow() if post.status == 'published' and not post.published_at else post.published_at
        category_ids = request.form.getlist('categories')
        post.categories = []
        for cid in category_ids:
            cat = Category.query.get(int(cid))
            if cat:
                post.categories.append(cat)
        db.session.commit()
        flash('Post updated!')
        return redirect(url_for('posts.view_post', slug=post.slug))
    return render_template('posts/edit.html', post=post, categories=categories)

@posts_bp.route('/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id and not current_user.is_admin:
        flash('Not authorized.')
        return redirect(url_for('posts.index'))
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.')
    return redirect(url_for('posts.index'))

@posts_bp.route('/post/<int:post_id>/like')
@login_required
def like_post(post_id):
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing:
        db.session.delete(existing)
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        post = Post.query.get(post_id)
        if post.user_id != current_user.id:
            notif = Notification(user_id=post.user_id, message=f'{current_user.username} liked your post "{post.title}"')
            db.session.add(notif)
    db.session.commit()
    return redirect(url_for('posts.view_post', slug=Post.query.get(post_id).slug))

@posts_bp.route('/category/<slug>')
def category(slug):
    cat = Category.query.filter_by(slug=slug).first_or_404()
    posts = Post.query.filter(Post.categories.contains(cat), Post.status == 'published').all()
    return render_template('posts/category.html', category=cat, posts=posts)
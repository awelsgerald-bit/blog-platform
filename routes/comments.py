from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Comment, Post, Notification

comments_bp = Blueprint('comments', __name__)

@comments_bp.route('/post/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    content = request.form.get('content')
    post = Post.query.get_or_404(post_id)
    if content:
        comment = Comment(content=content, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        if post.user_id != current_user.id:
            notif = Notification(user_id=post.user_id, message=f'{current_user.username} commented on your post "{post.title}"')
            db.session.add(notif)
        db.session.commit()
    return redirect(url_for('posts.view_post', slug=post.slug))

@comments_bp.route('/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    post = Post.query.get(comment.post_id)
    if comment.user_id != current_user.id and not current_user.is_admin:
        flash('Not authorized.')
        return redirect(url_for('posts.view_post', slug=post.slug))
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('posts.view_post', slug=post.slug))
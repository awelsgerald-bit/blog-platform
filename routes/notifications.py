from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import db, Notification

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def index():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    for n in notifications:
        n.is_read = True
    db.session.commit()
    return render_template('notifications/index.html', notifications=notifications)
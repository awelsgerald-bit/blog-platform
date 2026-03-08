from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from apscheduler.schedulers.background import BackgroundScheduler
from config import Config
from models import db, User, Post
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ── Auto-publish scheduled posts ──
def publish_scheduled_posts():
    with app.app_context():
        now = datetime.utcnow()
        posts = Post.query.filter_by(status='scheduled').filter(Post.scheduled_at <= now).all()
        for post in posts:
            post.status = 'published'
            post.published_at = now
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(publish_scheduled_posts, 'interval', minutes=1)
scheduler.start()

# ── Register routes ──
from routes.auth import auth_bp
from routes.posts import posts_bp
from routes.comments import comments_bp
from routes.admin import admin_bp
from routes.notifications import notifications_bp

app.register_blueprint(auth_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(comments_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(notifications_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    """
    Represents a registered user of the Trend to Script application.
    Each user has their own receiver email — trends and content emails
    will be sent to their configured address, not a global .env value.
    """
    __tablename__ = 'users'

    id             = db.Column(db.Integer, primary_key=True)
    username       = db.Column(db.String(80), unique=True, nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)  # login email
    password_hash  = db.Column(db.String(256), nullable=False)
    receiver_email = db.Column(db.String(120), nullable=True)                # where to send trends
    
    # Article Metadata Preferences
    author_name    = db.Column(db.String(100), default='The Crazy Careers')
    read_time      = db.Column(db.String(50), default='5 min read')
    publish_date   = db.Column(db.String(50), default='Auto')
    
    workflows_run  = db.Column(db.Integer, default=0)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, username, email, password_hash, receiver_email=None, **kwargs):
        super(User, self).__init__(
            username=username,
            email=email,
            password_hash=password_hash,
            receiver_email=receiver_email,
            **kwargs
        )

    def __repr__(self):
        return f'<User {self.username}>'

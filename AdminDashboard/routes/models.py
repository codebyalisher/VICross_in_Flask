from datetime import datetime, timedelta
from AdminDashboard.database import db  
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin 
 
class User(db.Model,UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # Adjusted length for security
    verified = db.Column(db.Boolean, default=False) 
    status = db.Column(db.String(50), default='pending') 
    role = db.Column(db.String(50), default='user')
    image=db.Column(db.String(255),nullable=True)
    image_file_id = db.Column(db.String(100))     
    background_image=db.Column(db.String(255),nullable=True)
    background_image_file_id = db.Column(db.String(100))
    company=db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, name=None, email=None, password=None, status='pending', role='user', verified=False,is_active=True, image=None,updated_at=None,company=None,background_image=None):
        self.name = name
        self.email = email
        if password:
            self.password_hash = generate_password_hash(password)
        self.status = status
        self.role = role
        self.verified = verified
        self.is_active =is_active
        self.image=image
        self.updated_at=updated_at
        self.company=company
        self.background_image=background_image

    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name!r}>'
    
    def get_id(self):
        """Return the unique identifier for the user."""
        return str(self.id)
    
    def to_dict(self):
        """Convert the User object to a dictionary"""
        return {            
            'name': self.name,
            'email': self.email,
            'verified': self.verified,
            'status': self.status,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'image': self.image,
            'company': self.company,
            'background_image': self.background_image            
        }

class OTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    otp = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expired_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)

    def __init__(self, email, otp,created_at,expired_at, is_used=False):
        self.email = email
        self.otp = otp
        self.created_at=created_at
        self.expired_at = expired_at 
        self.is_used = is_used       
    
    def __repr__(self):
        return f'<OTP for {self.email} - OTP: {self.otp}>'

    def to_dict(self):
        """Convert OTP object to dictionary."""
        return {
            'email': self.email,
            'otp': self.otp,
            'created_at': self.created_at,
            'expired_at': self.expired_at,
            'is_used': self.is_used
        }
        
        
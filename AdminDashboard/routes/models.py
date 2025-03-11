from enum import Enum
from flask_login import UserMixin 
from AdminDashboard.database import db  
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
 
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
    trade_booths = db.relationship('TradeBooth', backref='creator', lazy=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self,trade_booths=None, name=None, email=None, password=None, status='pending', role='user', verified=False,is_active=True, image=None,updated_at=None,company=None,background_image=None,image_file_id=None,background_image_file_id=None):
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
        self.image_file_id=image_file_id
        self.background_image_file_id=background_image_file_id
        self.trade_booths = trade_booths

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
            'background_image': self.background_image  ,
            'image_file_id': self.image_file_id,
            'background_image_file_id': self.background_image    ,
            'trade_booths':self.trade_booths      
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
 
class TradeBoothStatus(Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    
class TradeBooth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text) 
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company', backref='trade_booths')      
    image_url = db.Column(db.String(255))
    status = db.Column(db.Enum(TradeBoothStatus), default=TradeBoothStatus.PENDING)
    image_file_id = db.Column(db.String(255))      # Specific field for PDF    
    document_pdf_url = db.Column(db.String(255))
    document_pdf_file_id = db.Column(db.String(255))     # Specific field for DOCX    
    document_docx_url = db.Column(db.String(255))
    document_docx_file_id = db.Column(db.String(255))
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, creator_id, title, date, start_time,end_time, location, description=None,image_url=None,status=None,company=None, image_file_id=None, document_pdf_url=None, document_pdf_file_id=None, document_docx_url=None, document_docx_file_id=None, created_at=None, updated_at=None):
        self.title = title
        self.date = date
        self.start_time=start_time
        self.end_time=end_time
        self.location = location
        self.description = description       
        self.image_url = image_url
        self.status = status
        self.image_file_id = image_file_id       
        self.document_pdf_url = document_pdf_url
        self.document_pdf_file_id = document_pdf_file_id               
        self.document_docx_url = document_docx_url
        self.document_docx_file_id = document_docx_file_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.creator_id = creator_id        
        self.company=company

    def to_dict(self):
        tradebooth_dict = {
            'id': self.id,
            'title': self.title,
            'date': self.date.strftime('%d %b, %Y'),
            'time': f"{self.start_time.strftime('%I.%M%p')} - {self.end_time.strftime('%I.%M%p')}",
            'description': self.description,
            'image_url': self.image_url,
            'creator_id': self.creator_id,
            'status': self.status.value,
        }
        if self.company:
            tradebooth_dict['company'] = self.company.to_dict() 
        return tradebooth_dict

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    image_file_id = db.Column(db.String(255))
    location = db.Column(db.String(100))
    size = db.Column(db.String(50))    
    def __init__(self, name, image_url=None, location=None, size=None, image_file_id=None):
        self.name = name
        self.image_url = image_url
        self.location = location
        self.size = size
        self.image_file_id = image_file_id      
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'image_url': self.image_url,
            'location': self.location,
            'size': self.size,
        }
        
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user = db.relationship('User', backref='messages')
    room = db.relationship('Room', backref='messages')

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
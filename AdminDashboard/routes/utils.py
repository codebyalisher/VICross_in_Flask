import os
import jwt
import re
import random
import logging
from functools import wraps
from flask_api import status
from flask import redirect, url_for
from flask_login import current_user
from flask_mail import Mail, Message
from AdminDashboard.database import db
from datetime import datetime, timedelta
from AdminDashboard.routes.models import OTP
from flask import current_app, request, jsonify
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


logging.basicConfig(level=logging.DEBUG)

mail = Mail()
    
def generate_verification_token(email):
    """Generates a token for email verification."""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

def get_email_token_expiration_time():
    """Fetch the email token expiration time from the app config."""    
    return current_app.config.get('EMAIL_TOKEN_EXP_TIME', 3600)

def verify_token(token, expiration=None):
    """Verifies the email verification token."""
    if expiration is None:
        expiration = current_app.config['EMAIL_TOKEN_EXP_TIME']
    try:
        expiration = int(expiration)
    except ValueError:
        expiration = 3600 

    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=current_app.config['SECURITY_PASSWORD_SALT'], max_age=expiration)
        return email
    except (BadSignature, SignatureExpired):
        raise ValueError("The token is invalid or has expired.")
    
def send_registration_email(user_email):
    """Sends the registration email with a verification link."""
    subject = "Please Verify Your Email Address"
    token = generate_verification_token(user_email)  # Generate the token
    hosted_server=current_app.config['HOST_SERVER']    
    verification_link = f'{hosted_server}/auth/verify-email/{token}'  # Link to the verification endpoint
    
    # Create the message
    msg = Message(subject,
                  recipients=[user_email],
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Use default sender
                  body=f"Please click the following link to verify your email: {verification_link}")
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_jwt(user, expiration=None):
    """
    Generate a JWT token for the authenticated user.
    """
    if expiration is None:
        expiration = current_app.config['JWT_TOKEN_EXPIRATION_TIME'] 
    try:
        expiration = int(expiration)
    except ValueError:
        expiration =1
    expiration_time =datetime.utcnow() + timedelta(hours=expiration)  

    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': expiration_time
    }

    token = jwt.encode(payload, current_app.config['ACCESS_TOKEN_SECRET_KEY'], algorithm='HS256')
    return token

def verify_jwt(token):
    """Verifies the JWT token and returns the payload if valid."""
    try:        
        payload = jwt.decode(token, current_app.config['ACCESS_TOKEN_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token has expired. Please login again.")
    except jwt.DecodeError:
        raise jwt.InvalidTokenError("There was an error decoding the token.")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token. Please login again.")

def generate_refresh_token(user):
    """
    Generate a refresh token for the user.
    """
    expiration_time =datetime.utcnow() + timedelta(days=7)  
    
    payload = {
        'user_id': user.id,  
        'email': user.email, 
        'exp': expiration_time 
    }
    
    refresh_token = jwt.encode(payload, current_app.config['REFRESH_TOKEN_SECRET_KEY'], algorithm='HS256')
    return refresh_token

def token_required(f):
    """
    Decorator to require a valid JWT token for access to a route.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')        
        if not token:
            return jsonify({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Token is missing"
            }), status.HTTP_401_UNAUTHORIZED

        try:
            token = token.split(' ')[1]  # Split Bearer token
        except IndexError:
            return jsonify({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": "Token format is incorrect"
            }), status.HTTP_401_UNAUTHORIZED        
        # Verify the token
        try:
            payload = verify_jwt(token)  # This will raise an exception if the token is invalid
        except jwt.InvalidTokenError as e:
            return jsonify({
                "status": status.HTTP_401_UNAUTHORIZED,
                "message": str(e)  # Provide the error message from verify_jwt
            }), status.HTTP_401_UNAUTHORIZED

        request.user_data = payload
        return f(*args, **kwargs)

    return decorated_function

def generate_otp():
    """Generate a 6-digit OTP."""
    otp = random.randint(100000, 999999)
    return otp

def send_otp_email(user_email,otp):
    """Sends the registration email with a verification link."""
    subject = "Your OTP for Password Reset"    
    otp_token = generate_verification_token(user_email) # Generate the token
        
    # Create the message
    msg = Message(subject,
                  recipients=[user_email],
                  sender=current_app.config['MAIL_DEFAULT_SENDER'],  # Use default sender
                  body=f"Your OTP is {otp}. It will expire in 10 minutes")
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def store_otp(email, otp):
    """Stores or updates the OTP for a given email."""
    expiration_minutes = current_app.config.get("OTP_EXPIRATION_TIME", 10) 
    try:
        expiration = int(expiration_minutes)
    except ValueError:
        expiration = 10  
    current_time = datetime.utcnow()
    expiration_time = current_time + timedelta(minutes=expiration)
    existing_otp = db.session.query(OTP).filter_by(email=email).first()
    if existing_otp:       
        if existing_otp.is_used:
            return "used"         
        if existing_otp.expired_at < current_time:            
            existing_otp.otp = otp
            existing_otp.expired_at = expiration_time
            existing_otp.is_used = False
            db.session.commit()
            return "expired" 
        return "valid"  
    else:        
        otp_entry = OTP(
            email=email,
            otp=otp,
            created_at=current_time,
            expired_at=expiration_time,
            is_used=False
        )
        db.session.add(otp_entry)
        db.session.commit()
        return "new"  

def validate_password(password):
    """
    Validates the password for length and format:
    - Length: at least 8 characters
    - Format: contains at least one uppercase letter, one lowercase letter, and one digit
    """
    # Check if password is at least 8 characters long
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    # Check if password contains at least one uppercase letter, one lowercase letter, and one digit
    if not re.search(r'[A-Z]', password):  # At least one uppercase letter
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r'[a-z]', password):  # At least one lowercase letter
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r'\d', password):  # At least one digit
        raise ValueError("Password must contain at least one digit.")

    # Password format is valid
    return True

def role_required(required_role):
    """Decorator to require a specific role for the user."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ensure the user is authenticated and has the required role
            if not current_user.is_authenticated or current_user.role != required_role:
                return jsonify({"status": status.HTTP_403_FORBIDDEN, 
                                 "message": "Permission denied. You don't have the permission."}), status.HTTP_403_FORBIDDEN
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def allowed_file(filename, allowed_extensions):
    """Checks if a file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
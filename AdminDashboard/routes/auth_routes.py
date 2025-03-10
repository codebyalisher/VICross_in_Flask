import base64
from flask_api import status
from flask import render_template
from AdminDashboard.database import db
from datetime import datetime, timedelta
from flask_login import login_user,current_user
from AdminDashboard.routes.models import User,OTP
from flask import Blueprint, request, jsonify, session
from AdminDashboard.routes.image_kit import get_image_from_imagekit
from werkzeug.security import check_password_hash, generate_password_hash
from AdminDashboard.routes.utils import verify_token,send_registration_email,generate_verification_token,token_required
from AdminDashboard.routes.utils import generate_jwt, generate_refresh_token,send_otp_email,validate_password,store_otp,generate_otp,role_required


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST, "message": "No input data provided"}),status.HTTP_400_BAD_REQUEST

    name = data.get('name')
    role=data.get('role')
    email = data.get('email')
    password = data.get('password')
    password_confirmation = data.get('password_confirmation')
    trade_booths=data.get('trade_booths')
   
    if not name or not email or not password or not password_confirmation:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST, "message": "All fields are required"}), status.HTTP_400_BAD_REQUEST

    if password != password_confirmation:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Passwords do not match"}),status.HTTP_400_BAD_REQUEST
    
    if trade_booths is None:        
        trade_booths = []
    # Check if the email already exists
    existing_user = db.session.query(User).filter_by(email=email).first()
    if existing_user:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "User with this email already exists"}),status.HTTP_400_BAD_REQUEST

    # Create a new user
    user = User(name=name, email=email, password=password,role=role,trade_booths=trade_booths)
    db.session.add(user)
    db.session.commit()
   
    send_registration_email(user.email)
    return jsonify({"status":status.HTTP_201_CREATED,"message": "Registration successful, please check your email to verify your account","data":user.to_dict()}),status.HTTP_201_CREATED

@bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Handles the email verification when the user clicks the link."""
    email = verify_token(token)
    if email is None:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST, "message": "The verification link has expired or is invalid."}),status.HTTP_400_BAD_REQUEST

    # Check if the user exists
    user = db.session.query(User).filter_by(email=email).first()
    if user is None:
        return jsonify({"status":status.HTTP_404_NOT_FOUND, "message": "User not found."}),status.HTTP_404_NOT_FOUND

    if user.verified:
        return jsonify({"status":status.HTTP_200_OK, "message": "Your email is already verified."}), status.HTTP_200_OK

    # Mark the user as verified
    user.verified = True
    db.session.commit()

    return jsonify({"status":status.HTTP_200_OK, "message": "Email verified successfully!"}),status.HTTP_200_OK

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "No input data provided",            
        }), status.HTTP_400_BAD_REQUEST
    
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST,
                      "message": "Email and Password are required", }),status.HTTP_400_BAD_REQUEST
    
    user = db.session.query(User).filter_by(email=email).first()
    if user is None:
        return jsonify({"status": status.HTTP_404_NOT_FOUND,
                      "message": "User Not Found",}),status.HTTP_404_NOT_FOUND

    if not user.check_password(password):
        return jsonify({"status": status.HTTP_401_UNAUTHORIZED,
                      "message": "Invalid Email or password",}),status.HTTP_401_UNAUTHORIZED
        
    if not user.verified:
        return jsonify({"status": status.HTTP_403_FORBIDDEN,"message": "Account is not verified. Please check your email for the verification link."}), status.HTTP_403_FORBIDDEN
    
    access_token = generate_jwt(user)
    refresh_token = generate_refresh_token(user)
    
    session.clear()
    session['user_id'] = user.id
    
    login_user(user)
    
    user_data = user.to_dict()
    user_data.pop('password_hash', None) 
    user_data.pop('created_at', None)
    user_data.pop('updated_at', None)
    user_data.pop('image', None)
    user_data.pop('background_image', None)
    user_data.pop('company', None)
    user_data.pop('image_file_id', None)
    user_data.pop('background_image_file_id', None)
    user_data.pop('trade_booths', None)       
    
    if user.image: 
        file_id = user.image  
        image = get_image_from_imagekit(file_id)
        if image and 'url' in image:
            user_data['image'] = image['url']  

    if user.background_image: 
        file_id = user.background_image 
        background_imagekit_result = get_image_from_imagekit(file_id)
        if background_imagekit_result and 'url' in background_imagekit_result:
            user_data['background_image'] = background_imagekit_result['url']

    return jsonify({"status":status.HTTP_200_OK,"message": "Login successful", "data": user_data,"access_token": access_token,"refresh_token": refresh_token}),status.HTTP_200_OK

@bp.route('/send_otp', methods=['POST'])
def send_otp():
    user_email = request.json.get('email')
    if not user_email:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "Email is required."}), status.HTTP_400_BAD_REQUEST
    user =db.session.query(User).filter_by(email=user_email).first()
    if not user:
        return jsonify({"status": status.HTTP_404_NOT_FOUND, "message": "User not found."}), status.HTTP_404_NOT_FOUND
    session['email'] = user_email    
    otp=generate_otp()    
    otp_status=store_otp(user_email,otp) 
    if otp_status == "used":        
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP has already been used. Please request a new one, after expiry of used otp."}), status.HTTP_400_BAD_REQUEST
    elif otp_status == "expired":        
        if send_otp_email(user_email, otp):
            return jsonify({"status": status.HTTP_200_OK, "message": "OTP will be sent to your email after expiration."}), status.HTTP_200_OK
    elif otp_status == "valid":        
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP is still valid. Please wait before requesting a new one."}), status.HTTP_400_BAD_REQUEST
    elif otp_status == "new":                
        if send_otp_email(user_email, otp):
            return jsonify({"status": status.HTTP_200_OK, "message": "OTP has been sent to your email."}), status.HTTP_200_OK
        else:
            return jsonify({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "Failed to send OTP."}), status.HTTP_500_INTERNAL_SERVER_ERROR
    else:        
        return jsonify({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "An unexpected error occurred."}), status.HTTP_500_INTERNAL_SERVER_ERROR

@bp.route('/resend_otp', methods=['POST'])
def resend_otp():
    email = session.get('email') 
    if not email:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST,"message": "No email found in session"}), status.HTTP_400_BAD_REQUEST

    otp_status = store_otp(email, generate_otp())     
    if otp_status == "used":
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP has already been used. Please request a new one,after expiry of used otp"}), status.HTTP_400_BAD_REQUEST
    
    elif otp_status == "expired":        
        send_otp_email(email, generate_otp())
        return jsonify({"status": status.HTTP_200_OK, "message": "OTP has been resent after expiration."}), status.HTTP_200_OK
    
    elif otp_status == "valid":        
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP is still valid. Please wait before requesting a new one."}), status.HTTP_400_BAD_REQUEST
    
    elif otp_status == "new":       
        send_otp_email(email, generate_otp())
        return jsonify({"status": status.HTTP_200_OK, "message": "OTP has been resent successfully."}), status.HTTP_200_OK
    else:
        return jsonify({"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "An unexpected error occurred."}), status.HTTP_500_INTERNAL_SERVER_ERROR

@bp.route('/verify_otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get('otp') 
    if not otp:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP is required."}), status.HTTP_400_BAD_REQUEST
    email = session.get('email')  
    if not email:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "Email not found in session."}), status.HTTP_400_BAD_REQUEST
    otp_entry = db.session.query(OTP).filter_by(email=email).first()
    if not otp_entry:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "No OTP found for this email."}), status.HTTP_400_BAD_REQUEST
    if otp_entry.otp != otp:              
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid OTP."}), status.HTTP_400_BAD_REQUEST
    if otp_entry.is_used:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP has already been used."}), status.HTTP_400_BAD_REQUEST
    current_time = datetime.utcnow()
    if otp_entry.expired_at < current_time:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP has expired."}), status.HTTP_400_BAD_REQUEST
    otp_entry.is_used = True
    db.session.commit()
    return jsonify({"status": status.HTTP_200_OK, "message": "OTP has been verified successfully."}), status.HTTP_200_OK

@bp.route('/reset_password', methods=['GET','POST'])
def reset_password(): 
    if request.method == 'GET':            
        return render_template('form.html')
    
    if request.method == 'POST':         
        email = session.get('email')        
        otp_entry = db.session.query(OTP).filter_by(email=email, is_used=True).first() 
        if not otp_entry:
            return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "OTP is not verified."}), status.HTTP_400_BAD_REQUEST
        
        if request.form.get('_method') == 'PUT':       
            user = db.session.query(User).filter_by(email=email).first()
            if user is None:
                return jsonify({"status":status.HTTP_404_NOT_FOUND,"message": "Email not found."}),status.HTTP_404_NOT_FOUND
            
            password = request.form.get('password')
            password_confirmation = request.form.get('confirmation_password') 
            
            if not password or not password_confirmation:
                return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Password and password confirmation are required."}),status.HTTP_400_BAD_REQUEST
            
            if password != password_confirmation:
                return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Passwords do not match."}),status.HTTP_400_BAD_REQUEST
                        
            try:
                
                validate_password(password)
            except ValueError as e:
                return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)}), status.HTTP_400_BAD_REQUEST
            
            if check_password_hash(user.password_hash,password):
                return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "This password has already been used."}), status.HTTP_400_BAD_REQUEST
            
            user = db.session.query(User).filter_by(email=email).first()                                 
            user.password_hash = generate_password_hash(password)                           
            db.session.commit()

            return jsonify({"status":status.HTTP_200_OK,"message": "Password has been successfully reset."}),status.HTTP_200_OK

    return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Invalid request."}),status.HTTP_400_BAD_REQUEST

@bp.route('/submit_reset_password', methods=['POST'])
def submit_reset_password_post():
    if request.form.get('_method') == 'PUT': 
        data = request.get_json()
        token = data.get('token')
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        
        if not token:
            return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Token is required."}),status.HTTP_400_BAD_REQUEST
        
        email = verify_token(token)
        
        if email is None:
            return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Invalid or expired token."}),status.HTTP_400_BAD_REQUEST
        
        if not password or not password_confirmation:
            return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Password and password confirmation are required."}),status.HTTP_400_BAD_REQUEST
        
        if password != password_confirmation:
            return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Passwords do not match."}),status.HTTP_400_BAD_REQUEST
        
        try:
            
            validate_password(password)
        except ValueError as e:
            return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": str(e)}), status.HTTP_400_BAD_REQUEST
        
        if check_password_hash(user.password_hash,password):
            return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "This password has already been used."}), status.HTTP_400_BAD_REQUEST
        
        user = db.session.query(User).filter_by(email=email).first()                                 
        user.password_hash = generate_password_hash(password)                           
        db.session.commit()
        
        return jsonify({"status":status.HTTP_200_OK,"message": "Password has been successfully changed."}),status.HTTP_200_OK
    
    return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Invalid request."}),status.HTTP_400_BAD_REQUEST

@bp.route('/change_password', methods=['POST'])
@token_required
def change_password():
    user_data = request.user_data
    user = db.session.query(User).filter_by(id=user_data['user_id']).first()
    
    if not user:
        return jsonify({"status":status.HTTP_404_NOT_FOUND,"message": "User not found."}),status.HTTP_404_NOT_FOUND
    
    password=request.json.get('password')
    new_password=request.json.get('new_password')
    
    if password is None or new_password is None:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Password and new password are required."}),status.HTTP_400_BAD_REQUEST
    if password != new_password:
        return jsonify({"status":status.HTTP_400_BAD_REQUEST,"message": "Passwords do not match."}),status.HTTP_400_BAD_REQUEST
    
    validated_password=validate_password(new_password)            
    user.password_hash = generate_password_hash(validated_password)
    db.session.commit()
    return jsonify({"status":status.HTTP_200_OK,"message": "Password has been successfully changed."}),status.HTTP_200_OK
  
@bp.route('/assign_role', methods=['POST'])
@role_required('admin')
@token_required 
def assign_role_to_user():
    """Assign a role to another user, only if the logged-in user is an admin."""
    
    target_user_email = request.json.get('email')  
    role_name = request.json.get('role')

    if not target_user_email or not role_name:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "Email of the target user and role are required."}), status.HTTP_400_BAD_REQUEST

    target_user =db.session.query(User).filter_by(email=target_user_email).first() 
    
    if not target_user:
        return jsonify({"status": status.HTTP_404_NOT_FOUND, "message": "User not found."}), status.HTTP_404_NOT_FOUND

    valid_roles = ['user', 'admin', 'staff']  
    if role_name not in valid_roles:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": "Invalid role."}), status.HTTP_400_BAD_REQUEST
    
    if target_user.role == role_name:
        return jsonify({"status": status.HTTP_400_BAD_REQUEST, "message": f"The role '{role_name}' is already assigned to the user '{target_user.name}'."}), status.HTTP_400_BAD_REQUEST
    
    target_user.role = role_name  
    db.session.commit()
    
    return jsonify({"status": status.HTTP_200_OK, "message": f"Role '{role_name}' assigned to user '{target_user.name}'."}), status.HTTP_200_OK

@bp.route('/all_users', methods=['GET'])
@token_required  
@role_required('admin')
def all_users():  
    users = db.session.query(User).all()
    if not users:
        return jsonify({
            "status":status.HTTP_404_NOT_FOUND,
            "message": "Users not found"
        }), status.HTTP_404_NOT_FOUND
        
    users_data = []
    for user in users:
        user_dict = user.to_dict()
        user_dict.pop('password_hash', None)
        user_dict.pop('created_at', None)
        user_dict.pop('updated_at', None)
        user_dict.pop('verified', None)
        user_dict.pop('is_active', None)
        user_dict.pop('company', None)
        user_dict['id'] = user.id
        users_data.append(user_dict)

    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Profile shown up successfully",
        "data": users_data 
    }), status.HTTP_200_OK


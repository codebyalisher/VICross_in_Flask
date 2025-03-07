import os
import base64
from flask_api import status
from AdminDashboard.database import db
from werkzeug.utils import secure_filename
from AdminDashboard.routes.models import User
from flask import Blueprint, request, jsonify, session
from AdminDashboard.routes.utils import token_required
from AdminDashboard.routes.image_kit import upload_image_to_imagekit,update_image_to_imagekit,delete_image_from_imagekit,get_image_from_imagekit

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/user-profile', methods=['GET'])
@token_required
def profile():    
    user_data = request.user_data  
    try:
        user = db.session.query(User).filter_by(id=user_data['user_id']).one()        
    except:
        return jsonify({
            "status":status.HTTP_404_NOT_FOUND,
            "message": "User not found"
        }),status.HTTP_404_NOT_FOUND 
    user_dict = user.to_dict()
    user_dict.pop('password_hash', None)
    user_dict.pop('created_at', None)
    user_dict.pop('updated_at', None)
    user_dict.pop('verified', None)
    user_dict.pop('is_active', None)
    user_dict.pop('role', None)
    user_dict.pop('status', None) 
    
    if user.image_file_id:
        file_id = user.image_file_id
        image=get_image_from_imagekit(file_id)
        if image and 'url' in image:
            user_dict['image'] = image['url']        
    
    if user.background_image_file_id:
        file_id = user.background_image_file_id
        background_imagekit_result=get_image_from_imagekit(file_id)
        if background_imagekit_result and 'url' in background_imagekit_result:             
            user_dict['background_image'] = background_imagekit_result['url']
                
    return jsonify({
        "status":status.HTTP_200_OK,
        "message": "Profile shown up successfully",
        "data": user_dict
    }),status.HTTP_200_OK
    
@bp.route('/update-user', methods=['PATCH'])
@token_required
def update():
    user_data = request.user_data    
    try:
        user = db.session.query(User).filter_by(id=user_data['user_id']).one()
    except:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "User not found"
        }), status.HTTP_404_NOT_FOUND
    data = request.form
    user.company = data.get('company')
    user.email = data.get('email')
    user.name = data.get('name')

    if 'image' in request.files:
        file = request.files['image']
        if not user.image:
            image_url, image_file_id = upload_image_to_imagekit(file)
            if not image_url:
                return jsonify({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Image upload failed"
                }), status.HTTP_400_BAD_REQUEST
            user.image = image_url
            user.image_file_id = image_file_id
        else:
            image_url = update_image_to_imagekit(file, user.image_file_id)
            if not image_url:
                return jsonify({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Image update failed"
                }), status.HTTP_400_BAD_REQUEST
            user.image = image_url

    if 'background_image' in request.files:
        background_image_file = request.files['background_image']
        if not user.background_image:
            background_image_url, background_image_file_id = upload_image_to_imagekit(background_image_file)
            if not background_image_url:
                return jsonify({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Background image upload failed"
                }), status.HTTP_400_BAD_REQUEST
            user.background_image = background_image_url
            user.background_image_file_id = background_image_file_id
        else:
            background_image_url = update_image_to_imagekit(background_image_file, user.background_image_file_id)
            if not background_image_url:
                return jsonify({
                    "status": status.HTTP_400_BAD_REQUEST,
                    "message": "Background image update failed"
                }), status.HTTP_400_BAD_REQUEST
            user.background_image = background_image_url

    db.session.commit()
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "User updated successfully"
    }), status.HTTP_200_OK

@bp.route('/delete-user', methods=['DELETE'])
@token_required
def delete():
    user_data = request.user_data
    try:
        user = db.session.query(User).filter_by(id=user_data['user_id']).one()
    except:
        return jsonify({
            "status":status.HTTP_404_NOT_FOUND,
            "message": "User not found"
        }),status.HTTP_404_NOT_FOUND
    image_delete_result = {'status': 'success'}
    background_image_delete_result = {'status': 'success'}
    if user.image_file_id:
        image_delete_result = delete_image_from_imagekit(user.image_file_id)
    if user.background_image_file_id:
        background_image_delete_result = delete_image_from_imagekit(user.background_image_file_id)
    if image_delete_result['status'] == 'success' and background_image_delete_result['status'] == 'success':
        user.image = None
        user.image_file_id = None
        user.background_image = None
        user.background_image_file_id = None
        db.session.delete(user)
        db.session.commit()
        return jsonify({
            "status":status.HTTP_200_OK,
            "message": "User deleted successfully"
        }),status.HTTP_200_OK
    else:
        error_message = "Error deleting images: "
        if image_delete_result['status'] != 'success':
            error_message += f"Image: {image_delete_result['message']}; "
        if background_image_delete_result['status'] != 'success':
            error_message += f"Background Image: {background_image_delete_result['message']}"
        return jsonify({
            "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": error_message
        }), status.HTTP_500_INTERNAL_SERVER_ERROR    


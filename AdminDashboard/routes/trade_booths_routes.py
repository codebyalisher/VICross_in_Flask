from flask_api import status
from datetime import datetime
from flask import current_app
from AdminDashboard.database import db
from flask import Blueprint, request, jsonify
from AdminDashboard.routes.models import TradeBooth
from AdminDashboard.routes.utils import token_required,allowed_file
from AdminDashboard.routes.image_kit import upload_tradebooth_files_to_imagekit,upload_image_to_imagekit,delete_image_from_imagekit,update_image_to_imagekit,get_image_from_imagekit

bp=Blueprint('trade_booths', __name__, url_prefix='/trade_booths')

@bp.route('/create-trade-booth', methods=['POST'])
@token_required
def create_trade_booth():
    data = request.form
    image_file = request.files.get('image_filename')
    pdf_file = request.files.get('document_pdf_filename')
    docx_file = request.files.get('document_docx_filename')
    
    ALLOWED_DOCUMENT_EXTENSIONS =current_app.config['ALLOWED_DOCUMENT_EXTENSIONS']
    
    if image_file and not TradeBooth.validate_image_size(image_file):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Image size must be 1920x1080"
        }), status.HTTP_400_BAD_REQUEST

    if pdf_file and not allowed_file(pdf_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid PDF file extension"
        }), status.HTTP_400_BAD_REQUEST

    if docx_file and not allowed_file(docx_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid DOCX file extension"
        }), status.HTTP_400_BAD_REQUEST

    image_url = None
    image_file_id = None
    pdf_url = None
    pdf_file_id = None
    docx_url = None
    docx_file_id = None

    if image_file:
        image_url, image_file_id = upload_image_to_imagekit(image_file)
        if not image_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Image upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR

    if pdf_file:
        pdf_url, pdf_file_id = upload_tradebooth_files_to_imagekit(pdf_file)
        if not pdf_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "PDF upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR

    if docx_file:
        docx_url, docx_file_id = upload_tradebooth_files_to_imagekit(docx_file)
        if not docx_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "DOCX upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR


    try:
        date_str = data.get('date')
        date_obj = datetime.strptime(date_str, '%d %b, %Y').date() #parse the date
    except ValueError:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid date format. Please use '24 Jan, 2025'"
        }), status.HTTP_400_BAD_REQUEST

    trade_booth = TradeBooth(
        creator_id=request.user_data['user_id'],
        title=data.get('title'),
        date=date_obj, #use the parsed date object
        time=datetime.strptime(data.get('time'), '%H:%M').time(),
        location=data.get('location'),
        description=data.get('description'),
        image_url=image_url,
        image_file_id=image_file_id,
        document_pdf_url=pdf_url,
        document_pdf_file_id=pdf_file_id,
        document_docx_url=docx_url,
        document_docx_file_id=docx_file_id
    )


    db.session.add(trade_booth)
    db.session.commit()

    return jsonify({
        "status": status.HTTP_201_CREATED,
        "message": "Trade booth created successfully",
        "data": trade_booth.to_dict()
    }), status.HTTP_201_CREATED
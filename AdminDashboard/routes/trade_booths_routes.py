from flask_api import status
from datetime import datetime
from flask import current_app
from AdminDashboard.database import db
from flask import Blueprint, request, jsonify
from AdminDashboard.routes.models import TradeBooth
from AdminDashboard.routes.utils import token_required,allowed_file
from AdminDashboard.routes.image_kit import upload_tradebooth_files_to_imagekit,update_tradebooth_files_to_imagekit,upload_image_to_imagekit,delete_image_from_imagekit,update_image_to_imagekit,get_image_from_imagekit

bp=Blueprint('trade_booths', __name__, url_prefix='/trade_booths')

@bp.route('/create-trade-booth', methods=['POST'])
@token_required
def create_trade_booth():
    data = request.form
    image_file = request.files.get('image')
    pdf_file = request.files.get('pdf')
    docx_file = request.files.get('docx')
    title = data.get('title')
    start_time=data.get('start_time')
    end_time=data.get('end_time')
    date_str = data.get('date')    
    ALLOWED_DOCUMENT_EXTENSIONS =current_app.config['ALLOWED_DOCUMENT_EXTENSIONS']
    if docx_file and not allowed_file(docx_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid DOCX file extension"
        }), status.HTTP_400_BAD_REQUEST
    if pdf_file and not allowed_file(pdf_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid PDF file extension"
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
    if not date_str or not start_time or not end_time:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Date, start time, and end time are required."
        }), status.HTTP_400_BAD_REQUEST  
    try:
        date_obj = datetime.strptime(date_str,'%d %b, %Y').date() 
        start_time = datetime.strptime(start_time, '%I:%M%p').time()
        end_time = datetime.strptime(end_time, '%I:%M%p').time()
    except ValueError:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid date or time format."
        }), status.HTTP_400_BAD_REQUEST
    if start_time >= end_time:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Start time must be before end time."
        }), status.HTTP_400_BAD_REQUEST
    trade_booth = TradeBooth(
        creator_id=request.user_data['user_id'],
        title=data.get('title'),
        date=date_obj, #use the parsed date object
        start_time=start_time,
        end_time=end_time,
        location=data.get('location'),
        description=data.get('description'),
        image_url=image_url,
        image_file_id=image_file_id,
        document_pdf_url=pdf_url,
        document_pdf_file_id=pdf_file_id,
        document_docx_url=docx_url,
        document_docx_file_id=docx_file_id
    )
    existing_trade_booth = db.session.query(TradeBooth).filter_by(title=title,start_time=start_time,end_time=end_time,date=date_obj,location=data.get('location')).first()
    if existing_trade_booth:
        return jsonify({
            "status": status.HTTP_409_CONFLICT,
            "message": "Trade booth with the given credentials already exists"
        }), status.HTTP_409_CONFLICT

    db.session.add(trade_booth)
    db.session.commit()

    return jsonify({
        "status": status.HTTP_201_CREATED,
        "message": "Trade booth created successfully",
        "data": trade_booth.to_dict()
    }), status.HTTP_201_CREATED

@bp.route('/get-all-trade-booths', methods=['GET'])
@token_required
def get_trade_booths():
    trade_booths = db.session.query(TradeBooth).all()
    trade_booths_list = [trade_booth.to_dict() for trade_booth in trade_booths]
    return jsonify({
        "status": status.HTTP_200_OK,
        "data": trade_booths_list
    }), status.HTTP_200_OK
    
@bp.route('/get-trade-booth-using-id/<int:trade_booth_id>', methods=['GET'])
@token_required
def get_trade_booth(trade_booth_id):
    trade_booth = db.session.query(TradeBooth).get(trade_booth_id)
    if not trade_booth:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Trade booth not found"
        }), status.HTTP_404_NOT_FOUND
    return jsonify({
        "status": status.HTTP_200_OK,
        "data": trade_booth.to_dict()
    }), status.HTTP_200_OK
    
@bp.route('/update-trade-booth/<int:trade_booth_id>', methods=['PUT'])
@token_required
def update_trade_booth(trade_booth_id):
    trade_booth = db.session.query(TradeBooth).get(trade_booth_id)
    if not trade_booth:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Trade booth not found"
        }), status.HTTP_404_NOT_FOUND
    data = request.form
    image_file = request.files.get('image_filename')
    pdf_file = request.files.get('document_pdf_filename')
    docx_file = request.files.get('document_docx_filename')
    title = data.get('title')
    start_time=data.get('start_time')
    end_time=data.get('end_time')
    date_str = data.get('date')    
    ALLOWED_DOCUMENT_EXTENSIONS =current_app.config['ALLOWED_DOCUMENT_EXTENSIONS']
    if docx_file and not allowed_file(docx_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid DOCX file extension"
        }), status.HTTP_400_BAD_REQUEST
    if pdf_file and not allowed_file(pdf_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid PDF file extension"
        }), status.HTTP_400_BAD_REQUEST
    image_url = None
    image_file_id = None
    pdf_url = None
    pdf_file_id = None
    docx_url = None
    docx_file_id = None
    if image_file:
        image_url, image_file_id = update_image_to_imagekit(image_file,trade_booth.image_file_id)
        if not image_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Image upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR
    if pdf_file:
        pdf_url, pdf_file_id = update_tradebooth_files_to_imagekit(pdf_file,trade_booth.document_pdf_file_id)
        if not pdf_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "PDF upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR
    if docx_file:        
        docx_url, docx_file_id = update_tradebooth_files_to_imagekit(docx_file,trade_booth.document_docx_file_id)
        if not docx_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "DOCX upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR
    if not date_str or not start_time or not end_time:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Date, start time, and end time are required."
        }), status.HTTP_400_BAD_REQUEST
    try:
        date_obj = datetime.strptime(date_str,'%d %b, %Y').date() 
        start_time = datetime.strptime(start_time, '%I:%M%p').time()
        end_time = datetime.strptime(end_time, '%I:%M%p').time()
    except ValueError:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Invalid date or time format."
        }), status.HTTP_400_BAD_REQUEST
    if start_time >= end_time:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Start time must be before end time."
        }), status.HTTP_400_BAD_REQUEST
    trade_booth.date = date_obj
    trade_booth.start_time = start_time
    trade_booth.end_time = end_time
    trade_booth.location = data.get('location')
    trade_booth.description = data.get('description')
    trade_booth.image_url = image_url
    trade_booth.image_file_id = image_file_id
    trade_booth.document_pdf_url = pdf_url
    trade_booth.document_pdf_file_id = pdf_file_id
    trade_booth.document_docx_url = docx_url
    trade_booth.document_docx_file_id = docx_file_id
    db.session.commit()
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Trade booth updated successfully",
        "data": trade_booth.to_dict()
    }), status.HTTP_200_OK
 
@bp.route('/delete-trade-booth/<int:trade_booth_id>', methods=['DELETE'])
@token_required
def delete_trade_booth(trade_booth_id):
    trade_booth = db.session.query(TradeBooth).get(trade_booth_id)
    if not trade_booth:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Trade booth not found"
        }), status.HTTP_404_NOT_FOUND
    if trade_booth.image_file_id:
        delete_image_from_imagekit(trade_booth.image_file_id)
    if trade_booth.document_pdf_file_id:
        delete_image_from_imagekit(trade_booth.document_pdf_file_id)
    if trade_booth.document_docx_file_id:
        delete_image_from_imagekit(trade_booth.document_docx_file_id)
    db.session.delete(trade_booth)
    db.session.commit()
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Trade booth deleted successfully"
    }), status.HTTP_200_OK   
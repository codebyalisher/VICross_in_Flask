from flask_api import status
from AdminDashboard.database import db
from flask import Blueprint, request, jsonify
from AdminDashboard.routes.models import TradeBooth,Company
from AdminDashboard.routes.utils import token_required
from AdminDashboard.routes.image_kit import upload_image_to_imagekit,delete_image_from_imagekit,update_image_to_imagekit

bp=Blueprint('Company_Details', __name__, url_prefix='/company')
@bp.route('/create-company', methods=['POST'])
@token_required
def create_company():
    name = request.form.get('name')
    location = request.form.get('location')
    size = request.form.get('size')
    image_file = request.files.get('image')
    if not name or not location or not size:
        return jsonify({
            "status": status.HTTP_400_BAD_REQUEST,
            "message": "Name, location, and size are required"
        }), status.HTTP_400_BAD_REQUEST
    image_url = None
    image_file_id = None
    if image_file:
        image_url, image_file_id = upload_image_to_imagekit(image_file)
        if not image_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Image upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR
    if db.session.query(Company).filter_by(name=name).first():
        return jsonify({
            "status": status.HTTP_409_CONFLICT,
            "message": "Company already exists"
        }), status.HTTP_409_CONFLICT
    company = Company(
        name=name,
        image_url=image_url,
        location=location,
        size=size,
        image_file_id = image_file_id)
    db.session.add(company)
    db.session.commit()
    return jsonify({
        "status": status.HTTP_201_CREATED,
        "message": "Company Created Successfully",
        "data": company.to_dict()
    }), status.HTTP_201_CREATED

@bp.route('/<int:tradebooth_id>/update-company/<int:company_id>', methods=['PUT'])
@token_required
def update_tradebooth_company(tradebooth_id, company_id):
    tradebooth = db.session.query(TradeBooth).get(tradebooth_id)
    company =db.session.query(Company).get(company_id)
    if not tradebooth or not company:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Tradebooth or Company not found"
        }), status.HTTP_404_NOT_FOUND
    name = request.form.get('name')
    location = request.form.get('location')
    size = request.form.get('size')
    image_file = request.files.get('image')
    if name or location or size:
        company.name = name
        company.location = location
        company.size = size
    if image_file:
        image_url, image_file_id = update_image_to_imagekit(image_file, company.image_file_id) #pass the old image id
        if not image_url:
            return jsonify({
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Image upload to ImageKit failed"
            }), status.HTTP_500_INTERNAL_SERVER_ERROR
        company.image_url = image_url
        company.image_file_id = image_file_id
    tradebooth.company = company
    if existing_company := db.session.query(Company).filter_by(name=name,size=size,location=location).first():
        return jsonify({
            "status": status.HTTP_409_CONFLICT,
            "message": "Company already exists with the given credentials"
        }), status.HTTP_409_CONFLICT        
    db.session.commit()
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Company updated successfully",
        "data":company.to_dict()
    }), status.HTTP_200_OK
    
@bp.route('/get-single-company/<int:company_id>', methods=['GET'])
@token_required
def get_company(company_id):
    company = db.session.query(Company).get(company_id)
    if not company:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Company not found"
        }), status.HTTP_404_NOT_FOUND
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Company retrieved successfully",
        "data": company.to_dict()
    }), status.HTTP_200_OK
    
@bp.route('/get-all-companies', methods=['GET'])
@token_required
def get_all_companies():
    companies = db.session.query(Company).all()
    companies_list = [company.to_dict() for company in companies]
    if not companies_list:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "No Data found"
        }), status.HTTP_404_NOT_FOUND
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Companies Data retrieved successfully",
        "data": companies_list
    }), status.HTTP_200_OK
    
@bp.route('/delete-company/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = db.session.query(Company).get(company_id)
    if not company:
        return jsonify({
            "status": status.HTTP_404_NOT_FOUND,
            "message": "Company not found"
        }), status.HTTP_404_NOT_FOUND
    if company.image_file_id:
        delete_image_from_imagekit(company.image_file_id)
    db.session.delete(company)
    db.session.commit()
    return jsonify({
        "status": status.HTTP_200_OK,
        "message": "Company deleted successfully"
    }), status.HTTP_200_OK
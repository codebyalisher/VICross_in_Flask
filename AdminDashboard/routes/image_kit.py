import logging
import mimetypes
from flask import current_app
from imagekitio import ImageKit
from werkzeug.utils import secure_filename
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from imagekitio.models.UpdateFileRequestOptions import UpdateFileRequestOptions


def image_kit():
    IMAGE_KIT_PUBLIC_KEY = current_app.config['IMAGE_KIT_PUBLIC_KEY']
    IMAGE_KIT_PRIVATE_KEY = current_app.config['IMAGE_KIT_PRIVATE_KEY']
    IMAGE_KIT_URL_ENDPOINT = current_app.config['IMAGE_KIT_URL_ENDPOINT']
    try:
        logging.debug("Initializing ImageKit client...")
        imagekit = ImageKit(
            private_key=IMAGE_KIT_PRIVATE_KEY,
            public_key=IMAGE_KIT_PUBLIC_KEY,
            url_endpoint=IMAGE_KIT_URL_ENDPOINT
        )

        logging.debug("ImageKit client initialized successfully")
        return imagekit
    except Exception as e:
        logging.error(f"Error initializing ImageKit client: {e}")
        return None

def upload_image_to_imagekit(file):
    imagekit = image_kit()
    if imagekit is None:
        logging.error("ImageKit client initialization failed.")
        return None
    file_name = secure_filename(file.filename)
    options = UploadFileRequestOptions(
    use_unique_file_name=True,
    tags=['user-upload'],
    folder='/user-images/',
    is_private_file=False,
    is_published=True )
    try:
        upload_info = imagekit.upload_file(
            file=file.stream,
            file_name=file_name ,
            options=options,            
        )
        logging.error(f"ImageKit upload result: {upload_info}")       
        return upload_info.url, upload_info.file_id
    except Exception as e:
        logging.error(f"Error uploading image to ImageKit: {e}")
        return None    

def update_image_to_imagekit(file, file_id):
    imagekit = image_kit()
    if imagekit is None:
        logging.error("ImageKit client initialization failed.")
        return None
    try:        
        upload_info = imagekit.upload_file(file = file.stream, file_name = file.filename)
        options = UpdateFileRequestOptions(
            tags=['updated-image'],   
        )
        imagekit.update_file_details(file_id=file_id, options=options)
        return upload_info.url, upload_info.file_id
    except Exception as e:
        logging.error(f"ImageKit API Error: {e}")
        return None
    except Exception as e:
        logging.error(f"Error updating image in ImageKit: {e}")
        return None

def delete_image_from_imagekit(file_id):
    imagekit = image_kit()
    if file_id is None:
        logging.warning("No file_id provided for deletion.")
        return {'status': 'warning', 'message': 'No file_id provided'}
    try:
        result = imagekit.delete_file(file_id=file_id)
        return {'status': 'success', 'message': 'File deleted successfully'}
    except Exception as e:
        logging.error(f"ImageKit API Error during deletion: {e}")
        return {'status': 'error', 'message': str(e)}
    except Exception as e:
        logging.error(f"Error deleting image from ImageKit: {e}")
        return {'status': 'error', 'message': str(e)}

def get_image_from_imagekit(file_id):
    imagekit = image_kit()
    try:
        result = imagekit.get_file_details(file_id=file_id)
        if result:
            return {'url': result.url, 'file_id': result.file_id}
        else:
            return None
    except Exception as e:
        logging.error(f"Error fetching image details: {e}")
        return None
    
def upload_image_to_imagekit_with_filepath(file_path):
    upload_info = imagekit.upload_file(
        file=open(file_path, "rb"),  # Open the file in binary mode
        file_name="your_image_name.jpg"  # Name to save the file as in ImageKit
    )
    image_url = upload_info.url
    return image_url





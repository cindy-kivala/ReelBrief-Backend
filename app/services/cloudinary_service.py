"""
Cloudinary Service
Owner: Cindy
Description: Manages file uploads, transformations, and deletions using Cloudinary API.
"""

# TODO: Cindy - Implement Cloudinary Service
import os
import logging
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename

# Add logger at the top
logger = logging.getLogger(__name__)


class CloudinaryService:
    """Service for handling Cloudinary file operations"""

    # Track if Cloudinary has been initialized
    _initialized = False

    @staticmethod
    def init_cloudinary():
        """Initialize Cloudinary configuration"""
        if not CloudinaryService._initialized:
            cloudinary.config(
                cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
                api_key=os.getenv('CLOUDINARY_API_KEY'),
                api_secret=os.getenv('CLOUDINARY_API_SECRET'),
                secure=True
            )
            CloudinaryService._initialized = True

# Required functions:
#
# def upload_file(file, folder):
#     """Upload a file to Cloudinary."""
    @staticmethod
    def upload_file(file, folder='reelbrief', resource_type='auto'):
        """
        Upload a file to Cloudinary.
        
        Args:
            file: File object from request.files
            folder: Cloudinary folder name (default: 'reelbrief')
            resource_type: Type of file ('image', 'video', 'raw', 'auto')
        
        Returns:
            dict: Upload response with URL, public_id, etc.
        
        Raises:
            Exception: If upload fails
        """
        try:
            CloudinaryService.init_cloudinary()
            
            # Secure the filename
            filename = secure_filename(file.filename)
            
            # Upload to Cloudinary
            upload_result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type=resource_type,
                use_filename=True,
                unique_filename=True,
                overwrite=False
            )
            
            return {
                'success': True,
                'url': upload_result.get('secure_url'),
                'public_id': upload_result.get('public_id'),
                'format': upload_result.get('format'),
                'resource_type': upload_result.get('resource_type'),
                'bytes': upload_result.get('bytes'),
                'width': upload_result.get('width'),
                'height': upload_result.get('height'),
                'thumbnail_url': CloudinaryService._generate_thumbnail_url(upload_result)
            }
        
        except Exception as e:
            logger.error(f"Cloudinary upload failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

#
# def delete_file(public_id):
#     """Delete a file from Cloudinary."""
    
    @staticmethod
    def delete_file(public_id, resource_type='image'):
        """
        Delete a file from Cloudinary.
        
        Args:
            public_id: The public ID of the file to delete
            resource_type: Type of file ('image', 'video', 'raw')
        
        Returns:
            dict: Deletion response
        """
        try:
            CloudinaryService.init_cloudinary()
            
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type=resource_type,
                invalidate=True
            )
            
            return {
                'success': result.get('result') == 'ok',
                'result': result.get('result')
            }
        
        except Exception as e:
            # CONFIRM: Use regular logger instead of current_app.logger
            logger.error(f"Cloudinary deletion failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
#
# def generate_secure_url(public_id):
#     """Return signed, secure URL for viewing file."""

    @staticmethod
    def generate_secure_url(public_id, transformation=None):
        """
        Generate a secure URL for viewing file.
        
        Args:
            public_id: The public ID of the file
            transformation: Optional transformation parameters
        
        Returns:
            str: Secure URL
        """
        try:
            CloudinaryService.init_cloudinary()
            
            if transformation:
                url = cloudinary.CloudinaryImage(public_id).build_url(**transformation)
            else:
                url = cloudinary.CloudinaryImage(public_id).build_url()
            
            return url
        
        except Exception as e:
            logger.error(f"URL generation failed: {str(e)}")
            return None
#
# def get_file_metadata(public_id):
#     """Retrieve metadata for uploaded asset."""
    @staticmethod
    def get_file_metadata(public_id, resource_type='image'):
        """
        Retrieve metadata for uploaded asset.
        
        Args:
            public_id: The public ID of the file
            resource_type: Type of file ('image', 'video', 'raw')
        
        Returns:
            dict: File metadata
        """
        try:
            CloudinaryService.init_cloudinary()
            
            result = cloudinary.api.resource(
                public_id,
                resource_type=resource_type
            )
            
            return {
                'success': True,
                'public_id': result.get('public_id'),
                'format': result.get('format'),
                'resource_type': result.get('resource_type'),
                'bytes': result.get('bytes'),
                'width': result.get('width'),
                'height': result.get('height'),
                'url': result.get('secure_url'),
                'created_at': result.get('created_at')
            }
        
        except Exception as e:
            logger.error(f"Metadata retrieval failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


    @staticmethod
    def _generate_thumbnail_url(upload_result):
        """
        Generate thumbnail URL for images/videos.
        
        Args:
            upload_result: Result from Cloudinary upload
        
        Returns:
            str: Thumbnail URL or None
        """
        public_id = upload_result.get('public_id')
        resource_type = upload_result.get('resource_type')
        
        if resource_type == 'image':
            # Generate 300x300 thumbnail for images
            return cloudinary.CloudinaryImage(public_id).build_url(
                width=300,
                height=300,
                crop='fill',
                quality='auto'
            )
        elif resource_type == 'video':
            # Generate video thumbnail from first frame
            return cloudinary.CloudinaryVideo(public_id).build_url(
                resource_type='video',
                format='jpg',
                transformation=[
                    {'width': 300, 'height': 300, 'crop': 'fill'},
                    {'start_offset': '0'}
                ]
            )
        
        return None

    @staticmethod
    def allowed_file(filename, allowed_extensions=None):
        """
        Check if file extension is allowed.
        
        Args:
            filename: Name of the file
            allowed_extensions: Set of allowed extensions (default: images, videos, docs)
        
        Returns:
            bool: True if file is allowed
        """
        if allowed_extensions is None:
            # Add pptx to allowed extensions
            allowed_extensions = {
                'png', 'jpg', 'jpeg', 'gif', 'webp',  # Images
                'mp4', 'mov', 'avi', 'mkv',  # Videos
                'pdf', 'doc', 'docx', 'txt', 'pptx'  # Documents (added pptx)
            }
        
        if '.' not in filename:
            return False
            
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in allowed_extensions
    
    @staticmethod
    def get_file_type(filename):
        """
        Determine file type from extension.
        
        Args:
            filename: Name of the file
        
        Returns:
            str: File type ('image', 'video', 'document', 'unknown')
        """
        if '.' not in filename:
            return 'unknown'

        extension = filename.rsplit('.', 1)[1].lower()
        
        image_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
        video_extensions = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
        document_extensions = {'pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx'}
        
        if extension in image_extensions:
            return 'image'
        elif extension in video_extensions:
            return 'video'
        elif extension in document_extensions:
            return 'document'
        
        return 'unknown'

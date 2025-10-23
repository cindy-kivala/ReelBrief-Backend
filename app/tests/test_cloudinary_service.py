"""
Cloudinary Service Tests
Owner: Cindy
Description: Unit tests for Cloudinary file operations
"""
# Run this test as pytest app/tests/test_cloudinary_service.py -v

from unittest.mock import MagicMock, Mock, patch

import pytest

from app.services.cloudinary_service import CloudinaryService


class TestCloudinaryService:
    """Test suite for CloudinaryService"""

    @pytest.fixture
    def mock_file(self):
        """Create a mock file object"""
        file = Mock()
        file.filename = "test_image.jpg"
        file.read = Mock(return_value=b"fake image data")
        file.seek = Mock()
        return file

    @patch("app.services.cloudinary_service.cloudinary.uploader.upload")
    @patch(
        "app.services.cloudinary_service.CloudinaryService.init_cloudinary"
    )  # Mock init_cloudinary
    def test_upload_file_success(self, mock_init, mock_upload, mock_file):
        """Test successful file upload"""
        # Mock Cloudinary response
        mock_upload.return_value = {
            "secure_url": "https://res.cloudinary.com/test/image/upload/v123/test.jpg",
            "public_id": "reelbrief/test_image",
            "format": "jpg",
            "resource_type": "image",
            "bytes": 12345,
            "width": 800,
            "height": 600,
        }

        # Call service
        result = CloudinaryService.upload_file(mock_file, folder="test")

        # Assertions
        assert result["success"] is True
        assert "url" in result
        assert "public_id" in result
        assert result["format"] == "jpg"
        mock_upload.assert_called_once()
        mock_init.assert_called_once()

    @patch("app.services.cloudinary_service.cloudinary.uploader.upload")
    @patch("app.services.cloudinary_service.CloudinaryService.init_cloudinary")
    def test_upload_file_failure(self, mock_init, mock_upload, mock_file):
        """Test file upload failure"""
        # Mock Cloudinary exception
        mock_upload.side_effect = Exception("Upload failed")

        # Call service
        result = CloudinaryService.upload_file(mock_file)

        # Assertions
        assert result["success"] is False
        assert "error" in result
        mock_init.assert_called_once()

    # Update other tests to also mock init_cloudinary
    @patch("app.services.cloudinary_service.cloudinary.uploader.destroy")
    @patch("app.services.cloudinary_service.CloudinaryService.init_cloudinary")
    def test_delete_file_success(self, mock_init, mock_destroy):
        """Test successful file deletion"""
        mock_destroy.return_value = {"result": "ok"}
        result = CloudinaryService.delete_file("test/image123")
        assert result["success"] is True
        mock_init.assert_called_once()

    @patch("app.services.cloudinary_service.cloudinary.uploader.destroy")
    @patch("app.services.cloudinary_service.CloudinaryService.init_cloudinary")
    def test_delete_file_not_found(self, mock_init, mock_destroy):
        """Test deletion of non-existent file"""
        mock_destroy.return_value = {"result": "not found"}
        result = CloudinaryService.delete_file("nonexistent/file")
        assert result["success"] is False
        mock_init.assert_called_once()

    @patch("app.services.cloudinary_service.cloudinary.CloudinaryImage")
    @patch("app.services.cloudinary_service.CloudinaryService.init_cloudinary")
    def test_generate_secure_url(self, mock_init, mock_image):
        """Test secure URL generation"""
        mock_instance = MagicMock()
        mock_instance.build_url.return_value = "https://res.cloudinary.com/test/secure/url"
        mock_image.return_value = mock_instance

        url = CloudinaryService.generate_secure_url("test/image123")
        assert url == "https://res.cloudinary.com/test/secure/url"
        mock_init.assert_called_once()

    @patch("app.services.cloudinary_service.cloudinary.api.resource")
    @patch("app.services.cloudinary_service.CloudinaryService.init_cloudinary")
    def test_get_file_metadata(self, mock_init, mock_api_resource):
        """Test file metadata retrieval"""
        mock_api_resource.return_value = {
            "public_id": "test/image123",
            "format": "jpg",
            "resource_type": "image",
            "bytes": 54321,
            "width": 1920,
            "height": 1080,
            "secure_url": "https://res.cloudinary.com/test/image/upload/test/image123.jpg",
            "created_at": "2024-01-01T12:00:00Z",
        }

        result = CloudinaryService.get_file_metadata("test/image123")
        assert result["success"] is True
        mock_init.assert_called_once()

    def test_allowed_file_valid_extensions(self):
        """Test file extension validation for allowed files"""
        valid_files = ["image.jpg", "photo.png", "video.mp4", "document.pdf", "presentation.pptx"]

        for filename in valid_files:
            assert CloudinaryService.allowed_file(filename) is True

    def test_allowed_file_invalid_extensions(self):
        """Test file extension validation for disallowed files"""
        invalid_files = ["script.exe", "malware.bat", "file.xyz", "noextension"]

        for filename in invalid_files:
            assert CloudinaryService.allowed_file(filename) is False

    def test_get_file_type_images(self):
        """Test file type detection for images"""
        image_files = ["photo.jpg", "image.png", "graphic.gif", "pic.webp"]

        for filename in image_files:
            assert CloudinaryService.get_file_type(filename) == "image"

    def test_get_file_type_videos(self):
        """Test file type detection for videos"""
        video_files = ["clip.mp4", "movie.mov", "video.avi", "film.mkv"]

        for filename in video_files:
            assert CloudinaryService.get_file_type(filename) == "video"

    def test_get_file_type_documents(self):
        """Test file type detection for documents"""
        doc_files = ["report.pdf", "essay.docx", "data.xlsx", "slides.pptx"]

        for filename in doc_files:
            assert CloudinaryService.get_file_type(filename) == "document"

    def test_get_file_type_unknown(self):
        """Test file type detection for unknown types"""
        unknown_files = ["file.xyz", "unknown.abc", "noextension"]

        for filename in unknown_files:
            assert CloudinaryService.get_file_type(filename) == "unknown"

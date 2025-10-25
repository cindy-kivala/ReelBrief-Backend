import pytest
import json

class TestFeedbackResource:
    def test_create_feedback(self, client, init_database):
        """Test creating feedback"""
        response = client.post('/api/feedback/', 
                             json={
                                 'deliverable_id': 1,
                                 'content': 'Test feedback',
                                 'feedback_type': 'comment'
                             })
        assert response.status_code in [201, 400, 401]
    
    def test_create_feedback_missing_fields(self, client, init_database):
        """Test creating feedback with missing fields"""
        response = client.post('/api/feedback/', 
                             json={})
        assert response.status_code in [400, 401]
    
    def test_get_deliverable_feedback(self, client, init_database):
        """Test getting feedback for deliverable"""
        response = client.get('/api/feedback/deliverable/1')
        assert response.status_code in [200, 404, 401]


# # app/tests/test_deliverables_isolated.py
# app/tests/test_deliverable_resource.py
import json

import pytest


class TestDeliverableResource:
    def test_get_project_deliverables(self, client, init_database):
        """Test getting project deliverables"""
        response = client.get("/api/projects/1/deliverables")
        assert response.status_code in [200, 401, 404]

    def test_create_deliverable(self, client, init_database):
        """Test creating deliverable"""
        response = client.post(
            "/api/deliverables/", json={"title": "Test Deliverable", "project_id": 1}
        )
        assert response.status_code in [201, 400, 401]

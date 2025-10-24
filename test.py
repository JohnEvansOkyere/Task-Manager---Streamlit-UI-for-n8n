"""
Tests for Task Manager API
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def mock_n8n_service():
    """Mock N8N service"""
    with patch('app.main.n8n_service') as mock:
        mock.send_message = AsyncMock(return_value={"tasks": []})
        mock.test_connection = AsyncMock(return_value=True)
        yield mock


class TestHealthEndpoint:
    """Tests for health check endpoint"""
    
    def test_health_check_success(self, client, mock_n8n_service):
        """Test successful health check"""
        mock_n8n_service.test_connection.return_value = True
        
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data


class TestRootEndpoint:
    """Tests for root endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "Task Manager API"


class TestTaskEndpoints:
    """Tests for task management endpoints"""
    
    def test_get_tasks_success(self, client, mock_n8n_service):
        """Test successful task retrieval"""
        mock_tasks = [
            {
                "task_name": "Test Task",
                "status": "TODO",
                "description": "Test description",
                "deadline": "2025-12-31"
            }
        ]
        mock_n8n_service.send_message.return_value = {"tasks": mock_tasks}
        
        response = client.get("/api/v1/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert data["count"] == 1
    
    def test_get_tasks_with_filter(self, client, mock_n8n_service):
        """Test task retrieval with status filter"""
        mock_n8n_service.send_message.return_value = {"tasks": []}
        
        response = client.get("/api/v1/tasks?status_filter=TODO")
        
        assert response.status_code == 200
        mock_n8n_service.send_message.assert_called_once()
    
    def test_create_task_success(self, client, mock_n8n_service):
        """Test successful task creation"""
        mock_n8n_service.send_message.return_value = {"success": True}
        
        task_data = {
            "task_name": "New Task",
            "status": "TODO",
            "description": "Test task",
            "deadline": "2025-12-31"
        }
        
        response = client.post("/api/v1/tasks", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert "Task 'New Task' created successfully" in data["message"]
    
    def test_create_task_validation_error(self, client):
        """Test task creation with invalid data"""
        task_data = {
            "task_name": "",  # Invalid: empty name
            "status": "TODO"
        }
        
        response = client.post("/api/v1/tasks", json=task_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_update_task_success(self, client, mock_n8n_service):
        """Test successful task update"""
        mock_n8n_service.send_message.return_value = {"success": True}
        
        update_data = {
            "status": "IN PROGRESS"
        }
        
        response = client.put("/api/v1/tasks/Test Task", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_update_task_no_fields(self, client):
        """Test task update with no fields"""
        update_data = {}
        
        response = client.put("/api/v1/tasks/Test Task", json=update_data)
        
        assert response.status_code == 400
    
    def test_delete_task_success(self, client, mock_n8n_service):
        """Test successful task deletion"""
        mock_n8n_service.send_message.return_value = {"success": True}
        
        response = client.delete("/api/v1/tasks/Test Task")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestMessageEndpoint:
    """Tests for natural language message endpoint"""
    
    def test_send_message_success(self, client, mock_n8n_service):
        """Test successful message processing"""
        mock_n8n_service.send_message.return_value = {
            "output": "Here are your tasks",
            "tasks": []
        }
        
        message_data = {
            "message": "Show me all tasks",
            "session_id": "test-session"
        }
        
        response = client.post("/api/v1/message", json=message_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "timestamp" in data


class TestStatsEndpoint:
    """Tests for statistics endpoint"""
    
    def test_get_stats_success(self, client, mock_n8n_service):
        """Test successful stats retrieval"""
        mock_tasks = [
            {"status": "TODO"},
            {"status": "IN PROGRESS"},
            {"status": "DONE"}
        ]
        mock_n8n_service.send_message.return_value = {"tasks": mock_tasks}
        
        response = client.get("/api/v1/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "by_status" in data
        assert "completion_rate" in data
        assert data["total_tasks"] == 3
        assert data["completion_rate"] > 0


class TestCacheService:
    """Tests for cache service"""
    
    def test_cache_set_and_get(self):
        """Test cache set and get operations"""
        from app.services.cache_service import CacheService
        
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=60)
        
        assert cache.get("test_key") == "test_value"
    
    def test_cache_expiry(self):
        """Test cache expiry"""
        from app.services.cache_service import CacheService
        from datetime import datetime, timedelta
        
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=0)
        
        # Force expiry
        cache.expiry["test_key"] = datetime.utcnow() - timedelta(seconds=1)
        
        assert cache.get("test_key") is None
    
    def test_cache_delete(self):
        """Test cache deletion"""
        from app.services.cache_service import CacheService
        
        cache = CacheService()
        cache.set("test_key", "test_value")
        cache.delete("test_key")
        
        assert cache.get("test_key") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
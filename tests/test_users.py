import pytest
from fastapi import status


class TestCreateUser:
    def test_create_user_success(self, client, sample_user_data):
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert "id" in data
        assert data["username"] == sample_user_data["username"]
        assert data["email"] == sample_user_data["email"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert data["role"] == sample_user_data["role"]
        assert data["active"] == sample_user_data["active"]
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_user_duplicate_username(self, client, sample_user_data):
        response1 = client.post("/api/v1/users/", json=sample_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        duplicate_data = sample_user_data.copy()
        duplicate_data["email"] = "different@example.com"
        response2 = client.post("/api/v1/users/", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "username" in response2.json()["detail"].lower()
    
    def test_create_user_duplicate_email(self, client, sample_user_data):
        response1 = client.post("/api/v1/users/", json=sample_user_data)
        assert response1.status_code == status.HTTP_201_CREATED
        
        duplicate_data = sample_user_data.copy()
        duplicate_data["username"] = "different_user"
        response2 = client.post("/api/v1/users/", json=duplicate_data)
        
        assert response2.status_code == status.HTTP_409_CONFLICT
        assert "email" in response2.json()["detail"].lower()
    
    def test_create_user_invalid_email(self, client, sample_user_data):
        invalid_data = sample_user_data.copy()
        invalid_data["email"] = "not-an-email"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_short_username(self, client, sample_user_data):
        invalid_data = sample_user_data.copy()
        invalid_data["username"] = "ab"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_invalid_username_chars(self, client, sample_user_data):
        invalid_data = sample_user_data.copy()
        invalid_data["username"] = "user@name!"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_invalid_role(self, client, sample_user_data):
        invalid_data = sample_user_data.copy()
        invalid_data["role"] = "superuser"
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_missing_required_field(self, client):
        incomplete_data = {
            "username": "testuser",
            "email": "test@example.com"
        }
        
        response = client.post("/api/v1/users/", json=incomplete_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_default_values(self, client):
        minimal_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=minimal_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["role"] == "user"
        assert data["active"] is True


class TestGetUsers:
    
    def test_get_all_users_empty(self, client):
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["users"] == []
        assert data["skip"] == 0
        assert data["limit"] == 100
    
    def test_get_all_users(self, client, multiple_users):
        response = client.get("/api/v1/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 2
    
    def test_get_users_pagination(self, client, multiple_users):
        response = client.get("/api/v1/users/?skip=0&limit=1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 2
        assert len(data["users"]) == 1
        assert data["skip"] == 0
        assert data["limit"] == 1
    
    def test_get_users_filter_by_active(self, client, created_user):
        inactive_user_data = {
            "username": "inactive_user",
            "email": "inactive@example.com",
            "first_name": "Inactive",
            "last_name": "User",
            "active": False
        }
        client.post("/api/v1/users/", json=inactive_user_data)
        
        response = client.get("/api/v1/users/?active=true")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(user["active"] is True for user in data["users"])
    
    def test_get_users_filter_by_role(self, client, multiple_users):
        response = client.get("/api/v1/users/?role=admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert all(user["role"] == "admin" for user in data["users"])


class TestGetUser:
    
    def test_get_user_success(self, client, created_user):
        user_id = created_user["id"]
        response = client.get(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == created_user["username"]
    
    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_user_invalid_id(self, client):
        response = client.get("/api/v1/users/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUpdateUser:
    
    def test_update_user_success(self, client, created_user):
        user_id = created_user["id"]
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "Name"
        assert data["username"] == created_user["username"]
        assert data["email"] == created_user["email"]
    
    def test_update_user_all_fields(self, client, created_user):
        user_id = created_user["id"]
        update_data = {
            "username": "updated_username",
            "email": "updated@example.com",
            "first_name": "Updated",
            "last_name": "User",
            "role": "admin",
            "active": False
        }
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == "updated_username"
        assert data["email"] == "updated@example.com"
        assert data["first_name"] == "Updated"
        assert data["last_name"] == "User"
        assert data["role"] == "admin"
        assert data["active"] is False
    
    def test_update_user_not_found(self, client):
        update_data = {"first_name": "Test"}
        response = client.put("/api/v1/users/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_update_user_duplicate_username(self, client, multiple_users):
        user1_id = multiple_users[0]["id"]
        user2_username = multiple_users[1]["username"]
        
        update_data = {"username": user2_username}
        response = client.put(f"/api/v1/users/{user1_id}", json=update_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "username" in response.json()["detail"].lower()
    
    def test_update_user_duplicate_email(self, client, multiple_users):
        user1_id = multiple_users[0]["id"]
        user2_email = multiple_users[1]["email"]
        
        update_data = {"email": user2_email}
        response = client.put(f"/api/v1/users/{user1_id}", json=update_data)
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email" in response.json()["detail"].lower()
    
    def test_update_user_invalid_email(self, client, created_user):
        user_id = created_user["id"]
        update_data = {"email": "notamemail"}
        
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_update_user_partial(self, client, created_user):
        user_id = created_user["id"]
        original_email = created_user["email"]
        
        update_data = {"first_name": "NewName"}
        response = client.put(f"/api/v1/users/{user_id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == "NewName"
        assert data["email"] == original_email


class TestDeleteUser:
    
    def test_delete_user_success(self, client, created_user):
        user_id = created_user["id"]
        response = client.delete(f"/api/v1/users/{user_id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_user_not_found(self, client):
        response = client.delete("/api/v1/users/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_user_invalid_id(self, client):
        response = client.delete("/api/v1/users/invalid")
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRootEndpoints:
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
    
    def test_health_endpoint(self, client):
        response = client.get("/health")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "app_name" in data
        assert "version" in data


class TestEdgeCases:
    
    def test_username_minimum_length(self, client):
        user_data = {
            "username": "abc",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_username_with_underscores(self, client):
        user_data = {
            "username": "user_name_123",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_empty_string_name(self, client):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_whitespace_only_name(self, client):
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "   ",
            "last_name": "User"
        }
        
        response = client.post("/api/v1/users/", json=user_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_pagination_negative_skip(self, client):
        response = client.get("/api/v1/users/?skip=-1")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_pagination_zero_limit(self, client):
        response = client.get("/api/v1/users/?limit=0")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_all_roles(self, client):
        roles = ["admin", "user", "guest"]
        
        for i, role in enumerate(roles):
            user_data = {
                "username": f"user_{role}",
                "email": f"{role}@example.com",
                "first_name": "Test",
                "last_name": "User",
                "role": role
            }
            
            response = client.post("/api/v1/users/", json=user_data)
            assert response.status_code == status.HTTP_201_CREATED
            assert response.json()["role"] == role


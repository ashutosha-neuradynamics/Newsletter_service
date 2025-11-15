import pytest


def test_create_subscriber(client):
    response = client.post(
        "/api/subscribers/",
        json={"email": "test@example.com"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_subscriber_invalid_email(client):
    response = client.post(
        "/api/subscribers/",
        json={"email": "invalid-email"}
    )
    assert response.status_code == 422


def test_create_subscriber_duplicate_email(client):
    client.post("/api/subscribers/", json={"email": "test@example.com"})
    response = client.post("/api/subscribers/", json={"email": "test@example.com"})
    assert response.status_code == 400


def test_list_subscribers(client):
    client.post("/api/subscribers/", json={"email": "user1@example.com"})
    client.post("/api/subscribers/", json={"email": "user2@example.com"})
    
    response = client.get("/api/subscribers/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_subscriber_by_id(client):
    create_response = client.post("/api/subscribers/", json={"email": "test@example.com"})
    subscriber_id = create_response.json()["id"]
    
    response = client.get(f"/api/subscribers/{subscriber_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["id"] == subscriber_id


def test_update_subscriber(client):
    create_response = client.post("/api/subscribers/", json={"email": "test@example.com"})
    subscriber_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/subscribers/{subscriber_id}",
        json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


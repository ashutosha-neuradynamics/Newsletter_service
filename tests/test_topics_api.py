import pytest


def test_create_topic(client):
    response = client.post(
        "/api/topics/",
        json={"name": "Technology", "description": "Tech news and updates"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Technology"
    assert data["description"] == "Tech news and updates"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_topic_duplicate_name(client):
    client.post("/api/topics/", json={"name": "Technology"})
    response = client.post("/api/topics/", json={"name": "Technology"})
    assert response.status_code == 400


def test_list_topics(client):
    client.post("/api/topics/", json={"name": "Technology"})
    client.post("/api/topics/", json={"name": "Science"})
    
    response = client.get("/api/topics/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(topic["name"] == "Technology" for topic in data)
    assert any(topic["name"] == "Science" for topic in data)


def test_get_topic_by_id(client):
    create_response = client.post("/api/topics/", json={"name": "Technology"})
    topic_id = create_response.json()["id"]
    
    response = client.get(f"/api/topics/{topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Technology"
    assert data["id"] == topic_id


def test_get_topic_not_found(client):
    response = client.get("/api/topics/999")
    assert response.status_code == 404


def test_update_topic(client):
    create_response = client.post("/api/topics/", json={"name": "Technology"})
    topic_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/topics/{topic_id}",
        json={"description": "Updated description", "is_active": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["is_active"] is False


def test_delete_topic(client):
    create_response = client.post("/api/topics/", json={"name": "Technology"})
    topic_id = create_response.json()["id"]
    
    response = client.delete(f"/api/topics/{topic_id}")
    assert response.status_code == 200
    
    get_response = client.get(f"/api/topics/{topic_id}")
    assert get_response.status_code == 404


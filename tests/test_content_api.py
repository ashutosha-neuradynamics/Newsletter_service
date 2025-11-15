from app.models import ContentStatus
from datetime import datetime, timedelta
import pytest


@pytest.fixture(scope="function")
def topic_id(client):
    response = client.post("/api/topics/", json={"name": "Technology"})
    return response.json()["id"]


def test_create_content(topic_id, client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    response = client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Weekly Update",
            "body": "This is the newsletter content",
            "scheduled_at": scheduled_at,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["topic_id"] == topic_id
    assert data["title"] == "Weekly Update"
    assert data["body"] == "This is the newsletter content"
    assert data["status"] == ContentStatus.PENDING.value
    assert "id" in data
    assert "created_at" in data


def test_create_content_invalid_topic(client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    response = client.post(
        "/api/content/",
        json={
            "topic_id": 999,
            "title": "Weekly Update",
            "body": "This is the newsletter content",
            "scheduled_at": scheduled_at,
        },
    )
    assert response.status_code == 404


def test_list_content(topic_id, client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Update 1",
            "body": "Content 1",
            "scheduled_at": scheduled_at,
        },
    )
    client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Update 2",
            "body": "Content 2",
            "scheduled_at": scheduled_at,
        },
    )

    response = client.get("/api/content/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_list_content_filter_by_topic(topic_id, client):
    topic2_response = client.post("/api/topics/", json={"name": "Science"})
    topic2_id = topic2_response.json()["id"]

    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Tech Update",
            "body": "Tech content",
            "scheduled_at": scheduled_at,
        },
    )
    client.post(
        "/api/content/",
        json={
            "topic_id": topic2_id,
            "title": "Science Update",
            "body": "Science content",
            "scheduled_at": scheduled_at,
        },
    )

    response = client.get(f"/api/content/?topic_id={topic_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["topic_id"] == topic_id


def test_list_content_filter_by_status(topic_id, client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Pending Update",
            "body": "Pending content",
            "scheduled_at": scheduled_at,
        },
    )

    response = client.get(f"/api/content/?status={ContentStatus.PENDING.value}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(content["status"] == ContentStatus.PENDING.value for content in data)


def test_get_content_by_id(topic_id, client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    create_response = client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Weekly Update",
            "body": "Content body",
            "scheduled_at": scheduled_at,
        },
    )
    content_id = create_response.json()["id"]

    response = client.get(f"/api/content/{content_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == content_id
    assert data["title"] == "Weekly Update"


def test_update_content(topic_id, client):
    scheduled_at = (datetime.utcnow() + timedelta(hours=1)).isoformat()
    create_response = client.post(
        "/api/content/",
        json={
            "topic_id": topic_id,
            "title": "Original Title",
            "body": "Original body",
            "scheduled_at": scheduled_at,
        },
    )
    content_id = create_response.json()["id"]

    response = client.patch(
        f"/api/content/{content_id}",
        json={"title": "Updated Title", "status": ContentStatus.CANCELLED.value},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["status"] == ContentStatus.CANCELLED.value

import pytest


@pytest.fixture(scope="function")
def topic_and_subscriber(client):
    topic_response = client.post("/api/topics/", json={"name": "Technology"})
    subscriber_response = client.post("/api/subscribers/", json={"email": "test@example.com"})
    return {
        "topic_id": topic_response.json()["id"],
        "subscriber_id": subscriber_response.json()["id"]
    }


def test_create_subscription(topic_and_subscriber, client):
    response = client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["subscriber_id"] == topic_and_subscriber["subscriber_id"]
    assert data["topic_id"] == topic_and_subscriber["topic_id"]
    assert data["is_active"] is True


def test_create_subscription_invalid_subscriber(topic_and_subscriber, client):
    response = client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": 999,
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    assert response.status_code == 404


def test_create_subscription_invalid_topic(topic_and_subscriber, client):
    response = client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": 999
        }
    )
    assert response.status_code == 404


def test_list_subscriptions(topic_and_subscriber, client):
    client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    
    response = client.get("/api/subscriptions/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_list_subscriptions_filter_by_subscriber(topic_and_subscriber, client):
    client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    
    response = client.get(f"/api/subscriptions/?subscriber_id={topic_and_subscriber['subscriber_id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(sub["subscriber_id"] == topic_and_subscriber["subscriber_id"] for sub in data)


def test_list_subscriptions_filter_by_topic(topic_and_subscriber, client):
    client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    
    response = client.get(f"/api/subscriptions/?topic_id={topic_and_subscriber['topic_id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(sub["topic_id"] == topic_and_subscriber["topic_id"] for sub in data)


def test_create_subscription_duplicate(topic_and_subscriber, client):
    client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    response = client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    assert response.status_code == 400


def test_update_subscription(topic_and_subscriber, client):
    create_response = client.post(
        "/api/subscriptions/",
        json={
            "subscriber_id": topic_and_subscriber["subscriber_id"],
            "topic_id": topic_and_subscriber["topic_id"]
        }
    )
    subscription_id = create_response.json()["id"]
    
    response = client.patch(
        f"/api/subscriptions/{subscription_id}",
        json={"is_active": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False


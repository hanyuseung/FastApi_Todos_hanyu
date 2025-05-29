import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from fastapi.testclient import TestClient
from main import app, save_todos, load_todos, TodoItem

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # 테스트 전 초기화
    save_todos([])
    yield
    # 테스트 후 정리
    save_todos([])

def test_get_todos_empty():
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_get_todos_with_items():
    # detail_content와 todayFlag를 포함하도록 생성
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        detail="Detailed info",
        completed=False,
        priority=1,
        todayFlag=True
    )
    save_todos([todo.dict()])

    response = client.get("/todos")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1

    item = data[0]
    assert item["title"] == "Test"
    assert item["description"] == "Test description"
    assert item["detail"] == "Detailed info"
    assert item["completed"] is False
    assert item["priority"] == 1
    assert item["todayFlag"] is True

def test_create_todo():
    # payload에 detail_content와 todayFlag 포함
    payload = {
        "id": 1,
        "title": "Test",
        "description": "Test description",
        "detail": "Some details",
        "completed": False,
        "priority": 1,
        "todayFlag": True
    }
    response = client.post("/todos", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Test"
    assert data["detail"] == "Some details"
    assert data["todayFlag"] is True

def test_create_todo_invalid():
    # 필수 필드(description, completed, priority) 빠진 경우 여전히 422
    todo = {"id": 1, "title": "Test"}
    response = client.post("/todos", json=todo)
    assert response.status_code == 422

def test_update_todo():
    # 먼저 아이템 저장
    original = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        detail="Old details",
        completed=False,
        priority=1,
        todayFlag=False
    )
    save_todos([original.dict()])

    # 업데이트할 payload
    updated = {
        "id": 1,
        "title": "Updated",
        "description": "Updated description",
        "detail": "New details",
        "completed": True,
        "priority": 2,
        "todayFlag": True
    }
    response = client.put("/todos/1", json=updated)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Updated"
    assert data["detail"] == "New details"
    assert data["completed"] is True
    assert data["priority"] == 2
    assert data["todayFlag"] is True

def test_update_todo_not_found():
    updated_todo = {
        "id": 1,
        "title": "Updated",
        "description": "Updated description",
        "detail": "Details",
        "completed": True,
        "priority": 2,
        "todayFlag": False
    }
    response = client.put("/todos/1", json=updated_todo)
    assert response.status_code == 404

def test_patch_completed():
    # completed만 패치하는 기존 엔드포인트 테스트
    todo = TodoItem(
        id=1,
        title="Test",
        description="Desc",
        detail="Info",
        completed=False,
        priority=1,
        todayFlag=False
    )
    save_todos([todo.dict()])

    response = client.patch("/todos/1/completed", json={"completed": True})
    assert response.status_code == 200

    data = response.json()
    assert data["completed"] is True

def test_delete_todo():
    todo = TodoItem(
        id=1,
        title="Test",
        description="Test description",
        detail="Detail",
        completed=False,
        priority=1,
        todayFlag=False
    )
    save_todos([todo.dict()])

    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"

def test_delete_todo_not_found():
    response = client.delete("/todos/1")
    assert response.status_code == 200
    assert response.json()["message"] == "To-Do item deleted"
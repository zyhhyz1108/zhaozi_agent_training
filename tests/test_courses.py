import pytest


def test_course_crud(client):
    # 1. 新增课程
    response = client.post(
        "/courses",
        json={
            "name": "Python 基础",
            "description": "学习函数和类",
        },
    )

    assert response.status_code == 201
    course = response.json()
    course_id = course["id"]
    assert course["status"] == "not_started"

    # 2. 查询单个课程
    response = client.get(f"/courses/{course_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Python 基础"

    # 3. 查询列表
    response = client.get("/courses")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [course_id]

    # 4. 只修改状态，确认其他字段未被覆盖
    response = client.patch(
        f"/courses/{course_id}",
        json={"status": "in_progress"},
    )

    assert response.status_code == 200
    updated = response.json()
    assert updated["status"] == "in_progress"
    assert updated["name"] == "Python 基础"
    assert updated["description"] == "学习函数和类"

    # 5. 再次查询，确认修改已经保存
    response = client.get(f"/courses/{course_id}")

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"

    # 6. 删除课程
    response = client.delete(f"/courses/{course_id}")

    assert response.status_code == 204
    assert response.content == b""

    # 7. 删除后查询
    response = client.get(f"/courses/{course_id}")

    assert response.status_code == 404

    # 8. 重复删除
    response = client.delete(f"/courses/{course_id}")

    assert response.status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"name": "   "},
        {"name": "Python", "status": "abc"},
        {"name": "Python", "status": None},
        {"name": "Python", "unknown_field": "不允许的字段"},
    ],
)
def test_create_course_invalid_input(client, payload):
    response = client.post("/courses", json=payload)

    assert response.status_code == 422
    assert client.get("/courses").json() == []


@pytest.mark.parametrize(
    "payload, expected_status",
    [
        ({}, 400),
        ({"name": "   "}, 422),
        ({"status": "abc"}, 422),
        ({"status": None}, 422),
    ],
)
def test_update_course_invalid_input(client, payload, expected_status):
    created = client.post(
        "/courses",
        json={"name": "Python 基础"},
    )
    assert created.status_code == 201
    original = created.json()
    course_id = original["id"]

    response = client.patch(
        f"/courses/{course_id}",
        json=payload,
    )

    assert response.status_code == expected_status

    # 非法修改不能改变原数据
    response = client.get(f"/courses/{course_id}")
    assert response.json() == original



def test_missing_course(client):
    assert client.get("/courses/999").status_code == 404

    response = client.patch(
        "/courses/999",
        json={"status": "completed"},
    )
    assert response.status_code == 404

    assert client.delete("/courses/999").status_code == 404
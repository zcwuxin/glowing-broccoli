"""
统一响应类测试示例
展示如何测试统一响应类
"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_response():
    """测试 ApiResponse"""
    response = client.get("/example/students/1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "查询成功"
    assert "data" in data
    assert data["data"]["name"] == "张三"


def test_list_response():
    """测试 ListResponse"""
    response = client.get("/example/students")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) == 3
    assert data["total"] == 3


def test_page_response():
    """测试 PageResponse"""
    response = client.get("/example/students/page?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 10
    assert data["total_pages"] == 10
    assert len(data["items"]) == 10


def test_success_response():
    """测试 SuccessResponse"""
    response = client.delete("/example/students/1")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "删除成功"


def test_detail_response():
    """测试 DetailResponse"""
    response = client.get("/example/students/1/detail")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert "data" in data
    assert "email" in data["data"]
    assert "phone" in data["data"]


def test_error_response():
    """测试 ErrorResponse - 参数校验错误"""
    response = client.get("/example/students/0/validate?name=a")
    assert response.status_code == 200  # 业务错误，HTTP状态码仍为200
    data = response.json()
    assert data["code"] == 400
    assert data["message"] == "参数校验失败"
    assert "errors" in data


def test_create_student():
    """测试创建学生 - 使用 CREATED 状态码"""
    response = client.post("/example/students?name=测试学生&age=22")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 201
    assert data["message"] == "创建成功"
    assert "data" in data
    assert data["data"]["name"] == "测试学生"
    assert data["data"]["age"] == 22


def test_update_student():
    """测试更新学生"""
    response = client.put("/example/students/1?name=更新后的名字")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == 200
    assert data["message"] == "更新成功"
    assert data["data"]["name"] == "更新后的名字"


def test_student_not_found():
    """测试学生不存在"""
    response = client.get("/example/students/404")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "学生不存在"


def test_helper_functions():
    """测试辅助函数"""
    response = client.get("/example/students/helper")
    assert response.status_code == 200
    data = response.json()
    assert "success_example" in data
    assert "success_list_example" in data
    assert "success_page_example" in data
    assert "error_example" in data


if __name__ == "__main__":
    # 运行所有测试
    print("开始测试统一响应类...")

    test_api_response()
    print("✓ ApiResponse 测试通过")

    test_list_response()
    print("✓ ListResponse 测试通过")

    test_page_response()
    print("✓ PageResponse 测试通过")

    test_success_response()
    print("✓ SuccessResponse 测试通过")

    test_detail_response()
    print("✓ DetailResponse 测试通过")

    test_error_response()
    print("✓ ErrorResponse 测试通过")

    test_create_student()
    print("✓ 创建学生测试通过")

    test_update_student()
    print("✓ 更新学生测试通过")

    test_student_not_found()
    print("✓ 学生不存在测试通过")

    test_helper_functions()
    print("✓ 辅助函数测试通过")

    print("\n所有测试通过！✓")

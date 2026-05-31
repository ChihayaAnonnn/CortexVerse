"""健康检查端点测试。"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """验证 /api/health 返回 200。"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

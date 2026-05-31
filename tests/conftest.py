"""测试通用配置与 fixtures。"""

import pytest
from fastapi.testclient import TestClient

from cortexverse.main import app


@pytest.fixture
def client() -> TestClient:
    """创建 FastAPI 测试客户端。"""
    return TestClient(app)

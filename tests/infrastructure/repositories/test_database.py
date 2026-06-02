"""数据库连接测试。"""

import pytest
from sqlalchemy import text

from cortexverse.infrastructure.repositories.database import DatabaseClient


@pytest.fixture
def db_client() -> DatabaseClient:
    """创建数据库客户端实例。"""
    return DatabaseClient()


class TestDatabaseConnection:
    """数据库连接测试。"""

    @pytest.mark.asyncio
    async def test_connection_success(self, db_client: DatabaseClient) -> None:
        """测试数据库连接成功。"""
        async with db_client.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

    @pytest.mark.asyncio
    async def test_connection_pool(self, db_client: DatabaseClient) -> None:
        """测试连接池可以创建多个会话。"""
        sessions = []
        for _ in range(3):
            session = db_client.get_session()
            sessions.append(session)

        # 验证所有会话都可以执行查询
        for session in sessions:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            await session.close()

    @pytest.mark.asyncio
    async def test_close_engine(self) -> None:
        """测试关闭引擎后连接释放。"""
        client = DatabaseClient()
        async with client.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1

        await client.close()
        # 关闭后引擎应该已经释放
        assert client.engine.pool.status() is not None

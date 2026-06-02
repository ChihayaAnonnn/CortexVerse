"""数据库客户端 — SQLAlchemy Async 引擎与会话管理。"""

from pathlib import Path

from loguru import logger
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cortexverse.infrastructure.repositories.world.models import Base

# 项目根目录
_ROOT_DIR = Path(__file__).resolve().parents[3]


class DatabaseSettings(BaseSettings):
    """数据库配置，从 .env 文件读取。"""

    database_url: str = "postgresql+asyncpg://cortexverse:cortexverse@localhost:5432/cortexverse"

    model_config = {
        "env_file": _ROOT_DIR / ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


class DatabaseClient:
    """异步数据库客户端。

    使用 SQLAlchemy AsyncSession 管理数据库连接。
    """

    def __init__(self, database_url: str | None = None) -> None:
        settings = DatabaseSettings()
        url = database_url or settings.database_url

        self._engine = create_async_engine(
            url,
            echo=False,
            pool_size=5,
            max_overflow=10,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("数据库客户端初始化完成")

    @property
    def engine(self):
        """获取 SQLAlchemy 异步引擎。"""
        return self._engine

    def get_session(self) -> AsyncSession:
        """获取一个新的异步会话。

        Returns:
            AsyncSession 实例，使用完毕后需调用 close()。
        """
        return self._session_factory()

    async def close(self) -> None:
        """关闭数据库引擎，释放所有连接。"""
        await self._engine.dispose()
        logger.info("数据库连接已关闭")

    async def init_db(self) -> None:
        """初始化数据库表结构。

        基于 ORM 模型的 Base.metadata 创建所有表。
        适用于开发环境快速建表，生产环境建议使用 Alembic 迁移。
        """
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("数据库表初始化完成")


# 全局单例
_db_client: DatabaseClient | None = None


def get_db_client() -> DatabaseClient:
    """获取全局数据库客户端单例。

    Returns:
        DatabaseClient 实例。
    """
    global _db_client
    if _db_client is None:
        _db_client = DatabaseClient()
    return _db_client

"""CortexVerse 入口模块。"""

from fastapi import FastAPI

from cortexverse.interfaces.api import router as api_router


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例。"""
    app = FastAPI(
        title="CortexVerse",
        description="系统驱动的虚拟内容生产线",
        version="0.1.0",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()

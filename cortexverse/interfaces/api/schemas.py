"""API 请求/响应模型。"""

from pydantic import BaseModel, Field

from cortexverse.domain.world.world_asset import WorldAsset


class WorldGenerateRequest(BaseModel):
    """世界构建请求。"""

    world_name: str = Field(description="世界名称/项目代号", min_length=1, max_length=100)
    genre_tags: list[str] = Field(description="题材标签列表", min_length=1, max_length=10)
    theme_input: str = Field(description="核心主题倾向", min_length=1, max_length=500)


class WorldGenerateResponse(BaseModel):
    """世界构建响应。"""

    world_id: str = Field(description="世界观全局唯一识别码")
    status: str = Field(description="状态：completed | failed")
    world_asset: WorldAsset | None = Field(default=None, description="构建完成的世界观资产")
    error: str | None = Field(default=None, description="错误信息")

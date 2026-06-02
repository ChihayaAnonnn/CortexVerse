"""LLM 客户端抽象基类。"""

from abc import ABC, abstractmethod

import instructor


class BaseLLMClient(ABC):
    """所有 LLM 客户端的抽象协议。

    子类必须实现 create_client()，返回 instructor 包装后的异步客户端。
    """

    @abstractmethod
    def create_client(self) -> instructor.AsyncInstructor:
        """创建并返回 instructor 异步客户端。"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """当前 provider 名称。"""

# !/usr/bin/env python
"""
==============================================================
Description  : HTTP响应适配器模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:40:00
Github       : https://github.com/sandorn/xthttp

本模块提供不同HTTP库的响应适配器，统一响应对象访问接口
==============================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

# 默认编码格式
DEFAULT_ENCODING = 'utf-8'

# 类型定义
RawResponseType = Any  # 原始响应对象类型（支持requests和aiohttp等）


class BaseRespAdapter(ABC):
    """响应适配器接口,定义统一的响应处理方法"""

    @abstractmethod
    def get_content(self) -> bytes:
        """获取原始响应内容（字节形式）"""
        pass

    @abstractmethod
    def get_status(self) -> int:
        """获取响应状态码"""
        pass

    @abstractmethod
    def get_url(self) -> str:
        """获取请求URL"""
        pass

    @abstractmethod
    def get_headers(self) -> dict[str, str]:
        """获取响应头部"""
        pass

    @abstractmethod
    def get_cookies(self) -> dict[str, str]:
        """获取响应Cookie"""
        pass

    @abstractmethod
    def get_encoding(self) -> str:
        """获取响应编码"""
        pass

    @abstractmethod
    def get_reason(self) -> str:
        """获取响应原因短语"""
        pass


class RequestsAdapter(BaseRespAdapter):
    """requests库响应适配器"""

    def __init__(self, raw_response: RawResponseType):
        self.raw_response = raw_response

    def get_content(self) -> bytes:
        """获取原始响应内容（字节形式）

        Returns:
            bytes: 响应内容的字节表示
        """
        return getattr(self.raw_response, 'content', b'')

    def get_status(self) -> int:
        """获取响应状态码

        Returns:
            int: HTTP状态码
        """
        return getattr(self.raw_response, 'status_code', 999)

    def get_url(self) -> str:
        """获取请求URL

        Returns:
            str: 请求的URL
        """
        return getattr(self.raw_response, 'url', '')

    def get_headers(self) -> dict[str, str]:
        """获取响应头部

        Returns:
            dict[str, str]: 头部字典
        """
        headers = getattr(self.raw_response, 'headers', {})
        return dict(headers) if headers else {}

    def get_cookies(self) -> dict[str, str]:
        """获取响应Cookie

        Returns:
            dict[str, str]: Cookie字典
        """
        cookies = getattr(self.raw_response, 'cookies', {})
        return dict(cookies) if cookies else {}

    def get_encoding(self) -> str:
        """获取响应编码

        Returns:
            str: 编码名称
        """
        return getattr(self.raw_response, 'encoding', DEFAULT_ENCODING)

    def get_reason(self) -> str:
        """获取响应原因短语

        Returns:
            str: 状态码对应的原因短语
        """
        return getattr(self.raw_response, 'reason', '')


class AiohttpAdapter(BaseRespAdapter):
    """aiohttp库响应适配器"""

    def __init__(self, raw_response: RawResponseType):
        self.raw_response = raw_response

    def get_content(self) -> bytes:
        """获取原始响应内容（字节形式）

        Returns:
            bytes: 响应内容的字节表示
        """
        content = getattr(self.raw_response, 'content', b'')
        # aiohttp的content可能已经是bytes类型
        return content if isinstance(content, bytes) else b''

    def get_status(self) -> int:
        """获取响应状态码

        Returns:
            int: HTTP状态码
        """
        return getattr(self.raw_response, 'status', 999)

    def get_url(self) -> str:
        """获取请求URL

        Returns:
            str: 请求的URL
        """
        request_info = getattr(self.raw_response, 'request_info', None)
        if request_info and hasattr(request_info, 'url'):
            return str(request_info.url)
        return ''

    def get_headers(self) -> dict[str, str]:
        """获取响应头部

        Returns:
            dict[str, str]: 头部字典
        """
        headers = getattr(self.raw_response, 'headers', {})
        return dict(headers) if headers else {}

    def get_cookies(self) -> dict[str, str]:
        """获取响应Cookie

        Returns:
            dict[str, str]: Cookie字典
        """
        cookies = getattr(self.raw_response, 'cookies', {})
        return dict(cookies) if cookies else {}

    def get_encoding(self) -> str:
        """获取响应编码

        Returns:
            str: 编码名称
        """
        return getattr(self.raw_response, 'charset', DEFAULT_ENCODING)

    def get_reason(self) -> str:
        """获取响应原因短语

        Returns:
            str: 状态码对应的原因短语
        """
        return getattr(self.raw_response, 'reason', '')


def select_adapter(response: RawResponseType) -> BaseRespAdapter:
    """根据响应对象类型选择合适的适配器

    Args:
        response: 原始HTTP响应对象

    Returns:
        BaseRespAdapter: 合适的适配器实例
    """
    # 检查是否为aiohttp响应
    response_module = getattr(response, '__module__', '')
    if 'aiohttp' in response_module:
        return AiohttpAdapter(response)

    # 对于其他所有情况(包括None),都使用RequestsAdapter作为默认适配器
    return RequestsAdapter(response)


__all__ = [
    'DEFAULT_ENCODING',
    'AiohttpAdapter',
    'BaseRespAdapter',
    'RequestsAdapter',
    'select_adapter',
]

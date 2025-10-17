# !/usr/bin/env python
"""
==============================================================
Description  : 统一响应处理模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:40:00
Github       : https://github.com/sandorn/xthttp

本模块提供统一的HTTP响应处理接口，支持多种HTTP库（如requests、aiohttp等），
自动处理编码检测、内容解析、DOM操作等功能。

核心功能：
1. 统一的响应对象访问接口
2. 智能编码检测与处理
3. 内置DOM解析和选择器支持
4. 中文内容特殊处理
5. 兼容同步和异步HTTP库

使用示例：
    >>> from xthttp.resp import create_response
    >>> from xthttp import get
    >>> # 创建响应对象
    >>> response = get('https://example.com')
    >>> unified_resp = create_response(response)
    >>> # 获取内容和信息
    >>> text = unified_resp.text
    >>> status = unified_resp.status
    >>> headers = unified_resp.headers
    >>> # DOM操作
    >>> title = unified_resp.query('title').text()
    >>> links = unified_resp.xpath('//a/@href')
==============================================================
"""

from __future__ import annotations

from typing import Any

from .adapters import select_adapter
from .unified_resp import HttpError, UnifiedResp

# 类型定义
RawResponseType = Any  # 原始响应对象类型
ContentDataType = str | bytes | None  # 响应内容类型


def create_response(response: RawResponseType = None, content: ContentDataType = None, index: int | None = None) -> UnifiedResp:
    """创建统一响应对象

    Args:
        response: 原始HTTP响应对象(如requests.Response, aiohttp.ClientResponse)
        content: 响应内容(字符串或字节流),可选
        index: 响应对象的唯一标识符,可选

    Returns:
        UnifiedResp: 统一响应对象
    """
    adapter = select_adapter(response)
    return UnifiedResp(response=response, content=content, index=index, adapter=adapter)


def is_success(response: UnifiedResp | RawResponseType) -> bool:
    """检查响应是否成功(状态码在200-299之间)

    Args:
        response: 响应对象(UnifiedResp或原始响应类型)

    Returns:
        bool: 状态码是否表示成功
    """
    if isinstance(response, UnifiedResp):
        return 200 <= response.status < 300

    # 处理原始响应对象
    status = getattr(response, 'status', getattr(response, 'status_code', 999))
    return 200 <= status < 300


# 导出所有公共接口
__all__ = [
    'HttpError',
    'UnifiedResp',
    'create_response',
    'is_success',
]

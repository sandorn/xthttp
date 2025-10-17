# !/usr/bin/env python
"""
==============================================================
Description  : 统一响应对象模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:40:00
Github       : https://github.com/sandorn/xthttp

本模块提供统一的HTTP响应对象，整合所有响应处理功能
==============================================================
"""

from __future__ import annotations

import json
from typing import Any

from .adapters import DEFAULT_ENCODING, BaseRespAdapter
from .dom_parser import get_dom_parser
from .encoding import decode_content, detect_encoding

# 类型定义
RawResponseType = Any  # 原始响应对象类型
ContentDataType = str | bytes | None  # 响应内容类型


class HttpError(Exception):
    """HTTP状态码错误异常"""

    def __init__(self, response, message: str | None = None):
        self.response = response
        self.status_code = response.status if response else 999
        self.message = message or f'HttpError({self.status_code})'
        super().__init__(self.message)


class UnifiedResp:
    """统一响应类,提供同步和异步HTTP响应的统一接口"""

    def __init__(
        self,
        response: RawResponseType = None,
        content: ContentDataType = None,
        index: int | None = None,
        url: str | None = None,
        adapter: BaseRespAdapter | None = None,
    ):
        """初始化统一响应对象

        Args:
            response: 原始HTTP响应对象
            content: 响应内容
            index: 响应对象的唯一标识符
            url: 请求URL
            adapter: 响应适配器
        """
        self._raw = response
        self._index = index if index is not None else id(self)
        self._adapter = adapter
        self._url = url if url is not None else (self._adapter.get_url() if self._adapter else '')

        # 处理内容
        self._content = self._process_content(content)

        # 确定编码
        self._encoding = detect_encoding(self._content, self._url)

        # 初始化DOM解析器
        self._dom_parser = get_dom_parser()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__} | Status:{self.status} | Id:{self.index} | Url:{self.url}'

    def __str__(self) -> str:
        return self.__repr__()

    def __bool__(self) -> bool:
        return self.status == 200

    def __len__(self) -> int:
        return len(self.text) if self.text else 0

    @property
    def ok(self) -> bool:
        """检查响应是否成功"""
        return 200 <= self.status < 300

    def raise_for_status(self) -> None:
        """检查状态码，如果不成功则抛出异常"""
        # 优先使用原始的 raise_for_status 方法
        raw_response = getattr(self._adapter, 'raw_response', None)
        if raw_response and hasattr(raw_response, 'raise_for_status'):
            raw_response.raise_for_status()
            return

        # 后备方案：使用自定义逻辑
        if not self.ok:
            raise HttpError(self)

    def _process_content(self, content: ContentDataType) -> bytes:
        """处理响应内容,转换为统一的字节格式

        Args:
            content: 响应内容

        Returns:
            bytes: 统一的字节格式内容
        """
        if isinstance(content, str):
            return content.encode(DEFAULT_ENCODING, 'replace')
        if isinstance(content, bytes):
            return content
        if self._adapter:
            return self._adapter.get_content()
        return b''

    @property
    def text(self) -> str:
        """获取响应的文本内容,自动处理编码

        Returns:
            str: 解码后的文本内容
        """
        if isinstance(self._content, str):
            return self._content

        if isinstance(self._content, bytes):
            return decode_content(self._content, self._encoding)

        if self._raw:
            return self._get_raw_text()

        return ''

    def _get_raw_text(self) -> str:
        """从原始响应对象获取文本

        Returns:
            str: 原始响应对象的文本内容
        """
        if not self._raw:
            return ''

        try:
            raw_text = None
            if callable(getattr(self._raw, 'text', None)):
                raw_text = self._raw.text()
            elif hasattr(self._raw, 'text'):
                raw_text = self._raw.text

            if raw_text is None:
                return ''

            if isinstance(raw_text, bytes):
                return decode_content(raw_text, self._encoding)
            if isinstance(raw_text, str):
                return raw_text
            return str(raw_text)

        except Exception as e:
            print(f'Error: 从原始响应获取文本失败: {e}')
            return ''

    @property
    def query(self) -> Any:
        """CSS选择器对象(PyQuery)

        Returns:
            Any: PyQuery对象
        """
        from pyquery import PyQuery

        self._dom_parser.parse_html(self.text)
        return self._dom_parser.get_pyquery() or PyQuery('')

    def xpath(self, *args: str) -> list[list[Any]]:
        """执行XPath选择查询

        Args:
            *args: XPath表达式

        Returns:
            list[list[Any]]: 查询结果列表
        """
        self._dom_parser.parse_html(self.text)
        return self._dom_parser.xpath(*args)

    @property
    def dom(self) -> Any | None:
        """lxml的DOM对象,用于XPath解析

        Returns:
            Any | None: lxml的DOM对象
        """
        self._dom_parser.parse_html(self.text)
        return self._dom_parser.get_dom()

    # ==================== 基本属性 ====================

    @property
    def content(self) -> bytes:
        """获取原始响应内容

        Returns:
            bytes: 原始响应内容
        """
        return self._content

    @property
    def encoding(self) -> str:
        """获取响应编码

        Returns:
            str: 响应编码
        """
        return self._encoding

    @property
    def index(self) -> int:
        """获取响应索引

        Returns:
            int: 响应索引
        """
        return self._index

    @property
    def raw(self) -> RawResponseType:
        """获取原始响应对象

        Returns:
            RawResponseType: 原始响应对象
        """
        return self._raw

    @property
    def elapsed(self) -> Any | None:
        """获取请求耗时

        Returns:
            Any | None: 请求耗时对象
        """
        if self._raw and hasattr(self._raw, 'elapsed'):
            return self._raw.elapsed
        return None

    @property
    def seconds(self) -> float:
        """获取请求耗时（秒）

        Returns:
            float: 请求耗时（秒）
        """
        elapsed = self.elapsed
        return elapsed.total_seconds() if elapsed else 0.0

    @property
    def url(self) -> str:
        """获取请求URL

        Returns:
            str: 请求URL
        """
        if self._adapter:
            return self._adapter.get_url()
        return getattr(self._raw, 'url', '')

    @property
    def cookies(self) -> dict[str, str]:
        """获取响应Cookie

        Returns:
            dict[str, str]: Cookie字典
        """
        if self._adapter:
            return self._adapter.get_cookies()
        if self._raw and hasattr(self._raw, 'cookies'):
            return dict(self._raw.cookies)
        return {}

    @property
    def headers(self) -> dict[str, str]:
        """获取响应头部

        Returns:
            dict[str, str]: 头部字典
        """
        if self._adapter:
            return self._adapter.get_headers()
        if self._raw and hasattr(self._raw, 'headers'):
            return dict(self._raw.headers)
        return {}

    @property
    def status(self) -> int:
        """获取响应状态码

        Returns:
            int: HTTP状态码
        """
        if self._adapter:
            return self._adapter.get_status()
        if self._raw:
            return getattr(self._raw, 'status', getattr(self._raw, 'status_code', 999))
        return 999

    @property
    def status_code(self) -> int:
        """获取响应状态码（别名）

        Returns:
            int: HTTP状态码
        """
        return self.status

    @property
    def reason(self) -> str:
        """获取响应原因短语

        Returns:
            str: 状态码对应的原因短语
        """
        if self._adapter:
            return self._adapter.get_reason()
        return getattr(self._raw, 'reason', '')

    @property
    def json(self) -> Any:
        """获取JSON响应内容

        Returns:
            Any: JSON解析后的对象
        """
        # 首先尝试使用raw对象的json方法
        if self._raw and hasattr(self._raw, 'json'):
            try:
                return self._raw.json()
            except (ValueError, TypeError, AttributeError):
                pass

        # 尝试使用标准json模块解析text属性
        try:
            if self.text:
                return json.loads(self.text)
        except (ValueError, TypeError):
            pass

        return {}


__all__ = [
    'HttpError',
    'UnifiedResp',
]

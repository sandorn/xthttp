# !/usr/bin/env python
"""
==============================================================
Description  : HTTP Headers工具模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:00:00
Github       : https://github.com/sandorn/xthttp

本模块提供HTTP请求头管理、User-Agent随机化、超时配置等功能
==============================================================
"""

from __future__ import annotations

from typing import Any

from .defaults import DefaultConfig, get_default_config
from .timeout import TimeoutConfig
from .user_agent import UserAgentManager, get_ua_manager


class Head:
    """HTTP Headers管理类，提供User-Agent随机化和headers更新功能"""

    def __init__(self) -> None:
        """初始化Headers管理器"""
        self._default_config = get_default_config()
        self._ua_manager = get_ua_manager()
        self.headers: dict[str, str] = self._default_config.copy_headers()

    def __setattr__(self, name: str, value: Any) -> None:
        """保护headers属性不被意外修改

        Args:
            name: 属性名
            value: 属性值

        Raises:
            TypeError: 当headers属性被设置为非字典类型时
        """
        if name == 'headers' and not isinstance(value, dict):
            raise TypeError('headers must be a dictionary')
        super().__setattr__(name, value)

    @property
    def randua(self) -> dict[str, str]:
        """获取随机User-Agent（使用fake_useragent库）

        Returns:
            dict[str, str]: 包含随机User-Agent的headers字典
        """
        self.headers['User-Agent'] = self._ua_manager.get_random_ua()
        return self.headers

    @property
    def ua(self) -> dict[str, str]:
        """获取预定义随机User-Agent的headers

        Returns:
            dict[str, str]: 包含预定义随机User-Agent的headers字典
        """
        self.headers['User-Agent'] = self._ua_manager.get_cached_ua()
        return self.headers

    def update_headers(self, headers: dict[str, str] | None = None) -> None:
        """安全更新headers，支持空值和类型验证

        Args:
            headers: 要更新的headers字典，可为None

        Raises:
            TypeError: 当headers不是字典类型时
            ValueError: 当headers格式无效时
        """
        if headers is None:
            return

        if not isinstance(headers, dict):
            raise TypeError(f'headers must be dict or None, got {type(headers).__name__}')

        try:
            # 过滤非字符串键值对和空值
            valid_headers = {str(key): str(value) for key, value in headers.items() if key is not None and value is not None}
            self.headers.update(valid_headers)
        except (AttributeError, ValueError) as e:
            raise ValueError(f'Invalid headers format: {e}') from e

    def reset_headers(self) -> None:
        """重置headers为默认配置"""
        self.headers = self._default_config.copy_headers()

    def get_header(self, key: str, default: str | None = None) -> str | None:
        """安全获取指定header值

        Args:
            key: header键名
            default: 默认值

        Returns:
            str | None: header值或默认值
        """
        return self.headers.get(str(key), default)

    def set_header(self, key: str, value: str) -> None:
        """安全设置单个header值

        Args:
            key: header键名
            value: header值

        Raises:
            TypeError: 当key或value不是字符串时
        """
        if not isinstance(key, str) or not isinstance(value, str):
            raise TypeError('Header key and value must be strings')
        self.headers[key] = value

    def remove_header(self, key: str) -> bool:
        """移除指定header

        Args:
            key: 要移除的header键名

        Returns:
            bool: 是否成功移除
        """
        if key in self.headers:
            del self.headers[key]
            return True
        return False

    def copy_headers(self) -> dict[str, str]:
        """返回headers的深拷贝

        Returns:
            dict[str, str]: headers字典的深拷贝
        """
        return self.headers.copy()


# 导出所有公共接口
__all__ = [
    'DefaultConfig',
    'Head',
    'TimeoutConfig',
    'UserAgentManager',
]

# !/usr/bin/env python
"""
==============================================================
Description  : 默认配置模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:00:00
Github       : https://github.com/sandorn/xthttp

本模块专门负责HTTP请求的默认配置管理
==============================================================
"""

from __future__ import annotations

from typing import Any

# 默认HTTP请求头配置
DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'Accept': '*/*,application/*,application/json,text/*,text/html',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Encoding': 'gzip,deflate,compress',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.6,en;q=0.4',
    'Accept-Charset': 'UTF-8,GB2312,GBK,GB18030,ISO-8859-1,ISO-8859-5;q=0.7,*;q=0.7',
    'Content-Type': 'text/html,application/x-www-form-unlencoded; charset=UTF-8',
    'Upgrade': 'HTTP/1.1',  # 强制降级到'HTTP/1.1'
    'Connection': 'Upgrade',
}


class DefaultConfig:
    """默认配置管理类"""

    def __init__(self) -> None:
        """初始化默认配置"""
        self.headers: dict[str, str] = DEFAULT_HEADERS.copy()

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
        self.headers = DEFAULT_HEADERS.copy()

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

    def get_all_headers(self) -> dict[str, str]:
        """获取所有headers

        Returns:
            dict[str, str]: 所有headers的副本
        """
        return self.headers.copy()


# 全局默认配置实例
_default_config: DefaultConfig | None = None


def get_default_config() -> DefaultConfig:
    """获取全局默认配置实例

    Returns:
        DefaultConfig: 全局默认配置实例
    """
    global _default_config
    if _default_config is None:
        _default_config = DefaultConfig()
    return _default_config


def get_default_headers() -> dict[str, str]:
    """获取默认headers的便捷函数

    Returns:
        dict[str, str]: 默认headers字典
    """
    return get_default_config().get_all_headers()


def update_default_headers(headers: dict[str, str]) -> None:
    """更新默认headers的便捷函数

    Args:
        headers: 要更新的headers字典
    """
    get_default_config().update_headers(headers)


def reset_default_headers() -> None:
    """重置默认headers的便捷函数"""
    get_default_config().reset_headers()


__all__ = [
    'DEFAULT_HEADERS',
    'DefaultConfig',
    'get_default_config',
    'get_default_headers',
    'reset_default_headers',
    'update_default_headers',
]

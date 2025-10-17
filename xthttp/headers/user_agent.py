# !/usr/bin/env python
"""
==============================================================
Description  : User-Agent管理模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:00:00
Github       : https://github.com/sandorn/xthttp

本模块专门负责User-Agent的管理和随机化功能
==============================================================
"""

from __future__ import annotations

import random
from typing import Any

from fake_useragent import UserAgent

# USER_AGENTS列表，保留主流浏览器最新版本
USER_AGENTS = [
    # Chrome最新版本
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
    # Firefox最新版本
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    # Safari最新版本
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.1 Safari/605.1.15',
    # Edge最新版本
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edg/120.0.0.0',
]


class UserAgentManager:
    """User-Agent管理器，提供User-Agent随机化和缓存功能"""

    def __init__(self) -> None:
        """初始化User-Agent管理器"""
        self._user_agent: UserAgent | None = None
        self._cached_ua: str | None = None

    def __setattr__(self, name: str, value: Any) -> None:
        """保护关键属性不被意外修改"""
        if name in ('_user_agent', '_cached_ua') and not name.startswith('_'):
            raise AttributeError(f"Can't set attribute '{name}'")
        super().__setattr__(name, value)

    @property
    def _ua_instance(self) -> UserAgent:
        """延迟加载UserAgent实例

        Returns:
            UserAgent: fake_useragent库的UserAgent实例
        """
        if self._user_agent is None:
            self._user_agent = UserAgent()
        return self._user_agent

    def get_random_ua(self) -> str:
        """获取随机User-Agent（使用fake_useragent库）

        Returns:
            str: 随机User-Agent字符串
        """
        return self._ua_instance.random

    def get_cached_ua(self) -> str:
        """获取预定义随机User-Agent（带缓存）

        Returns:
            str: 预定义随机User-Agent字符串
        """
        if self._cached_ua is None:
            self._cached_ua = random.choice(USER_AGENTS)  # noqa: S311
        return self._cached_ua

    def reset_cache(self) -> None:
        """重置User-Agent缓存"""
        self._cached_ua = None

    def get_predefined_ua(self, index: int | None = None) -> str:
        """获取预定义User-Agent列表中的指定项

        Args:
            index: 指定索引，如果为None则随机选择

        Returns:
            str: User-Agent字符串

        Raises:
            IndexError: 当索引超出范围时
        """
        if index is None:
            return random.choice(USER_AGENTS)  # noqa: S311

        if not 0 <= index < len(USER_AGENTS):
            raise IndexError(f'User-Agent index {index} out of range [0, {len(USER_AGENTS)})')

        return USER_AGENTS[index]

    def get_all_ua(self) -> list[str]:
        """获取所有预定义User-Agent列表

        Returns:
            list[str]: 所有User-Agent字符串的列表
        """
        return USER_AGENTS.copy()


# 全局User-Agent管理器实例
_ua_manager: UserAgentManager | None = None


def get_ua_manager() -> UserAgentManager:
    """获取全局User-Agent管理器实例

    Returns:
        UserAgentManager: 全局User-Agent管理器实例
    """
    global _ua_manager
    if _ua_manager is None:
        _ua_manager = UserAgentManager()
    return _ua_manager


def get_random_user_agent() -> str:
    """获取随机User-Agent的便捷函数

    Returns:
        str: 随机User-Agent字符串
    """
    return get_ua_manager().get_random_ua()


def get_cached_user_agent() -> str:
    """获取缓存User-Agent的便捷函数

    Returns:
        str: 缓存User-Agent字符串
    """
    return get_ua_manager().get_cached_ua()


__all__ = [
    'USER_AGENTS',
    'UserAgentManager',
    'get_cached_user_agent',
    'get_random_user_agent',
    'get_ua_manager',
]

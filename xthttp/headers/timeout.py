# !/usr/bin/env python
"""
==============================================================
Description  : 超时配置管理模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:00:00
Github       : https://github.com/sandorn/xthttp

本模块专门负责HTTP请求的超时配置管理

from xthttp import TimeoutConfig

# 获取默认超时配置
requests_timeout = TimeoutConfig.get_requests_timeout()  # (8, 30)
aiohttp_timeout = TimeoutConfig.get_aiohttp_timeout()   # ClientTimeout对象

# 创建自定义超时配置
custom_timeout = TimeoutConfig.create_requests_timeout(5, 15)
custom_aiohttp_timeout = TimeoutConfig.create_aiohttp_timeout(total=60, connect=10)

# 更新超时配置
TimeoutConfig.update_requests_timeout(3, 20)
TimeoutConfig.update_aiohttp_timeout(total=90, connect=12)

==============================================================
"""

from __future__ import annotations

from aiohttp import ClientTimeout


class TimeoutConfig:
    """超时配置管理类"""

    # 异步HTTP请求超时配置
    AIOHTTP_TIMEOUT = ClientTimeout(
        total=30,  # 总超时30秒
        connect=8,  # 连接超时8秒
        sock_read=20,  # 读取超时20秒
        sock_connect=8,  # socket连接8秒
    )

    # 同步请求超时配置 (connect_timeout, read_timeout)
    REQUESTS_TIMEOUT = (8, 30)

    @classmethod
    def get_aiohttp_timeout(cls) -> ClientTimeout:
        """获取aiohttp超时配置

        Returns:
            ClientTimeout: aiohttp超时配置对象
        """
        return cls.AIOHTTP_TIMEOUT

    @classmethod
    def get_requests_timeout(cls) -> tuple[int, int]:
        """获取requests超时配置

        Returns:
            tuple[int, int]: (连接超时, 读取超时) 的元组
        """
        return cls.REQUESTS_TIMEOUT

    @classmethod
    def create_aiohttp_timeout(
        cls,
        total: int = 30,
        connect: int = 8,
        sock_read: int = 20,
        sock_connect: int = 8,
    ) -> ClientTimeout:
        """创建自定义aiohttp超时配置

        Args:
            total: 总超时时间（秒）
            connect: 连接超时时间（秒）
            sock_read: 读取超时时间（秒）
            sock_connect: socket连接超时时间（秒）

        Returns:
            ClientTimeout: 自定义aiohttp超时配置对象
        """
        return ClientTimeout(
            total=total,
            connect=connect,
            sock_read=sock_read,
            sock_connect=sock_connect,
        )

    @classmethod
    def create_requests_timeout(
        cls,
        connect_timeout: int = 8,
        read_timeout: int = 30,
    ) -> tuple[int, int]:
        """创建自定义requests超时配置

        Args:
            connect_timeout: 连接超时时间（秒）
            read_timeout: 读取超时时间（秒）

        Returns:
            tuple[int, int]: (连接超时, 读取超时) 的元组
        """
        return (connect_timeout, read_timeout)

    @classmethod
    def update_aiohttp_timeout(
        cls,
        total: int | None = None,
        connect: int | None = None,
        sock_read: int | None = None,
        sock_connect: int | None = None,
    ) -> None:
        """更新全局aiohttp超时配置

        Args:
            total: 总超时时间（秒）
            connect: 连接超时时间（秒）
            sock_read: 读取超时时间（秒）
            sock_connect: socket连接超时时间（秒）
        """
        current = cls.AIOHTTP_TIMEOUT
        cls.AIOHTTP_TIMEOUT = ClientTimeout(
            total=total if total is not None else current.total,
            connect=connect if connect is not None else current.connect,
            sock_read=sock_read if sock_read is not None else current.sock_read,
            sock_connect=sock_connect if sock_connect is not None else current.sock_connect,
        )

    @classmethod
    def update_requests_timeout(
        cls,
        connect_timeout: int | None = None,
        read_timeout: int | None = None,
    ) -> None:
        """更新全局requests超时配置

        Args:
            connect_timeout: 连接超时时间（秒）
            read_timeout: 读取超时时间（秒）
        """
        current_connect, current_read = cls.REQUESTS_TIMEOUT
        cls.REQUESTS_TIMEOUT = (
            connect_timeout if connect_timeout is not None else current_connect,
            read_timeout if read_timeout is not None else current_read,
        )


__all__ = [
    'TimeoutConfig',
]

# !/usr/bin/env python
"""
==============================================================
Description  : HTTP请求工具模块 - 提供简化的requests调用和会话管理功能
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-14 22:00:00
Github       : https://github.com/sandorn/xthttp

本模块提供以下核心功能:
- 简化的HTTP请求方法(get, post等),自动添加请求头和超时设置
- 请求重试机制,提高网络请求稳定性
- 会话管理,支持Cookie持久化和请求头管理
- 与htmlResponse集成,方便后续解析处理

主要特性:
- 自动随机User-Agent设置,减少请求被拦截的风险
- 统一的异常处理和响应封装
- 支持同步函数的重试机制
- 会话复用,提高请求效率
==============================================================
"""

from __future__ import annotations

from functools import partial
from typing import Any

import requests
from nswrapslite.retry import spider_retry
from resp import UnifiedResp as htmlResponse
from xt_head import TIMEOUT, Head

# 支持的HTTP请求方法
REQUEST_METHODS = ('get', 'post', 'head', 'options', 'put', 'delete', 'trace', 'connect', 'patch')


@spider_retry
def _retry_request(method: str, url: str, *args: Any, **kwargs: Any) -> htmlResponse:
    """利用spider_retry实现请求重试机制

    Args:
        method: HTTP请求方法
        url: 请求URL
        *args: 传递给requests.request的位置参数
        **kwargs: 传递给requests.request的关键字参数
            callback: 回调函数(会被忽略)
            index: 响应对象的索引标识,默认为url的id
            timeout: 请求超时时间,默认使用TIMEOUT常量

    Returns:
        htmlResponse: 包装后的响应对象

    Raises:
        requests.HTTPError: 当HTTP状态码不是2xx时抛出
    """
    # 移除不支持的参数
    _ = kwargs.pop('callback', None)
    index = kwargs.pop('index', id(url))
    timeout = kwargs.pop('timeout', TIMEOUT)

    response = requests.request(method, url, *args, timeout=timeout, **kwargs)
    response.raise_for_status()
    return htmlResponse(response, response.content, index, url)


def single_parse(method: str, url: str, *args: Any, **kwargs: Any) -> htmlResponse:
    """执行单次HTTP请求,自动设置默认请求头和超时

    Args:
        method: HTTP请求方法
        url: 请求URL
        *args: 传递给_retry_request的位置参数
        **kwargs: 传递给_retry_request的关键字参数
            headers: 请求头,默认为随机User-Agent
            timeout: 请求超时时间,默认使用TIMEOUT常量
            cookies: Cookie字典,默认为空字典

    Returns:
        htmlResponse: 包装后的响应对象,如果方法不支持则返回错误信息
    """
    method_lower = method.lower()

    if method_lower not in REQUEST_METHODS:
        raise ValueError(f'未知的HTTP请求方法: {method}')

    # 设置默认参数
    kwargs.setdefault('headers', Head().randua)  # 自动设置随机User-Agent
    kwargs.setdefault('timeout', TIMEOUT)  # 自动设置超时时间
    kwargs.setdefault('cookies', {})  # 自动设置空Cookie字典

    return _retry_request(method_lower, url, *args, **kwargs)


# 创建常用请求方法的快捷方式
get = partial(single_parse, 'get')
post = partial(single_parse, 'post')
head = partial(single_parse, 'head')
options = partial(single_parse, 'options')
put = partial(single_parse, 'put')
delete = partial(single_parse, 'delete')
patch = partial(single_parse, 'patch')


class SessionClient:
    """会话客户端 - 封装requests.Session,管理Cookie持久化和请求重试

    提供会话级别的HTTP请求管理,支持Cookie保存和请求头持久化,
    适用于需要维持会话状态的场景。

    Example:
        >>> with SessionClient() as client:
        >>> # 登录获取Cookie
        >>>     client.post('https://example.com/login', data={'username': 'user', 'password': 'pass'})
        >>> # 使用同一会话访问需要登录的页面
        >>>     response = client.get('https://example.com/user/profile')
    """

    __slots__ = ('args', 'kwargs', 'method', 'session', 'timeout', 'url')

    def __init__(self):
        """初始化会话客户端"""
        self.session = requests.session()
        self.timeout: float = TIMEOUT
        self.method: str = ''
        self.args: tuple = ()
        self.kwargs: dict[str, Any] = {}
        self.url: str = ''

    def __enter__(self):
        """支持上下文管理器协议,用于自动关闭会话"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文时关闭会话"""
        self.session.close()

    def __getitem__(self, method: str):
        """支持通过索引方式设置请求方法

        Args:
            method: HTTP请求方法

        Returns:
            指向create_task方法的引用,用于链式调用
        """
        self.method = method.lower()  # 保存请求方法
        return self.create_task  # 返回创建任务的方法

    def __getattr__(self, method: str):
        """支持通过属性访问设置请求方法

        Args:
            method: HTTP请求方法名称

        Returns:
            指向create_task方法的引用,用于链式调用
        """
        return self.__getitem__(method)

    def create_task(self, *args, **kwargs) -> htmlResponse:
        """创建并执行请求任务

        Args:
            *args: 位置参数,第一个参数为URL
            **kwargs: 关键字参数
                headers: 请求头,默认为随机User-Agent
                cookies: Cookie字典,默认为空字典
                timeout: 请求超时时间,默认使用TIMEOUT常量
                callback: 回调函数(会被忽略)

        Returns:
            htmlResponse: 包装后的响应对象

        Raises:
            ValueError: 当请求方法不在支持列表中时
        """
        self.url = args[0]

        if self.method not in REQUEST_METHODS:
            raise ValueError(f'未知的HTTP请求方法: {self.method}')

        self.args = args[1:]

        # 更新请求头和Cookie
        self.update_headers(kwargs.pop('headers', Head().randua))
        self.update_cookies(kwargs.pop('cookies', {}))

        # 移除不支持的参数并设置默认值
        _ = kwargs.pop('callback', None)
        kwargs.setdefault('timeout', TIMEOUT)
        self.kwargs = kwargs

        return self._fetch()

    @spider_retry
    def _fetch(self) -> htmlResponse:
        """执行请求并处理响应

        Returns:
            htmlResponse: 包装后的响应对象
        """
        response = self.session.request(self.method, self.url, *self.args, **self.kwargs)
        response.raise_for_status()
        self.update_cookies(dict(response.cookies))
        return htmlResponse(response, response.content, id(self.url), self.url)

    def update_cookies(self, cookie_dict: dict[str, str]) -> None:
        """更新会话的Cookie

        Args:
            cookie_dict: 包含Cookie键值对的字典
        """
        self.session.cookies.update(cookie_dict)

    def update_headers(self, header_dict: dict[str, str]) -> None:
        """更新会话的请求头

        Args:
            header_dict: 包含请求头键值对的字典
        """
        self.session.headers.update(header_dict)


if __name__ == '__main__':
    """模块使用示例和测试"""

    def basic_request_example():
        """基础请求示例"""

        @spider_retry(max_retries=2, delay=0.5, custom_message='测试爬虫请求')
        def make_spider_request(url):
            """模拟爬虫请求函数"""
            print(f'发送请求到: {url}')
            return get(url, timeout=3)

        # 测试成功的请求
        print('\n--- 成功的爬虫请求示例 ---')
        result1 = make_spider_request('https://httpbin.org/get')
        print(f'请求结果1: {type(result1).__name__}({result1})')

        # 测试超时的请求
        print('\n--- 超时的爬虫请求示例 ---')
        result2 = make_spider_request('https://httpbin.org/delay/10')  # 这个接口会延迟10秒响应
        print(f'请求结果2: {type(result2).__name__}({result2})')

        # 测试404错误的请求
        print('\n--- 404错误的爬虫请求示例 ---')
        result3 = make_spider_request('https://httpbin.org/status/404')
        print(f'请求结果3: {type(result3).__name__}({result3})')

    def session_example():
        """会话请求示例"""
        print('执行会话请求')
        # 使用上下文管理器创建会话
        with SessionClient() as client:
            result1 = client.get('https://httpbin.org/get')
            print(f'请求结果1: {type(result1).__name__}({result1})')

            # 测试超时的请求
            print('\n--- 超时的爬虫请求示例 ---')
            result2 = client.get('https://httpbin.org/delay/10', timeout=1)  # 这个接口会延迟10秒响应
            print(f'请求结果2: {type(result2).__name__}({result2})')

            # 测试404错误的请求
            print('\n--- 404错误的爬虫请求示例 ---')
            result3 = client.get('https://httpbin.org/status/404')
            print(f'请求结果3: {type(result3).__name__}({result3})')

    def post_request_example():
        """POST请求示例"""
        print('执行POST请求')
        data = {'key1': 'value1', 'key2': 'value2'}
        response = post('https://httpbin.org/post', data=data)
        if isinstance(response, htmlResponse):
            try:
                # 使用标准json模块解析JSON数据
                import json

                json_data = json.loads(response.text)
                form_data = json_data.get('form', {})
                print(f'POST数据接收: {form_data}')
            except Exception as e:
                print(f'解析POST响应失败: {e!s}')
                print(f'响应内容: {response.text[:100]}...')

    # 执行示例
    print('=== HTTP请求工具模块测试开始 ===')
    # basic_request_example()
    session_example()
    post_request_example()
    print('=== HTTP请求工具模块测试完成 ===')

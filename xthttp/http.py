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
- 与UnifiedResp集成,方便后续解析处理

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
from xtwraps.retry import spider_retry

from .headers import Head, TimeoutConfig
from .resp import UnifiedResp, create_response

# 支持的HTTP请求方法（使用集合提高查找效率）
REQUEST_METHODS: set[str] = {'get', 'post', 'head', 'options', 'put', 'delete', 'trace', 'connect', 'patch'}


@spider_retry
def _retry_request(method: str, url: str, *args: Any, **kwargs: Any) -> UnifiedResp:
    """利用spider_retry实现请求重试机制

    Args:
        method: HTTP请求方法（已转换为小写）
        url: 请求URL
        *args: 传递给requests.request的位置参数
        **kwargs: 传递给requests.request的关键字参数
            callback: 回调函数（会被忽略）
            index: 响应对象的索引标识，默认为url的id
            timeout: 请求超时时间，默认使用timeout常量

    Returns:
        UnifiedResp: 包装后的响应对象

    Raises:
        requests.HTTPError: 当HTTP状态码不是2xx时抛出
    """
    # 使用字典视图减少复制操作
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in {'callback', 'index', 'timeout'}}

    index = kwargs.get('index', id(url))
    timeout = kwargs.get('timeout', TimeoutConfig.get_requests_timeout())

    response = requests.request(method, url, *args, timeout=timeout, **filtered_kwargs)
    response.raise_for_status()
    return create_response(response, response.content, index)


def single_parse(method: str, url: str, *args: Any, **kwargs: Any) -> UnifiedResp:
    """执行单次HTTP请求，自动设置默认请求头和超时

    Args:
        method: HTTP请求方法
        url: 请求URL
        *args: 传递给_retry_request的位置参数
        **kwargs: 传递给_retry_request的关键字参数
            headers: 请求头，默认为随机User-Agent
            timeout: 请求超时时间，默认使用timeout常量
            cookies: Cookie字典，默认为空字典

    Returns:
        UnifiedResp: 包装后的响应对象，如果方法不支持则返回错误信息

    Raises:
        ValueError: 当请求方法不在支持列表中时
    """
    method_lower = method.lower()

    if method_lower not in REQUEST_METHODS:
        raise ValueError(f'未知的HTTP请求方法: {method}')

    # 设置默认参数（使用字典的setdefault方法）
    kwargs.setdefault('headers', Head().randua)  # 自动设置随机User-Agent
    kwargs.setdefault('timeout', TimeoutConfig.get_requests_timeout())  # 自动设置超时时间
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
    """会话客户端 - 封装requests.Session，管理Cookie持久化和请求重试

    提供会话级别的HTTP请求管理，支持Cookie保存和请求头持久化，
    适用于需要维持会话状态的场景。

    Attributes:
        session (requests.Session): 底层的requests会话对象
        timeout (tuple): 请求超时配置 (连接超时, 读取超时)
        method (str): 当前请求方法
        args (tuple): 当前请求的位置参数
        kwargs (dict[str, Any]): 当前请求的关键字参数
        url (str): 当前请求URL
        _head_instance (Head): 请求头管理实例

    Example:
        >>> # 基本使用
        >>> with SessionClient() as client:
        >>>     response = client.get('https://httpbin.org/get')
        >>>     print(response.status)
        >>> # 会话状态管理
        >>> with SessionClient() as client:
        >>> # 登录获取Cookie
        >>>     login_resp = client.post('https://example.com/login',
        >>>                            data={'username': 'user', 'password': 'pass'})
        >>> # 使用同一会话访问需要登录的页面
        >>>     profile_resp = client.get('https://example.com/user/profile')
        >>>     print(f'登录状态: {login_resp.status}, 个人资料: {profile_resp.status}')
    """

    __slots__ = ('_head_instance', 'args', 'kwargs', 'method', 'session', 'timeout', 'url')

    def __init__(self) -> None:
        """初始化会话客户端

        创建新的会话实例，初始化所有必要的属性和配置。
        会话将自动配置默认超时时间和请求头管理。

        Note:
            会话对象会自动管理Cookie和连接池，支持HTTP/1.1的持久连接。
        """
        self.session = requests.session()
        self.timeout: tuple = TimeoutConfig.get_requests_timeout()
        self.method: str = ''
        self.args: tuple = ()
        self.kwargs: dict[str, Any] = {}
        self.url: str = ''
        self._head_instance: Head = Head()

    def __enter__(self) -> SessionClient:
        """支持上下文管理器协议，用于自动关闭会话

        使SessionClient支持with语句，确保会话资源得到正确释放。

        Returns:
            SessionClient: 当前会话实例，支持链式调用

        Example:
            >>> with SessionClient() as client:
            >>>     response = client.get('https://httpbin.org/get')
            >>> # 会话会自动关闭
        """
        return self

    def __exit__(self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: Any) -> None:
        """退出上下文时关闭会话

        自动清理会话资源，包括关闭底层连接池和清理Cookie。

        Args:
            exc_type (type[BaseException] | None): 异常类型，如果有异常发生
            exc_val (BaseException | None): 异常值，如果有异常发生
            exc_tb (Any): 异常回溯信息，如果有异常发生

        Note:
            无论是否发生异常，都会正确关闭会话资源。
        """
        self.session.close()

    def __getitem__(self, method: str):
        """支持通过索引方式设置请求方法

        允许使用字典风格的语法来设置HTTP请求方法，支持链式调用。

        Args:
            method (str): HTTP请求方法，如 'get', 'post', 'put' 等

        Returns:
            Callable: 指向create_task方法的引用，用于链式调用

        Example:
            >>> client = SessionClient()
            >>> response = client['get']('https://httpbin.org/get')
            >>> # 等价于 client.get('https://httpbin.org/get')

        Note:
            方法名会自动转换为小写，支持大小写不敏感的调用。
        """
        self.method = method.lower()  # 保存请求方法
        return self.create_task  # 返回创建任务的方法

    def __getattr__(self, method: str):
        """支持通过属性访问设置请求方法

        允许使用属性风格的语法来设置HTTP请求方法，支持链式调用。
        这是Python的动态属性访问机制，当访问不存在的属性时会调用此方法。

        Args:
            method (str): HTTP请求方法名称，如 'get', 'post', 'put' 等

        Returns:
            Callable: 指向create_task方法的引用，用于链式调用

        Example:
            >>> client = SessionClient()
            >>> response = client.get('https://httpbin.org/get')
            >>> response = client.post('https://httpbin.org/post', data={'key': 'value'})

        Note:
            方法名会自动转换为小写，支持大小写不敏感的调用。
            内部调用__getitem__方法实现相同功能。
        """
        return self.__getitem__(method)

    def create_task(self, *args: Any, **kwargs: Any) -> UnifiedResp:
        """创建并执行请求任务

        这是会话客户端的核心方法，负责创建和执行HTTP请求任务。
        支持自动重试机制和统一的响应处理。

        Args:
            *args (Any): 位置参数，第一个参数必须为URL字符串
            **kwargs (Any): 关键字参数，支持以下选项：
                headers (dict[str, str]): 请求头字典，默认为随机User-Agent
                cookies (dict[str, str]): Cookie字典，默认为空字典
                timeout (float | tuple): 请求超时时间，默认使用timeout常量
                callback (Callable): 回调函数（会被忽略，用于兼容性）
                data (dict | str | bytes): POST请求体数据
                json (dict): JSON格式的请求体数据
                params (dict): URL查询参数
                files (dict): 文件上传数据

        Returns:
            UnifiedResp: 包装后的统一响应对象，包含状态码、内容、头部等信息

        Raises:
            ValueError: 当URL参数为空或请求方法不在支持列表中时
            requests.RequestException: 当网络请求失败时
            requests.HTTPError: 当HTTP状态码表示错误时

        Example:
            >>> client = SessionClient()
            >>> # GET请求
            >>> response = client.create_task('https://httpbin.org/get')
            >>> # POST请求
            >>> response = client.create_task('https://httpbin.org/post',
            >>>                              data={'key': 'value'})
            >>> # 带自定义头部
            >>> response = client.create_task('https://httpbin.org/get',
            >>>                              headers={'Authorization': 'Bearer token'})
        """
        if not args:
            raise ValueError('URL参数不能为空')

        self.url = args[0]

        if self.method not in REQUEST_METHODS:
            raise ValueError(f'未知的HTTP请求方法: {self.method}')

        self.args = args[1:]

        # 更新请求头和Cookie（使用单例Head实例）
        headers = kwargs.pop('headers', self._head_instance.randua)
        cookies = kwargs.pop('cookies', {})

        self.update_headers(headers)
        self.update_cookies(cookies)

        # 移除不支持的参数并设置默认值
        kwargs.pop('callback', None)
        kwargs.setdefault('timeout', TimeoutConfig.get_requests_timeout())

        self.kwargs = kwargs

        return self.start()

    @spider_retry
    def start(self) -> UnifiedResp:
        """执行请求并处理响应

        实际执行HTTP请求的核心方法，使用spider_retry装饰器提供自动重试功能。
        请求执行完成后会自动更新会话的Cookie状态。

        Returns:
            UnifiedResp: 包装后的统一响应对象，包含完整的响应信息

        Raises:
            requests.RequestException: 当网络请求失败时
            requests.HTTPError: 当HTTP状态码表示错误时
            requests.Timeout: 当请求超时时
            requests.ConnectionError: 当连接失败时

        Note:
            此方法会自动更新会话的Cookie状态，确保后续请求能够保持会话状态。
            使用spider_retry装饰器，在请求失败时会自动重试。
        """
        response = self.session.request(self.method, self.url, *self.args, **self.kwargs)
        response.raise_for_status()
        self.update_cookies(dict(response.cookies))
        return create_response(response, response.content, id(self.url))

    def update_cookies(self, cookie_dict: dict[str, str]) -> None:
        """更新会话的Cookie

        向当前会话添加或更新Cookie信息，这些Cookie会在后续请求中自动发送。

        Args:
            cookie_dict (dict[str, str]): 包含Cookie键值对的字典，键为Cookie名称，值为Cookie值

        Raises:
            TypeError: 当cookie_dict不是字典类型时

        Example:
            >>> client = SessionClient()
            >>> client.update_cookies({'session_id': 'abc123', 'user_id': '456'})
            >>> # 后续请求会自动包含这些Cookie

        Note:
            Cookie更新是累积的，新Cookie会与现有Cookie合并，同名Cookie会被覆盖。
        """
        if not isinstance(cookie_dict, dict):
            raise TypeError('cookie_dict必须是字典类型')
        self.session.cookies.update(cookie_dict)

    def update_headers(self, header_dict: dict[str, str]) -> None:
        """更新会话的请求头

        向当前会话添加或更新HTTP请求头，这些头部会在后续请求中自动发送。

        Args:
            header_dict (dict[str, str]): 包含请求头键值对的字典，键为头部名称，值为头部值

        Raises:
            TypeError: 当header_dict不是字典类型时

        Example:
            >>> client = SessionClient()
            >>> client.update_headers({'Authorization': 'Bearer token', 'X-Custom': 'value'})
            >>> # 后续请求会自动包含这些头部

        Note:
            请求头更新是累积的，新头部会与现有头部合并，同名头部会被覆盖。
        """
        if not isinstance(header_dict, dict):
            raise TypeError('header_dict必须是字典类型')
        self.session.headers.update(header_dict)

    def get_current_headers(self) -> dict[str, str | bytes]:
        """获取当前会话的请求头

        返回当前会话中所有请求头的副本，包括默认头部和用户自定义头部。

        Returns:
            dict[str, str | bytes]: 当前请求头的副本，键为头部名称，值为头部值

        Example:
            >>> client = SessionClient()
            >>> client.update_headers({'Authorization': 'Bearer token'})
            >>> headers = client.get_current_headers()
            >>> print(headers.get('Authorization'))  # 'Bearer token'

        Note:
            返回的是请求头的副本，修改返回的字典不会影响会话的请求头。
        """
        # 使用 dict() 构造函数处理 MutableMapping 类型
        return dict(self.session.headers)

    def get_current_cookies(self) -> dict[str, str]:
        """获取当前会话的Cookie

        返回当前会话中所有Cookie的副本，包括从服务器接收到的Cookie和用户设置的Cookie。

        Returns:
            dict[str, str]: 当前Cookie的副本，键为Cookie名称，值为Cookie值

        Example:
            >>> client = SessionClient()
            >>> client.update_cookies({'session_id': 'abc123'})
            >>> cookies = client.get_current_cookies()
            >>> print(cookies.get('session_id'))  # 'abc123'

        Note:
            返回的是Cookie的副本，修改返回的字典不会影响会话的Cookie。
        """
        # 使用 dict() 构造函数处理 RequestsCookieJar 类型
        return dict(self.session.cookies)


__all__ = (
    'SessionClient',
    'delete',
    'get',
    'head',
    'options',
    'patch',
    'post',
    'put',
)

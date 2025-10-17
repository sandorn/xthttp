# xthttp

[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

一个高性能的 Python HTTP 客户端库，提供同步和异步 HTTP 请求功能，支持智能编码检测、DOM 解析、自动重试等特性。

## ✨ 特性

-   🚀 **双模式支持**：同时支持同步和异步 HTTP 请求
-   🎯 **智能编码检测**：自动检测和转换网页编码，支持中文内容
-   🔍 **DOM 解析**：内置 CSS 选择器和 XPath 查询功能
-   🔄 **自动重试**：网络失败时自动重试机制
-   🍪 **会话管理**：支持 Cookie 持久化和会话状态保持
-   🛡️ **并发控制**：异步请求支持并发数量限制
-   📦 **统一接口**：不同 HTTP 库的统一响应接口
-   🎨 **类型安全**：完整的类型注解支持

## 📦 安装

```bash
pip install xthttp
```

## 🚀 快速开始

### 同步请求

```python
from xthttp import get, post, SessionClient

# 简单GET请求
response = get('https://httpbin.org/get')
print(f'状态码: {response.status}')
print(f'响应内容: {response.text[:100]}')

# POST请求
response = post('https://httpbin.org/post', data={'key': 'value'})
print(f'JSON响应: {response.json}')

# 会话管理
with SessionClient() as client:
    # 登录
    login_resp = client.post('https://example.com/login',
                           data={'username': 'user', 'password': 'pass'})
    # 访问需要登录的页面
    profile_resp = client.get('https://example.com/profile')
```

### 异步请求

```python
import asyncio
from xthttp.ahttp import AsyncHttpClient

async def main():
    client = AsyncHttpClient(max_concurrent=5)

    # 单个请求
    response = await client.request('get', 'https://httpbin.org/get')
    print(f'状态码: {response.status}')

    # 批量请求
    urls = ['https://httpbin.org/get', 'https://httpbin.org/post']
    responses = await client.multi_request('get', urls)
    for resp in responses:
        if not isinstance(resp, Exception):
            print(f'URL: {resp.url}, 状态: {resp.status}')

asyncio.run(main())
```

### DOM 解析

```python
from xthttp import get

response = get('https://example.com')

# CSS选择器
title = response.css_select('title').text()
links = response.css_select('a')
for link in links:
    print(link.attr('href'))

# XPath查询
titles = response.xpath('//title/text()')
all_links = response.xpath('//a/@href')
```

## 📚 详细文档

### 核心类

#### `SessionClient`

同步 HTTP 客户端，支持会话管理和 Cookie 持久化。

```python
from xthttp import SessionClient

with SessionClient() as client:
    # 设置请求头
    client.update_headers({'Authorization': 'Bearer token'})

    # 设置Cookie
    client.update_cookies({'session_id': 'abc123'})

    # 发送请求
    response = client.get('https://api.example.com/data')
```

#### `AsyncHttpClient`

异步 HTTP 客户端，支持并发控制和批量请求。

```python
from xthttp.ahttp import AsyncHttpClient

client = AsyncHttpClient(max_concurrent=10)

# 并发控制
async def fetch_data():
    response = await client.request('get', 'https://api.example.com/data')
    return response.json

# 批量请求
urls = [f'https://api.example.com/data/{i}' for i in range(100)]
responses = await client.batch_request('get', urls)
```

#### `UnifiedResp`

统一响应对象，提供一致的 API 接口。

```python
response = get('https://example.com')

# 基本属性
print(response.status)      # 状态码
print(response.url)         # 请求URL
print(response.text)        # 文本内容
print(response.json)        # JSON数据
print(response.headers)     # 响应头
print(response.cookies)     # Cookie

# DOM操作
title = response.css_select('title').text()
links = response.xpath('//a/@href')
```

### 编码检测

xthttp 内置智能编码检测功能，特别优化了中文内容的处理：

```python
from xthttp import get

# 自动检测编码
response = get('https://www.baidu.com')
print(response.encoding)  # 自动检测的编码
print(response.text)      # 正确解码的中文内容
```

### 请求头管理

```python
from xthttp.headers import Head

head = Head()

# 随机User-Agent
headers = head.randua
print(headers['User-Agent'])  # 随机生成的User-Agent

# 自定义请求头
head.update_headers({
    'Authorization': 'Bearer token',
    'X-Custom-Header': 'value'
})
```

## 🔧 配置

### 超时设置

```python
from xthttp.headers import TimeoutConfig

# 设置默认超时时间
TimeoutConfig.set_requests_timeout((5, 30))  # 连接超时5秒，读取超时30秒
```

### 并发控制

```python
from xthttp.ahttp import AsyncHttpClient

# 设置最大并发数
client = AsyncHttpClient(max_concurrent=20)
```

## 📋 示例

查看 `examples/` 目录获取更多使用示例：

-   `demo_http.py` - 同步 HTTP 请求示例
-   `demo_ahttp.py` - 异步 HTTP 请求示例
-   `demo_resp.py` - 响应处理和 DOM 解析示例

## 🤝 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解如何参与项目开发。

## 📄 许可证

本项目采用 MIT 许可证。详情请查看 [LICENSE](LICENSE) 文件。

## 🔗 相关链接

-   [GitHub 仓库](https://github.com/sandorn/xthttp)
-   [文档](https://github.com/sandorn/xthttp/wiki)
-   [问题反馈](https://github.com/sandorn/xthttp/issues)

## 📈 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本更新历史。

---

**xthttp** - 让 HTTP 请求更简单、更高效！

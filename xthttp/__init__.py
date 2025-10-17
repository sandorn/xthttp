# d:/CODE/xjlib/xthttp/__init__.py
"""HTTP请求与响应处理模块"""

from __future__ import annotations

from .ahttp import AsyncHttpClient, ahttp_get, ahttp_get_all, ahttp_get_all_sequential, ahttp_post, ahttp_post_all
from .headers import Head, TimeoutConfig
from .http import SessionClient, delete, get, head, options, patch, post, put
from .resp import HttpError, UnifiedResp, create_response, is_success

__version__ = '0.1.0'
__all__ = (
    'AsyncHttpClient',
    'Head',
    'HttpError',
    'SessionClient',
    'TimeoutConfig',
    'UnifiedResp',
    'ahttp_get',
    'ahttp_get_all',
    'ahttp_get_all_sequential',
    'ahttp_post',
    'ahttp_post_all',
    'create_response',
    'delete',
    'get',
    'head',
    'is_success',
    'options',
    'patch',
    'post',
    'put',
)

# !/usr/bin/env python
"""
==============================================================
Description  : 编码检测和处理模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:40:00
Github       : https://github.com/sandorn/xthttp

本模块提供简化的编码检测和处理功能，优化性能
==============================================================
"""

from __future__ import annotations

import hashlib
import re
from contextlib import suppress

from .adapters import DEFAULT_ENCODING

# 中文编码集合
CHINESE_ENCODINGS = {'utf-8', 'gbk', 'gb18030', 'big5', 'gb2312'}

# 中文域名集合
CHINESE_DOMAINS = {'baidu.com', 'sina.com', '163.com', 'qq.com', 'alibaba.com', 'taobao.com', 'jd.com', 'sohu.com', 'zhihu.com', 'weibo.com'}


class EncodingDetector:
    """编码检测器，提供简化的编码检测功能"""

    def __init__(self):
        """初始化编码检测器"""
        self._chardet_available = self._check_chardet_availability()
        # 添加编码检测结果缓存，提高性能
        self._encoding_cache: dict[str, str] = {}
        # 缓存大小限制，防止内存泄漏
        self._max_cache_size = 1000

    def _check_chardet_availability(self) -> bool:
        """检查chardet库是否可用"""
        try:
            import chardet

            _ = chardet.__version__

            return True
        except ImportError as e:
            print(f'Warning: 导入chardet失败: {e}')
            return False

    def detect_encoding(self, content: bytes, url: str = '') -> str:
        """检测内容编码

        Args:
            content: 响应内容字节
            url: 请求URL

        Returns:
            str: 检测到的编码名称
        """
        if not content:
            return DEFAULT_ENCODING

        # 1. 从内容中提取声明的编码
        declared_encoding = self._extract_encoding_from_content(content)
        if declared_encoding:
            return declared_encoding

        # 2. 使用chardet检测（如果可用）
        if self._chardet_available:
            detected_encoding = self._detect_with_chardet(content)
            if detected_encoding:
                return detected_encoding

        # 3. 基于URL和内容特征判断
        return self._detect_by_heuristics(content, url)

    def _extract_encoding_from_content(self, content: bytes) -> str | None:
        """从内容中提取编码声明

        Args:
            content: 响应内容字节

        Returns:
            str | None: 提取到的编码名称
        """
        if not content:
            return None

        # 只检查前2KB内容
        sample = content[:2048].lower()

        # 检查meta标签中的charset
        charset_patterns = [
            rb'charset\s*=\s*["\']?\s*([\w-]+)',
            rb'encoding\s*=\s*["\']?\s*([\w-]+)',
        ]

        for pattern in charset_patterns:
            match = re.search(pattern, sample)
            if match:
                encoding = match.group(1).decode('ascii', errors='ignore').lower()
                encoding = encoding.replace('_', '-')

                # 标准化编码名称
                if encoding in ['utf8', 'utf8mb4']:
                    return 'utf-8'
                if encoding in ['gb2312']:
                    return 'gbk'
                if encoding in CHINESE_ENCODINGS:
                    return encoding

        return None

    def _detect_with_chardet(self, content: bytes) -> str | None:
        """使用chardet检测编码，带缓存机制

        Args:
            content: 响应内容字节

        Returns:
            str | None: 检测到的编码名称
        """
        try:
            import chardet

            # 只检测前64KB内容以提高性能
            sample = content[:65536]

            # 使用内容hash作为缓存键，避免重复检测相同内容
            # 使用sha256而不是md5，更安全
            content_hash = hashlib.sha256(sample).hexdigest()

            # 检查缓存
            if content_hash in self._encoding_cache:
                return self._encoding_cache[content_hash]

            result = chardet.detect(sample)
            encoding = result.get('encoding')
            confidence = result.get('confidence', 0)

            if encoding and confidence > 0.6:
                encoding = encoding.lower()
                if encoding in ['utf8', 'utf8mb4']:
                    encoding = 'utf-8'
                elif encoding in ['gb2312']:
                    encoding = 'gbk'

                # 缓存检测结果，并检查缓存大小
                self._encoding_cache[content_hash] = encoding
                self._cleanup_cache_if_needed()
                return encoding

        except Exception as e:
            print(f'Warning: 使用chardet检测编码失败: {e}')
        return None

    def _cleanup_cache_if_needed(self) -> None:
        """清理缓存，防止内存泄漏"""
        if len(self._encoding_cache) > self._max_cache_size:
            # 删除最旧的缓存项（简单的FIFO策略）
            # 使用迭代器而不是创建完整列表，节省内存
            keys_to_remove = list(self._encoding_cache.keys())[: len(self._encoding_cache) // 2]
            for key in keys_to_remove:
                del self._encoding_cache[key]

    def _detect_by_heuristics(self, content: bytes, url: str) -> str:
        """基于启发式规则检测编码

        Args:
            content: 响应内容字节
            url: 请求URL

        Returns:
            str: 检测到的编码名称
        """
        # 检查是否为中文网站
        is_chinese_domain = self._is_chinese_domain(url)

        # 检查内容是否包含中文特征
        has_chinese = self._has_chinese_content(content)

        # 如果有中文特征或是中文网站，优先使用中文编码
        if has_chinese or is_chinese_domain:
            # 尝试中文编码
            for encoding in ['utf-8', 'gbk', 'gb18030']:
                if self._can_decode(content, encoding):
                    return encoding

        # 默认尝试UTF-8
        if self._can_decode(content, 'utf-8'):
            return 'utf-8'

        # 最后尝试latin-1（总是能解码）
        return 'latin-1'

    def _is_chinese_domain(self, url: str) -> bool:
        """判断是否为中文网站域名

        Args:
            url: 请求URL

        Returns:
            bool: 是否为中文网站
        """
        if not url:
            return False

        url_lower = url.lower()
        return any(domain in url_lower for domain in CHINESE_DOMAINS)

    def _has_chinese_content(self, content: bytes) -> bool:
        """检查内容是否包含中文特征

        Args:
            content: 响应内容字节

        Returns:
            bool: 是否包含中文内容
        """
        if not content:
            return False

        # 只检查前4KB内容以提高性能
        sample = content[:4096]

        # 1. 快速字节模式匹配（高频中文词汇）
        chinese_patterns = [
            b'\xe4\xbd\xa0\xe5\xa5\xbd',  # 你好
            b'\xe4\xb8\xad\xe5\x9b\xbd',  # 中国
            b'\xe4\xb8\xad\xe6\x96\x87',  # 中文
            b'\xe7\x9a\x84',  # 的
            b'\xe6\x98\xaf',  # 是
        ]

        if any(pattern in sample for pattern in chinese_patterns):
            return True

        # 2. UTF-8 编码模式检测
        utf8_pattern = rb'\xe4[\xb8-\xbf][\x80-\xbf]'
        if re.search(utf8_pattern, sample):
            return True

        # 3. GBK 编码检测
        return bool(re.search(rb'[\xb0-\xf7][\xa1-\xfe]', sample))

    def _can_decode(self, content: bytes, encoding: str) -> bool:
        """检查内容是否可以用指定编码解码

        Args:
            content: 响应内容字节
            encoding: 编码名称

        Returns:
            bool: 是否可以解码
        """
        try:
            content.decode(encoding, errors='strict')
            return True
        except (UnicodeDecodeError, LookupError):
            return False

    def decode_content(self, content: bytes, encoding: str) -> str:
        """解码字节内容，带有回退机制

        Args:
            content: 响应内容字节
            encoding: 编码名称

        Returns:
            str: 解码后的字符串
        """
        if not content:
            return ''

        # 首选编码解码
        try:
            return content.decode(encoding, errors='strict')
        except (UnicodeDecodeError, LookupError):
            pass

        # 回退解码策略
        fallback_encodings = ['utf-8', 'gbk', 'latin-1']

        for fallback_encoding in fallback_encodings:
            if fallback_encoding != encoding:
                try:
                    return content.decode(fallback_encoding, errors='strict')
                except (UnicodeDecodeError, LookupError):
                    continue

        # 最后使用宽松方式
        with suppress(Exception):
            return content.decode('utf-8', errors='replace')

        return content.decode('latin-1', errors='replace')


# 全局编码检测器实例
_encoding_detector: EncodingDetector | None = None


def get_encoding_detector() -> EncodingDetector:
    """获取全局编码检测器实例

    Returns:
        EncodingDetector: 全局编码检测器实例
    """
    global _encoding_detector
    if _encoding_detector is None:
        _encoding_detector = EncodingDetector()
    return _encoding_detector


def detect_encoding(content: bytes, url: str = '') -> str:
    """检测内容编码的便捷函数

    Args:
        content: 响应内容字节
        url: 请求URL

    Returns:
        str: 检测到的编码名称
    """
    return get_encoding_detector().detect_encoding(content, url)


def decode_content(content: bytes, encoding: str) -> str:
    """解码字节内容的便捷函数

    Args:
        content: 响应内容字节
        encoding: 编码名称

    Returns:
        str: 解码后的字符串
    """
    return get_encoding_detector().decode_content(content, encoding)


__all__ = [
    'CHINESE_DOMAINS',
    'CHINESE_ENCODINGS',
    'EncodingDetector',
    'decode_content',
    'detect_encoding',
    'get_encoding_detector',
]

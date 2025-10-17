# !/usr/bin/env python
"""
==============================================================
Description  : DOM解析和XPath查询模块
Develop      : VSCode
Author       : sandorn sandorn@live.cn
LastEditTime : 2025-10-17 09:40:00
Github       : https://github.com/sandorn/xthttp

本模块提供DOM解析和XPath查询功能
==============================================================
"""

from __future__ import annotations

from typing import Any

from pyquery import PyQuery


class DOMParser:
    """DOM解析器，提供HTML解析和查询功能"""

    def __init__(self):
        """初始化DOM解析器"""
        self._dom_cache: Any | None = None
        self._query_cache: PyQuery | None = None
        self._text_content: str = ''

    def parse_html(self, text: str) -> None:
        """解析HTML文本

        Args:
            text: HTML文本内容
        """
        self._text_content = text
        self._dom_cache = None
        self._query_cache = None

    def get_dom(self) -> Any | None:
        """获取lxml的DOM对象

        Returns:
            Any | None: lxml的DOM对象
        """
        if self._dom_cache is None and self._text_content:
            try:
                # 检查内容长度
                if len(self._text_content) > 10 * 1024 * 1024:
                    print('Warning: HTML内容过大,可能影响解析性能')

                from lxml import html

                self._dom_cache = html.fromstring(self._text_content)

            except Exception as e:
                print(f'Warning: DOM对象创建失败: {e}')
                self._dom_cache = self._parse_with_fallback()

        return self._dom_cache

    def get_pyquery(self) -> PyQuery | None:
        """获取PyQuery对象

        Returns:
            PyQuery | None: PyQuery对象
        """
        if self._query_cache is None and self._text_content:
            try:
                self._query_cache = PyQuery(self._text_content, parser='html')
            except UnicodeDecodeError:
                # 如果Unicode解码失败，尝试使用字节
                try:
                    self._query_cache = PyQuery(self._text_content.encode('utf-8', 'ignore'), parser='html', encoding='utf-8')
                except Exception:
                    self._query_cache = PyQuery('')
        return self._query_cache

    def xpath(self, *args: str) -> list[list[Any]]:
        """执行XPath选择查询

        Args:
            *args: XPath表达式

        Returns:
            list[list[Any]]: 查询结果列表
        """
        results = []
        if not args:
            return results

        dom = self.get_dom()
        if dom is None:
            return [[] for _ in args]

        for arg in args:
            if not arg or not arg.strip():
                results.append([])
                continue

            try:
                if hasattr(dom, 'xpath'):
                    results.append(dom.xpath(arg))
                else:
                    results.append([])
            except Exception as e:
                print(f'Warning: XPath查询失败: {arg}, 错误: {e}')
                results.append([])

        return results

    def css_select(self, selector: str) -> PyQuery:
        """CSS选择器查询

        Args:
            selector: CSS选择器

        Returns:
            PyQuery: 查询结果
        """
        query = self.get_pyquery()
        if query is None:
            return PyQuery('')

        try:
            return query(selector)
        except Exception as e:
            print(f'Warning: CSS选择器查询失败: {selector}, 错误: {e}')
            return PyQuery('')

    def _parse_with_fallback(self) -> Any | None:
        """使用后备解析器解析HTML

        Returns:
            Any | None: 解析后的DOM对象
        """
        # 方法1: 尝试使用soupparser
        try:
            from lxml.html import soupparser

            return soupparser.fromstring(self._text_content)
        except ImportError as e:
            print(f'Warning: 导入soupparser失败: {e}')
        except Exception as e:
            print(f'Warning: 使用soupparser解析html失败: {e}')

        # 方法2: 尝试使用html5lib
        try:
            import html5lib
            from lxml import html

            document = html5lib.parse(self._text_content, treebuilder='lxml')
            return document.getroot()
        except ImportError as e:
            print(f'Warning: 导入html5lib失败: {e}')
        except Exception as e:
            print(f'Warning: 使用html5lib解析html失败: {e}')

        # 方法3: 尝试使用更宽松的HTMLParser
        try:
            from lxml import html

            parser = html.HTMLParser(
                encoding='utf-8',
                recover=True,
                remove_comments=True,
                remove_pis=True,
            )
            return html.fromstring(self._text_content.encode('utf-8'), parser=parser)
        except Exception as e:
            print(f'Warning: 所有HTML解析方法都失败: {e}')

        return None

    def clear_cache(self) -> None:
        """清除缓存"""
        self._dom_cache = None
        self._query_cache = None


# 全局DOM解析器实例
_dom_parser: DOMParser | None = None


def get_dom_parser() -> DOMParser:
    """获取全局DOM解析器实例

    Returns:
        DOMParser: 全局DOM解析器实例
    """
    global _dom_parser
    if _dom_parser is None:
        _dom_parser = DOMParser()
    return _dom_parser


def parse_html(text: str) -> DOMParser:
    """解析HTML文本的便捷函数

    Args:
        text: HTML文本内容

    Returns:
        DOMParser: 解析器实例
    """
    parser = get_dom_parser()
    parser.parse_html(text)
    return parser


__all__ = [
    'DOMParser',
    'get_dom_parser',
    'parse_html',
]

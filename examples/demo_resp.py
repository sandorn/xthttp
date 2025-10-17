from __future__ import annotations

from xthttp.resp import UnifiedResp
from xthttp.resp.encoding import decode_content, detect_encoding
from xtlog import mylog


def run_test(url: str, expected_encoding: str | None = None):
    """运行测试"""
    mylog.info('=' * 70)
    mylog.info(f'正在测试网址: {url}')
    if expected_encoding:
        mylog.info(f'预期编码: {expected_encoding}')

    try:
        # 导入get函数
        from xthttp.requ import get

        # 获取原始响应
        unified_resp = get(url)
        if isinstance(unified_resp, UnifiedResp):
            mylog.info(f'响应状态: {unified_resp.status}|{unified_resp.index}')
            mylog.info(f'响应URL: {unified_resp.url}')
            mylog.info(f'检测到的编码: {unified_resp.encoding}')
        else:
            mylog.error(f'响应对象type: {type(unified_resp).__name__}')
            return

        # 编码验证
        if expected_encoding:
            encoding_match = unified_resp.encoding.lower() == expected_encoding.lower()
            mylog.info(f'编码匹配: {"✓" if encoding_match else "✗"} (预期: {expected_encoding}, 实际: {unified_resp.encoding})')

        # 显示响应头中的编码信息
        content_type = unified_resp.headers.get('content-type', '')
        mylog.info(f'Content-Type: {content_type}')

        # 详细的编码分析
        mylog.info('--- 编码分析详情 ---')
        raw_content = unified_resp.content
        mylog.info(f'原始内容大小: {len(raw_content)} 字节')

        # 手动检测编码
        manual_encoding = detect_encoding(raw_content, url)
        mylog.info(f'手动检测编码: {manual_encoding}')

        # 测试不同编码的解码效果
        test_encodings = ['utf-8', 'gbk', 'gb18030', 'big5', 'iso-8859-1']
        mylog.info('不同编码解码测试:')
        for test_encoding in test_encodings:
            try:
                test_text = decode_content(raw_content, test_encoding)
                # 检查解码后的文本是否包含乱码
                has_garbled = any(ord(char) > 127 and char not in ',.!?;:"\'()[]<>' for char in test_text[:50])
                status = '✓' if not has_garbled else '✗'
                mylog.info(f'  {test_encoding}: {status} (前50字符: {test_text[:50]!r})')
            except Exception as e:
                mylog.info(f'  {test_encoding}: ✗ 解码失败 ({e})')

        # 测试HTML解析功能
        title = unified_resp.xpath('//title/text()')
        mylog.info(f'页面标题: {title[0] if title and title[0] else "未找到"}')

        # 显示页面内容的前100个字符，用于验证编码是否正确
        page_content = unified_resp.text[:100]
        mylog.info(f'页面内容预览: {page_content!r}')

        # 检查是否包含乱码
        has_garbled = any(ord(char) > 127 and char not in ',.!?;:"\'()[]<>' for char in page_content)
        if has_garbled:
            mylog.warning('检测到可能的乱码字符')
        else:
            mylog.info('✓ 编码解码正常, 无乱码')

        # 增加更多的xpath测试内容
        xpath_result = unified_resp.xpath('//title/text()')
        mylog.info(f'xpath(//title/text()) : {xpath_result}')

        xpath_multi = unified_resp.xpath('//title/text()', '//title/text()')
        mylog.info(f'xpath([//title/text(), //title/text()]) : {xpath_multi}')

        query_result = unified_resp.query('title').text()
        mylog.info(f'query(title).text() : {query_result}')

        # 只有在DOM有效时才执行这个测试
        if unified_resp.dom is not None and hasattr(unified_resp.dom, 'xpath'):
            try:
                dom_result = unified_resp.dom.xpath('//title/text()')
                mylog.info(f'dom.xpath(//title/text()) : {dom_result}')
            except Exception as e:
                mylog.warning(f'direct dom.xpath failed: {e}')
        else:
            mylog.info('dom.xpath: DOM对象不可用')

        mylog.info('测试完成!')
    except Exception as e:
        mylog.error(f'测试失败: {e}')
        import traceback

        mylog.error(f'详细堆栈: {traceback.format_exc()}')


def test_encoding_fallback():
    """测试编码回退机制"""
    mylog.info('=' * 70)
    mylog.info('测试编码回退机制')

    # 创建一些测试数据
    test_data = {
        'utf8_text': '你好世界 Hello World 中文测试'.encode(),
        'gbk_text': '你好世界 Hello World 中文测试'.encode('gbk'),
        'mixed_text': 'Hello 世界 中文'.encode(),
    }

    for name, content in test_data.items():
        mylog.info(f'\n测试数据: {name}')
        mylog.info(f'原始字节: {content[:20]}...')

        # 测试不同编码的解码
        for encoding in ['utf-8', 'gbk', 'gb18030', 'latin-1']:
            try:
                decoded = decode_content(content, encoding)
                mylog.info(f'  {encoding}: {decoded[:30]!r}')
            except Exception as e:
                mylog.info(f'  {encoding}: 解码失败 - {e}')


# 多种编码格式的测试网站
test_cases = [
    # UTF-8 编码网站
    {'url': 'https://www.baidu.com', 'expected_encoding': 'utf-8', 'description': '百度 - UTF-8编码'},
    {'url': 'https://zh.wikipedia.org', 'expected_encoding': 'utf-8', 'description': '维基百科中文 - UTF-8编码'},
    {'url': 'https://www.github.com', 'expected_encoding': 'utf-8', 'description': 'GitHub - UTF-8编码'},
    # GBK/GB2312 编码网站
    {'url': 'https://www.sina.com.cn', 'expected_encoding': 'gbk', 'description': '新浪网 - GBK编码'},
    {'url': 'https://www.163.com', 'expected_encoding': 'gbk', 'description': '网易 - GBK编码'},
    # 其他编码网站
    {
        'url': 'https://www.yahoo.co.jp',
        'expected_encoding': 'utf-8',  # 现代网站通常使用UTF-8
        'description': '雅虎日本 - 日文网站',
    },
    {
        'url': 'https://www.naver.com',
        'expected_encoding': 'utf-8',  # 现代网站通常使用UTF-8
        'description': 'NAVER韩国 - 韩文网站',
    },
    # 国际网站
    {'url': 'https://www.bbc.com', 'expected_encoding': 'utf-8', 'description': 'BBC - 英文网站'},
    {'url': 'https://www.google.com', 'expected_encoding': 'utf-8', 'description': 'Google - 国际网站'},
    # 中文技术网站
    {'url': 'https://www.csdn.net', 'expected_encoding': 'utf-8', 'description': 'CSDN - 中文技术网站'},
    {'url': 'https://www.zhihu.com', 'expected_encoding': 'utf-8', 'description': '知乎 - 中文问答网站'},
]

# 运行测试
mylog.info('开始测试多种编码格式的网站...')
mylog.info(f'总共 {len(test_cases)} 个测试用例')

# 首先运行编码回退测试
test_encoding_fallback()

# 然后运行网站测试
for i, test_case in enumerate(test_cases, 1):
    mylog.info(f'\n[{i}/{len(test_cases)}] {test_case["description"]}')
    run_test(test_case['url'], test_case['expected_encoding'])

mylog.info('\n\n所有测试完成!')
mylog.info('=' * 70)
mylog.info('测试总结:')
mylog.info('1. 编码回退机制测试: 验证不同编码格式的解码能力')
mylog.info('2. UTF-8编码网站: 百度、维基百科、GitHub、BBC、Google、CSDN、知乎等')
mylog.info('3. GBK编码网站: 新浪网、网易等传统中文网站')
mylog.info('4. 国际网站: 雅虎日本、NAVER韩国等')
mylog.info('5. 通过测试验证unified_resp的编码检测和解码功能')
mylog.info('=' * 70)

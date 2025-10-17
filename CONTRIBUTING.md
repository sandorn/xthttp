# 贡献指南

感谢您对 xthttp 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

-   🐛 Bug 报告
-   ✨ 新功能建议
-   📚 文档改进
-   🔧 代码优化
-   🧪 测试用例

## 📋 贡献流程

### 1. Fork 项目

1. 点击 GitHub 页面右上角的 "Fork" 按钮
2. 将 fork 的仓库克隆到本地：
    ```bash
    git clone https://github.com/你的用户名/xthttp.git
    cd xthttp
    ```

### 2. 创建开发环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装开发依赖
pip install -e ".[test]"
```

### 3. 创建分支

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 或创建修复分支
git checkout -b fix/your-bug-fix
```

### 4. 开发

-   编写代码
-   添加测试用例
-   更新文档
-   确保代码质量

### 5. 测试

```bash
# 运行代码检查
ruff check .
ruff format .

# 运行类型检查
basedpyright .

# 运行测试
pytest
```

### 6. 提交

```bash
# 添加更改
git add .

# 提交更改
git commit -m "feat: 添加新功能描述"

# 推送到你的 fork
git push origin feature/your-feature-name
```

### 7. 创建 Pull Request

1. 在 GitHub 上创建 Pull Request
2. 填写详细的描述
3. 等待代码审查

## 📝 代码规范

### Python 代码风格

我们使用以下工具来保证代码质量：

-   **Ruff**: 代码检查和格式化
-   **BasedPyright**: 类型检查
-   **Google 风格**: 文档字符串格式

### 代码检查

```bash
# 自动修复代码问题
ruff check --fix .

# 格式化代码
ruff format .

# 类型检查
basedpyright .
```

### 文档字符串

使用 Google 风格的文档字符串：

```python
def example_function(param1: str, param2: int = 10) -> bool:
    """函数简短描述

    详细描述函数的功能和用途。

    Args:
        param1 (str): 参数1的描述
        param2 (int, optional): 参数2的描述，默认为10

    Returns:
        bool: 返回值的描述

    Raises:
        ValueError: 当参数无效时抛出

    Example:
        >>> result = example_function("test", 20)
        >>> print(result)
        True
    """
    pass
```

### 类型注解

所有公共函数和类都应该有完整的类型注解：

```python
from typing import Any, Dict, List, Optional

def process_data(data: List[Dict[str, Any]]) -> Optional[str]:
    """处理数据并返回结果"""
    pass
```

## 🧪 测试

### 添加测试用例

在 `tests/` 目录下添加测试文件：

```python
import pytest
from xthttp import get

def test_basic_get():
    """测试基本GET请求"""
    response = get('https://httpbin.org/get')
    assert response.status == 200
    assert 'httpbin' in response.text
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_http.py

# 运行测试并生成覆盖率报告
pytest --cov=xthttp
```

## 📚 文档

### 更新文档

-   **README.md**: 主要功能和使用示例
-   **CHANGELOG.md**: 版本更新记录
-   **代码注释**: 函数和类的文档字符串

### 文档要求

-   使用清晰的中文描述
-   提供实际可运行的代码示例
-   包含完整的参数说明
-   说明可能的异常情况

## 🐛 Bug 报告

### 报告 Bug

在创建 Issue 时，请包含以下信息：

1. **环境信息**:

    - Python 版本
    - 操作系统
    - xthttp 版本

2. **重现步骤**:

    - 详细的操作步骤
    - 最小可重现的代码示例

3. **期望行为**:

    - 描述您期望的结果

4. **实际行为**:
    - 描述实际发生的情况
    - 错误信息或异常堆栈

### Bug 报告模板

````markdown
## Bug 描述

简要描述遇到的问题

## 重现步骤

1. 执行 '...'
2. 点击 '...'
3. 看到错误

## 期望行为

描述您期望的结果

## 实际行为

描述实际发生的情况

## 环境信息

-   Python 版本: 3.13.x
-   操作系统: Windows/macOS/Linux
-   xthttp 版本: 0.1.0

## 代码示例

```python
# 最小可重现的代码
```
````

## 错误信息

```
错误堆栈信息
```

````

## ✨ 功能建议

### 提出新功能

1. 在 Issues 中创建 "Feature Request" 标签的 Issue
2. 详细描述功能需求和使用场景
3. 讨论实现方案和可能的挑战

### 功能建议模板

```markdown
## 功能描述
简要描述建议的新功能

## 使用场景
描述在什么情况下会用到这个功能

## 实现建议
如果有想法，可以描述实现方案

## 替代方案
描述其他可能的解决方案
````

## 🔄 发布流程

### 版本发布

1. 更新 `CHANGELOG.md`
2. 更新版本号（`pyproject.toml` 和 `__init__.py`）
3. 创建 Release Tag
4. 发布到 PyPI

### 版本号规则

-   **主版本号**: 不兼容的 API 修改
-   **次版本号**: 向下兼容的功能性新增
-   **修订号**: 向下兼容的问题修正

## 📞 联系方式

-   **GitHub Issues**: [项目 Issues](https://github.com/sandorn/xthttp/issues)
-   **邮箱**: sandorn@live.cn

## 📄 许可证

通过贡献代码，您同意您的贡献将在 MIT 许可证下发布。

---

再次感谢您的贡献！🎉

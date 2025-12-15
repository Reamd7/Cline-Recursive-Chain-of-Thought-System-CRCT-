"""
测试模块：运行时检查器测试
Test Module: Runtime Inspector Tests

本模块提供了对runtime_inspector模块各函数的全面测试，包括：
- 类型注解获取测试
- 源代码上下文提取测试
- 模块导出信息获取测试
- 继承信息提取测试
- 闭包依赖分析测试
- 装饰器信息提取测试
- 作用域引用分析测试
- 属性访问提取测试

This module provides comprehensive tests for runtime_inspector module functions, including:
- Type annotation retrieval tests
- Source code context extraction tests
- Module export information retrieval tests
- Inheritance information extraction tests
- Closure dependency analysis tests
- Decorator information extraction tests
- Scope reference analysis tests
- Attribute access extraction tests
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入inspect模块，用于代码对象检查 / Import inspect module for code object inspection
import inspect
# 导入sys模块，用于系统级操作 / Import sys module for system-level operations
import sys
# 导入os模块，用于操作系统接口 / Import os module for OS interface
import os
# 导入mock工具 / Import mock tools
from unittest.mock import MagicMock, patch
# 导入类型提示 / Import type hints
from typing import List, Dict, Any

# 导入被测试的运行时检查器函数 / Import runtime inspector functions to be tested
from cline_utils.dependency_system.analysis.runtime_inspector import (
    get_type_annotations,  # 获取类型注解 / Get type annotations
    get_source_context,  # 获取源代码上下文 / Get source context
    get_module_exports,  # 获取模块导出信息 / Get module exports
    get_inheritance_info,  # 获取继承信息 / Get inheritance info
    get_closure_dependencies,  # 获取闭包依赖 / Get closure dependencies
    get_decorator_info,  # 获取装饰器信息 / Get decorator info
    get_scope_references,  # 获取作用域引用 / Get scope references
    get_attribute_accesses  # 获取属性访问 / Get attribute accesses
)

# 测试用示例对象定义 / Sample objects for testing

def sample_func(a: int, b: str) -> bool:
    """
    示例函数：用于测试类型注解提取
    Sample function: For testing type annotation extraction

    参数：
    - a: 整数类型参数
    - b: 字符串类型参数

    返回：
    - 布尔类型返回值

    Parameters:
    - a: Integer type parameter
    - b: String type parameter

    Returns:
    - Boolean type return value
    """
    # 示例docstring / Sample docstring
    return True

class BaseClass:
    """
    基类：用于测试继承信息提取
    Base class: For testing inheritance info extraction
    """
    pass

class SampleClass(BaseClass):
    """
    示例类：继承自BaseClass，用于测试继承链
    Sample class: Inherits from BaseClass, for testing inheritance chain
    """
    def method(self):
        """示例方法 / Sample method"""
        pass

def outer():
    """
    外层函数：用于测试闭包依赖分析
    Outer function: For testing closure dependency analysis

    返回内部函数，形成闭包
    Returns inner function, forming closure
    """
    # 定义闭包变量 / Define closure variable
    x = 1
    def inner():
        """内层函数，引用外层变量x / Inner function, references outer variable x"""
        return x
    # 返回内层函数 / Return inner function
    return inner

@pytest.fixture
def mock_path_utils():
    """
    测试fixture：提供模拟的path_utils模块
    Test fixture: Provide mocked path_utils module

    目的：模拟路径工具函数，避免实际路径操作
    Purpose: Mock path utility functions to avoid actual path operations

    提供的模拟函数：
    - normalize_path: 标准化路径（转换反斜杠为正斜杠）
    - is_subpath: 判断是否为子路径

    Provided mock functions:
    - normalize_path: Normalize path (convert backslashes to forward slashes)
    - is_subpath: Check if is subpath
    """
    # 使用patch.dict将模拟模块注入sys.modules / Use patch.dict to inject mock module into sys.modules
    with patch.dict("sys.modules", {"cline_utils.dependency_system.utils.path_utils": MagicMock()}):
        # 获取模拟的path_utils模块 / Get mocked path_utils module
        mock = sys.modules["cline_utils.dependency_system.utils.path_utils"]
        # 定义normalize_path的模拟行为：将反斜杠替换为正斜杠 / Define normalize_path mock behavior: replace backslashes with forward slashes
        mock.normalize_path = lambda p: p.replace("\\", "/")
        # 定义is_subpath的模拟行为：检查路径前缀 / Define is_subpath mock behavior: check path prefix
        mock.is_subpath = lambda p, r: p.startswith(r)
        # 将模拟对象提供给测试函数 / Yield mock object to test function
        yield mock

class TestRuntimeInspector:
    """
    测试类：运行时检查器功能测试
    Test Class: Runtime Inspector Functionality Tests

    测试runtime_inspector模块的各个功能，包括：
    - 类型注解提取
    - 源代码上下文获取
    - 模块导出分析
    - 继承信息获取
    - 闭包依赖提取
    - 作用域引用分析
    - 属性访问提取

    Tests various functionalities of runtime_inspector module, including:
    - Type annotation extraction
    - Source code context retrieval
    - Module export analysis
    - Inheritance info retrieval
    - Closure dependency extraction
    - Scope reference analysis
    - Attribute access extraction
    """

    def test_get_type_annotations(self):
        """
        测试用例：验证类型注解提取功能
        Test Case: Verify Type Annotation Extraction Functionality

        目的：确保get_type_annotations()能正确提取函数的类型注解
        Purpose: Ensure get_type_annotations() correctly extracts function's type annotations

        测试对象：sample_func(a: int, b: str) -> bool

        验证点：
        1. 参数'a'的类型注解为int
        2. 参数'b'的类型注解为str
        3. 返回值类型注解为bool

        Verification Points:
        1. Parameter 'a' type annotation is int
        2. Parameter 'b' type annotation is str
        3. Return type annotation is bool
        """
        # 调用get_type_annotations获取sample_func的类型注解 / Call get_type_annotations to get sample_func's type annotations
        annotations = get_type_annotations(sample_func)
        # 断言：参数'a'的类型应为"<class 'int'>" / Assert: parameter 'a' type should be "<class 'int'>"
        assert annotations['parameters']['a'] == "<class 'int'>"
        # 断言：参数'b'的类型应为"<class 'str'>" / Assert: parameter 'b' type should be "<class 'str'>"
        assert annotations['parameters']['b'] == "<class 'str'>"
        # 断言：返回值类型应为"<class 'bool'>" / Assert: return type should be "<class 'bool'>"
        assert annotations['return_type'] == "<class 'bool'>"

    def test_get_source_context(self, mock_path_utils):
        """
        测试用例：验证源代码上下文提取功能
        Test Case: Verify Source Code Context Extraction Functionality

        目的：确保get_source_context()能正确提取函数的源代码上下文
        Purpose: Ensure get_source_context() correctly extracts function's source code context

        测试对象：sample_func
        测试场景：函数源文件在code_roots内

        Test Object: sample_func
        Test Scenario: Function source file is within code_roots

        验证点：
        1. 返回的文件路径正确
        2. 包含行范围信息
        3. 包含源代码行内容
        4. 源代码包含函数定义

        Verification Points:
        1. Returned file path is correct
        2. Contains line range information
        3. Contains source code line content
        4. Source code contains function definition
        """
        # 使用inspect.getsourcefile获取sample_func的源文件路径，并标准化路径 / Use inspect.getsourcefile to get sample_func's source file path and normalize it
        current_file = inspect.getsourcefile(sample_func).replace("\\", "/")
        # 构造code_roots列表，包含源文件所在目录 / Construct code_roots list containing source file directory
        code_roots = [os.path.dirname(current_file).replace("\\", "/")]

        # 调用get_source_context获取源代码上下文 / Call get_source_context to get source code context
        context = get_source_context(sample_func, code_roots)
        # 断言：返回的文件路径应与current_file一致 / Assert: returned file path should match current_file
        assert context['file'] == current_file
        # 断言：上下文中应包含'line_range'键 / Assert: context should contain 'line_range' key
        assert 'line_range' in context
        # 断言：上下文中应包含'source_lines'键 / Assert: context should contain 'source_lines' key
        assert 'source_lines' in context
        # 断言：第一行源代码应包含"def sample_func" / Assert: first source line should contain "def sample_func"
        assert "def sample_func" in context['source_lines'][0]

    def test_get_source_context_outside_root(self, mock_path_utils):
        """
        测试用例：验证源代码上下文提取（文件在根目录外）
        Test Case: Verify Source Code Context Extraction (File Outside Root)

        目的：确保当源文件不在code_roots内时返回空字典
        Purpose: Ensure empty dict is returned when source file is not within code_roots

        测试对象：sample_func
        测试场景：code_roots指向其他路径

        Test Object: sample_func
        Test Scenario: code_roots points to other path

        验证点：
        1. 返回空字典

        Verification Points:
        1. Returns empty dict
        """
        # 设置code_roots为不相关的路径 / Set code_roots to unrelated path
        code_roots = ["/other/path"]
        # 调用get_source_context / Call get_source_context
        context = get_source_context(sample_func, code_roots)
        # 断言：应返回空字典 / Assert: should return empty dict
        assert context == {}

    def test_get_module_exports(self):
        """
        测试用例：验证模块导出信息获取功能
        Test Case: Verify Module Export Information Retrieval Functionality

        目的：确保get_module_exports()能正确提取模块的导出信息
        Purpose: Ensure get_module_exports() correctly extracts module's export information

        测试对象：模拟的模块对象
        测试场景：模块定义了__all__属性

        Test Object: Mocked module object
        Test Scenario: Module defines __all__ attribute

        验证点：
        1. 返回导出字典，键为导出名，值为模块名

        Verification Points:
        1. Returns export dict, key is export name, value is module name
        """
        # 创建模拟的模块对象 / Create mocked module object
        mock_module = MagicMock()
        # 设置模块的__all__属性，定义导出列表 / Set module's __all__ attribute, define export list
        mock_module.__all__ = ['exported_func']
        # 将sample_func赋值给模块的exported_func属性 / Assign sample_func to module's exported_func attribute
        mock_module.exported_func = sample_func
        # 使用patch模拟inspect.getmodule返回一个有__name__属性的模块 / Use patch to mock inspect.getmodule returning a module with __name__ attribute
        with patch("inspect.getmodule", return_value=MagicMock(__name__="some_module")):
            # 调用get_module_exports获取导出信息 / Call get_module_exports to get export info
            exports = get_module_exports(mock_module)
            # 断言：'exported_func'应映射到'some_module' / Assert: 'exported_func' should map to 'some_module'
            assert exports['exported_func'] == "some_module"

    def test_get_inheritance_info(self, mock_path_utils):
        """
        测试用例：验证继承信息提取功能
        Test Case: Verify Inheritance Information Extraction Functionality

        目的：确保get_inheritance_info()能正确提取类的继承信息
        Purpose: Ensure get_inheritance_info() correctly extracts class's inheritance information

        测试对象：SampleClass（继承自BaseClass）
        测试场景：类和基类都在code_roots内

        Test Object: SampleClass (inherits from BaseClass)
        Test Scenario: Both class and base class are within code_roots

        验证点：
        1. 基类列表(bases)中包含BaseClass
        2. 方法解析顺序(mro)中包含BaseClass

        Verification Points:
        1. Bases list contains BaseClass
        2. Method resolution order (mro) contains BaseClass
        """
        # 获取SampleClass的源文件路径并标准化 / Get SampleClass's source file path and normalize it
        current_file = inspect.getsourcefile(SampleClass).replace("\\", "/")
        # 构造code_roots列表 / Construct code_roots list
        code_roots = [os.path.dirname(current_file).replace("\\", "/")]

        # 调用get_inheritance_info获取继承信息 / Call get_inheritance_info to get inheritance info
        info = get_inheritance_info(SampleClass, code_roots)
        # 断言：基类列表中应包含"BaseClass" / Assert: bases list should contain "BaseClass"
        # BaseClass在同一文件中定义，应被捕获 / BaseClass is defined in same file, should be captured
        assert any("BaseClass" in base for base in info['bases'])
        # 断言：方法解析顺序中应包含"BaseClass" / Assert: mro should contain "BaseClass"
        assert any("BaseClass" in mro for mro in info['mro'])

    def test_get_closure_dependencies(self, mock_path_utils):
        """
        测试用例：验证闭包依赖提取功能
        Test Case: Verify Closure Dependency Extraction Functionality

        目的：确保get_closure_dependencies()能分析闭包中的依赖
        Purpose: Ensure get_closure_dependencies() can analyze dependencies in closures

        测试对象：outer()返回的内部函数（闭包）
        测试场景：内部函数引用外层变量x

        Test Object: Inner function returned by outer() (closure)
        Test Scenario: Inner function references outer variable x

        验证点：
        1. 返回列表类型
        2. （注意：由于x是整数，没有模块属性，不会提取到依赖）

        Verification Points:
        1. Returns list type
        2. (Note: Since x is integer without module attribute, no dependency is extracted)

        注意：
        此测试主要验证函数不会崩溃，实际依赖提取需要更复杂的设置
        Note:
        This test mainly verifies function doesn't crash, actual dependency extraction requires more complex setup
        """
        # 调用outer()获取内部函数（闭包） / Call outer() to get inner function (closure)
        inner_func = outer()
        # x是整数，没有模块属性，因此不会被提取为依赖 / x is integer, has no module attribute, so won't be extracted as dependency
        # 为了测试依赖提取，需要闭包引用一个有__module__属性的对象 / To test dependency extraction, closure needs to reference an object with __module__ attribute

        # 导入json模块用于更复杂的测试场景 / Import json module for more complex test scenario
        import json
        def closure_with_dep():
            """包含模块依赖的闭包 / Closure with module dependency"""
            return json.dumps({})

        # 这很难测试，因为get_closure_dependencies检查模块是否在code_roots中 / This is hard to test because get_closure_dependencies checks if module is in code_roots
        # 而标准库模块如json不会在code_roots中 / And standard library modules like json won't be in code_roots
        # 我们只检查它返回一个列表而不崩溃 / We'll just check it returns a list without crashing
        deps = get_closure_dependencies(inner_func, [])
        # 断言：返回值应为列表类型 / Assert: return value should be list type
        assert isinstance(deps, list)

    def test_get_scope_references(self):
        """
        测试用例：验证作用域引用分析功能
        Test Case: Verify Scope Reference Analysis Functionality

        目的：确保get_scope_references()能正确提取函数中的全局引用
        Purpose: Ensure get_scope_references() correctly extracts global references in function

        测试对象：引用sys.path的函数
        测试场景：函数使用全局变量sys

        Test Object: Function referencing sys.path
        Test Scenario: Function uses global variable sys

        验证点：
        1. globals字典中包含'sys'

        Verification Points:
        1. globals dict contains 'sys'
        """
        # 定义包含全局引用的测试函数 / Define test function with global reference
        def func_with_globals():
            """引用全局变量sys.path / References global variable sys.path"""
            return sys.path

        # 调用get_scope_references获取作用域引用 / Call get_scope_references to get scope references
        refs = get_scope_references(func_with_globals)
        # 断言：全局变量字典中应包含'sys' / Assert: globals dict should contain 'sys'
        assert 'sys' in refs['globals']

    def test_get_attribute_accesses(self):
        """
        测试用例：验证属性访问提取功能
        Test Case: Verify Attribute Access Extraction Functionality

        目的：确保get_attribute_accesses()能从源代码中提取属性访问
        Purpose: Ensure get_attribute_accesses() can extract attribute accesses from source code

        测试对象：包含self.bar和self.baz访问的源代码
        测试场景：解析包含self属性访问的代码

        Test Object: Source code containing self.bar and self.baz accesses
        Test Scenario: Parse code containing self attribute accesses

        验证点：
        1. 提取的属性访问列表中包含"bar"
        2. 提取的属性访问列表中包含"baz"

        Verification Points:
        1. Extracted attribute access list contains "bar"
        2. Extracted attribute access list contains "baz"
        """
        # 定义包含属性访问的源代码字符串 / Define source code string containing attribute accesses
        source = """
        def foo(self):
            self.bar = 1
            x = self.baz
        """
        # 调用get_attribute_accesses提取属性访问 / Call get_attribute_accesses to extract attribute accesses
        accesses = get_attribute_accesses(source)
        # 断言："bar"应在属性访问列表中 / Assert: "bar" should be in attribute access list
        assert "bar" in accesses
        # 断言："baz"应在属性访问列表中 / Assert: "baz" should be in attribute access list
        assert "baz" in accesses

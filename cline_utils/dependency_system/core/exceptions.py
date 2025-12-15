"""
============================================================================
依赖追踪系统自定义异常类 (Custom Exception Classes)
============================================================================

这个模块定义了依赖追踪系统中使用的所有自定义异常类。
所有异常都继承自基础异常类 DependencySystemError，形成清晰的异常层次结构。

异常层次结构:
-------------
DependencySystemError (基础异常)
├── TrackerError (追踪器相关异常)
├── EmbeddingError (嵌入相关异常)
├── AnalysisError (分析相关异常)
├── ConfigurationError (配置相关异常)
└── CacheError (缓存相关异常)

使用示例:
---------
>>> from cline_utils.dependency_system.core.exceptions import TrackerError
>>> raise TrackerError("追踪器文件未找到")

版本: v8.0
作者: CRCT 项目组
============================================================================
"""

# ============================================================================
# 基础异常类
# ============================================================================

class DependencySystemError(Exception):
    """
    依赖系统基础异常类 (Base Exception for Dependency System)

    这是所有依赖追踪系统异常的基类。
    所有特定的异常类型都应该继承此类。

    使用场景:
    --------
    - 捕获所有依赖系统相关的异常
    - 作为其他具体异常类的父类

    示例:
    ----
    >>> try:
    ...     # 执行依赖系统操作
    ...     pass
    ... except DependencySystemError as e:
    ...     print(f"依赖系统错误: {e}")
    """
    pass

# ============================================================================
# 具体异常类
# ============================================================================

class TrackerError(DependencySystemError):
    """
    追踪器操作相关异常 (Tracker Operation Exception)

    当追踪器文件的读取、写入、解析或更新操作失败时抛出此异常。

    常见场景:
    --------
    - 追踪器文件不存在或无法访问
    - 追踪器文件格式错误
    - 追踪器更新失败
    - 依赖关系验证失败

    示例:
    ----
    >>> raise TrackerError("无法读取追踪器文件: tracker.md")
    """
    pass

class EmbeddingError(DependencySystemError):
    """
    嵌入操作相关异常 (Embedding Operation Exception)

    当 Symbol Essence Strings (SES) 生成或嵌入向量计算失败时抛出此异常。

    常见场景:
    --------
    - 嵌入模型加载失败
    - 嵌入向量计算失败
    - SES 生成失败
    - 嵌入缓存错误

    v8.0 新增场景:
    -------------
    - Qwen3 模型加载失败
    - GGUF 模型初始化错误
    - 运行时符号检查失败

    示例:
    ----
    >>> raise EmbeddingError("Qwen3 模型加载失败")
    """
    pass

class AnalysisError(DependencySystemError):
    """
    分析操作相关异常 (Analysis Operation Exception)

    当代码分析、依赖解析或项目分析失败时抛出此异常。

    常见场景:
    --------
    - AST 解析失败
    - Tree-sitter 解析错误
    - 依赖关系分析失败
    - 项目结构分析错误
    - 符号映射合并失败

    示例:
    ----
    >>> raise AnalysisError("Python AST 解析失败: 语法错误")
    """
    pass

class ConfigurationError(DependencySystemError):
    """
    配置相关异常 (Configuration Exception)

    当配置文件加载、解析或验证失败时抛出此异常。

    常见场景:
    --------
    - 配置文件不存在或格式错误
    - 配置项缺失或无效
    - 配置值类型错误
    - 配置验证失败

    v8.0 新增场景:
    -------------
    - 硬件资源配置不足
    - 模型选择配置错误
    - 缓存策略配置无效

    示例:
    ----
    >>> raise ConfigurationError("配置文件缺少必需的项: reranker_model")
    """
    pass

class CacheError(DependencySystemError):
    """
    缓存操作相关异常 (Cache Operation Exception)

    当缓存的读取、写入、压缩或失效操作失败时抛出此异常。

    常见场景:
    --------
    - 缓存文件损坏
    - 缓存读写失败
    - 缓存压缩/解压缩错误
    - 缓存失效操作失败

    v8.0 新增场景:
    -------------
    - 多层缓存同步失败
    - 缓存策略执行错误
    - 重排序缓存历史追踪失败

    示例:
    ----
    >>> raise CacheError("缓存文件解压缩失败")
    """
    pass
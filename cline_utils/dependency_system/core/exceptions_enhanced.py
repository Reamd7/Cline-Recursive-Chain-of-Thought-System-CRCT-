"""
项目分析器系统的增强异常类型 / Enhanced exception types for the project analyzer system.

提供具体的、可操作的异常类型，用于更好的错误处理和调试。
Provides specific, actionable exception types for better error handling and debugging.

异常层次结构 / Exception Hierarchy:
- ProjectAnalyzerError (基础异常 / Base exception)
  ├── ConfigurationError (配置错误 / Configuration errors)
  ├── ResourceValidationError (资源验证错误 / Resource validation errors)
  │   ├── MemoryLimitError (内存不足错误 / Memory insufficiency)
  │   └── DiskSpaceError (磁盘空间不足错误 / Disk space insufficiency)
  ├── FileAnalysisError (文件分析错误 / File analysis errors)
  │   ├── BinaryFileError (二进制文件错误 / Binary file errors)
  │   ├── EncodingError (编码错误 / Encoding errors)
  │   └── ParsingError (解析错误 / Parsing errors)
  ├── ModelError (模型错误 / Model errors)
  │   └── EmbeddingGenerationError (嵌入生成错误 / Embedding generation errors)
  ├── TrackerUpdateError (跟踪器更新错误 / Tracker update errors)
  ├── StateManagementError (状态管理错误 / State management errors)
  ├── CacheError (缓存错误 / Cache errors)
  ├── ValidationError (验证错误 / Validation errors)
  ├── PathError (路径错误 / Path errors)
  ├── PermissionError (权限错误 / Permission errors)
  ├── NetworkError (网络错误 / Network errors)
  └── TimeoutError (超时错误 / Timeout errors)
"""

# ============================================================================
# 标准库导入 / Standard Library Imports
# ============================================================================
import logging  # 日志记录 / Logging
from typing import Any, Dict, Optional, List  # 类型提示 / Type hints
from pathlib import Path  # 路径操作 / Path operations

# ============================================================================
# 日志配置 / Logging Configuration
# ============================================================================
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器 / Get logger for this module


# ============================================================================
# 基础异常类 / Base Exception Classes
# ============================================================================

class ProjectAnalyzerError(Exception):
    """
    项目分析器的基础异常类 / Base exception for all project analyzer errors.

    所有项目分析器特定的异常都应该继承自这个类。
    All project analyzer specific exceptions should inherit from this class.

    特性 / Features:
    - 自动日志记录错误信息 / Automatic error logging
    - 支持附加详细信息字典 / Supports additional details dictionary
    - 统一的错误消息格式 / Unified error message format

    Attributes:
        message: 错误消息 / Error message
        details: 额外的错误详情 / Additional error details
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化项目分析器错误 / Initialize project analyzer error.

        Args:
            message: 错误消息 / Error message
            details: 可选的详细信息字典 / Optional details dictionary
        """
        super().__init__(message)  # 调用父类构造函数 / Call parent constructor
        self.message = message  # 存储错误消息 / Store error message
        self.details = details or {}  # 存储详细信息，默认空字典 / Store details, default empty dict

        # 自动记录错误到日志 / Automatically log error
        logger.error(f"ProjectAnalyzerError: {message}", extra={"details": self.details})


# ============================================================================
# 配置相关异常 / Configuration Related Exceptions
# ============================================================================

class ConfigurationError(ProjectAnalyzerError):
    """
    配置相关错误 / Configuration-related errors.

    用于配置文件解析、配置值验证或配置加载失败等场景。
    Used for config file parsing, config value validation, or config loading failures.

    示例场景 / Example Scenarios:
    - 配置文件格式错误 / Invalid config file format
    - 缺少必需的配置项 / Missing required configuration
    - 配置值类型不匹配 / Configuration value type mismatch
    """
    pass  # 继承所有父类功能 / Inherits all parent functionality


# ============================================================================
# 资源验证异常 / Resource Validation Exceptions
# ============================================================================

class ResourceValidationError(ProjectAnalyzerError):
    """
    系统资源验证错误 / System resource validation errors.

    当系统资源（内存、磁盘空间等）不足以执行操作时抛出。
    Raised when system resources (memory, disk space, etc.) are insufficient.

    Attributes:
        resource_type: 资源类型（如 "memory", "disk_space"）/ Resource type
        current: 当前可用资源量 / Current available resource amount
        required: 所需资源量 / Required resource amount
    """

    def __init__(self, resource_type: str, current: Any, required: Any, **kwargs):
        """
        初始化资源验证错误 / Initialize resource validation error.

        Args:
            resource_type: 资源类型 / Resource type
            current: 当前值 / Current value
            required: 需求值 / Required value
            **kwargs: 传递给父类的其他参数 / Additional arguments for parent class
        """
        self.resource_type = resource_type  # 存储资源类型 / Store resource type
        self.current = current  # 存储当前值 / Store current value
        self.required = required  # 存储需求值 / Store required value

        # 构建错误消息 / Build error message
        message = f"Insufficient {resource_type}: current={current}, required={required}"
        super().__init__(message, **kwargs)


class MemoryLimitError(ResourceValidationError):
    """
    内存不足错误 / Insufficient memory for operation.

    当可用内存不足以执行操作时抛出。
    Raised when available memory is insufficient for the operation.

    Attributes:
        current_mb: 当前可用内存（MB）/ Current available memory in MB
        required_mb: 所需内存（MB）/ Required memory in MB
    """

    def __init__(self, current_mb: float, required_mb: float, **kwargs):
        """
        初始化内存不足错误 / Initialize memory limit error.

        Args:
            current_mb: 当前可用内存（MB）/ Current available memory in MB
            required_mb: 所需内存（MB）/ Required memory in MB
            **kwargs: 传递给父类的其他参数 / Additional arguments for parent class
        """
        self.current_mb = current_mb  # 存储当前内存 / Store current memory
        self.required_mb = required_mb  # 存储需求内存 / Store required memory

        # 调用父类，传递 "memory" 作为资源类型 / Call parent with "memory" as resource type
        super().__init__("memory", current_mb, required_mb, **kwargs)


class DiskSpaceError(ResourceValidationError):
    """
    磁盘空间不足错误 / Insufficient disk space for operation.

    当磁盘可用空间不足以执行操作时抛出。
    Raised when available disk space is insufficient for the operation.

    Attributes:
        current_mb: 当前可用磁盘空间（MB）/ Current available disk space in MB
        required_mb: 所需磁盘空间（MB）/ Required disk space in MB
        path: 相关路径 / Related path
    """

    def __init__(self, current_mb: float, required_mb: float, path: str, **kwargs):
        """
        初始化磁盘空间不足错误 / Initialize disk space error.

        Args:
            current_mb: 当前可用磁盘空间（MB）/ Current available disk space in MB
            required_mb: 所需磁盘空间（MB）/ Required disk space in MB
            path: 检查的路径 / Path being checked
            **kwargs: 传递给父类的其他参数 / Additional arguments for parent class
        """
        self.current_mb = current_mb  # 存储当前磁盘空间 / Store current disk space
        self.required_mb = required_mb  # 存储需求磁盘空间 / Store required disk space
        self.path = path  # 存储路径 / Store path

        # 调用父类，传递 "disk_space" 作为资源类型 / Call parent with "disk_space" as resource type
        super().__init__("disk_space", current_mb, required_mb, **kwargs)


# ============================================================================
# 文件分析异常 / File Analysis Exceptions
# ============================================================================

class FileAnalysisError(ProjectAnalyzerError):
    """
    文件分析特定错误 / File analysis specific errors.

    当文件分析过程中发生错误时抛出。
    Raised when errors occur during file analysis.

    Attributes:
        file_path: 发生错误的文件路径 / File path where error occurred
        error_type: 错误类型描述 / Error type description
    """

    def __init__(self, file_path: str, error_type: str, **kwargs):
        """
        初始化文件分析错误 / Initialize file analysis error.

        Args:
            file_path: 文件路径 / File path
            error_type: 错误类型 / Error type
            **kwargs: 传递给父类的其他参数 / Additional arguments for parent class
        """
        self.file_path = str(file_path)  # 存储文件路径（转为字符串）/ Store file path (convert to string)
        self.error_type = error_type  # 存储错误类型 / Store error type

        # 构建错误消息 / Build error message
        message = f"Analysis failed for {file_path}: {error_type}"
        super().__init__(message, **kwargs)


class BinaryFileError(FileAnalysisError):
    """二进制文件错误 / Binary file detected during text analysis."""

    def __init__(self, file_path: str, file_size: int = 0, **kwargs):
        self.file_size = file_size  # 存储文件大小 / Store file size
        message = f"Binary file detected: {file_path} (size: {file_size} bytes)"
        super().__init__(file_path, "binary_file", **kwargs)


class EncodingError(FileAnalysisError):
    """文件编码错误 / File encoding related errors."""

    def __init__(self, file_path: str, encoding_attempted: str = "utf-8", **kwargs):
        self.encoding_attempted = encoding_attempted  # 存储尝试的编码 / Store attempted encoding
        message = f"Encoding error for {file_path} with {encoding_attempted}"
        super().__init__(file_path, "encoding_error", **kwargs)


class ParsingError(FileAnalysisError):
    """源文件的语法或解析错误 / Syntax or parsing errors in source files."""

    def __init__(self, file_path: str, line_number: Optional[int] = None,
                 syntax_details: Optional[str] = None, **kwargs):
        self.line_number = line_number  # 存储错误行号 / Store error line number
        self.syntax_details = syntax_details  # 存储语法错误详情 / Store syntax error details

        # 步骤 1: 获取或创建 details 字典 / Get or create details dictionary
        details = kwargs.get('details', {})

        # 步骤 2: 添加行号到详情 / Add line number to details
        if line_number is not None:
            details['line_number'] = line_number

        # 步骤 3: 添加语法详情 / Add syntax details
        if syntax_details:
            details['syntax_details'] = syntax_details

        # 步骤 4: 更新 kwargs / Update kwargs
        kwargs['details'] = details

        # 步骤 5: 构建错误消息 / Build error message
        message = f"Parsing error in {file_path}"
        if line_number:
            message += f" at line {line_number}"
        if syntax_details:
            message += f": {syntax_details}"

        super().__init__(file_path, "parsing_error", **kwargs)


# ============================================================================
# AI 模型异常 / AI Model Exceptions
# ============================================================================

class ModelError(ProjectAnalyzerError):
    """AI 模型相关错误 / AI model related errors."""

    def __init__(self, model_name: str, error_type: str, **kwargs):
        self.model_name = model_name  # 存储模型名称 / Store model name
        self.error_type = error_type  # 存储错误类型 / Store error type
        message = f"Model error [{model_name}]: {error_type}"
        super().__init__(message, **kwargs)


class EmbeddingGenerationError(ModelError):
    """嵌入生成特定错误 / Embedding generation specific errors."""

    def __init__(self, model_name: str, file_count: int = 0, **kwargs):
        self.file_count = file_count  # 存储处理的文件数量 / Store number of files processed
        message = f"Embedding generation failed for {model_name} (files: {file_count})"
        super().__init__(model_name, "embedding_generation", **kwargs)


# ============================================================================
# 其他特定异常 / Other Specific Exceptions
# ============================================================================

class TrackerUpdateError(ProjectAnalyzerError):
    """跟踪器文件更新错误 / Tracker file update errors."""

    def __init__(self, tracker_path: str, operation: str, **kwargs):
        self.tracker_path = str(tracker_path)  # 存储跟踪器路径 / Store tracker path
        self.operation = operation  # 存储操作类型 / Store operation type
        message = f"Tracker update failed for {tracker_path} during {operation}"
        super().__init__(message, **kwargs)


class StateManagementError(ProjectAnalyzerError):
    """状态管理和备份/恢复错误 / State management and backup/restore errors."""

    def __init__(self, operation: str, **kwargs):
        self.operation = operation  # 存储操作类型 / Store operation type
        message = f"State management error during {operation}"
        super().__init__(message, **kwargs)


class CacheError(ProjectAnalyzerError):
    """缓存相关错误 / Cache-related errors."""

    def __init__(self, cache_name: str, operation: str, **kwargs):
        self.cache_name = cache_name  # 存储缓存名称 / Store cache name
        self.operation = operation  # 存储操作类型 / Store operation type
        message = f"Cache error [{cache_name}] during {operation}"
        super().__init__(message, **kwargs)


class ValidationError(ProjectAnalyzerError):
    """数据验证错误 / Data validation errors."""

    def __init__(self, field_name: str, value: Any, expected: str, **kwargs):
        self.field_name = field_name  # 存储字段名 / Store field name
        self.value = value  # 存储实际值 / Store actual value
        self.expected = expected  # 存储期望值描述 / Store expected value description
        message = f"Validation error: {field_name}={value} (expected: {expected})"
        super().__init__(message, **kwargs)


class PathError(ProjectAnalyzerError):
    """路径相关错误 / Path-related errors."""

    def __init__(self, path: str, error_type: str, **kwargs):
        self.path = str(path)  # 存储路径 / Store path
        self.error_type = error_type  # 存储错误类型 / Store error type
        message = f"Path error [{path}]: {error_type}"
        super().__init__(message, **kwargs)


class PermissionError(ProjectAnalyzerError):
    """文件/目录权限错误 / File/directory permission errors."""

    def __init__(self, path: str, operation: str, **kwargs):
        self.path = str(path)  # 存储路径 / Store path
        self.operation = operation  # 存储操作类型 / Store operation type
        message = f"Permission denied for {path} during {operation}"
        super().__init__(message, **kwargs)


class NetworkError(ProjectAnalyzerError):
    """网络相关错误 / Network-related errors."""

    def __init__(self, url: str, operation: str, **kwargs):
        self.url = url  # 存储 URL / Store URL
        self.operation = operation  # 存储操作类型 / Store operation type
        message = f"Network error for {url} during {operation}"
        super().__init__(message, **kwargs)


class TimeoutError(ProjectAnalyzerError):
    """操作超时错误 / Operation timeout errors."""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        self.operation = operation  # 存储操作类型 / Store operation type
        self.timeout_seconds = timeout_seconds  # 存储超时秒数 / Store timeout seconds
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(message, **kwargs)


# ============================================================================
# 错误恢复辅助函数 / Error Recovery Helpers
# ============================================================================

def handle_file_analysis_error(file_path: str, original_error: Exception) -> FileAnalysisError:
    """
    将各种文件相关的异常转换为 FileAnalysisError / Convert various file-related exceptions to FileAnalysisError.

    这个函数作为错误转换器，将Python标准异常映射到我们的自定义异常层次结构。
    This function acts as an error converter, mapping Python standard exceptions to our custom exception hierarchy.

    Args:
        file_path: 发生错误的文件路径 / File path where error occurred
        original_error: 原始捕获的异常 / Original caught exception

    Returns:
        适当的 FileAnalysisError 子类实例 / Appropriate FileAnalysisError subclass instance
    """
    # 步骤 1: 检查权限错误 / Check for permission errors
    if isinstance(original_error, PermissionError):
        return PermissionError(file_path, "read")

    # 步骤 2: 检查编码错误 / Check for encoding errors
    elif isinstance(original_error, UnicodeDecodeError):
        return EncodingError(file_path, str(original_error.encoding))

    # 步骤 3: 检查语法错误 / Check for syntax errors
    elif isinstance(original_error, SyntaxError):
        return ParsingError(
            file_path,
            original_error.lineno,
            str(original_error),
            details={'filename': original_error.filename, 'offset': original_error.offset}
        )

    # 步骤 4: 未处理的错误，创建通用文件分析错误
    # Unhandled error, create generic file analysis error
    else:
        return FileAnalysisError(
            file_path,
            f"unhandled_error: {type(original_error).__name__}",
            details={'original_error': str(original_error), 'error_type': type(original_error).__name__}
        )


def handle_model_error(original_error: Exception, model_name: str) -> ModelError:
    """
    将各种模型相关的异常转换为 ModelError / Convert various model-related exceptions to ModelError.

    Args:
        original_error: 原始捕获的异常 / Original caught exception
        model_name: 模型名称 / Model name

    Returns:
        ModelError 实例 / ModelError instance
    """
    # 构建错误类型字符串 / Build error type string
    error_type = f"{type(original_error).__name__}: {str(original_error)}"
    return ModelError(model_name, error_type)


def log_and_reraise(logger_instance: logging.Logger, error: Exception,
                   context: str = "", reraise: bool = True) -> Optional[Exception]:
    """
    记录错误并可选地重新抛出增强的异常 / Log error and optionally re-raise with enhanced context.

    这个函数提供统一的错误记录和处理机制。
    This function provides a unified error logging and handling mechanism.

    Args:
        logger_instance: 日志记录器实例 / Logger instance
        error: 要处理的异常 / Exception to handle
        context: 错误上下文描述 / Error context description
        reraise: 是否重新抛出异常 / Whether to re-raise the exception

    Returns:
        如果不重新抛出，返回处理后的异常；否则返回 None
        Processed exception if not re-raising, None otherwise

    Raises:
        如果 reraise=True，重新抛出增强的异常
        Re-raises enhanced exception if reraise=True
    """
    # 步骤 1: 记录错误到日志 / Log error
    if context:
        logger_instance.error(f"Error in {context}: {error}")
    else:
        logger_instance.error(f"Error: {error}")

    # 步骤 2: 处理已知的 ProjectAnalyzerError
    # Handle known ProjectAnalyzerError
    if isinstance(error, ProjectAnalyzerError):
        # 已经被记录和增强 / Already logged and enhanced
        if reraise:
            raise error
        return error

    # 步骤 3: 包装未知错误 / Wrap unknown errors
    else:
        # 创建增强的错误实例 / Create enhanced error instance
        enhanced_error = ProjectAnalyzerError(
            f"{type(error).__name__}: {str(error)}",
            details={'original_type': type(error).__name__, 'context': context}
        )

        if reraise:
            raise enhanced_error from error  # 保留原始异常链 / Preserve original exception chain
        return enhanced_error


# ============================================================================
# 文件结束 / End of File
# ============================================================================

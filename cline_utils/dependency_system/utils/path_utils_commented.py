# cline_utils/dependency_system/utils/path_utils.py
# 路径工具模块 - Path Utilities Module

"""
Core module for path utilities.
Handles path normalization, validation, and comparison.

核心路径工具模块
处理路径标准化、验证和比较
"""

# ==================== 导入依赖模块 - Import Dependencies ====================
import fnmatch  # Unix shell 风格路径名匹配 - Unix shell-style pathname matching
import logging  # 日志记录 - Logging functionality
import os  # 操作系统接口 - Operating system interface
import re  # 正则表达式 - Regular expressions
from typing import List  # 类型提示：列表 - Type hint: List

# ==================== 日志配置 - Logger Configuration ====================
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器 - Get logger for current module


# ==================== 路径标准化函数 - Path Normalization Function ====================
def normalize_path(path: str) -> str:
    """
    Normalize a file path for consistent comparison.
    标准化文件路径以便进行一致的比较

    处理步骤 - Processing Steps:
    1. 将路径转换为绝对路径 - Convert to absolute path
    2. 标准化路径分隔符 - Normalize path separators
    3. 处理Windows驱动器字母大小写 - Handle Windows drive letter case
    4. 移除尾部斜杠 - Remove trailing slashes

    Args:
        path: 要标准化的路径 - Path to normalize

    Returns:
        str: 标准化后的路径 - Normalized path
    """
    # ========== 步骤1: 导入缓存装饰器 - Import Cache Decorator ==========
    from .cache_manager import cached  # 导入缓存管理器 - Import cache manager

    # ========== 步骤2: 定义带缓存的内部函数 - Define Cached Internal Function ==========
    @cached(
        "path_normalization",  # 缓存名称 - Cache name
        key_func=lambda p: f"normalize:{p if p else 'empty'}",  # 缓存键生成函数 - Cache key function
    )
    def _normalize_path(p: str) -> str:
        """
        内部标准化函数（带缓存）- Internal normalization function (with cache)

        Args:
            p: 待处理路径 - Path to process

        Returns:
            str: 标准化后的路径 - Normalized path
        """
        # ========== 情况1: 空路径处理 - Empty Path Handling ==========
        if not p:
            return ""  # 空路径返回空字符串 - Return empty string for empty path

        # ========== 步骤3: 转换为绝对路径 - Convert to Absolute Path ==========
        # 如果不是绝对路径，基于当前工作目录转换 - If not absolute, convert based on CWD
        if not os.path.isabs(p):
            p = os.path.abspath(p)  # 获取绝对路径 - Get absolute path

        # ========== 步骤4: 标准化路径格式 - Normalize Path Format ==========
        normalized = os.path.normpath(p).replace("\\", "/")  # 标准化路径，统一使用正斜杠 - Normalize path, use forward slashes
        # normpath: 折叠多余的分隔符和上级引用 - Collapse redundant separators and up-level references
        # replace: 将反斜杠转换为正斜杠（Windows兼容）- Convert backslashes to forward slashes (Windows compatibility)

        # ========== 步骤5: Windows驱动器字母小写化 - Lowercase Windows Drive Letter ==========
        if os.name == "nt" and re.match(r"^[a-zA-Z]:", normalized):
            # 检查是否为Windows系统且路径以驱动器字母开头 - Check if Windows and path starts with drive letter
            normalized = normalized[0].lower() + normalized[1:]  # 将驱动器字母转换为小写 - Convert drive letter to lowercase
            # 例如：C:/path -> c:/path - e.g., C:/path -> c:/path

        # ========== 步骤6: 移除尾部斜杠 - Remove Trailing Slash ==========
        # 除非路径就是根目录 - Unless the path is the root directory
        if len(normalized) > 1 and normalized.endswith("/"):
            # Unix风格路径：移除尾部斜杠 - Unix-style path: remove trailing slash
            normalized = normalized.rstrip("/")  # 去除右侧的斜杠 - Strip slashes from right
        elif (
            os.name == "nt" and len(normalized) > 3 and normalized.endswith("/")
        ):  # Windows风格：C:/ - Windows-style: C:/
            normalized = normalized.rstrip("/")  # 去除尾部斜杠 - Strip trailing slash

        # ========== 步骤7: 返回标准化路径 - Return Normalized Path ==========
        return normalized

    # ========== 步骤8: 调用内部函数并返回 - Call Internal Function and Return ==========
    return _normalize_path(path)


# ==================== 文件类型判断函数 - File Type Detection Function ====================
def get_file_type(file_path: str) -> str:
    """
    Determines the file type based on its extension.
    根据文件扩展名判断文件类型

    支持的文件类型 - Supported File Types:
    - py: Python源文件 - Python source files
    - js/ts/jsx/tsx: JavaScript/TypeScript文件 - JavaScript/TypeScript files
    - md/rst: 文档文件 - Documentation files
    - html/htm: HTML文件 - HTML files
    - css: 样式表文件 - Stylesheet files
    - svelte: Svelte组件 - Svelte components
    - sql: SQL脚本 - SQL scripts
    - yaml/yml: YAML配置 - YAML configurations
    - json: JSON数据 - JSON data
    - txt: 文本文件 - Text files
    - generic: 其他类型 - Other types

    Args:
        file_path: 文件路径 - The path to the file

    Returns:
        str: 文件类型标识 - The file type as a string
    """

    def _get_file_type(fp: str) -> str:
        """
        内部文件类型判断函数 - Internal file type detection function

        Args:
            fp: 文件路径 - File path

        Returns:
            str: 文件类型 - File type
        """
        # ========== 步骤1: 提取文件扩展名 - Extract File Extension ==========
        _, ext = os.path.splitext(fp)  # 分离路径和扩展名 - Split path and extension
        # splitext: 返回(主文件名, 扩展名) - Returns (filename, extension)
        ext = ext.lower()  # 转换为小写以便比较 - Convert to lowercase for comparison

        # ========== 步骤2: 根据扩展名返回类型 - Return Type Based on Extension ==========
        # Python文件 - Python files
        if ext == ".py":
            return "py"

        # JavaScript/TypeScript文件 - JavaScript/TypeScript files
        elif ext in (".js", ".ts", ".jsx", ".tsx"):
            return "js"

        # 文档文件 - Documentation files
        elif ext in (".md", ".rst"):
            return "md"

        # HTML文件 - HTML files
        elif ext in (".html", ".htm"):
            return "html"

        # CSS样式表 - CSS stylesheets
        elif ext == ".css":
            return "css"

        # Svelte组件 - Svelte components
        elif ext == ".svelte":
            return "svelte"

        # SQL脚本 - SQL scripts
        elif ext == ".sql":
            return "sql"

        # YAML配置文件 - YAML configuration files
        elif ext in (".yaml", ".yml"):
            return "yaml"

        # JSON数据文件 - JSON data files
        elif ext == ".json":
            return "json"

        # 文本文件 - Text files
        elif ext == ".txt":
            return "txt"

        # 默认：通用类型 - Default: generic type
        else:
            return "generic"

    # ========== 步骤3: 调用内部函数 - Call Internal Function ==========
    return _get_file_type(file_path)


# ==================== 相对路径解析函数 - Relative Path Resolution Function ====================
def resolve_relative_path(
    source_dir: str, relative_path: str, default_extension: str = ".js"
) -> str:
    """
    Resolve a relative import path to an absolute path based on the source directory.
    基于源目录将相对导入路径解析为绝对路径

    用途 - Purpose:
    - 处理相对导入（如 './module' 或 '../utils'）- Handle relative imports
    - 添加默认扩展名（如果缺少）- Add default extension if missing
    - 返回标准化的绝对路径 - Return normalized absolute path

    Args:
        source_dir: 源文件所在目录 - The directory of the source file
        relative_path: 相对导入路径 - The relative import path
        default_extension: 默认文件扩展名 - The file extension to append if none is present

    Returns:
        str: 解析后的绝对路径 - The resolved absolute path

    示例 - Example:
        source_dir = 'h:/project/src'
        relative_path = './module3'
        result = 'h:/project/src/module3.js'
    """
    # ========== 步骤1: 合并源目录和相对路径 - Combine Source Directory and Relative Path ==========
    resolved = os.path.normpath(os.path.join(source_dir, relative_path))
    # join: 连接路径组件 - Join path components
    # normpath: 标准化路径（处理 .. 和 .）- Normalize path (handle .. and .)

    # ========== 步骤2: 添加默认扩展名（如果缺少）- Add Default Extension (if missing) ==========
    if not os.path.splitext(resolved)[1]:
        # splitext返回(文件名, 扩展名)，[1]是扩展名 - splitext returns (name, ext), [1] is extension
        resolved += default_extension  # 添加默认扩展名 - Append default extension

    # ========== 步骤3: 标准化并返回 - Normalize and Return ==========
    return normalize_path(resolved)  # 使用标准化函数处理 - Process with normalize function


# ==================== 获取相对路径函数 - Get Relative Path Function ====================
def get_relative_path(path: str, base_path: str) -> str:
    """
    Get a path relative to a base path.
    获取相对于基准路径的相对路径

    Args:
        path: 要转换的路径 - Path to convert
        base_path: 基准路径 - Base path to make relative to

    Returns:
        str: 相对路径 - Relative path

    示例 - Example:
        path = 'c:/project/src/file.py'
        base_path = 'c:/project'
        result = 'src/file.py'
    """
    # ========== 步骤1: 标准化输入路径 - Normalize Input Paths ==========
    norm_path = normalize_path(path)  # 标准化目标路径 - Normalize target path
    norm_base = normalize_path(base_path)  # 标准化基准路径 - Normalize base path

    # ========== 步骤2: 计算相对路径 - Calculate Relative Path ==========
    try:
        # 使用os.path.relpath计算相对路径 - Use os.path.relpath to calculate relative path
        return os.path.relpath(norm_path, norm_base).replace(
            "\\", "/"
        )  # 统一使用正斜杠 - Ensure forward slashes
    except ValueError:
        # ValueError: 不同驱动器（Windows）- Different drives (Windows)
        return norm_path  # 返回标准化的绝对路径 - Return normalized absolute path


# ==================== 获取项目根目录函数 - Get Project Root Function ====================
def get_project_root() -> str:
    """
    Find the project root directory.
    查找项目根目录

    查找策略 - Search Strategy:
    1. 从当前目录开始向上查找 - Start from current directory and search upward
    2. 寻找根目录标识文件 - Look for root indicator files
    3. 如果找不到，返回当前工作目录 - If not found, return current working directory

    Returns:
        str: 项目根目录路径 - Path to the project root directory
    """
    # ========== 步骤1: 导入缓存装饰器 - Import Cache Decorator ==========
    from .cache_manager import cached

    # ========== 步骤2: 定义带缓存的内部函数 - Define Cached Internal Function ==========
    @cached(
        "project_root",  # 缓存名称 - Cache name
        key_func=lambda: f"project_root:{normalize_path(os.getcwd())}",  # 缓存键依赖于当前工作目录 - Cache key depends on CWD
    )
    def _get_project_root() -> str:
        """
        内部项目根目录查找函数（带缓存）- Internal project root finder (with cache)

        Returns:
            str: 项目根目录路径 - Project root directory path
        """
        # ========== 步骤1: 获取当前目录 - Get Current Directory ==========
        current_dir = os.path.abspath(os.getcwd())  # 获取当前工作目录的绝对路径 - Get absolute path of CWD

        # ========== 步骤2: 定义根目录标识符 - Define Root Indicators ==========
        root_indicators = ["project_root.cfg"]  # 根目录标识文件列表 - Root indicator file list
        # 可以添加更多标识，如 .git, package.json 等 - Can add more indicators like .git, package.json

        # ========== 步骤3: 向上遍历目录树 - Traverse Directory Tree Upward ==========
        while True:
            # 遍历每个根目录标识符 - Iterate through each root indicator
            for indicator in root_indicators:
                # 检查当前目录是否包含标识文件 - Check if current directory contains indicator file
                if os.path.exists(os.path.join(current_dir, indicator)):
                    return normalize_path(current_dir)  # 找到根目录，返回标准化路径 - Found root, return normalized path

            # ========== 步骤4: 移动到父目录 - Move to Parent Directory ==========
            parent_dir = os.path.dirname(current_dir)  # 获取父目录 - Get parent directory

            # ========== 步骤5: 检查是否到达文件系统根 - Check if Reached Filesystem Root ==========
            if parent_dir == current_dir:  # 父目录等于当前目录意味着已到根 - Parent equals current means root reached
                break  # 退出循环 - Break loop

            current_dir = parent_dir  # 更新当前目录为父目录 - Update current to parent

        # ========== 步骤6: 未找到标识符，返回当前工作目录 - No Indicator Found, Return CWD ==========
        return normalize_path(os.path.abspath(os.getcwd()))  # 返回标准化的当前工作目录 - Return normalized CWD

    # ========== 步骤3: 调用内部函数 - Call Internal Function ==========
    return _get_project_root()


# ==================== 路径连接函数 - Join Paths Function ====================
def join_paths(base_path: str, *paths: str) -> str:
    """
    Join paths and normalize the result.
    连接路径并标准化结果

    Args:
        base_path: 基础路径 - Base path
        *paths: 额外的路径组件 - Additional path components

    Returns:
        str: 连接并标准化后的路径 - Joined and normalized path

    示例 - Example:
        base_path = 'c:/project'
        paths = ('src', 'utils', 'file.py')
        result = 'c:/project/src/utils/file.py'
    """
    # ========== 步骤1: 连接路径 - Join Paths ==========
    joined = os.path.join(base_path, *paths)  # 使用os.path.join连接所有路径组件 - Join all path components

    # ========== 步骤2: 标准化并返回 - Normalize and Return ==========
    return normalize_path(joined)  # 标准化连接后的路径 - Normalize joined path


# ==================== 路径排除检查函数 - Path Exclusion Check Function ====================
def is_path_excluded(path: str, excluded_paths: List[str]) -> bool:
    """
    Check if a path should be excluded based on a list of exclusion patterns.
    基于排除模式列表检查路径是否应被排除

    支持两种模式 - Supports Two Modes:
    1. 通配符模式（*, ?）- Wildcard patterns (*, ?)
    2. 精确路径或子路径匹配 - Exact path or subpath matching

    Args:
        path: 要检查的路径 - Path to check
        excluded_paths: 排除模式列表 - List of exclusion patterns

    Returns:
        bool: 如果路径应被排除返回True - True if the path should be excluded

    示例 - Example:
        path = 'c:/project/node_modules/lib.js'
        excluded_paths = ['*/node_modules/*', 'c:/project/temp']
        result = True (匹配通配符模式)
    """
    # ========== 步骤1: 空列表快速返回 - Quick Return for Empty List ==========
    if not excluded_paths:
        return False  # 没有排除规则，不排除 - No exclusion rules, don't exclude

    # ========== 步骤2: 标准化输入路径 - Normalize Input Path ==========
    norm_path = normalize_path(path)  # 标准化待检查路径 - Normalize path to check

    # ========== 步骤3: 遍历排除模式 - Iterate Through Exclusion Patterns ==========
    for excluded in excluded_paths:
        # ========== 步骤3.1: 标准化排除模式 - Normalize Exclusion Pattern ==========
        norm_excluded = normalize_path(excluded)  # 标准化排除模式/路径 - Normalize exclusion pattern/path

        # ========== 步骤3.2: 检查是否为通配符模式 - Check if Wildcard Pattern ==========
        if "*" in norm_excluded or "?" in norm_excluded:
            # 使用fnmatch进行通配符匹配 - Use fnmatch for wildcard matching
            # *: 匹配任意字符 - Matches any characters
            # ?: 匹配单个字符 - Matches single character
            if fnmatch.fnmatch(norm_path, norm_excluded):
                return True  # 匹配通配符模式，排除 - Matches wildcard, exclude

        # ========== 步骤3.3: 精确匹配或子路径匹配 - Exact Match or Subpath Match ==========
        elif norm_path == norm_excluded or is_subpath(norm_path, norm_excluded):
            return True  # 精确匹配或是子路径，排除 - Exact match or subpath, exclude

    # ========== 步骤4: 不匹配任何排除规则 - No Match for Any Exclusion Rule ==========
    return False  # 不排除 - Don't exclude


# ==================== 子路径检查函数 - Subpath Check Function ====================
def is_subpath(path: str, parent_path: str) -> bool:
    """
    Check if a path is a subpath of another path.
    检查一个路径是否是另一个路径的子路径

    Args:
        path: 要检查的路径 - Path to check
        parent_path: 潜在的父路径 - Potential parent path

    Returns:
        bool: 如果path是parent_path的子路径返回True - True if path is a subpath of parent_path

    示例 - Example:
        path = 'c:/project/src/file.py'
        parent_path = 'c:/project/src'
        result = True
    """
    # ========== 步骤1: 标准化两个路径 - Normalize Both Paths ==========
    norm_path = normalize_path(path)  # 标准化待检查路径 - Normalize path to check
    norm_parent = normalize_path(parent_path)  # 标准化父路径 - Normalize parent path

    # ========== 步骤2: 边界情况检查 - Edge Case Checks ==========
    # 确保父路径非空且路径不相同 - Ensure parent is not empty and paths are not identical
    if not norm_parent or norm_path == norm_parent:
        return False  # 父路径为空或路径相同，不是子路径 - Parent empty or paths same, not subpath

    # ========== 步骤3: 添加路径分隔符 - Append Path Separator ==========
    parent_with_sep = norm_parent + "/"  # 添加分隔符确保匹配完整目录名 - Add separator to ensure matching whole directory names
    # 例如：避免 'c:/project1' 匹配 'c:/project' - e.g., prevent 'c:/project1' from matching 'c:/project'

    # ========== 步骤4: 检查是否以父路径开头 - Check if Starts with Parent Path ==========
    return norm_path.startswith(parent_with_sep)  # 检查是否以父路径+分隔符开头 - Check if starts with parent+separator


# ==================== 获取公共路径前缀函数 - Get Common Path Prefix Function ====================
def get_common_path(paths: List[str]) -> str:
    """
    Find the common path prefix for a list of paths.
    查找路径列表的公共路径前缀

    Args:
        paths: 路径列表 - List of paths

    Returns:
        str: 公共路径前缀 - Common path prefix

    示例 - Example:
        paths = ['c:/project/src/a.py', 'c:/project/src/b.py', 'c:/project/doc/readme.md']
        result = 'c:/project'
    """
    # ========== 步骤1: 空列表处理 - Empty List Handling ==========
    if not paths:
        return ""  # 空列表返回空字符串 - Empty list returns empty string

    # ========== 步骤2: 标准化所有路径 - Normalize All Paths ==========
    norm_paths = [normalize_path(p) for p in paths]  # 列表推导式标准化每个路径 - List comprehension to normalize each path

    # ========== 步骤3: 计算公共路径 - Calculate Common Path ==========
    try:
        # os.path.commonpath: 找到最长公共子路径 - Find longest common sub-path
        return normalize_path(os.path.commonpath(norm_paths))  # 标准化公共路径 - Normalize common path
    except ValueError:
        # ValueError: 不同驱动器（Windows）或无公共路径 - Different drives (Windows) or no common path
        return ""  # 返回空字符串 - Return empty string


# ==================== 验证项目路径函数 - Validate Project Path Function ====================
def is_valid_project_path(path: str) -> bool:
    """
    Check if a path is within the project root directory.
    检查路径是否在项目根目录内

    Args:
        path: 要检查的路径 - Path to check

    Returns:
        bool: 如果路径在项目根目录内返回True - True if the path is within the project root

    用途 - Purpose:
    - 确保只处理项目内的文件 - Ensure only processing files within project
    - 防止访问项目外的敏感文件 - Prevent access to sensitive files outside project
    """
    # ========== 步骤1: 导入缓存装饰器 - Import Cache Decorator ==========
    from .cache_manager import cached

    # ========== 步骤2: 定义带缓存的内部函数 - Define Cached Internal Function ==========
    @cached(
        "valid_project_paths",  # 缓存名称 - Cache name
        key_func=lambda p: f"valid_project_path:{normalize_path(p)}:{get_project_root()}",  # 缓存键依赖于路径和项目根 - Cache key depends on path and project root
    )
    def _is_valid_project_path(p: str) -> bool:
        """
        内部路径验证函数（带缓存）- Internal path validation function (with cache)

        Args:
            p: 待验证路径 - Path to validate

        Returns:
            bool: 路径是否有效 - Whether path is valid
        """
        # ========== 步骤1: 获取项目根目录 - Get Project Root ==========
        project_root = get_project_root()  # 获取项目根目录路径 - Get project root path

        # ========== 步骤2: 标准化输入路径 - Normalize Input Path ==========
        norm_p = normalize_path(p)  # 标准化待验证路径 - Normalize path to validate

        # ========== 步骤3: 检查路径是否在项目根内 - Check if Path is Within Project Root ==========
        # 两种情况：1. 路径等于根目录  2. 路径以"根目录/"开头 - Two cases: 1. Path equals root  2. Path starts with "root/"
        return norm_p == project_root or norm_p.startswith(project_root + "/")

    # ========== 步骤3: 调用内部函数 - Call Internal Function ==========
    return _is_valid_project_path(path)


# ==================== 文件结束标记 - End of File Marker ====================
# EoF

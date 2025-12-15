# =============================================================================
# io/update_doc_tracker.py
# =============================================================================
"""
文档追踪器更新模块 (Documentation Tracker Update Module)
========================================================

功能概述 (Overview):
    本模块负责管理文档追踪器(doc tracker)的特定数据和行为，使用上下文键(contextual keys)
    来跟踪和管理项目中的文档文件。

主要功能 (Main Features):
    1. 文档文件包含逻辑 - 根据配置的文档目录过滤文件
    2. 追踪器路径管理 - 获取文档追踪器文件的存储路径
    3. 数据结构导出 - 提供标准化的追踪器数据接口

依赖关系 (Dependencies):
    - core.key_manager: KeyInfo类，用于管理路径和键的映射关系
    - utils.config_manager: 配置管理器，读取项目配置
    - utils.path_utils: 路径工具函数，用于路径规范化和验证

作者 (Author): Cline Dependency System
版本 (Version): 8.0.0
"""

# =============================================================================
# 标准库导入 (Standard Library Imports)
# =============================================================================
import logging  # 日志记录模块
import os  # 操作系统接口模块，用于路径操作
from typing import Dict, List  # 类型提示：字典和列表类型

# =============================================================================
# 第三方库导入 (Third-party Library Imports)
# =============================================================================
# 无第三方库依赖

# =============================================================================
# 本地模块导入 (Local Module Imports)
# =============================================================================

# --- 核心模块 (Core Modules) ---
from cline_utils.dependency_system.core.key_manager import KeyInfo
# KeyInfo类用于存储路径与键字符串的映射关系，以及是否为目录的信息

# --- 工具模块 (Utility Modules) ---
from cline_utils.dependency_system.utils.config_manager import ConfigManager
# ConfigManager用于读取.clinerules配置文件中的设置

from cline_utils.dependency_system.utils.path_utils import (
    is_subpath,      # 判断一个路径是否为另一个路径的子路径
    join_paths,      # 安全地连接路径组件
    normalize_path,  # 规范化路径格式（处理斜杠、相对路径等）
)

# =============================================================================
# 日志配置 (Logger Configuration)
# =============================================================================
logger = logging.getLogger(__name__)  # 创建模块级别的日志记录器


# =============================================================================
# 文档文件包含逻辑 (Document File Inclusion Logic)
# =============================================================================

def doc_file_inclusion_logic(
    project_root: str, path_to_key_info: Dict[str, KeyInfo]
) -> Dict[str, KeyInfo]:
    """
    文档文件包含逻辑函数 (Document File Inclusion Logic Function)
    ===========================================================

    功能说明 (Description):
        根据配置的文档目录，确定哪些文件/目录（由KeyInfo表示）应该包含在文档追踪器中。
        该函数会过滤出所有位于配置的文档根目录下的项目。

    参数 (Args):
        project_root (str): 项目根目录的绝对路径
        path_to_key_info (Dict[str, KeyInfo]): 全局映射表，从规范化路径映射到KeyInfo对象
            - 键：规范化的文件/目录路径（字符串）
            - 值：对应的KeyInfo对象，包含key_string和is_directory属性

    返回值 (Returns):
        Dict[str, KeyInfo]: 过滤后的字典，映射每个被过滤项的规范化路径到其对应的KeyInfo对象
            - 键：规范化的路径（字符串）
            - 值：KeyInfo对象

    示例 (Example):
        >>> project_root = "/home/user/project"
        >>> path_to_key_info = {
        ...     "/home/user/project/docs/api.md": KeyInfo("docs/api.md", False),
        ...     "/home/user/project/src/main.py": KeyInfo("src/main.py", False)
        ... }
        >>> filtered = doc_file_inclusion_logic(project_root, path_to_key_info)
        >>> # 返回只包含docs目录下文件的字典

    工作流程 (Workflow):
        1. 从配置中读取文档目录列表
        2. 将相对路径转换为绝对路径并规范化
        3. 遍历所有KeyInfo对象
        4. 检查每个路径是否在文档根目录下
        5. 过滤并返回符合条件的项目
    """

    # -------------------------------------------------------------------------
    # 步骤1: 初始化配置管理器 (Step 1: Initialize Configuration Manager)
    # -------------------------------------------------------------------------
    config_manager = ConfigManager()  # 创建配置管理器实例，用于读取项目配置

    # -------------------------------------------------------------------------
    # 步骤2: 获取文档目录配置 (Step 2: Get Documentation Directories)
    # -------------------------------------------------------------------------
    # 从配置文件中获取文档目录的相对路径列表
    # 例如：["docs", "documentation", "README.md"]
    doc_directories_rel: List[str] = config_manager.get_doc_directories()

    # -------------------------------------------------------------------------
    # 步骤3: 初始化过滤结果容器 (Step 3: Initialize Filtered Results)
    # -------------------------------------------------------------------------
    # 创建空字典，用于存储过滤后的结果
    # 键：规范化的路径（字符串）
    # 值：对应的KeyInfo对象
    filtered_items: Dict[str, KeyInfo] = {}

    # -------------------------------------------------------------------------
    # 步骤4: 转换为绝对路径 (Step 4: Convert to Absolute Paths)
    # -------------------------------------------------------------------------
    # 将配置中的相对路径转换为绝对路径并规范化
    # 例如："docs" -> "/home/user/project/docs"
    abs_doc_roots: List[str] = [
        normalize_path(os.path.join(project_root, p))  # 连接项目根路径和相对路径，然后规范化
        for p in doc_directories_rel  # 遍历所有配置的文档目录
    ]

    # -------------------------------------------------------------------------
    # 步骤5: 验证配置有效性 (Step 5: Validate Configuration)
    # -------------------------------------------------------------------------
    # 检查是否配置了文档目录
    if not abs_doc_roots:
        # 如果没有配置任何文档目录，记录警告并返回空字典
        logger.warning(
            "No documentation directories configured for doc tracker filtering."
        )
        return {}  # 返回空字典，表示没有文件需要追踪

    # -------------------------------------------------------------------------
    # 步骤6: 遍历并过滤KeyInfo对象 (Step 6: Iterate and Filter KeyInfo)
    # -------------------------------------------------------------------------
    # 遍历全局路径到KeyInfo的映射表
    for norm_path, key_info in path_to_key_info.items():
        # norm_path: 当前迭代的规范化路径
        # key_info: 对应的KeyInfo对象

        # 检查当前路径是否等于或位于任何配置的文档根目录下
        if any(
            # 条件1: 路径完全等于文档根目录
            norm_path == doc_root or
            # 条件2: 路径是文档根目录的子路径
            is_subpath(norm_path, doc_root)
            for doc_root in abs_doc_roots  # 遍历所有文档根目录
        ):
            # 如果满足条件，将该项添加到过滤结果中
            filtered_items[norm_path] = key_info  # 键：路径，值：KeyInfo对象

    # -------------------------------------------------------------------------
    # 步骤7: 记录过滤结果 (Step 7: Log Filtering Results)
    # -------------------------------------------------------------------------
    # 记录过滤后选中的项目数量
    logger.info(f"Doc tracker filter selected {len(filtered_items)} items.")

    # -------------------------------------------------------------------------
    # 步骤8: 返回过滤结果 (Step 8: Return Filtered Results)
    # -------------------------------------------------------------------------
    return filtered_items  # 返回包含所有符合条件的路径和KeyInfo的字典


# =============================================================================
# 文档追踪器路径获取 (Doc Tracker Path Retrieval)
# =============================================================================

def get_doc_tracker_path(project_root: str) -> str:
    """
    获取文档追踪器文件路径 (Get Doc Tracker File Path)
    ================================================

    功能说明 (Description):
        获取文档追踪器文件(doc_tracker.md)的完整绝对路径。
        该路径由配置的内存目录和追踪器文件名组成。

    参数 (Args):
        project_root (str): 项目根目录的绝对路径

    返回值 (Returns):
        str: 文档追踪器文件的完整绝对路径
            例如："/home/user/project/cline_docs/memory/doc_tracker.md"

    示例 (Example):
        >>> project_root = "/home/user/project"
        >>> tracker_path = get_doc_tracker_path(project_root)
        >>> print(tracker_path)
        /home/user/project/cline_docs/memory/doc_tracker.md

    配置选项 (Configuration):
        - memory_dir: 内存目录的相对路径（默认："cline_docs/memory"）
        - doc_tracker_filename: 追踪器文件名（默认："doc_tracker.md"）

    工作流程 (Workflow):
        1. 读取配置中的内存目录路径
        2. 构建内存目录的绝对路径
        3. 读取配置中的追踪器文件名
        4. 组合生成完整的追踪器文件路径
    """

    # -------------------------------------------------------------------------
    # 步骤1: 初始化配置管理器 (Step 1: Initialize Config Manager)
    # -------------------------------------------------------------------------
    config_manager = ConfigManager()  # 创建配置管理器实例

    # -------------------------------------------------------------------------
    # 步骤2: 获取内存目录相对路径 (Step 2: Get Memory Directory Path)
    # -------------------------------------------------------------------------
    # 从配置中获取内存目录的相对路径
    # 默认值："cline_docs/memory"
    # 可以在.clinerules配置文件中覆盖此设置
    memory_dir_rel = config_manager.get_path("memory_dir", "cline_docs/memory")

    # -------------------------------------------------------------------------
    # 步骤3: 构建内存目录绝对路径 (Step 3: Build Absolute Memory Dir Path)
    # -------------------------------------------------------------------------
    # 将项目根路径和相对路径组合，生成内存目录的绝对路径
    memory_dir_abs = join_paths(project_root, memory_dir_rel)

    # -------------------------------------------------------------------------
    # 步骤4: 获取追踪器文件名 (Step 4: Get Tracker Filename)
    # -------------------------------------------------------------------------
    # 从配置中获取文档追踪器的文件名
    # 默认值："doc_tracker.md"
    # 可以在.clinerules配置文件的[paths]部分自定义
    tracker_filename = config_manager.get_path("doc_tracker_filename", "doc_tracker.md")

    # 确保获取的只是文件名，而不是可能包含路径的字符串
    # 这可以防止配置错误导致的路径问题
    tracker_filename = os.path.basename(tracker_filename)

    # -------------------------------------------------------------------------
    # 步骤5: 组合生成完整路径 (Step 5: Combine to Full Path)
    # -------------------------------------------------------------------------
    # 将内存目录绝对路径和追踪器文件名组合
    # 例如："/project/cline_docs/memory" + "doc_tracker.md"
    #       -> "/project/cline_docs/memory/doc_tracker.md"
    return join_paths(memory_dir_abs, tracker_filename)


# =============================================================================
# 数据结构导出 (Data Structure Export)
# =============================================================================

# 文档追踪器数据结构 (Doc Tracker Data Structure)
# ------------------------------------------------
# 此字典定义了文档追踪器的核心行为和配置
# 被tracker_io模块导入和使用，用于更新文档追踪器

doc_tracker_data = {
    # --- 文件包含逻辑 (File Inclusion Logic) ---
    # 定义哪些文件应该被包含在文档追踪器中
    # 函数签名：(project_root: str, path_to_key_info: Dict[str, KeyInfo]) -> Dict[str, KeyInfo]
    # 输入：项目根路径和全局路径到KeyInfo的映射
    # 输出：过滤后的路径到KeyInfo的映射
    "file_inclusion": doc_file_inclusion_logic,

    # --- 追踪器路径获取 (Tracker Path Getter) ---
    # 返回文档追踪器文件的存储路径
    # 函数签名：(project_root: str) -> str
    # 输入：项目根路径
    # 输出：追踪器文件的完整路径
    "get_tracker_path": get_doc_tracker_path,
}

# =============================================================================
# 文件结束 (End of File)
# =============================================================================

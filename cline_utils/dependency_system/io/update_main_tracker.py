# =============================================================================
# io/update_main_tracker.py
# =============================================================================
"""
主追踪器更新模块 (Main Tracker Update Module)
============================================

功能概述 (Overview):
    本模块负责管理主追踪器(main tracker)的特定数据，包括键过滤和依赖聚合逻辑。
    使用上下文键(contextual keys)来管理模块间的依赖关系。

主要功能 (Main Features):
    1. 模块键过滤 - 确定哪些模块应该包含在主追踪器中
    2. 依赖聚合 - 从迷你追踪器聚合依赖关系到主追踪器
    3. 层级回滚 - 将子模块的依赖关系传递给父模块
    4. 路径管理 - 获取主追踪器文件的存储路径

核心概念 (Core Concepts):
    - 主追踪器：跟踪模块级别（目录）之间的依赖关系
    - 迷你追踪器：跟踪单个模块内部文件之间的依赖关系
    - 依赖聚合：将文件级别的依赖关系汇总为模块级别的依赖关系
    - 层级回滚：父模块继承子模块的外部依赖关系

依赖关系 (Dependencies):
    - core.dependency_grid: 依赖网格的压缩/解压缩功能
    - core.key_manager: 键管理和排序功能
    - utils.path_utils: 路径操作工具函数
    - utils.config_manager: 配置管理器
    - utils.tracker_utils: 追踪器文件读取工具

作者 (Author): Cline Dependency System
版本 (Version): 8.0.0
"""

# =============================================================================
# 标准库导入 (Standard Library Imports)
# =============================================================================
import os  # 操作系统接口模块，用于路径操作
import logging  # 日志记录模块
from collections import defaultdict  # 默认字典，用于简化嵌套字典操作
from typing import Dict, List, Optional, Set, Tuple  # 类型提示

# =============================================================================
# 本地模块导入 (Local Module Imports)
# =============================================================================

# --- 核心模块 (Core Modules) ---
from cline_utils.dependency_system.core.dependency_grid import (
    decompress,         # 解压缩依赖网格行数据
    PLACEHOLDER_CHAR,   # 占位符字符（通常为'.'）
    DIAGONAL_CHAR       # 对角线字符（通常为'/'）
)
from cline_utils.dependency_system.core.key_manager import (
    KeyInfo,                           # 键信息类，存储路径和键的映射
    sort_keys,                         # 键排序函数
    get_key_from_path,                 # 从路径获取键的函数
    sort_key_strings_hierarchically    # 层级键字符串排序函数
)

# --- 工具模块 (Utility Modules) ---
from cline_utils.dependency_system.utils.path_utils import (
    is_subpath,      # 判断是否为子路径
    normalize_path,  # 规范化路径
    join_paths,      # 安全连接路径
    get_project_root # 获取项目根目录
)
from cline_utils.dependency_system.utils.config_manager import ConfigManager
# 配置管理器，用于读取项目配置

from cline_utils.dependency_system.utils.tracker_utils import read_tracker_file_structured
# 追踪器文件结构化读取函数

# =============================================================================
# 日志配置 (Logger Configuration)
# =============================================================================
logger = logging.getLogger(__name__)  # 创建模块级别的日志记录器

# =============================================================================
# 主追踪器路径管理 (Main Tracker Path Management)
# =============================================================================

def get_main_tracker_path(project_root: str) -> str:
    """
    获取主追踪器文件路径 (Get Main Tracker File Path)
    ================================================

    功能说明 (Description):
        获取主追踪器文件(module_relationship_tracker.md)的完整绝对路径。

    参数 (Args):
        project_root (str): 项目根目录的绝对路径

    返回值 (Returns):
        str: 主追踪器文件的完整绝对路径
            例如："/project/cline_docs/memory/module_relationship_tracker.md"

    配置选项 (Configuration):
        - memory_dir: 内存目录的相对路径（默认："cline_docs/memory"）
        - main_tracker_filename: 主追踪器文件名（默认："module_relationship_tracker.md"）
    """

    # -------------------------------------------------------------------------
    # 步骤1: 初始化配置管理器 (Step 1: Initialize Config Manager)
    # -------------------------------------------------------------------------
    config_manager = ConfigManager()  # 创建配置管理器实例

    # -------------------------------------------------------------------------
    # 步骤2: 获取并构建内存目录路径 (Step 2: Get Memory Directory Path)
    # -------------------------------------------------------------------------
    # 从配置获取内存目录的相对路径，默认为"cline_docs/memory"
    memory_dir_rel = config_manager.get_path("memory_dir", "cline_docs/memory")
    # 构建内存目录的绝对路径
    memory_dir_abs = join_paths(project_root, memory_dir_rel)

    # -------------------------------------------------------------------------
    # 步骤3: 获取追踪器文件名 (Step 3: Get Tracker Filename)
    # -------------------------------------------------------------------------
    # 从配置获取主追踪器文件名
    # 可以在.clinerules的[paths]部分配置'main_tracker_filename'
    tracker_filename = config_manager.get_path("main_tracker_filename", "module_relationship_tracker.md")
    # 确保只获取文件名，而不是可能包含路径的字符串
    tracker_filename = os.path.basename(tracker_filename)

    # -------------------------------------------------------------------------
    # 步骤4: 组合生成完整路径 (Step 4: Combine to Full Path)
    # -------------------------------------------------------------------------
    return join_paths(memory_dir_abs, tracker_filename)


# =============================================================================
# 模块键过滤逻辑 (Module Key Filtering Logic)
# =============================================================================

def main_key_filter(project_root: str, path_to_key_info: Dict[str, KeyInfo]) -> Dict[str, KeyInfo]:
    """
    主追踪器模块键过滤函数 (Main Tracker Module Key Filter)
    ======================================================

    功能说明 (Description):
        确定哪些模块（由KeyInfo表示的目录）应该包含在主追踪器中。
        只包含配置的代码根目录下的目录。

    参数 (Args):
        project_root (str): 项目根目录的绝对路径
        path_to_key_info (Dict[str, KeyInfo]): 全局映射表
            - 键：规范化的路径（字符串）
            - 值：对应的KeyInfo对象

    返回值 (Returns):
        Dict[str, KeyInfo]: 过滤后的模块字典
            - 键：规范化的模块路径（目录路径）
            - 值：对应的KeyInfo对象

    过滤条件 (Filter Criteria):
        1. 必须是目录（is_directory=True）
        2. 必须在配置的代码根目录内或等于代码根目录

    示例 (Example):
        >>> project_root = "/home/user/project"
        >>> path_to_key_info = {
        ...     "/home/user/project/src": KeyInfo("src", True),
        ...     "/home/user/project/src/main.py": KeyInfo("src/main.py", False)
        ... }
        >>> filtered = main_key_filter(project_root, path_to_key_info)
        >>> # 返回只包含目录的字典
    """

    # -------------------------------------------------------------------------
    # 步骤1: 初始化配置和容器 (Step 1: Initialize Config and Containers)
    # -------------------------------------------------------------------------
    config_manager = ConfigManager()  # 创建配置管理器实例
    # 从配置获取代码根目录的相对路径列表
    root_directories_rel: List[str] = config_manager.get_code_root_directories()
    # 创建空字典，用于存储过滤后的模块
    filtered_modules: Dict[str, KeyInfo] = {}

    # -------------------------------------------------------------------------
    # 步骤2: 转换为绝对路径集合 (Step 2: Convert to Absolute Paths Set)
    # -------------------------------------------------------------------------
    # 将相对路径转换为绝对路径并规范化，使用集合存储以提高查找效率
    abs_code_roots: Set[str] = {
        normalize_path(os.path.join(project_root, p))  # 连接并规范化路径
        for p in root_directories_rel  # 遍历所有配置的代码根目录
    }

    # -------------------------------------------------------------------------
    # 步骤3: 验证配置有效性 (Step 3: Validate Configuration)
    # -------------------------------------------------------------------------
    if not abs_code_roots:
        # 如果没有定义代码根目录，记录警告并返回空字典
        logger.warning("No code root directories defined for main tracker key filtering.")
        return {}

    # -------------------------------------------------------------------------
    # 步骤4: 遍历并过滤模块 (Step 4: Iterate and Filter Modules)
    # -------------------------------------------------------------------------
    # 遍历全局路径到KeyInfo的映射表
    for norm_path, key_info in path_to_key_info.items():
        # norm_path: 当前迭代的规范化路径
        # key_info: 对应的KeyInfo对象

        # 检查是否为目录
        if key_info.is_directory:
            # 检查目录是否等于或位于任何代码根目录下
            if any(
                # 条件1: 路径完全等于代码根目录
                norm_path == root_dir or
                # 条件2: 路径是代码根目录的子路径
                is_subpath(norm_path, root_dir)
                for root_dir in abs_code_roots  # 遍历所有代码根目录
            ):
                # 如果满足条件，将该模块添加到过滤结果中
                filtered_modules[norm_path] = key_info

    # -------------------------------------------------------------------------
    # 步骤5: 记录过滤结果 (Step 5: Log Filtering Results)
    # -------------------------------------------------------------------------
    logger.info(f"Main key filter selected {len(filtered_modules)} module paths for the main tracker.")

    # -------------------------------------------------------------------------
    # 步骤6: 返回过滤结果 (Step 6: Return Filtered Results)
    # -------------------------------------------------------------------------
    return filtered_modules

# =============================================================================
# 层级辅助函数 (Hierarchical Helper Functions)
# =============================================================================

def _get_descendants_paths(parent_path: str, hierarchy: Dict[str, List[str]]) -> Set[str]:
    """
    获取所有后代路径辅助函数 (Get All Descendant Paths Helper)
    =========================================================

    功能说明 (Description):
        获取给定父路径的所有后代路径（包括父路径自身）。
        使用广度优先搜索(BFS)遍历层级结构。

    参数 (Args):
        parent_path (str): 父路径（可能未规范化）
        hierarchy (Dict[str, List[str]]): 层级映射表
            - 键：父路径
            - 值：直接子路径列表

    返回值 (Returns):
        Set[str]: 包含父路径及其所有后代路径的集合

    算法 (Algorithm):
        - 使用广度优先搜索(BFS)遍历层级树
        - 使用队列存储待处理的路径
        - 使用集合避免重复处理

    示例 (Example):
        >>> hierarchy = {
        ...     "/project/src": ["/project/src/utils", "/project/src/core"],
        ...     "/project/src/utils": ["/project/src/utils/helpers"]
        ... }
        >>> descendants = _get_descendants_paths("/project/src", hierarchy)
        >>> # 返回：{"/project/src", "/project/src/utils", "/project/src/core", ...}
    """

    # -------------------------------------------------------------------------
    # 步骤1: 规范化父路径 (Step 1: Normalize Parent Path)
    # -------------------------------------------------------------------------
    # 确保路径从一开始就是规范化的，即使调用者没有保证
    norm_parent_path = normalize_path(parent_path)

    # -------------------------------------------------------------------------
    # 步骤2: 初始化结果集合 (Step 2: Initialize Result Set)
    # -------------------------------------------------------------------------
    # 创建集合，包含父路径自身（因为函数说明中提到包括self）
    descendants = {norm_parent_path}

    # -------------------------------------------------------------------------
    # 步骤3: 初始化BFS队列 (Step 3: Initialize BFS Queue)
    # -------------------------------------------------------------------------
    # 使用适当的队列/栈进行广度优先搜索(BFS)
    # 获取父路径的直接子路径，并规范化后加入队列
    queue = [normalize_path(p) for p in hierarchy.get(norm_parent_path, [])]

    # 创建已处理路径集合，避免重复处理
    processed = {norm_parent_path}

    # -------------------------------------------------------------------------
    # 步骤4: BFS遍历 (Step 4: BFS Traversal)
    # -------------------------------------------------------------------------
    while queue:  # 当队列不为空时继续循环
        # 从队列前端取出一个子路径（BFS风格）
        child_path = queue.pop(0)

        # 检查该路径是否已经处理过
        if child_path not in processed:
            # 将子路径添加到后代集合中
            descendants.add(child_path)
            # 标记为已处理
            processed.add(child_path)

            # 获取当前子路径的所有子路径（孙路径）
            # 规范化后添加到队列中，继续遍历
            grandchildren = [normalize_path(p) for p in hierarchy.get(child_path, [])]
            queue.extend(grandchildren)  # 将孙路径添加到队列末尾

    # -------------------------------------------------------------------------
    # 步骤5: 返回结果 (Step 5: Return Result)
    # -------------------------------------------------------------------------
    return descendants  # 返回包含所有后代路径的集合

# =============================================================================
# 依赖聚合逻辑 (Dependency Aggregation Logic)
# =============================================================================

def aggregate_dependencies_contextual(
    project_root: str,
    path_to_key_info: Dict[str, KeyInfo],
    filtered_modules: Dict[str, KeyInfo],
    file_to_module: Optional[Dict[str, str]] = None
) -> Dict[str, List[Tuple[str, str]]]:
    """
    上下文依赖聚合函数 (Contextual Dependency Aggregation Function)
    ==============================================================

    功能说明 (Description):
        从迷你追踪器聚合依赖关系到主追踪器，使用路径作为主要标识符，
        处理上下文键(contextual keys)，并包含层级回滚(hierarchical rollup)。

    核心概念 (Core Concepts):
        1. 依赖聚合：将文件级别的依赖关系汇总为模块级别的依赖关系
        2. 外部依赖：源文件和目标文件属于不同模块的依赖关系
        3. 层级回滚：父模块继承子模块的外部依赖关系
        4. 优先级合并：相同依赖关系保留优先级最高的依赖字符

    参数 (Args):
        project_root (str): 项目根目录的绝对路径

        path_to_key_info (Dict[str, KeyInfo]): 全局路径到KeyInfo的映射表
            - 键：规范化的路径
            - 值：KeyInfo对象

        filtered_modules (Dict[str, KeyInfo]): 主追踪器的模块映射表
            - 键：规范化的模块路径（目录路径）
            - 值：KeyInfo对象

        file_to_module (Optional[Dict[str, str]]): 文件到模块的映射表
            - 键：规范化的文件路径
            - 值：包含该文件的模块路径
            - 默认值：None（如果为None将返回空字典）

    返回值 (Returns):
        Dict[str, List[Tuple[str, str]]]: 聚合后的依赖关系字典
            - 键：源模块路径
            - 值：元组列表，每个元组包含：
                - [0]: 目标模块路径
                - [1]: 聚合后的依赖字符（如'<', '>', 'x', '='等）

    算法流程 (Algorithm Flow):
        第1步：从所有相关迷你追踪器收集直接外部依赖
        第2步：执行层级回滚，将子模块依赖传递给父模块
        第3步：转换为最终输出格式

    依赖字符优先级 (Dependency Character Priority):
        - 更高的优先级会覆盖更低的优先级
        - 相同优先级下，'<'和'>'会合并为'x'（双向依赖）
        - 优先级由ConfigManager定义

    示例 (Example):
        >>> result = aggregate_dependencies_contextual(
        ...     project_root="/project",
        ...     path_to_key_info={...},
        ...     filtered_modules={...},
        ...     file_to_module={...}
        ... )
        >>> print(result)
        {
            "/project/src/core": [
                ("/project/src/utils", "<"),
                ("/project/lib", "=")
            ]
        }

    异常处理 (Exception Handling):
        - 如果file_to_module为None，记录错误并返回空字典
        - 如果迷你追踪器读取失败，记录错误并继续处理其他追踪器
        - 如果行解压失败，记录警告并跳过该行
    """
    # =========================================================================
    # 函数初始化部分 (Function Initialization Section)
    # =========================================================================

    # -------------------------------------------------------------------------
    # 导入必要的函数 (Import Necessary Functions)
    # -------------------------------------------------------------------------
    # 动态导入get_tracker_path函数，用于获取迷你追踪器文件路径
    from cline_utils.dependency_system.io.tracker_io import get_tracker_path as get_any_tracker_path

    # -------------------------------------------------------------------------
    # 参数验证 (Parameter Validation)
    # -------------------------------------------------------------------------

    # 检查file_to_module映射是否提供
    if not file_to_module:
        # 如果没有提供文件到模块的映射，无法进行聚合
        logger.error("File-to-module mapping missing, cannot perform main tracker aggregation.")
        return {}  # 返回空字典

    # 检查是否有过滤后的模块
    if not filtered_modules:
        # 如果没有模块需要聚合，记录警告并返回空字典
        logger.warning("No module paths/keys provided for main tracker aggregation.")
        return {}  # 返回空字典

    # -------------------------------------------------------------------------
    # 初始化配置和优先级函数 (Initialize Config and Priority Function)
    # -------------------------------------------------------------------------
    config = ConfigManager()  # 创建配置管理器实例
    get_priority = config.get_char_priority  # 获取依赖字符优先级函数的引用

    # -------------------------------------------------------------------------
    # 初始化聚合依赖存储结构 (Initialize Aggregated Dependencies Storage)
    # -------------------------------------------------------------------------
    # 存储结构：module_path -> target_module_path -> (highest_priority_char, highest_priority)
    # 使用嵌套的defaultdict自动初始化新条目
    # 外层：源模块路径 -> 内层字典
    # 内层：目标模块路径 -> (依赖字符, 优先级) 元组
    # 默认值：(PLACEHOLDER_CHAR, -1) 表示无依赖
    aggregated_deps_prio = defaultdict(lambda: defaultdict(lambda: (PLACEHOLDER_CHAR, -1)))

    # 记录开始聚合的日志
    logger.info(f"Starting aggregation for {len(filtered_modules)} main tracker modules...")

    # =========================================================================
    # 第1步：从迷你追踪器收集直接外部依赖 (Step 1: Gather Direct Foreign Dependencies)
    # =========================================================================
    # 目标：遍历所有相关的迷你追踪器，提取跨模块的依赖关系

    # -------------------------------------------------------------------------
    # 初始化计数器 (Initialize Counter)
    # -------------------------------------------------------------------------
    processed_mini_trackers = 0  # 记录已处理的迷你追踪器数量

    # -------------------------------------------------------------------------
    # 遍历主追踪器中的所有模块 (Iterate Through Main Tracker Modules)
    # -------------------------------------------------------------------------
    # 遍历为主追踪器指定的模块
    for source_module_path, _ in filtered_modules.items():
        # source_module_path: 当前处理的源模块路径
        # _: KeyInfo对象（在此处不使用，用下划线表示）

        # ---------------------------------------------------------------------
        # 路径规范化 (Path Normalization)
        # ---------------------------------------------------------------------
        # filtered_modules中的路径应该已经是规范化的
        # 直接使用source_module_path，无需再次规范化
        norm_source_module_path = source_module_path

        # ---------------------------------------------------------------------
        # 获取迷你追踪器路径 (Get Mini Tracker Path)
        # ---------------------------------------------------------------------
        # 根据模块路径获取对应的迷你追踪器文件路径
        mini_tracker_path = get_any_tracker_path(
            project_root,                           # 项目根目录
            tracker_type="mini",                    # 追踪器类型：迷你追踪器
            module_path=norm_source_module_path     # 模块路径
        )

        # ---------------------------------------------------------------------
        # 检查追踪器文件是否存在 (Check Tracker File Existence)
        # ---------------------------------------------------------------------
        # 如果迷你追踪器文件不存在，跳过当前模块
        if not os.path.exists(mini_tracker_path):
            continue  # 继续处理下一个模块

        # ---------------------------------------------------------------------
        # 更新计数器 (Update Counter)
        # ---------------------------------------------------------------------
        processed_mini_trackers += 1  # 已处理的追踪器数量加1

        # ---------------------------------------------------------------------
        # 读取和处理迷你追踪器 (Read and Process Mini Tracker)
        # ---------------------------------------------------------------------
        try:
            # .................................................................
            # 读取迷你追踪器文件 (Read Mini Tracker File)
            # .................................................................
            # read_tracker_file_structured返回基于文件内容的数据，键为字符串
            mini_data = read_tracker_file_structured(mini_tracker_path)

            # .................................................................
            # 提取依赖网格和键定义 (Extract Grid and Key Definitions)
            # .................................................................
            # 获取依赖网格：{源键字符串: 压缩的依赖行}
            mini_grid = mini_data.get("grid", {})

            # 获取键定义（本地于此迷你追踪器）
            # 格式：{键字符串: 路径字符串（可能未规范化）}
            mini_keys_defined_raw = mini_data.get("keys", {})

            # .................................................................
            # 规范化键定义中的路径 (Normalize Paths in Key Definitions)
            # .................................................................
            # 规范化迷你追踪器中定义的路径，以便一致查找
            mini_keys_defined = {
                k: normalize_path(p)  # 规范化路径
                for k, p in mini_keys_defined_raw.items()  # 遍历原始键定义
            }

            # .................................................................
            # 验证网格和键定义 (Validate Grid and Keys)
            # .................................................................
            # 如果网格或键定义为空，记录调试信息并跳过
            if not mini_grid or not mini_keys_defined:
                logger.debug(f"Mini tracker {os.path.basename(mini_tracker_path)} grid/keys empty.")
                continue  # 跳过当前追踪器

            # .................................................................
            # 排序键字符串 (Sort Key Strings)
            # .................................................................
            # 获取此迷你追踪器中定义的键字符串列表并按层级排序
            mini_grid_key_strings = sort_key_strings_hierarchically(list(mini_keys_defined.keys()))
            # 注意：这里使用标准排序，通常足够保持网格一致性
            # 如果需要自然排序（如key_manager.sort_keys），需要单独的工具函数

            # .................................................................
            # 创建键字符串到索引的映射 (Create Key String to Index Mapping)
            # .................................................................
            # 建立键字符串到列索引的映射，用于解析依赖网格
            key_string_to_idx_mini = {k: i for i, k in enumerate(mini_grid_key_strings)}

            # .................................................................
            # 遍历网格行 (Iterate Through Grid Rows)
            # .................................................................
            # 使用键字符串遍历迷你追踪器网格的行（源）
            for mini_source_key_string, compressed_row in mini_grid.items():
                # mini_source_key_string: 源文件/目录的键字符串
                # compressed_row: 压缩的依赖关系行

                # .............................................................
                # 验证源键是否在索引映射中 (Validate Source Key in Index Map)
                # .............................................................
                if mini_source_key_string not in key_string_to_idx_mini:
                    continue  # 如果源键不在映射中，跳过此行

                # .............................................................
                # 获取源路径 (Get Source Path)
                # .............................................................
                # 在此迷你追踪器中查找键字符串对应的路径
                mini_source_path = mini_keys_defined.get(mini_source_key_string)
                if not mini_source_path:
                    continue  # 路径必须在本地定义，否则跳过

                # .............................................................
                # 确定源路径所属的模块 (Determine Source Module)
                # .............................................................
                # 使用全局映射表确定源路径所属的模块
                # mini_source_path应该已经从mini_keys_defined创建时规范化
                actual_source_module_path = file_to_module.get(mini_source_path)
                if not actual_source_module_path:
                    # 如果在file_to_module映射中找不到路径，跳过
                    continue

                # .............................................................
                # 重要检查：仅聚合属于当前模块的源 (Critical Check)
                # .............................................................
                # 只有当源的模块就是此迷你追踪器代表的模块时才聚合
                if actual_source_module_path != norm_source_module_path:
                    continue  # 源不属于当前模块，跳过

                # .............................................................
                # 处理目标列（依赖关系）(Process Target Columns)
                # .............................................................
                try:
                    # 解压缩依赖行
                    decompressed_row = list(decompress(compressed_row))

                    # 验证行长度是否匹配
                    if len(decompressed_row) != len(mini_grid_key_strings):
                        logger.warning(f"Row length mismatch for '{mini_source_key_string}' in {mini_tracker_path}.")
                        continue  # 长度不匹配，跳过此行

                    # 遍历每一列（目标）
                    for col_idx, dep_char in enumerate(decompressed_row):
                        # col_idx: 列索引
                        # dep_char: 依赖字符

                        # 跳过占位符和对角线字符
                        if dep_char in (PLACEHOLDER_CHAR, DIAGONAL_CHAR):
                            continue  # 无实际依赖关系

                        # 获取目标键字符串
                        mini_target_key_string = mini_grid_key_strings[col_idx]

                        # 查找目标键字符串对应的路径
                        target_path = mini_keys_defined.get(mini_target_key_string)
                        if not target_path:
                            continue  # 目标路径必须在本地定义

                        # 确定目标路径所属的模块
                        # target_path应该已经是规范化的
                        target_module_path = file_to_module.get(target_path)
                        if not target_module_path:
                            continue  # 找不到目标模块，跳过

                        # .................................................
                        # 检查外部关系 (Check Foreign Relationship)
                        # .................................................
                        # 只处理跨模块的依赖关系（源模块 != 目标模块）
                        if target_module_path != actual_source_module_path:
                            # 使用模块路径作为aggregated_deps_prio的键

                            # 获取当前依赖字符的优先级
                            current_priority = get_priority(dep_char)

                            # 获取已存储的依赖字符和优先级
                            _stored_char, stored_priority = aggregated_deps_prio[actual_source_module_path][target_module_path]

                            # 优先级比较和更新
                            if current_priority > stored_priority:
                                # 当前优先级更高，更新存储的依赖
                                aggregated_deps_prio[actual_source_module_path][target_module_path] = (dep_char, current_priority)

                            elif current_priority == stored_priority and current_priority > -1:
                                # 处理优先级相等的冲突
                                # 特殊情况：'<'和'>'合并为'x'（双向依赖）
                                if {dep_char, _stored_char} == {'<', '>'}:
                                    if aggregated_deps_prio[actual_source_module_path][target_module_path][0] != 'x':
                                        # 更新为双向依赖标记'x'
                                        aggregated_deps_prio[actual_source_module_path][target_module_path] = ('x', current_priority)
                                # 其他相等优先级冲突：保持现有值

                except Exception as decomp_err:
                    # 解压或处理行时出错
                    logger.warning(f"Error decompressing/processing row for '{mini_source_key_string}' in {mini_tracker_path}: {decomp_err}")

        except Exception as read_err:
            # 读取或处理迷你追踪器时出错
            logger.error(f"Error reading or processing mini tracker {mini_tracker_path} during aggregation: {read_err}", exc_info=True)

    # -------------------------------------------------------------------------
    # 记录第1步完成 (Log Step 1 Completion)
    # -------------------------------------------------------------------------
    logger.info(f"Processed {processed_mini_trackers} mini-trackers for direct dependencies.")

    # =========================================================================
    # 第2步：执行层级回滚 (Step 2: Perform Hierarchical Rollup)
    # =========================================================================
    # 目标：将子模块的外部依赖关系传递给父模块

    logger.info("Performing hierarchical rollup...")  # 记录开始层级回滚

    # -------------------------------------------------------------------------
    # 构建层级映射 (Build Hierarchy Mapping)
    # -------------------------------------------------------------------------
    # 使用filtered_modules中的规范化路径构建 父路径 -> 直接子路径 的映射
    hierarchy: Dict[str, List[str]] = defaultdict(list)

    # 获取所有模块路径的排序列表
    module_paths_list = sorted(list(filtered_modules.keys()))

    # 遍历所有模块路径对，建立父子关系
    for p_path in module_paths_list:
        # p_path: 潜在的父路径（已规范化）

        for c_path in module_paths_list:
            # c_path: 潜在的子路径（已规范化）

            # 跳过相同的路径
            if p_path == c_path:
                continue

            # 检查c_path是否直接位于p_path内部
            # 条件1：c_path以"p_path/"开头
            # 条件2：c_path的父目录就是p_path（确保是直接子目录，而非孙目录）
            if c_path.startswith(p_path + os.sep) and normalize_path(os.path.dirname(c_path)) == p_path:
                hierarchy[p_path].append(c_path)  # 添加到子路径列表

    # -------------------------------------------------------------------------
    # 迭代传播依赖关系 (Iteratively Propagate Dependencies)
    # -------------------------------------------------------------------------
    # 使用多轮迭代确保依赖关系从子模块完全传播到父模块

    changed_in_pass = True  # 标记：本轮是否有变化
    max_passes = len(module_paths_list)  # 安全断路：最大迭代次数
    current_pass = 0  # 当前迭代轮数

    # 当有变化且未超过最大轮数时继续迭代
    while changed_in_pass and current_pass < max_passes:
        changed_in_pass = False  # 重置变化标记
        current_pass += 1  # 轮数加1

        logger.debug(f"Hierarchy Rollup Pass {current_pass}")  # 记录当前轮数

        # 遍历所有潜在的父模块
        for parent_path in module_paths_list:
            # parent_path: 当前处理的父路径

            # .................................................................
            # 计算所有后代路径 (Calculate All Descendant Paths)
            # .................................................................
            # 每个父路径每轮只计算一次所有后代路径
            all_descendants_paths = _get_descendants_paths(parent_path, hierarchy)

            # .................................................................
            # 检查直接子模块以继承依赖 (Check Direct Children for Inheritance)
            # .................................................................
            # 遍历父模块的直接子模块
            for child_path in hierarchy.get(parent_path, []):
                # child_path: 当前子模块路径

                # 获取子模块的所有依赖关系（复制为列表以避免迭代时修改）
                child_deps = list(aggregated_deps_prio.get(child_path, {}).items())

                # 遍历子模块的每个依赖关系
                for target_path, (dep_char, priority) in child_deps:
                    # target_path: 依赖的目标模块路径
                    # dep_char: 依赖字符
                    # priority: 依赖优先级

                    # .........................................................
                    # 继承条件检查 (Inheritance Conditions Check)
                    # .........................................................
                    # 满足以下所有条件时才继承依赖：
                    # 1. 依赖是有意义的（优先级 > -1）
                    # 2. 目标不是父模块自身
                    # 3. 目标不是父模块的另一个后代
                    if priority > -1 and target_path != parent_path and target_path not in all_descendants_paths:

                        # 获取父模块当前存储的依赖信息
                        _parent_stored_char, parent_stored_priority = aggregated_deps_prio[parent_path][target_path]

                        # .....................................................
                        # 优先级比较和更新 (Priority Comparison and Update)
                        # .....................................................

                        if priority > parent_stored_priority:
                            # 子模块的优先级更高，继承该依赖
                            aggregated_deps_prio[parent_path][target_path] = (dep_char, priority)
                            changed_in_pass = True  # 标记有变化

                        elif priority == parent_stored_priority and priority > -1:
                            # 优先级相等的情况
                            # 将'<'和'>'合并为'x'（双向依赖）
                            if {_parent_stored_char, dep_char} == {'<', '>'}:
                                if aggregated_deps_prio[parent_path][target_path][0] != 'x':
                                    # 更新为双向依赖标记'x'
                                    aggregated_deps_prio[parent_path][target_path] = ('x', priority)
                                    changed_in_pass = True  # 标记有变化
                            # 其他相等优先级情况：保持现有值

    # -------------------------------------------------------------------------
    # 检查是否达到最大轮数 (Check Maximum Passes Reached)
    # -------------------------------------------------------------------------
    if current_pass == max_passes and changed_in_pass:
        # 如果达到最大轮数但仍有变化，可能存在循环或非常深的嵌套
        logger.warning("Hierarchical rollup reached max passes, potentially indicating a cycle or very deep nesting.")

    # =========================================================================
    # 第3步：转换为最终输出格式 (Step 3: Convert to Final Output Format)
    # =========================================================================
    # 目标：将内部存储格式转换为函数返回的标准格式

    # -------------------------------------------------------------------------
    # 初始化最终建议字典 (Initialize Final Suggestions Dictionary)
    # -------------------------------------------------------------------------
    final_suggestions = defaultdict(list)  # {源模块路径: [(目标模块路径, 依赖字符), ...]}

    # -------------------------------------------------------------------------
    # 排序源路径以确保输出顺序确定性 (Sort Source Paths for Deterministic Output)
    # -------------------------------------------------------------------------
    sorted_source_paths = sorted(aggregated_deps_prio.keys())

    # -------------------------------------------------------------------------
    # 遍历所有源模块 (Iterate Through All Source Modules)
    # -------------------------------------------------------------------------
    for source_path in sorted_source_paths:
        # source_path: 当前源模块路径

        # ---------------------------------------------------------------------
        # 验证源路径 (Validate Source Path)
        # ---------------------------------------------------------------------
        # 确保source_path确实是我们关心的模块路径
        # （按构造应该是，但检查更安全）
        if source_path not in filtered_modules:
            continue  # 不在过滤模块列表中，跳过

        # ---------------------------------------------------------------------
        # 获取目标模块字典 (Get Target Modules Dictionary)
        # ---------------------------------------------------------------------
        targets = aggregated_deps_prio[source_path]  # {目标模块路径: (依赖字符, 优先级)}

        # ---------------------------------------------------------------------
        # 排序目标路径 (Sort Target Paths)
        # ---------------------------------------------------------------------
        # 对每个源模块内的目标路径排序，确保顺序确定性
        sorted_target_paths = sorted(targets.keys())

        # ---------------------------------------------------------------------
        # 遍历目标模块 (Iterate Through Target Modules)
        # ---------------------------------------------------------------------
        for target_path in sorted_target_paths:
            # target_path: 当前目标模块路径

            # 获取依赖字符和优先级
            dep_char, _priority = targets[target_path]

            # .................................................................
            # 验证并添加到最终结果 (Validate and Add to Final Result)
            # .................................................................
            # 确保目标路径也是模块路径，且依赖不是占位符
            if target_path in filtered_modules and dep_char != PLACEHOLDER_CHAR:
                # 添加(目标路径, 依赖字符)元组到最终建议列表
                final_suggestions[source_path].append((target_path, dep_char))

        # 注意：元组(target_path, dep_char)的排序已通过遍历排序后的target paths隐式处理
        # 如需显式按元组排序：final_suggestions[source_path].sort()

    # -------------------------------------------------------------------------
    # 记录完成并返回结果 (Log Completion and Return Result)
    # -------------------------------------------------------------------------
    logger.info("Main tracker aggregation finished.")  # 记录聚合完成

    # 将defaultdict转换为普通字典并返回
    return dict(final_suggestions)


# =============================================================================
# 数据结构导出 (Data Structure Export)
# =============================================================================

# 主追踪器数据结构 (Main Tracker Data Structure)
# ------------------------------------------------
# 此字典定义了主追踪器的更新方式
# 由tracker_io.update_tracker导入和使用，当tracker_type为'main'时

main_tracker_data = {
    # --- 键过滤器 (Key Filter) ---
    # 确定哪些模块（目录）应该包含在主追踪器中
    # 函数签名：(project_root: str, path_to_key_info: Dict[str, KeyInfo]) -> Dict[str, KeyInfo]
    # 输入：项目根路径和全局路径到KeyInfo的映射
    # 输出：过滤后的模块路径到KeyInfo的映射
    "key_filter": main_key_filter,

    # --- 依赖聚合 (Dependency Aggregation) ---
    # 从迷你追踪器聚合依赖关系到主追踪器
    # 函数签名：详见aggregate_dependencies_contextual的文档字符串
    # 包含层级回滚功能
    "dependency_aggregation": aggregate_dependencies_contextual,

    # --- 追踪器路径获取 (Tracker Path Getter) ---
    # 返回主追踪器文件的存储路径
    # 函数签名：(project_root: str) -> str
    # 输入：项目根路径
    # 输出：主追踪器文件的完整路径
    "get_tracker_path": get_main_tracker_path
}

# =============================================================================
# 文件结束 (End of File)
# =============================================================================
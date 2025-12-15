# cline_utils/dependency_system/utils/tracker_utils.py
# 跟踪器工具模块（第1部分）- Tracker Utilities Module (Part 1)

"""
Tracker utilities for managing dependency tracking files.
Handles reading, parsing, and aggregating dependency information.

跟踪器工具，用于管理依赖跟踪文件
处理依赖信息的读取、解析和聚合
"""

# ==================== 导入依赖模块 - Import Dependencies ====================
import glob  # 文件名模式匹配 - Filename pattern matching
import hashlib  # 哈希算法 - Hash algorithms
import logging  # 日志记录 - Logging
import os  # 操作系统接口 - Operating system interface
import re  # 正则表达式 - Regular expressions
from collections import defaultdict  # 默认字典 - Default dictionary
from typing import Any, Dict, List, Optional, Set, Tuple  # 类型提示 - Type hints

# 从核心模块导入依赖网格组件 - Import dependency grid components from core module
from cline_utils.dependency_system.core.dependency_grid import (
    DIAGONAL_CHAR,  # 对角线字符（自依赖）- Diagonal character (self-dependency)
    EMPTY_CHAR,  # 空字符（无依赖）- Empty character (no dependency)
    decompress,  # 解压缩函数 - Decompress function
)

# 从核心模块导入键管理组件 - Import key management components from core module
from cline_utils.dependency_system.core.key_manager import KeyInfo, validate_key

# 从工具模块导入 - Import from utility modules
from .cache_manager import cached  # 缓存装饰器 - Cache decorator
from .config_manager import ConfigManager  # 配置管理器 - Configuration manager
from .path_utils import normalize_path  # 路径标准化函数 - Path normalization function

# ==================== 日志配置 - Logger Configuration ====================
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器 - Get logger for current module

# ==================== 类型别名定义 - Type Alias Definitions ====================
PathMigrationInfo = Dict[str, Tuple[Optional[str], Optional[str]]]
# 路径迁移信息：映射路径到(旧键, 新键)元组 - Path migration info: maps path to (old_key, new_key) tuple


# ==================== 全局实例解析辅助函数 - Global Instance Resolution Helpers ====================
def resolve_key_global_instance_to_ki(
    key_hash_instance_str: str, current_global_path_to_key_info: Dict[str, KeyInfo]
) -> Optional[KeyInfo]:
    """
    Resolves a KEY or KEY#global_instance string to a specific KeyInfo object
    from the provided current_global_path_to_key_info.
    This is now a simple pass-through since the global map is authoritative.

    将KEY或KEY#global_instance字符串解析为特定的KeyInfo对象
    这是一个简单的传递函数，因为全局映射是权威的

    Args:
        key_hash_instance_str: 键字符串，格式为"KEY"或"KEY#instance" - Key string in format "KEY" or "KEY#instance"
        current_global_path_to_key_info: 当前全局路径到KeyInfo的映射 - Current global path to KeyInfo mapping

    Returns:
        Optional[KeyInfo]: 匹配的KeyInfo对象，如果未找到返回None - Matching KeyInfo object, or None if not found
    """
    # ========== 步骤1: 空字符串检查 - Empty String Check ==========
    if not key_hash_instance_str:
        return None  # 空字符串返回None - Return None for empty string

    # ========== 步骤2: 遍历全局映射查找匹配 - Iterate Global Map to Find Match ==========
    for ki in current_global_path_to_key_info.values():
        # 遍历所有KeyInfo对象 - Iterate through all KeyInfo objects
        if ki.key_string == key_hash_instance_str:
            # 检查键字符串是否匹配 - Check if key string matches
            return ki  # 找到匹配，返回KeyInfo - Found match, return KeyInfo

    # ========== 步骤3: 未找到匹配 - No Match Found ==========
    return None  # 返回None表示未找到 - Return None indicating not found


# ==================== 模块级缓存 - Module-Level Cache ====================
# 用于get_key_global_instance_string的缓存，在运行期间持久化 - Cache for get_key_global_instance_string, persists during runtime
_module_level_base_key_to_sorted_KIs_cache: Dict[str, List[KeyInfo]] = defaultdict(list)
# 默认字典：基础键 -> 排序的KeyInfo列表 - Default dict: base key -> sorted KeyInfo list


def clear_global_instance_resolution_cache():
    """
    Clears the module-level cache for GI string resolution.
    清除全局实例字符串解析的模块级缓存

    用途 - Purpose:
    - 测试时清理缓存 - Clean cache during testing
    - 在不同运行之间重置 - Reset between different runs
    """
    # ========== 步骤1: 清空缓存字典 - Clear Cache Dictionary ==========
    _module_level_base_key_to_sorted_KIs_cache.clear()  # 清空所有缓存条目 - Clear all cache entries

    # ========== 步骤2: 记录日志 - Log Action ==========
    logger.debug("TrackerUtils: Cleared module-level GI resolution cache.")  # 调试日志 - Debug log


def get_key_global_instance_string(
    ki_obj_to_format: KeyInfo,
    current_global_path_to_key_info: Dict[str, KeyInfo],
    # Optional cache can be passed for specific contexts, otherwise uses module-level
    # 可选缓存可用于特定上下文，否则使用模块级缓存 - Optional cache for specific contexts
    base_key_to_sorted_KIs_cache: Optional[Dict[str, List[KeyInfo]]] = None,
) -> Optional[str]:
    """
    Returns the persisted KEY or KEY#GI for the given KeyInfo.
    This is now a simple pass-through since the global map is authoritative.

    返回给定KeyInfo的持久化KEY或KEY#GI
    这是一个简单的传递函数，因为全局映射是权威的

    Args:
        ki_obj_to_format: 要格式化的KeyInfo对象 - KeyInfo object to format
        current_global_path_to_key_info: 当前全局映射 - Current global mapping
        base_key_to_sorted_KIs_cache: 可选的缓存字典 - Optional cache dictionary

    Returns:
        Optional[str]: 键字符串，如果失败返回None - Key string, or None if failed
    """
    # ========== 步骤1: 空对象检查 - Null Object Check ==========
    if not ki_obj_to_format:
        # 如果KeyInfo对象为None - If KeyInfo object is None
        logger.warning(
            "TrackerUtils.GetGlobalInstanceString: Received None for ki_obj_to_format."
        )  # 记录警告 - Log warning
        return None  # 返回None - Return None

    # ========== 步骤2: 直接返回键字符串 - Directly Return Key String ==========
    return ki_obj_to_format.key_string  # 返回KeyInfo的键字符串 - Return KeyInfo's key string


def get_globally_resolved_key_info_for_cli(
    base_key_str: str,
    user_instance_num: Optional[int],
    global_map: Dict[str, KeyInfo],
    key_role: str,
) -> Optional[KeyInfo]:
    """
    Resolves a key provided via the CLI to a KeyInfo object.
    This is now a simple pass-through since the global map is authoritative.

    将通过CLI提供的键解析为KeyInfo对象
    这是一个简单的传递函数，因为全局映射是权威的

    Args:
        base_key_str: 基础键字符串（不带实例号）- Base key string (without instance number)
        user_instance_num: 用户指定的实例号（可选）- User-specified instance number (optional)
        global_map: 全局键映射 - Global key map
        key_role: 键的角色（用于错误消息）- Role of the key (for error messages)

    Returns:
        Optional[KeyInfo]: 解析的KeyInfo对象，如果失败返回None - Resolved KeyInfo object, or None if failed
    """
    # ========== 步骤1: 构建要查找的键 - Construct Key to Find ==========
    key_to_find = (
        f"{base_key_str}#{user_instance_num}" if user_instance_num else base_key_str
    )
    # 如果有实例号，格式为"KEY#num"；否则就是"KEY" - If instance number, format as "KEY#num"; otherwise just "KEY"

    # ========== 步骤2: 在全局映射中查找 - Search in Global Map ==========
    for ki in global_map.values():
        # 遍历所有KeyInfo对象 - Iterate through all KeyInfo objects
        if ki.key_string == key_to_find:
            # 如果键字符串匹配 - If key string matches
            return ki  # 返回匹配的KeyInfo - Return matching KeyInfo

    # ========== 步骤3: 处理歧义或未找到 - Handle Ambiguity or Not Found ==========
    # 查找所有以基础键开头的匹配项 - Find all matches starting with base key
    matching_infos = [
        info for info in global_map.values() if info.key_string.startswith(base_key_str)
    ]

    # 情况1：基础键未找到 - Case 1: Base key not found
    if not matching_infos:
        print(
            f"Error: Base {key_role} key '{base_key_str}' not found in global key map."
        )  # 打印错误消息 - Print error message
        return None  # 返回None - Return None

    # 情况2：基础键有多个实例但用户未指定 - Case 2: Multiple instances but user didn't specify
    if len(matching_infos) > 1 and not user_instance_num:
        print(
            f"Error: {key_role.capitalize()} key '{base_key_str}' is globally ambiguous. Please specify which instance you mean using '#<num>':"
        )  # 打印歧义错误 - Print ambiguity error
        # 列出所有匹配项供用户选择 - List all matches for user selection
        for i, ki in enumerate(sorted(matching_infos, key=lambda k: k.norm_path)):
            print(
                f"  [{i+1}] {ki.key_string} (Path: {ki.norm_path})  (Use as '{ki.key_string}')"
            )  # 打印每个选项 - Print each option
        return None  # 返回None让用户重新指定 - Return None for user to re-specify

    # ========== 步骤4: 未在循环中找到（理论上不应到达）- Not Found in Loop (shouldn't reach) ==========
    return None  # 返回None - Return None


# ==================== 解析辅助函数 - Parsing Helpers ====================
# 正则表达式模式：匹配KEY或KEY#num格式 - Regex pattern: matches KEY or KEY#num format
KEY_GI_PATTERN_PART = r"[a-zA-Z0-9]+(?:#[0-9]+)?"  # 捕获KEY或KEY#num - Capture KEY or KEY#num


def read_key_definitions_from_lines(lines: List[str]) -> List[Tuple[str, str]]:
    """
    Reads key definitions from lines. Returns a list of (key_string, path_string) tuples.
    从行中读取键定义。返回(键字符串, 路径字符串)元组列表

    格式示例 - Format Example:
        ---KEY_DEFINITIONS_START---
        1A: /path/to/file.py
        1B#2: /path/to/another.py
        ---KEY_DEFINITIONS_END---

    Args:
        lines: 文件行列表 - List of file lines

    Returns:
        List[Tuple[str, str]]: (键, 路径)元组列表 - List of (key, path) tuples
    """
    # ========== 步骤1: 初始化结果列表和状态标志 - Initialize Result List and State Flag ==========
    key_path_pairs: List[Tuple[str, str]] = []  # 结果列表 - Result list
    in_section = False  # 是否在KEY_DEFINITIONS区段内 - Whether inside KEY_DEFINITIONS section

    # ========== 步骤2: 编译正则表达式模式 - Compile Regex Patterns ==========
    key_def_start_pattern = re.compile(
        r"^---KEY_DEFINITIONS_START---$", re.IGNORECASE
    )  # 区段开始标记 - Section start marker
    key_def_end_pattern = re.compile(
        r"^---KEY_DEFINITIONS_END---$", re.IGNORECASE
    )  # 区段结束标记 - Section end marker
    definition_pattern = re.compile(
        rf"^({KEY_GI_PATTERN_PART})\s*:\s*(.*)$"
    )  # 定义行模式：KEY: path - Definition line pattern: KEY: path

    # ========== 步骤3: 遍历所有行 - Iterate Through All Lines ==========
    for line in lines:
        # ========== 步骤3.1: 检查结束标记 - Check End Marker ==========
        if key_def_end_pattern.match(line.strip()):
            break  # 找到结束标记，退出循环 - Found end marker, exit loop

        # ========== 步骤3.2: 处理区段内的行 - Process Lines Inside Section ==========
        if in_section:
            line_content = line.strip()  # 去除首尾空白 - Strip whitespace

            # 跳过空行和标题行 - Skip empty lines and title lines
            if not line_content or line_content.lower().startswith("key definitions:"):
                continue  # 继续下一行 - Continue to next line

            # ========== 步骤3.3: 匹配定义行 - Match Definition Line ==========
            match = definition_pattern.match(line_content)  # 尝试匹配定义模式 - Try to match definition pattern
            if match:
                k_gi, v_path = match.groups()  # 提取键和路径 - Extract key and path
                # k_gi现在是完整的KEY#GI或KEY - k_gi is now the full KEY#GI or KEY

                # ========== 步骤3.4: 验证键格式 - Validate Key Format ==========
                if validate_key(k_gi):  # validate_key已支持KEY#GI格式 - validate_key already handles KEY#GI format
                    key_path_pairs.append(
                        (k_gi, normalize_path(v_path.strip()))
                    )  # 添加到结果列表 - Add to result list
                else:  # 键格式无效 - Invalid key format
                    logger.warning(
                        f"TrackerUtils.ReadDefinitions: Skipping invalid key format '{k_gi}'."
                    )  # 记录警告 - Log warning

        # ========== 步骤3.5: 检查开始标记 - Check Start Marker ==========
        elif key_def_start_pattern.match(line.strip()):
            in_section = True  # 进入KEY_DEFINITIONS区段 - Enter KEY_DEFINITIONS section

    # ========== 步骤4: 返回结果 - Return Result ==========
    return key_path_pairs  # 返回(键, 路径)元组列表 - Return list of (key, path) tuples


def read_grid_from_lines(
    lines: List[str]
) -> Tuple[List[str], List[Tuple[str, str]]]:
    """
    Reads grid from lines. Returns: (grid_column_header_key_strings, list_of_grid_rows)
    where list_of_grid_rows is List[(row_key_string_label, compressed_row_data_string)]

    从行中读取网格。返回：(网格列头键字符串列表, 网格行列表)
    其中网格行列表是List[(行键字符串标签, 压缩的行数据字符串)]

    格式示例 - Format Example:
        ---GRID_START---
        X 1A 1B 1C
        1A = ...-x<>
        1B = x..-><
        ---GRID_END---

    Args:
        lines: 文件行列表 - List of file lines

    Returns:
        Tuple[List[str], List[Tuple[str, str]]]: (列头, 行数据)元组 - (column headers, row data) tuple
    """
    # ========== 步骤1: 初始化结果变量和状态标志 - Initialize Result Variables and State Flag ==========
    grid_column_header_keys_gi: List[str] = []  # 列头键列表（将存储KEY或KEY#GI）- Column header keys (will store KEY or KEY#GI)
    grid_rows_data_gi: List[Tuple[str, str]] = []  # 行数据列表（KEY或KEY#GI, 压缩数据）- Row data list (KEY or KEY#GI, compressed data)
    in_section = False  # 是否在GRID区段内 - Whether inside GRID section

    # ========== 步骤2: 编译正则表达式模式 - Compile Regex Patterns ==========
    grid_start_pattern = re.compile(
        r"^---GRID_START---$", re.IGNORECASE
    )  # 网格开始标记 - Grid start marker
    grid_end_pattern = re.compile(
        r"^---GRID_END---$", re.IGNORECASE
    )  # 网格结束标记 - Grid end marker
    row_label_pattern = re.compile(
        rf"^({KEY_GI_PATTERN_PART})\s*=\s*(.*)$"
    )  # 行标签模式：KEY = data - Row label pattern: KEY = data

    # ========== 步骤3: 遍历所有行 - Iterate Through All Lines ==========
    for line in lines:
        # ========== 步骤3.1: 检查结束标记 - Check End Marker ==========
        if grid_end_pattern.match(line.strip()):
            break  # 找到结束标记，退出循环 - Found end marker, exit loop

        # ========== 步骤3.2: 处理区段内的行 - Process Lines Inside Section ==========
        if in_section:
            line_content = line.strip()  # 去除首尾空白 - Strip whitespace

            # ========== 步骤3.3: 处理列头行 - Process Column Header Line ==========
            if line_content.upper().startswith("X "):
                # 列头行以"X "开头 - Column header line starts with "X "
                potential_keys = line_content.split()[
                    1:
                ]  # 分割并跳过"X" - Split and skip "X"
                # 验证每个键，键现在可以是KEY或KEY#GI - Validate each key, keys can now be KEY or KEY#GI
                grid_column_header_keys_gi = [
                    k for k in potential_keys if validate_key(k)
                ]
                # 检查是否有无效键被跳过 - Check if any invalid keys were skipped
                if len(grid_column_header_keys_gi) != len(potential_keys):
                    logger.warning(
                        f"TrackerUtils.ReadGrid: Some X-header keys are invalid and were skipped."
                    )  # 记录警告 - Log warning
                continue  # 继续下一行 - Continue to next line

            # 跳过空行和单独的"X" - Skip empty lines and standalone "X"
            if not line_content or line_content == "X":
                continue  # 继续下一行 - Continue to next line

            # ========== 步骤3.4: 处理数据行 - Process Data Row ==========
            match = row_label_pattern.match(line_content)  # 尝试匹配行模式 - Try to match row pattern
            if match:
                k_label_gi, v_data = match.groups()  # 提取键标签和数据 - Extract key label and data
                # k_label_gi是KEY或KEY#GI - k_label_gi is KEY or KEY#GI

                # ========== 步骤3.5: 验证键格式 - Validate Key Format ==========
                if validate_key(k_label_gi):  # 验证键 - Validate key
                    grid_rows_data_gi.append(
                        (k_label_gi, v_data.strip())
                    )  # 添加到行数据列表 - Add to row data list
                else:  # 键格式无效 - Invalid key format
                    logger.warning(
                        f"TrackerUtils.ReadGrid: Skipping row with invalid key label format '{k_label_gi}'."
                    )  # 记录警告 - Log warning

        # ========== 步骤3.6: 检查开始标记 - Check Start Marker ==========
        elif grid_start_pattern.match(line.strip()):
            in_section = True  # 进入GRID区段 - Enter GRID section

    # ========== 步骤4: 返回结果 - Return Result ==========
    # 一致性检查将在read_tracker_file_structured中进行 - Consistency check will be done in read_tracker_file_structured
    return grid_column_header_keys_gi, grid_rows_data_gi  # 返回列头和行数据 - Return column headers and row data


# ==================== 读取跟踪文件结构化数据函数 - Read Tracker File Structured Data Function ====================
@cached(
    "tracker_data_structured",  # 缓存名称 - Cache name
    key_func=lambda tracker_path: f"tracker_data_structured:{normalize_path(tracker_path)}:{(os.path.getmtime(tracker_path) if os.path.exists(tracker_path) else 0)}",
    # 缓存键包含路径和修改时间 - Cache key includes path and modification time
)
def read_tracker_file_structured(tracker_path: str) -> Dict[str, Any]:
    """
    Read a tracker file and parse its contents into list-based structures
    compatible with the new format (handles duplicate key strings).

    读取跟踪文件并将其内容解析为基于列表的结构
    兼容新格式（处理重复的键字符串）

    Args:
        tracker_path: 跟踪文件路径 - Path to the tracker file

    Returns:
        Dict[str, Any]: 包含以下键的字典 - Dictionary containing:
            - "definitions_ordered": List[Tuple[str,str]] - 有序定义列表
            - "grid_headers_ordered": List[str] - 有序网格头列表
            - "grid_rows_ordered": List[Tuple[str,str]] - 有序网格行列表 (行标签, 压缩数据)
            - "last_key_edit": str - 最后键编辑时间
            - "last_grid_edit": str - 最后网格编辑时间
    """
    # ========== 步骤1: 标准化路径 - Normalize Path ==========
    tracker_path = normalize_path(tracker_path)  # 标准化跟踪文件路径 - Normalize tracker file path

    # ========== 步骤2: 初始化空结果结构 - Initialize Empty Result Structure ==========
    empty_result = {
        "definitions_ordered": [],  # 空定义列表 - Empty definitions list
        "grid_headers_ordered": [],  # 空网格头列表 - Empty grid headers list
        "grid_rows_ordered": [],  # 空网格行列表 - Empty grid rows list
        "last_key_edit": "",  # 空最后键编辑 - Empty last key edit
        "last_grid_edit": "",  # 空最后网格编辑 - Empty last grid edit
    }

    # ========== 步骤3: 检查文件是否存在 - Check if File Exists ==========
    if not os.path.exists(tracker_path):
        # 文件不存在 - File doesn't exist
        logger.debug(
            f"Tracker file not found: {tracker_path}. Returning empty structured data."
        )  # 记录调试信息 - Log debug info
        return empty_result  # 返回空结果 - Return empty result

    # ========== 步骤4: 读取文件内容 - Read File Content ==========
    try:
        with open(tracker_path, "r", encoding="utf-8") as f:
            # 打开文件读取 - Open file for reading
            lines = f.readlines()  # 读取所有行 - Read all lines

        # ========== 步骤5: 解析定义和网格 - Parse Definitions and Grid ==========
        # 使用之前定义的辅助函数解析 - Parse using helper functions defined earlier
        definitions = read_key_definitions_from_lines(lines)  # 解析键定义 - Parse key definitions
        grid_headers, grid_rows = read_grid_from_lines(lines)  # 解析网格 - Parse grid

        # ========== 步骤6: 提取元数据 - Extract Metadata ==========
        content_str = "".join(lines)  # 将所有行连接成字符串 - Join all lines into string

        # 提取最后键编辑时间 - Extract last key edit time
        last_key_edit_match = re.search(
            r"^last_KEY_edit\s*:\s*(.*)$", content_str, re.MULTILINE | re.IGNORECASE
        )  # 搜索最后键编辑行 - Search for last key edit line
        last_key_edit = (
            last_key_edit_match.group(1).strip() if last_key_edit_match else ""
        )  # 提取值或空字符串 - Extract value or empty string

        # 提取最后网格编辑时间 - Extract last grid edit time
        last_grid_edit_match = re.search(
            r"^last_GRID_edit\s*:\s*(.*)$", content_str, re.MULTILINE | re.IGNORECASE
        )  # 搜索最后网格编辑行 - Search for last grid edit line
        last_grid_edit = (
            last_grid_edit_match.group(1).strip() if last_grid_edit_match else ""
        )  # 提取值或空字符串 - Extract value or empty string

        # ========== 步骤7: 一致性检查 - Consistency Check ==========
        # 检查定义、头和行的数量是否一致 - Check if counts of definitions, headers, and rows are consistent
        if (
            definitions
            and grid_headers
            and grid_rows
            and not (len(definitions) == len(grid_headers) == len(grid_rows))
        ):
            # 数量不一致 - Counts inconsistent
            logger.warning(
                f"ReadStructured: Inconsistent counts in '{os.path.basename(tracker_path)}'. "
                f"Defs: {len(definitions)}, Headers: {len(grid_headers)}, Rows: {len(grid_rows)}. "
                f"Data might be misaligned."
            )  # 记录警告 - Log warning
        elif (
            definitions
            and grid_rows
            and not grid_headers
            and len(definitions) == len(grid_rows)
        ):
            # 缺少网格头但定义和行匹配 - Missing grid headers but definitions and rows match
            logger.debug(
                f"ReadStructured: Grid headers missing but defs and rows match for '{os.path.basename(tracker_path)}'. "
                f"Imputing headers from defs."
            )  # 记录调试信息 - Log debug info
            grid_headers = [d[0] for d in definitions]  # 从定义推断头 - Impute headers from definitions

        # ========== 步骤8: 记录成功信息 - Log Success Info ==========
        logger.debug(
            f"Read structured tracker '{os.path.basename(tracker_path)}': "
            f"{len(definitions)} defs, {len(grid_headers)} grid headers, {len(grid_rows)} grid rows."
        )  # 记录调试信息 - Log debug info

        # ========== 步骤9: 返回结构化数据 - Return Structured Data ==========
        return {
            "definitions_ordered": definitions,  # 有序定义列表 - Ordered definitions list
            "grid_headers_ordered": grid_headers,  # 有序网格头列表 - Ordered grid headers list
            "grid_rows_ordered": grid_rows,  # 有序网格行列表 - Ordered grid rows list
            "last_key_edit": last_key_edit,  # 最后键编辑时间 - Last key edit time
            "last_grid_edit": last_grid_edit,  # 最后网格编辑时间 - Last grid edit time
        }

    # ========== 步骤10: 异常处理 - Exception Handling ==========
    except Exception as e:
        # 发生异常 - Exception occurred
        logger.exception(
            f"Error reading structured tracker file {tracker_path}: {e}"
        )  # 记录异常 - Log exception
        return empty_result  # 返回空结果 - Return empty result


# ==================== 文件结束标记 - End of File Marker (Part 1) ====================
# 第1部分结束，第2部分包含find_all_tracker_paths和aggregate_all_dependencies - Part 1 ends, Part 2 contains find_all_tracker_paths and aggregate_all_dependencies

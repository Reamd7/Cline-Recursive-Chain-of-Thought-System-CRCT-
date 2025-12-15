# core/dependency_grid.py

"""
依赖网格核心模块 / Core module for dependency grid operations.

本模块负责依赖网格的创建、压缩、解压缩和依赖管理，采用以键为中心的设计。
网格结构由有序的 List[KeyInfo] 定义，而网格字典使用 KeyInfo.key_string 作为键。

Handles grid creation, compression, decompression, and dependency management with key-centric design.
Grid structure is defined by an ordered List[KeyInfo], while the grid dictionary uses KeyInfo.key_string.

主要功能 / Key Features:
- RLE 压缩和解压缩依赖字符串 / RLE compression/decompression of dependency strings
- 网格创建和验证 / Grid creation and validation
- 依赖关系的添加和删除 / Adding and removing dependencies
- 依赖关系检索和查询 / Dependency retrieval and querying
- 网格格式化和显示 / Grid formatting and display
"""

# ============================================================================
# 标准库导入 / Standard Library Imports
# ============================================================================
import os  # 操作系统接口 / Operating system interface
import re  # 正则表达式操作 / Regular expression operations
from typing import Dict, List, Tuple, Optional  # 类型提示 / Type hints
from collections import defaultdict  # 默认字典 / Default dictionary for grouping

# ============================================================================
# 内部模块导入 / Internal Module Imports
# ============================================================================
# 从 utils 或同级 core 模块导入必要的工具 / Import only from utils or sibling core modules
from cline_utils.dependency_system.utils.cache_manager import cached, invalidate_dependent_entries, clear_all_caches
# 导入缓存装饰器和缓存管理功能 / Import cache decorators and cache management functions
from cline_utils.dependency_system.utils.config_manager import ConfigManager
# 导入配置管理器 / Import configuration manager

# 从键管理器导入 KeyInfo 用于类型提示和使用 / Import KeyInfo for type hinting and usage
from .key_manager import KeyInfo, sort_key_strings_hierarchically, validate_key

# ============================================================================
# 日志配置 / Logging Configuration
# ============================================================================
import logging
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器 / Get logger for this module

# ============================================================================
# 常量定义 / Constants Definition
# ============================================================================
# 网格字符定义 / Grid character definitions
DIAGONAL_CHAR = "o"       # 对角线字符，表示自引用 / Diagonal character for self-reference
PLACEHOLDER_CHAR = "p"    # 占位符字符，表示未定义的依赖 / Placeholder for undefined dependencies
EMPTY_CHAR = "."          # 空字符，表示无依赖 / Empty character for no dependency

# 编译正则表达式模式用于 RLE 压缩方案（重复字符，排除 'o'）
# Compile regex pattern for RLE compression scheme (repeating characters, excluding 'o')
# 模式说明：([^o])\1{2,} 匹配 3 个或更多连续的非 'o' 字符
# Pattern explanation: ([^o])\1{2,} matches 3 or more consecutive non-'o' characters
COMPRESSION_PATTERN = re.compile(r'([^o])\1{2,}')


# ============================================================================
# RLE 压缩和解压缩函数 / RLE Compression and Decompression Functions
# ============================================================================

def compress(s: str) -> str:
    """
    使用游程编码（RLE）压缩依赖字符串 / Compress a dependency string using Run-Length Encoding (RLE).

    仅压缩 3 个或更多重复字符的序列（排除 'o'）
    Only compresses sequences of 3 or more repeating characters (excluding 'o').

    工作原理 / How it works:
    1. 查找重复字符序列（3+ 次）/ Find repeating character sequences (3+ times)
    2. 将其替换为 "字符+数量" 格式 / Replace with "character+count" format
    3. 保留单个或双重字符不变 / Keep single or double characters unchanged

    示例 / Examples:
        "nnnnnpppdd" -> "n5p3dd"  (dd 不压缩，因为只有 2 个 / dd not compressed as only 2)
        "pppppppp" -> "p8"
        "o" -> "o" ('o' 永不压缩 / 'o' never compressed)

    Args:
        s: 待压缩的字符串 / String to compress (e.g., "nnnnnpppdd")

    Returns:
        压缩后的字符串 / Compressed string (e.g., "n5p3dd")
    """
    # 步骤 1: 边界检查 - 短字符串或空字符串直接返回
    # Step 1: Boundary check - return short or empty strings directly
    if not s or len(s) <= 3:
        return s

    # 步骤 2: 使用正则表达式替换重复序列
    # Step 2: Use regex to replace repeating sequences
    # lambda 函数：m.group(1) 是字符，len(m.group()) 是重复次数
    # lambda function: m.group(1) is the character, len(m.group()) is the repeat count
    return COMPRESSION_PATTERN.sub(lambda m: m.group(1) + str(len(m.group())), s)

@cached("grid_decompress", key_func=lambda s: f"decompress:{s}")
def decompress(s: str) -> str:
    """
    解压缩游程编码的依赖字符串，带缓存 / Decompress a Run-Length Encoded dependency string with caching.

    缓存策略 / Caching Strategy:
    - 使用 "grid_decompress" 缓存命名空间 / Uses "grid_decompress" cache namespace
    - 缓存键基于输入字符串 / Cache key based on input string
    - 避免重复解压缩相同字符串 / Avoids repeated decompression of same strings

    工作原理 / How it works:
    1. 遍历压缩字符串 / Iterate through compressed string
    2. 识别 "字符+数字" 模式 / Identify "character+number" patterns
    3. 展开为重复字符 / Expand into repeated characters
    4. 保留非压缩字符不变 / Keep non-compressed characters unchanged

    示例 / Examples:
        "n5p3dd" -> "nnnnnpppdd"
        "p8" -> "pppppppp"
        "abc" -> "abc" (无数字，无需解压缩 / no digits, no decompression needed)

    Args:
        s: 压缩后的字符串 / Compressed string (e.g., "n5p3d2")

    Returns:
        解压缩后的字符串 / Decompressed string (e.g., "nnnnnpppdd")
    """
    # 步骤 1: 快速路径 - 短字符串或无数字的字符串直接返回
    # Step 1: Fast path - return short strings or strings without digits directly
    if not s or (len(s) <= 3 and not any(c.isdigit() for c in s)):
        return s

    # 步骤 2: 解压缩循环 / Decompression loop
    result = []  # 存储结果字符 / Store result characters
    i = 0  # 当前位置指针 / Current position pointer

    while i < len(s):
        # 检查下一个字符是否为数字（表示压缩序列）
        # Check if next character is a digit (indicates compressed sequence)
        if i + 1 < len(s) and s[i + 1].isdigit():
            char = s[i]  # 获取要重复的字符 / Get character to repeat
            j = i + 1    # 开始解析数字部分 / Start parsing number part

            # 收集所有连续的数字字符 / Collect all consecutive digit characters
            while j < len(s) and s[j].isdigit():
                j += 1

            # 将数字字符串转换为整数 / Convert digit string to integer
            count = int(s[i + 1:j])

            # 添加重复的字符到结果 / Add repeated character to result
            result += char * count

            # 移动指针到数字后的位置 / Move pointer past the number
            i = j
        else:
            # 非压缩字符，直接添加 / Non-compressed character, add directly
            result += s[i]
            i += 1

    # 步骤 3: 合并结果列表为字符串 / Merge result list into string
    return "".join(result)

# ============================================================================
# 网格创建函数 / Grid Creation Functions
# ============================================================================

@cached("initial_grids",
       key_func=lambda key_info_list: f"initial_grid:{':'.join(sort_key_strings_hierarchically([ki.key_string for ki in key_info_list]))}")
def create_initial_grid(key_info_list: List[KeyInfo]) -> Dict[str, str]:
    """
    创建初始依赖网格，包含占位符和对角线标记 / Create an initial dependency grid with placeholders and diagonal markers.

    网格字典使用 KeyInfo.key_string 作为键 / The grid dictionary is keyed by KeyInfo.key_string.

    网格结构 / Grid Structure:
    - 每行代表一个源文件/目录 / Each row represents a source file/directory
    - 每列代表一个目标文件/目录 / Each column represents a target file/directory
    - 对角线位置（row == col）标记为 'o' / Diagonal positions (row == col) marked as 'o'
    - 其他位置初始化为占位符 'p' / Other positions initialized as placeholder 'p'

    缓存策略 / Caching Strategy:
    - 基于键列表的排序顺序生成缓存键 / Cache key based on sorted order of key list
    - 相同的键列表会返回缓存的网格 / Same key list returns cached grid

    示例 / Example:
        key_info_list = [KeyInfo("1A", ...), KeyInfo("1B", ...)]
        返回 / Returns:
        {
            "1A": "op",  # 1A 行：对角线 'o'，然后占位符 'p'
            "1B": "po"   # 1B 行：占位符 'p'，然后对角线 'o'
        }

    Args:
        key_info_list: KeyInfo 对象列表，定义网格结构和顺序
                      List of KeyInfo objects defining the grid structure and order.

    Returns:
        字典，将 key_strings 映射到压缩的依赖字符串
        Dictionary mapping key_strings to compressed dependency strings.

    Raises:
        ValueError: 如果 key_info_list 包含无效的 KeyInfo 对象
                   If key_info_list contains invalid KeyInfo objects
    """
    # 步骤 1: 验证输入 / Validate input
    # 检查列表是否为空或包含无效的 KeyInfo / Check if list is empty or contains invalid KeyInfo
    if not key_info_list or not all(isinstance(ki, KeyInfo) and validate_key(ki.key_string) for ki in key_info_list):
        logger.error(f"Invalid key_info_list provided for initial grid: {key_info_list}")
        raise ValueError("All items in key_info_list must be valid KeyInfo objects with valid key_strings")

    # 步骤 2: 初始化网格和变量 / Initialize grid and variables
    grid = {}  # 存储最终的网格 / Store final grid
    num_keys = len(key_info_list)  # 网格的维度（行数和列数）/ Grid dimensions (rows and columns)

    # 从 key_info_list 提取有序的键字符串列表
    # Extract ordered list of key strings from key_info_list
    # 这个顺序决定了网格的行和列顺序 / This order determines grid row and column order
    key_strings_ordered = [ki.key_string for ki in key_info_list]

    # 步骤 3: 为每个键创建一行 / Create a row for each key
    for i, row_key_str in enumerate(key_strings_ordered):
        # 创建一行，初始全部为占位符 / Create a row, initially all placeholders
        row_list_chars = [PLACEHOLDER_CHAR] * num_keys

        # 设置对角线位置为 'o'（表示自引用）/ Set diagonal position to 'o' (self-reference)
        row_list_chars[i] = DIAGONAL_CHAR

        # 压缩行并存储到网格中 / Compress row and store in grid
        grid[row_key_str] = compress("".join(row_list_chars))

    # 步骤 4: 返回创建的网格 / Return created grid
    return grid

# ============================================================================
# 字符访问辅助函数 / Character Access Helpers
# ============================================================================

def _parse_count(s: str, start: int) -> Tuple[int, int]:
    """
    从字符串中解析计数值的辅助函数 / Helper function to parse the count from a string.

    用于从压缩字符串中提取重复次数（数字部分）
    Used to extract repeat count (numeric part) from compressed string.

    示例 / Example:
        _parse_count("p5dd", 1) -> (5, 2)  # 从索引 1 开始，解析出 5，返回索引 2
        _parse_count("n12x", 1) -> (12, 3) # 从索引 1 开始，解析出 12，返回索引 3

    Args:
        s: 待解析的字符串 / The string to parse
        start: 解析的起始索引 / The starting index for parsing

    Returns:
        元组包含 / Tuple containing:
        - 解析出的计数值（整数）/ The parsed count as an integer
        - 计数值后的索引位置 / The index after the count
    """
    j = start  # 开始位置 / Starting position
    # 向前移动直到遇到非数字字符 / Move forward until non-digit character
    while j < len(s) and s[j].isdigit():
        j += 1
    # 返回解析的整数和结束位置 / Return parsed integer and end position
    return int(s[start:j]), j


def get_char_at(s: str, index: int) -> str:
    """
    获取解压缩字符串中特定索引位置的字符 / Get the character at a specific index in a decompressed string.

    这个函数直接在压缩字符串上操作，无需完全解压缩，提高效率。
    This function operates directly on compressed string without full decompression for efficiency.

    工作原理 / How it works:
    1. 遍历压缩字符串 / Iterate through compressed string
    2. 跟踪解压缩后的虚拟索引 / Track virtual index in decompressed string
    3. 识别目标索引所在的压缩段 / Identify compressed segment containing target index
    4. 返回该段的字符 / Return character of that segment

    示例 / Example:
        s = "p5dd"  # 解压缩后为 "pppppdd"
        get_char_at(s, 0) -> 'p'  # 第 0 个字符
        get_char_at(s, 4) -> 'p'  # 第 4 个字符（仍在 p5 范围内）
        get_char_at(s, 5) -> 'd'  # 第 5 个字符（第一个 d）

    Args:
        s: 压缩后的字符串 / The compressed string
        index: 解压缩字符串中的索引位置 / The index in the decompressed string

    Returns:
        指定索引位置的字符 / The character at the specified index

    Raises:
        IndexError: 如果索引超出范围 / If the index is out of range
    """
    decompressed_index = 0  # 跟踪解压缩后的虚拟索引 / Track virtual index in decompressed string
    i = 0  # 压缩字符串中的当前位置 / Current position in compressed string

    while i < len(s):
        # 检查是否为压缩序列（字符后跟数字）
        # Check if this is a compressed sequence (character followed by digit)
        if i + 1 < len(s) and s[i + 1].isdigit():
            char = s[i]  # 获取重复的字符 / Get repeated character
            count, i = _parse_count(s, i + 1)  # 解析重复次数 / Parse repeat count

            # 检查目标索引是否在这个重复序列中
            # Check if target index falls within this repeated sequence
            if decompressed_index + count > index:
                return char  # 返回这个字符 / Return this character

            decompressed_index += count  # 跳过这个序列 / Skip this sequence
        else:
            # 非压缩字符 / Non-compressed character
            if decompressed_index == index:
                return s[i]  # 找到目标索引的字符 / Found character at target index

            decompressed_index += 1  # 移动到下一个虚拟位置 / Move to next virtual position
            i += 1  # 移动到下一个实际位置 / Move to next actual position

    # 如果到达这里，索引超出范围 / If reached here, index is out of range
    raise IndexError("Index out of range")

def set_char_at(s: str, index: int, new_char: str) -> str:
    """
    设置特定索引位置的字符并返回压缩后的字符串 / Set a character at a specific index and return the compressed string.

    这个函数用于修改网格中的单个依赖关系。
    This function is used to modify a single dependency in the grid.

    工作原理 / How it works:
    1. 解压缩原始字符串 / Decompress original string
    2. 替换指定位置的字符 / Replace character at specified position
    3. 重新压缩字符串 / Recompress the string
    4. 返回新的压缩字符串 / Return new compressed string

    示例 / Example:
        s = "p5dd"  # 解压缩为 "pppppdd"
        set_char_at(s, 2, '>') -> 可能返回 "pp>p3dd" 或压缩形式
        # 将索引 2 的字符从 'p' 改为 '>'

    Args:
        s: 压缩后的字符串 / The compressed string
        index: 解压缩字符串中的索引位置 / The index in the decompressed string
        new_char: 要设置的新字符 / The new character to set

    Returns:
        更新后的压缩字符串 / The updated compressed string

    Raises:
        ValueError: 如果 new_char 不是单字符字符串 / If new_char is not a single character string
        IndexError: 如果索引超出范围 / If the index is out of range
    """
    # 步骤 1: 验证 new_char 是单个字符 / Validate new_char is a single character
    if not isinstance(new_char, str) or len(new_char) != 1:
        logger.error(f"Invalid new_char: {new_char}")
        raise ValueError("new_char must be a single character")

    # 步骤 2: 解压缩字符串 / Decompress string
    decompressed = decompress(s)

    # 步骤 3: 验证索引在有效范围内 / Validate index is within valid range
    if index >= len(decompressed):
        raise IndexError("Index out of range")

    # 步骤 4: 构建新的解压缩字符串，替换目标位置的字符
    # Build new decompressed string, replacing character at target position
    decompressed = decompressed[:index] + new_char + decompressed[index + 1:]

    # 步骤 5: 重新压缩并返回 / Recompress and return
    return compress(decompressed)

# ============================================================================
# 网格验证函数 / Grid Validation Functions
# ============================================================================

@cached("grid_validation",
       key_func=lambda grid, key_info_list: f"validate_grid:{hash(str(sorted(grid.items())))}:{':'.join(sort_key_strings_hierarchically([ki.key_string for ki in key_info_list]))}")
def validate_grid(grid: Dict[str, str], key_info_list: List[KeyInfo]) -> bool:
    """
    验证依赖网格与 KeyInfo 对象列表的一致性 / Validate a dependency grid for consistency with an ordered list of KeyInfo objects.

    网格键为 KeyInfo.key_string / Grid keys are KeyInfo.key_string.

    验证检查 / Validation Checks:
    1. 网格必须是字典类型 / Grid must be a dictionary
    2. key_info_list 必须是 KeyInfo 对象列表 / key_info_list must be a list of KeyInfo objects
    3. 网格行键必须与预期键匹配 / Grid row keys must match expected keys
    4. 每行长度必须等于键的数量 / Each row length must equal number of keys
    5. 对角线位置必须是 'o' / Diagonal positions must be 'o'

    Args:
        grid: 字典，将 key_strings 映射到压缩的依赖字符串
             Dictionary mapping key_strings to compressed dependency strings.
        key_info_list: 预排序的 KeyInfo 对象列表，定义网格
                      Pre-sorted list of KeyInfo objects defining the grid.

    Returns:
        如果有效返回 True，否则返回 False / True if valid, False otherwise
    """
    # 步骤 1: 验证参数类型 / Validate parameter types
    if not isinstance(grid, dict):
        logger.error("Grid validation failed: 'grid' not a dict.")
        return False

    if not isinstance(key_info_list, list) or not all(isinstance(ki, KeyInfo) for ki in key_info_list):
        logger.error("Grid validation failed: 'key_info_list' not a list of KeyInfo objects.")
        return False

    # 步骤 2: 从 KeyInfo 列表提取有序的键字符串
    # Extract ordered key strings from KeyInfo list
    ordered_key_strings = [ki.key_string for ki in key_info_list]

    # 步骤 3: 处理空网格的情况 / Handle empty grid case
    num_keys = len(ordered_key_strings)
    if num_keys == 0 and not grid:
        return True  # 空网格和空键列表是有效的 / Empty grid and empty key list is valid

    if num_keys == 0 and grid:
        logger.error("Grid validation failed: Grid not empty but key_info_list is.")
        return False

    # 步骤 4: 创建预期键和实际键的集合 / Create sets of expected and actual keys
    expected_keys_set = set(ordered_key_strings)
    actual_grid_keys_set = set(grid.keys())

    # 步骤 5: 检查行键是否匹配预期键 / Check row keys match expected keys
    missing_rows = expected_keys_set - actual_grid_keys_set  # 缺失的行 / Missing rows
    extra_rows = actual_grid_keys_set - expected_keys_set    # 多余的行 / Extra rows

    if missing_rows:
        logger.error(f"Grid validation failed: Missing rows for key_strings: {sorted(list(missing_rows))}")
        return False

    if extra_rows:
        logger.error(f"Grid validation failed: Extra rows found for key_strings: {sorted(list(extra_rows))}")
        return False

    # 步骤 6: 检查每行的长度和对角线字符 / Check row lengths and diagonal character
    # 使用 key_info_list 的顺序进行迭代 / Iterate using the order from key_info_list
    for idx, key_str in enumerate(ordered_key_strings):
        # 获取压缩的行数据 / Get compressed row data
        compressed_row = grid.get(key_str)
        if compressed_row is None:
            logger.error(f"Grid validation failed: Row missing for key_string '{key_str}'.")
            return False

        # 尝试解压缩行 / Try to decompress row
        try:
            decompressed = decompress(compressed_row)
        except Exception as e:
            logger.error(f"Grid validation failed: Error decompressing row for key_string '{key_str}': {e}")
            return False

        # 检查行长度 / Check row length
        if len(decompressed) != num_keys:
            logger.error(
                f"Grid validation failed: Row for key_string '{key_str}' length incorrect "
                f"(Exp:{num_keys}, Got:{len(decompressed)})."
            )
            return False

        # 检查对角线字符 / Check diagonal character
        if decompressed[idx] != DIAGONAL_CHAR:
            logger.error(
                f"Grid validation failed: Row for key_string '{key_str}' has incorrect diagonal character "
                f"at index {idx} (Expected: '{DIAGONAL_CHAR}', Got: '{decompressed[idx]}'). "
                f"Row: '{decompressed}'"
            )
            return False

    # 步骤 7: 所有检查通过 / All checks passed
    logger.debug("Grid validation successful.")
    return True

# ============================================================================
# 网格修改函数 / Grid Modification Functions
# ============================================================================

def add_dependency_to_grid(grid: Dict[str, str], source_key_str: str, target_key_str: str,
                            key_info_list: List[KeyInfo], dep_type: str = ">") -> Dict[str, str]:
    """
    向网格中添加两个键之间的依赖关系 / Add a dependency between two keys in the grid.

    网格键为 KeyInfo.key_string / Grid keys are KeyInfo.key_string.

    依赖类型字符 / Dependency Type Characters:
    - '>': 直接依赖 / Direct dependency
    - '<': 反向依赖 / Reverse dependency
    - 'x': 排除依赖 / Excluded dependency
    - 'd': 已弃用依赖 / Deprecated dependency
    - 's': 软依赖 / Soft dependency
    - 'S': 强依赖 / Strong dependency

    Args:
        grid: 字典，将 key_strings 映射到压缩的依赖字符串
             Dictionary mapping key_strings to compressed dependency strings.
        source_key_str: 源键字符串（行）/ Source key_string (row).
        target_key_str: 目标键字符串（列）/ Target key_string (column).
        key_info_list: KeyInfo 对象列表，用于索引映射
                      List of KeyInfo objects for index mapping.
        dep_type: 依赖类型字符，默认为 '>'
                 Dependency type character, defaults to '>'.

    Returns:
        更新后的网格 / Updated grid.

    Raises:
        ValueError: 如果键字符串不在 key_info_list 中或尝试修改对角线元素
                   If key_strings not in key_info_list or attempting to modify diagonal element
    """
    # 步骤 1: 提取有序的键字符串列表 / Extract ordered list of key strings
    ordered_key_strings = [ki.key_string for ki in key_info_list]

    # 步骤 2: 验证源键和目标键都存在 / Validate both source and target keys exist
    if source_key_str not in ordered_key_strings or target_key_str not in ordered_key_strings:
        raise ValueError(f"Key_strings {source_key_str} or {target_key_str} not in key_info_list")

    # 步骤 3: 获取索引位置 / Get index positions
    source_idx = ordered_key_strings.index(source_key_str)
    target_idx = ordered_key_strings.index(target_key_str)

    # 步骤 4: 检查是否尝试修改对角线元素 / Check if attempting to modify diagonal element
    if source_idx == target_idx:
        # 对角线元素 ('o') 不能直接更改 / Diagonal elements ('o') cannot be changed directly.
        # 网格验证确保它们是 'o' / Grid validation ensures they are 'o'.
        # 这防止意外覆盖并维护网格完整性 / This prevents accidental overwrites and maintains grid integrity.
        raise ValueError(
            f"Cannot directly modify diagonal element for key_string '{source_key_str}'. "
            f"Self-dependency must be 'o'."
        )

    # 步骤 5: 创建网格副本以避免修改原始网格 / Create a copy of the grid to avoid modifying the original
    new_grid = grid.copy()

    # 步骤 6: 获取并解压缩源行 / Get and decompress source row
    # source_key_str 用于从网格字典获取行 / source_key_str is used to get the row from the grid dict
    row = decompress(new_grid.get(source_key_str, compress(PLACEHOLDER_CHAR * len(ordered_key_strings))))

    # 步骤 7: 构建新行，替换目标位置的字符 / Build new row, replacing character at target position
    new_row = row[:target_idx] + dep_type + row[target_idx + 1:]

    # 步骤 8: 压缩并存储新行 / Compress and store new row
    new_grid[source_key_str] = compress(new_row)

    # 步骤 9: 使相关缓存失效 / Invalidate related caches
    # 使解压缩缓存失效 / Invalidate decompression cache
    invalidate_dependent_entries('grid_decompress', f"decompress:{new_grid.get(source_key_str)}")

    # 使验证缓存失效 / Invalidate validation cache
    # 使用 key_info_list 形成缓存键 / Use key_info_list to form the cache key
    cache_key_validate = f"validate_grid:{hash(str(sorted(new_grid.items())))}:{':'.join(sort_key_strings_hierarchically([ki.key_string for ki in key_info_list]))}"
    invalidate_dependent_entries('grid_validation', cache_key_validate)

    # 步骤 10: 返回更新后的网格 / Return updated grid
    return new_grid

def remove_dependency_from_grid(grid: Dict[str, str], source_key_str: str, target_key_str: str,
                                key_info_list: List[KeyInfo]) -> Dict[str, str]:
    """
    从网格中移除两个键之间的依赖关系 / Remove a dependency between two keys in the grid.

    网格键为 KeyInfo.key_string / Grid keys are KeyInfo.key_string.

    移除操作将依赖字符设置为空字符 '.' / Removal operation sets dependency character to empty char '.'.

    Args:
        grid: 字典，将 key_strings 映射到压缩的依赖字符串
             Dictionary mapping key_strings to compressed dependency strings.
        source_key_str: 源键字符串（行）/ Source key_string (row).
        target_key_str: 目标键字符串（列）/ Target key_string (column).
        key_info_list: KeyInfo 对象列表，用于索引映射
                      List of KeyInfo objects for index mapping.

    Returns:
        更新后的网格 / Updated grid.

    Raises:
        ValueError: 如果键字符串不在 key_info_list 中
                   If key_strings not in key_info_list
    """
    # 步骤 1: 提取有序的键字符串列表 / Extract ordered list of key strings
    ordered_key_strings = [ki.key_string for ki in key_info_list]

    # 步骤 2: 验证源键和目标键都存在 / Validate both source and target keys exist
    if source_key_str not in ordered_key_strings or target_key_str not in ordered_key_strings:
        raise ValueError(f"Key_strings {source_key_str} or {target_key_str} not in key_info_list")

    # 步骤 3: 获取索引位置 / Get index positions
    source_idx = ordered_key_strings.index(source_key_str)
    target_idx = ordered_key_strings.index(target_key_str)

    # 步骤 4: 如果是对角线元素，直接返回（无需修改）/ If diagonal element, return directly (no modification needed)
    if source_idx == target_idx:
        return grid

    # 步骤 5: 创建网格副本 / Create grid copy
    new_grid = grid.copy()

    # 步骤 6: 获取并解压缩源行 / Get and decompress source row
    row = decompress(new_grid.get(source_key_str, compress(PLACEHOLDER_CHAR * len(ordered_key_strings))))

    # 步骤 7: 构建新行，将目标位置设置为空字符 / Build new row, set target position to empty character
    new_row = row[:target_idx] + EMPTY_CHAR + row[target_idx + 1:]

    # 步骤 8: 压缩并存储新行 / Compress and store new row
    new_grid[source_key_str] = compress(new_row)

    # 步骤 9: 使相关缓存失效 / Invalidate related caches
    invalidate_dependent_entries('grid_decompress', f"decompress:{new_grid[source_key_str]}")
    cache_key_validate = f"validate_grid:{hash(str(sorted(new_grid.items())))}:{':'.join(sort_key_strings_hierarchically([ki.key_string for ki in key_info_list]))}"
    invalidate_dependent_entries('grid_validation', cache_key_validate)

    # 步骤 10: 返回更新后的网格 / Return updated grid
    return new_grid

# ============================================================================
# 依赖检索函数 / Dependency Retrieval Functions
# ============================================================================

@cached("grid_dependencies",
        key_func=lambda grid, source_key_str, key_info_list: f"grid_deps:{hash(str(sorted(grid.items())))}:{source_key_str}:{':'.join(sort_key_strings_hierarchically([ki.key_string for ki in key_info_list]))}")
def get_dependencies_from_grid(grid: Dict[str, str], source_key_str: str, key_info_list: List[KeyInfo]) -> Dict[str, List[str]]:
    """
    获取特定键的依赖关系，按关系类型分类 / Get dependencies for a specific key_string, categorized by relationship type.

    网格键为 KeyInfo.key_string，返回相关的 key_strings。
    Grid keys are KeyInfo.key_string. Returns related key_strings.

    依赖字符含义 / Dependency Character Meanings:
    - '<': 反向依赖 / Reverse dependencies
    - '>': 直接依赖 / Direct dependencies
    - 'x': 排除依赖 / Excluded dependencies
    - 'd': 已弃用依赖 / Deprecated dependencies
    - 's': 软依赖 / Soft dependencies
    - 'S': 强依赖 / Strong dependencies
    - 'p': 占位符依赖 / Placeholder dependencies

    Args:
        grid: 字典，将 key_strings 映射到压缩的依赖字符串
             Dictionary mapping key_strings to compressed dependency strings.
        source_key_str: 要获取依赖关系的键字符串
                       Key_string to get dependencies for.
        key_info_list: KeyInfo 对象列表，用于索引映射和上下文
                      List of KeyInfo objects for index mapping and context.

    Returns:
        字典，将依赖字符映射到相关 key_strings 的列表
        Dictionary mapping dependency characters to lists of related key_strings.

    Raises:
        ValueError: 如果 source_key_str 不在 key_info_list 中
                   If source_key_str not in key_info_list
    """
    # 步骤 1: 提取有序的键字符串列表 / Extract ordered list of key strings
    ordered_key_strings = [ki.key_string for ki in key_info_list]

    # 步骤 2: 验证源键存在 / Validate source key exists
    if source_key_str not in ordered_key_strings:
        raise ValueError(f"Source key_string {source_key_str} not in key_info_list")

    # 步骤 3: 初始化结果字典 / Initialize results dictionary
    results = defaultdict(set)  # 使用集合避免重复 / Use sets to avoid duplicates
    source_idx = ordered_key_strings.index(source_key_str)  # 获取源键的索引 / Get source key index
    defined_dep_chars = {'<', '>', 'x', 'd', 's', 'S'}  # 已定义的依赖字符 / Defined dependency characters

    # 步骤 4: 获取源键的行数据 / Get source key's row data
    # 网格字典的行键是 source_key_str / The row key for the grid dictionary is source_key_str
    row_key_compressed = grid.get(source_key_str)

    # 步骤 5: 检查行是否存在 / Check if row exists
    if not row_key_compressed:
        # 源键在网格中没有行（如果网格有效，这不应该发生）
        # Source key has no row in grid (should not happen if grid is valid)
        logger.warning(f"No grid row found for source_key_str '{source_key_str}' during dependency retrieval.")
        return {k: list(v) for k, v in results.items()}

    # 步骤 6: 遍历列，检查依赖关系 / Iterate through columns, check dependencies
    # 使用 key_info_list 获取顺序和目标 key_strings
    # Use key_info_list for order and target key_strings
    for col_idx, target_ki in enumerate(key_info_list):
        target_key_str = target_ki.key_string

        # 跳过自引用（对角线）/ Skip self-reference (diagonal)
        if source_idx == col_idx:
            continue

        # 步骤 6.1: 获取当前位置的依赖字符 / Get dependency character at current position
        char_outgoing = EMPTY_CHAR
        try:
            char_outgoing = get_char_at(row_key_compressed, col_idx)
        except IndexError:
            logger.warning(
                f"IndexError getting char at col {col_idx} for row '{source_key_str}'. "
                f"Row length might be wrong."
            )
            pass

        # 步骤 6.2: 根据依赖字符分类 / Categorize by dependency character
        if char_outgoing == 'x':
            results['x'].add(target_key_str)
        elif char_outgoing == 'd':
            results['d'].add(target_key_str)
        elif char_outgoing == 'S':
            results['S'].add(target_key_str)
        elif char_outgoing == 's':
            results['s'].add(target_key_str)
        elif char_outgoing == '>':
            results['>'].add(target_key_str)
        elif char_outgoing == '<':
            results['<'].add(target_key_str)
        elif char_outgoing not in defined_dep_chars:
            # 未定义的字符，检查是否为占位符 / Undefined character, check if placeholder
            if char_outgoing == 'p':
                results['p'].add(target_key_str)

    # 步骤 7: 将集合转换为列表并返回 / Convert sets to lists and return
    return {k: list(v) for k, v in results.items()}


# ============================================================================
# 网格格式化函数 / Grid Formatting Functions
# ============================================================================

def format_grid_for_display(grid: Dict[str, str], key_info_list: List[KeyInfo]) -> str:
    """
    格式化网格以便显示 / Format a grid for display.

    使用 KeyInfo.key_string 作为标签 / Uses KeyInfo.key_string for labels.

    输出格式示例 / Output Format Example:
        X 1A 1B 1C
        1A = op3
        1B = po3
        1C = p3o

    Args:
        grid: 字典，将 key_strings 映射到压缩的依赖字符串
             Dictionary mapping key_strings to compressed dependency strings.
        key_info_list: 网格中的 KeyInfo 对象列表，定义顺序
                      List of KeyInfo objects in the grid, defining order.

    Returns:
        网格的格式化字符串表示 / Formatted string representation of the grid.
    """
    # 步骤 1: 提取有序的键字符串列表 / Extract ordered list of key strings
    ordered_key_strings = [ki.key_string for ki in key_info_list]

    # 步骤 2: 创建结果列表，从列标题开始 / Create result list, starting with column headers
    result = ["X " + " ".join(ordered_key_strings)]

    # 步骤 3: 遍历每个键，添加行数据 / Iterate through each key, add row data
    # 使用 key_info_list 的顺序进行迭代 / Iterate using the order from key_info_list
    for key_str in ordered_key_strings:
        # 从网格获取行数据，使用 key_str / Get row from grid using key_str
        compressed_row_data = grid.get(key_str, compress(PLACEHOLDER_CHAR * len(ordered_key_strings)))

        # 添加行：键 = 压缩数据 / Add row: key = compressed data
        result.append(f"{key_str} = {compressed_row_data}")

    # 步骤 4: 合并行并返回 / Join rows and return
    return "\n".join(result)


# ============================================================================
# 缓存管理函数 / Cache Management Functions
# ============================================================================

def clear_cache():
    """
    清除所有函数缓存 / Clear all function caches via cache_manager.

    这个函数通过 cache_manager 清除所有缓存的函数调用结果。
    This function clears all cached function call results via cache_manager.

    使用场景 / Use Cases:
    - 网格结构发生重大变化后 / After major grid structure changes
    - 内存压力较大时 / When memory pressure is high
    - 测试或调试时需要强制重新计算 / When testing/debugging requires forced recalculation
    """
    clear_all_caches()  # 调用缓存管理器的清除函数 / Call cache manager's clear function


# ============================================================================
# 文件结束 / End of File
# ============================================================================
# EoF
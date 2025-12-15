"""
测试模块：集成缓存测试
Test Module: Integration Cache Tests

本模块测试缓存管理器的集成测试用例（IS-01到IS-04），包括：
- 源文件修改时的缓存集成（IS-01）
- 配置文件排除规则修改时的缓存集成（IS-02）
- .clinerules根目录修改时的缓存集成（IS-03）
- 嵌入向量强制重新生成时的缓存集成（IS-04）

This module tests integration cache test cases (IS-01 to IS-04), including:
- Cache integration on source file modification (IS-01)
- Cache integration on config file exclusion modification (IS-02)
- Cache integration on .clinerules roots modification (IS-03)
- Cache integration on forced embedding regeneration (IS-04)
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入os模块用于文件系统操作 / Import os module for filesystem operations
import os
# 导入time模块用于时间操作和延迟 / Import time module for time operations and delays
import time
# 导入shutil模块用于目录操作 / Import shutil module for directory operations
import shutil
# 导入json模块用于配置文件处理 / Import json module for config file handling
import json
# 导入Path类用于路径操作 / Import Path class for path operations
from pathlib import Path
# 导入numpy用于嵌入向量测试（测试夹具需要）/ Import numpy for embedding tests (needed by test fixtures)
import numpy as np

# 导入密钥管理器核心功能 / Import key manager core functions
from cline_utils.dependency_system.core.key_manager import sort_key_strings_hierarchically, KeyInfo
# 导入缓存管理器功能 / Import cache manager functions
from cline_utils.dependency_system.utils.cache_manager import get_cache_stats, clear_all_caches
# 导入路径工具模块 / Import path utilities module
from cline_utils.dependency_system.utils import path_utils
# 导入配置管理器模块 / Import config manager module
from cline_utils.dependency_system.utils import config_manager
# 导入嵌入管理器模块 / Import embedding manager module
from cline_utils.dependency_system.analysis import embedding_manager
# 导入依赖网格核心模块 / Import dependency grid core module
from cline_utils.dependency_system.core import dependency_grid
# 导入跟踪器IO模块 / Import tracker I/O module
from cline_utils.dependency_system.io import tracker_io
# 导入依赖分析器模块（用于夹具/辅助函数）/ Import dependency analyzer (for fixtures/helpers)
from cline_utils.dependency_system.analysis import dependency_analyzer
# 导入项目分析器用于集成测试 / Import project analyzer for integration tests
from cline_utils.dependency_system.analysis.project_analyzer import analyze_project

# ========================================
# 辅助函数 / Helper Functions
# ========================================

def touch(filepath):
    """
    辅助函数：更新文件的修改时间
    Helper Function: Update file modification time

    目的：用于测试文件修改时间变化对缓存失效的影响
    Purpose: Used to test the impact of file mtime changes on cache invalidation

    参数 / Args:
        filepath: 要更新的文件路径 / File path to update
    """
    try:
        # 使用Path.touch()更新文件修改时间 / Update file mtime using Path.touch()
        Path(filepath).touch()
    except OSError as e:
        # 捕获并打印错误信息 / Catch and print error message
        print(f"Error touching file {filepath}: {e}")

def read_tracker_file_compat(tracker_path):
    """
    辅助函数：以兼容格式读取跟踪器文件
    Helper Function: Read tracker file in compatible format

    目的：将结构化的跟踪器数据转换为测试友好的格式
    Purpose: Convert structured tracker data to test-friendly format

    参数 / Args:
        tracker_path: 跟踪器文件路径 / Tracker file path

    返回 / Returns:
        字典包含'keys'和'grid'，或None如果读取失败
        Dictionary containing 'keys' and 'grid', or None if read fails

    数据转换 / Data Conversion:
    输入（结构化格式）：
    {
        "definitions_ordered": [("1A1", "src/a.py"), ("1A2", "src/b.py")],
        "grid_rows_ordered": [("1A1", "o<"), ("1A2", ">o")]
    }

    输出（简化格式）：
    {
        "keys": {"1A1": "src/a.py", "1A2": "src/b.py"},
        "grid": {"1A1": "o<", "1A2": ">o"}
    }

    这种简化格式更便于测试中的查找和验证操作
    This simplified format is more convenient for lookup and validation in tests
    """
    # 读取结构化的跟踪器数据 / Read structured tracker data
    # read_tracker_file_structured返回包含有序列表的字典
    # read_tracker_file_structured returns dict with ordered lists
    data = tracker_io.read_tracker_file_structured(tracker_path)
    # 如果数据为空或没有定义列表，返回None / If data empty or no definitions, return None
    # 这可能发生在文件不存在、格式错误或为空文件时
    # This can happen if file doesn't exist, is malformed, or empty
    if not data or not data.get("definitions_ordered"):
        return None

    # 从有序定义创建键到路径的映射 / Create key-to-path mapping from ordered definitions
    # definitions_ordered是(key, path)元组的列表
    # definitions_ordered is list of (key, path) tuples
    # 转换为字典便于通过键查找路径 / Convert to dict for easy path lookup by key
    keys_map = {k: p for k, p in data["definitions_ordered"]}
    # 从有序网格行创建网格字典 / Create grid dictionary from ordered grid rows
    # grid_rows_ordered是(key, row_string)元组的列表
    # grid_rows_ordered is list of (key, row_string) tuples
    # row_string是压缩的依赖字符串，如"o<px"
    # row_string is compressed dependency string like "o<px"
    grid = {k: v for k, v in data["grid_rows_ordered"]}

    # 返回包含键映射和网格的字典 / Return dictionary containing keys map and grid
    # 这个格式直接用于测试中的断言和验证
    # This format is directly used for assertions and validation in tests
    return {
        "keys": keys_map,
        "grid": grid
    }

def get_char_at_key(grid, source_key, target_key, sorted_keys):
    """
    辅助函数：从网格中获取特定位置的依赖字符
    Helper Function: Get dependency character at specific position in grid

    目的：从压缩的网格行中提取源键对目标键的依赖关系字符
    Purpose: Extract dependency character from source key to target key from compressed grid row

    参数 / Args:
        grid: 依赖网格字典 / Dependency grid dictionary
              格式：{"1A1": "o<p", "1A2": ">ox", ...}
        source_key: 源键（行键）/ Source key (row key)
                   表示依赖关系的"从"方
        target_key: 目标键（列键）/ Target key (column key)
                   表示依赖关系的"到"方
        sorted_keys: 已排序的键列表 / Sorted key list
                    用于确定列索引，如["1A1", "1A2", "1B"]

    返回 / Returns:
        依赖字符，或None如果未找到 / Dependency character, or None if not found
        可能的字符：'o'（自己）、'<'（依赖）、'>'（被依赖）、
                   'x'（互相依赖）、'p'（占位符）、'n'（无关）等

    示例 / Example:
        grid = {"1A1": "o<p", "1A2": ">ox"}
        sorted_keys = ["1A1", "1A2", "1B"]
        get_char_at_key(grid, "1A1", "1A2", sorted_keys)
        # 返回 '<'，表示1A1依赖1A2

    工作原理 / How It Works:
    1. 查找源键在网格中的行
    2. 找到目标键在sorted_keys中的索引（列位置）
    3. 从压缩的行字符串中提取该位置的字符
    4. 压缩格式使用游程编码减少存储空间
    """
    # 如果源键不在网格中，返回None / If source key not in grid, return None
    # 这可能发生在键被排除或文件被删除时
    # This can happen if key was excluded or file was deleted
    if source_key not in grid:
        return None
    # 获取压缩的行数据 / Get compressed row data
    # 压缩格式如"o<3p2n"，表示"o<ppppnn"
    # Compressed format like "o<3p2n" represents "o<ppppnn"
    row_compressed = grid[source_key]
    try:
        # 找到目标键在排序列表中的索引 / Find target key index in sorted list
        # 索引即为列位置（0-based）/ Index is the column position (0-based)
        target_idx = sorted_keys.index(target_key)
        # 使用dependency_grid.get_char_at获取字符 / Use dependency_grid.get_char_at to get character
        # 此函数处理压缩格式的解压缩 / This function handles decompression of compressed format
        return dependency_grid.get_char_at(row_compressed, target_idx)
    except ValueError:
        # 如果目标键不在排序列表中，返回None / If target key not in sorted list, return None
        # 这表示目标键可能是新添加的或已被删除
        # This indicates target key might be newly added or already removed
        return None

def get_mini_tracker_path(project_root, relative_dir):
    """
    辅助函数：查找指定目录的mini-tracker文件
    Helper Function: Find mini-tracker file for specified directory

    目的：定位以_module.md结尾的跟踪器文件
    Purpose: Locate tracker file ending with _module.md

    参数 / Args:
        project_root: 项目根目录 / Project root directory
                     如：/tmp/test_project_is
        relative_dir: 相对目录路径 / Relative directory path
                     如："src"、"lib"、"docs"

    返回 / Returns:
        跟踪器文件路径，或None如果未找到 / Tracker file path, or None if not found
        如：/tmp/test_project_is/src/src_module.md

    工作原理 / How It Works:
    - 每个根目录有一个mini-tracker文件
    - 文件名格式：{dir_name}_module.md
    - 例如：src目录 → src_module.md
    - 例如：lib目录 → lib_module.md
    - 这些文件存储该目录下文件间的依赖关系

    为什么需要这个函数 / Why This Function:
    - 测试需要验证特定目录的跟踪器内容
    - 文件名可能因目录名不同而变化
    - 使用glob模式匹配确保找到正确的文件
    - 避免硬编码文件名，提高测试的灵活性
    """
    # 构建目录完整路径 / Build complete directory path
    # Path对象支持/操作符进行路径拼接
    # Path object supports / operator for path joining
    dir_path = project_root / relative_dir
    # 查找第一个以_module.md结尾的文件 / Find first file ending in _module.md
    # glob返回生成器，遍历找到第一个匹配的文件
    # glob returns generator, iterate to find first matching file
    for f in dir_path.glob("*_module.md"):
        # 找到第一个就返回，通常只有一个
        # Return first found, usually only one exists
        return f
    # 如果未找到，返回None / If not found, return None
    # 这可能发生在analyze_project未运行或目录为空时
    # This can happen if analyze_project hasn't run or directory is empty
    return None


# ========================================
# 模拟类 / Mock Classes
# ========================================

class MockEmbeddingModel:
    """
    模拟嵌入模型类
    Mock Embedding Model Class

    目的：提供确定性的嵌入向量生成，避免下载真实模型
    Purpose: Provide deterministic embedding generation, avoid downloading real models

    特性：
    - 基于文本内容的哈希值生成确定性嵌入
    - 确保相同文本总是产生相同嵌入
    - 避免下载大型语言模型

    Features:
    - Generate deterministic embeddings based on text content hash
    - Ensure same text always produces same embedding
    - Avoid downloading large language models

    设计原理 / Design Rationale:
    - 真实的嵌入模型（如sentence-transformers）体积大（几百MB）且下载慢
    - 测试不需要真实的语义理解，只需要一致的向量表示
    - 使用文本哈希值作为随机种子，确保确定性输出
    - 这使测试快速、可重复，且不依赖外部资源

    实现细节 / Implementation Details:
    - 模拟SentenceTransformer的encode接口
    - 返回384维的numpy数组（与真实模型维度一致）
    - 添加0.1的偏置确保向量分量主要为正值
    - 避免极端的相似度值（全0或全1）
    """
    def __init__(self, embedding_dim=384):
        """
        初始化模拟嵌入模型
        Initialize Mock Embedding Model

        参数 / Args:
            embedding_dim: 嵌入向量维度，默认384 / Embedding dimension, default 384
                          这与sentence-transformers/all-MiniLM-L6-v2模型一致
                          This matches sentence-transformers/all-MiniLM-L6-v2 model
        """
        # 设置嵌入向量维度 / Set embedding dimension
        # 384是常见的轻量级嵌入模型维度 / 384 is common for lightweight embedding models
        self.embedding_dim = embedding_dim

    def encode(self, texts, **kwargs):
        """
        编码文本为嵌入向量
        Encode texts to embedding vectors

        参数 / Args:
            texts: 要编码的文本列表 / List of texts to encode
            **kwargs: 其他参数（兼容性）/ Other parameters (for compatibility)
                     例如：batch_size, show_progress_bar等

        返回 / Returns:
            嵌入向量列表 / List of embedding vectors
            每个向量是shape为(embedding_dim,)的numpy数组

        工作原理 / How It Works:
        1. 对每个文本计算哈希值
        2. 使用哈希作为随机种子
        3. 生成随机向量（正态分布）
        4. 添加偏置使分量偏向正值
        5. 返回float32数组（与真实模型一致）
        """
        # 基于文本内容返回确定性嵌入 / Return deterministic embeddings based on text content
        embeddings = []
        # 遍历每个文本 / Iterate through each text
        for text in texts:
            # 使用文本哈希值作为随机种子以获得确定性输出
            # Use hash of text to seed random generator for deterministic output
            # 这确保相同文本->相同嵌入，不同文本->不同嵌入
            # This ensures same text -> same embedding, different text -> different embedding
            # hash()返回值可能为负，使用abs()确保正值
            # hash() can return negative, use abs() to ensure positive
            # 模2^32确保值在RandomState种子范围内
            # Modulo 2^32 to ensure value in RandomState seed range
            seed = abs(hash(text)) % (2**32)
            # 创建具有固定种子的随机数生成器 / Create random number generator with fixed seed
            # RandomState确保确定性，即使在不同机器上也一致
            # RandomState ensures determinism, consistent even across different machines
            rng = np.random.RandomState(seed)
            # 使用randn + 偏置确保一些正相似度但不太高
            # Use randn + bias to ensure some positive similarity but not too high
            # randn: 标准正态分布，均值0，标准差1
            # randn: standard normal distribution, mean 0, std 1
            # +0.1: 偏置使均值变为0.1，大部分值为正
            # +0.1: bias shifts mean to 0.1, most values positive
            # 这避免了0.0裁剪（如果为负）和'S'依赖（如果太高）
            # This avoids 0.0 clipping (if negative) and 'S' dependency (if too high)
            # astype(np.float32): 与真实嵌入模型的数据类型一致
            # astype(np.float32): consistent with real embedding model data type
            embeddings.append(rng.randn(self.embedding_dim).astype(np.float32) + 0.1)
        # 返回嵌入向量列表 / Return list of embeddings
        return embeddings

# ========================================
# 测试夹具 / Test Fixtures
# ========================================

@pytest.fixture(scope="function", autouse=True)
def mock_embedding_model(monkeypatch):
    """
    测试夹具：模拟嵌入模型以防止下载
    Test Fixture: Mock embedding model to prevent downloads

    目的：自动为所有测试注入模拟的嵌入模型，避免真实模型下载
    Purpose: Auto-inject mock embedding model for all tests, avoid real model downloads

    使用autouse=True使其自动应用于所有测试
    Uses autouse=True to automatically apply to all tests
    """
    # 创建模拟模型实例 / Create mock model instance
    mock_model = MockEmbeddingModel()
    # 使用monkeypatch替换真实的MODEL_INSTANCE / Use monkeypatch to replace real MODEL_INSTANCE
    monkeypatch.setattr(embedding_manager, "MODEL_INSTANCE", mock_model)

    # 同时模拟配置，使其认为已选择模型 / Also mock the config so it thinks a model is selected
    monkeypatch.setattr(embedding_manager, "SELECTED_MODEL_CONFIG", {
        "type": "sentence-transformer",  # 模型类型
        "embedding_dim": 384,  # 嵌入维度
        "name": "mock-model"  # 模型名称
    })

    # 确保_load_model被调用时不覆盖模拟 / Ensure _load_model doesn't overwrite mock if called
    monkeypatch.setattr(embedding_manager, "_load_model", lambda *args, **kwargs: True)
    # 确保_unload_model不清除模拟实例 / Ensure _unload_model doesn't clear the mock instance
    monkeypatch.setattr(embedding_manager, "_unload_model", lambda: None)

    # 激进的模拟：防止任何sentence_transformers或transformers的导入
    # AGGRESSIVE MOCKING: Prevent any import of sentence_transformers or transformers
    # 这确保即使_load_model被绕过也不会发生下载
    # This ensures NO downloads can possibly happen even if _load_model is bypassed
    import sys
    from unittest.mock import MagicMock

    # 创建sentence_transformers模拟模块 / Create sentence_transformers mock module
    mock_st = MagicMock()
    mock_st.SentenceTransformer.return_value = mock_model
    monkeypatch.setitem(sys.modules, "sentence_transformers", mock_st)

    # 创建transformers模拟模块 / Create transformers mock module
    mock_tf = MagicMock()
    mock_tf.AutoTokenizer.from_pretrained.return_value = MagicMock()
    mock_tf.AutoModel.from_pretrained.return_value = MagicMock()
    monkeypatch.setitem(sys.modules, "transformers", mock_tf)

    # 模拟重排序器以防止下载 / Mock reranker to prevent download
    monkeypatch.setattr(embedding_manager, "rerank_candidates_with_qwen3", lambda *args, **kwargs: [])

    # 确保MODEL_INSTANCE已设置 / Ensure MODEL_INSTANCE is set
    embedding_manager.MODEL_INSTANCE = mock_model

    # 模拟_get_tokenizer以防止下载 / Mock _get_tokenizer to prevent download
    monkeypatch.setattr(embedding_manager, "_get_tokenizer", lambda: MagicMock())

# 注意：夹具在这里重新定义。如果一起运行测试，考虑使用共享的conftest.py
# NOTE: Fixtures are redefined here. If running tests together, consider a shared conftest.py

@pytest.fixture(scope="function")
def clear_cache_fixture():
    """
    测试夹具：确保每个测试函数运行前后缓存状态清洁
    Test Fixture: Ensure clean cache state before and after each test function

    目的：通过analyze_project隐式需要缓存清理
    Purpose: Needed by some tests implicitly via analyze_project potentially
    """
    # 测试前清除所有缓存 / Clear all caches before test
    clear_all_caches()
    # 让测试函数执行 / Let test function execute
    yield
    # 测试后清除所有缓存 / Clear all caches after test
    clear_all_caches()

@pytest.fixture(scope="session")
def temp_test_dir(tmp_path_factory):
    """
    测试夹具：创建测试会话唯一的临时目录
    Test Fixture: Create a temporary directory unique to the test session

    目的：提供隔离的测试环境
    Purpose: Provide an isolated test environment
    """
    # 创建名为"cache_tests_integration"的唯一临时目录
    # Create unique temporary directory named "cache_tests_integration"
    return tmp_path_factory.mktemp("cache_tests_integration")

@pytest.fixture(scope="function")
def test_project(temp_test_dir):
    """
    测试夹具：设置用于所有IS测试的最小临时项目结构
    Test Fixture: Set up a minimal temporary project structure for all IS tests

    目的：创建包含必要文件和目录的完整测试项目
    Purpose: Create a complete test project with necessary files and directories

    项目结构 / Project structure:
        test_project_is/
        ├── .clinerules              # 项目标记文件（包含根目录配置）
        ├── .clinerules.config.json  # 配置文件
        ├── src/                     # 源代码目录
        │   ├── module_a.py          # 测试模块A（求和函数）
        │   └── module_b.py          # 测试模块B（用户类）
        ├── docs/                    # 文档目录
        │   └── readme.md
        ├── cline_docs/              # 内存文件目录（跟踪器存储）
        ├── lib/                     # 库目录（用于IS-03测试）
        │   └── helper.py
        └── cache/                   # 缓存目录
            └── embeddings/          # 嵌入向量目录

    用于的测试 / Used by tests:
        - IS-01: 源文件修改
        - IS-02: 配置文件排除
        - IS-03: .clinerules根目录修改
        - IS-04: 嵌入向量重新生成
    """
    # 创建项目目录路径（唯一名称） / Create project directory path (unique name)
    project_dir = temp_test_dir / "test_project_is"
    # 创建项目目录 / Create project directory
    project_dir.mkdir(exist_ok=True)

    # 重置ConfigManager单例以确保它获取新的项目根
    # Reset ConfigManager singleton to ensure it picks up the new project root
    config_manager.ConfigManager._instance = None

    # 创建空的.clinerules文件（IS-03需要）/ Create empty .clinerules (IS-03 needs this)
    (project_dir / ".clinerules").touch()

    # 创建基础配置 / Create base config
    base_config = {
        "paths": {
            "doc_dir": "docs",  # 文档目录
            "memory_dir": "cline_docs",  # 内存目录
            "cache_dir": "cache",  # 缓存目录
            "embeddings_dir": "cache/embeddings"  # 明确设置以匹配测试期望
        },
        "exclusions": {
            "dirs": [".git", "venv"],  # 排除的目录
            "files": ["*.log"]  # 排除的文件
        },
        "thresholds": {
            "code_similarity": 0.7  # 代码相似度阈值
        }
    }
    # 写入配置文件（IS-02需要）/ Write config file (IS-02 needs this)
    (project_dir / ".clinerules.config.json").write_text(json.dumps(base_config))

    # 创建src目录 / Create src directory
    (project_dir / "src").mkdir(exist_ok=True)
    # 创建内容不同的模块以避免意外的语义相似性('S')
    # Make content distinct to avoid accidental semantic similarity ('S')
    (project_dir / "src" / "module_a.py").write_text("def calculate_sum(a, b):\n    return a + b")
    (project_dir / "src" / "module_b.py").write_text("class UserProfile:\n    def __init__(self, name):\n        self.name = name")

    # 创建docs目录（IS-03需要）/ Create docs directory (IS-03 needs this)
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "docs" / "readme.md").write_text("# Test Readme")

    # 创建cline_docs目录（跟踪器路径需要）/ Create cline_docs directory (needed for tracker path)
    (project_dir / "cline_docs").mkdir(exist_ok=True)

    # 创建lib目录（IS-03需要此根目录）/ Create lib directory (IS-03 needs this root dir)
    (project_dir / "lib").mkdir(exist_ok=True)
    (project_dir / "lib" / "helper.py").write_text("def helper_func(): return 1")

    # 为IS-04创建虚拟缓存目录和嵌入文件
    # Create dummy cache dir and embedding files for IS-04
    cache_dir = project_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    embedding_dir = cache_dir / "embeddings"
    embedding_dir.mkdir(exist_ok=True)
    # 只有在不存在时才创建虚拟嵌入 - analyze_project应该创建它们
    # Create dummy embeddings ONLY if they don't exist - analyze_project should create them
    # 注释掉，让analyze_project初始创建它们更好
    # Commented out, better to let analyze_project create them initially

    # 为IS-03写入初始的.clinerules内容 / Write initial .clinerules for IS-03
    initial_clinerules_content = """
[COUNT]
n + 1 = (x)
[LAST_ACTION_STATE]
last_action: "Test Init IS03"
current_phase: "Execution"
next_action: "Complete Test"
next_phase: "Execution"
---
[CODE_ROOT_DIRECTORIES]
- src
[DOC_DIRECTORIES]
- docs
[LEARNING_JOURNAL]
- Test entry.
[Character_Definitions]
```
- <: Row depends on column.
```
---
**IMPORTANT**
1. Understand the Objective
"""
    # 写入.clinerules内容 / Write .clinerules content
    (project_dir / ".clinerules").write_text(initial_clinerules_content)

    # 保存当前工作目录 / Save current working directory
    original_cwd = os.getcwd()
    # 切换到项目目录 / Change to project directory
    os.chdir(project_dir)
    # 让测试函数使用此项目 / Let test function use this project
    yield project_dir
    # 测试后恢复原工作目录 / Restore original working directory after test
    os.chdir(original_cwd)

# ========================================
# 集成测试用例 (IS-01到IS-04)
# Integration Tests (IS-01 to IS-04)
# ========================================


def test_is01_source_file_modification(test_project):
    """
    测试用例IS-01：验证源文件修改后analyze_project正确更新跟踪器
    Test Case IS-01: Verify analyze_project updates trackers correctly after source file change

    目的：测试源代码文件修改时，依赖分析系统能否正确检测并更新依赖关系
    Purpose: Test if dependency analysis system correctly detects and updates dependencies when source files are modified

    测试场景：
    1. 初始分析运行 - 生成基础跟踪器
    2. 修改源文件添加依赖 - module_a导入module_b
    3. 再次分析 - 验证依赖字符从'p'/'n'变为'<'或其他依赖标记

    Test scenarios:
    1. Initial analysis run - generate baseline tracker
    2. Modify source file to add dependency - module_a imports module_b
    3. Run analysis again - verify dependency char changes from 'p'/'n' to '<' or other dependency marker

    涉及的缓存：
    - 文件内容缓存（基于mtime）
    - 依赖分析缓存
    - 跟踪器读取缓存

    Caches involved:
    - File content cache (mtime-based)
    - Dependency analysis cache
    - Tracker read cache

    测试流程详解 / Detailed Test Flow:
    1. 初始状态：module_a和module_b互相独立，无导入关系
    2. 运行首次分析：系统扫描文件，生成依赖网格，无直接依赖
    3. 修改module_a：添加"import module_b"，建立显式依赖
    4. 文件mtime更新：触发缓存失效机制
    5. 再次分析：系统检测到mtime变化，重新分析module_a
    6. 验证依赖更新：网格中module_a对module_b的字符应从'p'变为'<'

    缓存失效机制 / Cache Invalidation Mechanism:
    - analyze_file函数会检查文件mtime
    - 如果mtime比缓存中的新，自动失效该文件的分析结果
    - 下游缓存（如依赖网格）也会相应更新
    - 这确保了增量分析的正确性
    """
    # 获取项目根目录，用于后续路径构建和验证
    # Get project root directory for subsequent path construction and validation
    project_root = test_project
    # 使用src的mini-tracker检查文件级依赖
    # Use mini-tracker for src to check file-level dependencies
    # tracker_path将在分析运行后确定
    # tracker_path will be determined after analysis runs

    # 不需要为此测试模拟clear_all_caches
    # No need to mock clear_all_caches for this test.
    # 我们依赖analyze_project基于mtime的内部缓存失效
    # We rely on analyze_project's internal cache invalidation based on mtime.

    # ===== 步骤1：初始分析运行 / Step 1: Initial analysis run =====
    print("\nRunning analyze_project (initial run)...")
    try:
        # 使用force_analysis=True确保基于当前状态生成跟踪器
        # Use force_analysis=True to ensure trackers are generated based on current state
        # 这会强制重新分析所有文件，忽略任何现有缓存
        # This forces re-analysis of all files, ignoring any existing cache
        # 对于集成测试的基线建立非常重要
        # Critical for establishing baseline in integration tests
        results1 = analyze_project(force_analysis=True)
    except Exception as e:
        # 如果初始分析失败，测试失败 / If initial analysis fails, fail the test
        # 打印详细错误信息以便调试 / Print detailed error for debugging
        pytest.fail(f"Initial analyze_project failed: {e}")

    # 检查跟踪器文件是否存在并读取其初始状态
    # Check if tracker file exists and read its initial state
    # 刷新路径以防它刚被创建 / Refresh path in case it was just created
    tracker_path = get_mini_tracker_path(project_root, "src")
    if not tracker_path or not tracker_path.exists():
        # 如果文件存在，analyze_project必须创建跟踪器
        # analyze_project MUST create the tracker if files are present
        pytest.fail(f"Initial run failed to create tracker file in src: {tracker_path}")

    # 读取跟踪器数据 / Read tracker data
    tracker_data1 = read_tracker_file_compat(str(tracker_path))
    if not tracker_data1 or 'grid' not in tracker_data1 or 'keys' not in tracker_data1:
        # 验证数据有效性 / Verify data validity
        pytest.fail("Could not read valid initial tracker data.")
    # 获取网格和键映射 / Get grid and keys map
    grid1 = tracker_data1['grid']
    keys1_map = tracker_data1['keys']  # 为清晰重命名 / Renamed for clarity

    # 使用normalize_path查找对应测试文件的键以保持一致性
    # Find keys corresponding to the test files using normalize_path for consistency
    module_a_norm_path = path_utils.normalize_path(str(project_root / "src" / "module_a.py"))
    module_b_norm_path = path_utils.normalize_path(str(project_root / "src" / "module_b.py"))

    # 在键映射中查找module_a和module_b的键 / Find keys for module_a and module_b in keys map
    key_a = next((k for k, p in keys1_map.items() if path_utils.normalize_path(p) == module_a_norm_path), None)
    key_b = next((k for k, p in keys1_map.items() if path_utils.normalize_path(p) == module_b_norm_path), None)

    # 验证键是否找到 / Verify keys were found
    if not key_a or not key_b:
        print(f"Keys found: {keys1_map}")
        print(f"Looking for: {module_a_norm_path} and {module_b_norm_path}")
        pytest.fail(f"Could not find keys for module_a.py or module_b.py in initial tracker.")

    # 验证初始时a和b之间没有依赖
    # Verify initially no dependency between a and b
    # module_a.py: "def calculate_sum(a, b): return a + b"
    # module_b.py: "class UserProfile: ..."
    # 两者都不导入对方，因此依赖字符应该是'p'（占位符）或'n'（无）
    # Neither imports the other, so dependency char should be 'p' (placeholder) or 'n' (none)
    sorted_keys1 = sort_key_strings_hierarchically(list(keys1_map.keys()))
    initial_dep_char = get_char_at_key(grid1, key_a, key_b, sorted_keys1)
    print(f"Initial dependency char {key_a} -> {key_b}: '{initial_dep_char}'")
    # 断言：初始依赖字符应为'p'、'n'或'?' / Assertion: Initial dependency char should be 'p', 'n', or '?'
    assert initial_dep_char in ('p', 'n', '?'), f"Initial dependency char expected to be 'p', 'n', or '?', but got '{initial_dep_char}'"

    # ===== 步骤2：修改源文件以添加依赖 / Step 2: Modify source file to add dependency =====
    # 构建module_a的完整路径 / Build complete path to module_a
    module_a_path_obj = project_root / "src" / "module_a.py"
    print(f"Modifying {module_a_path_obj} to import module_b...")
    # 添加导入语句以创建显式依赖关系
    # Add import statement to create explicit dependency
    # 原内容："def calculate_sum(a, b): return a + b"
    # Original content: "def calculate_sum(a, b): return a + b"
    # 新内容：添加"import module_b"在开头
    # New content: Add "import module_b" at the beginning
    # 这将建立module_a -> module_b的单向依赖
    # This will establish a unidirectional dependency from module_a to module_b
    module_a_path_obj.write_text("import module_b\n\ndef calculate_sum(a, b):\n    return a + b")
    # 确保mtime变化，某些文件系统的时间戳精度可能较低
    # Ensure mtime change, some filesystems have low timestamp precision
    # 0.1秒的延迟足以确保大多数系统能检测到变化
    # 0.1s delay is sufficient for most systems to detect change
    time.sleep(0.1)

    # ===== 步骤3：修改后再次运行分析 / Step 3: Run analysis again after modification =====
    print("Running analyze_project (after modification)...")
    # 依赖analyze_project的内部缓存处理（analyze_file中的mtime检查）
    # Rely on analyze_project's internal cache handling (mtime checks in analyze_file)
    try:
        # 不强制，让缓存工作（除了修改的文件） / Don't force, let caching work (except for modified file)
        results2 = analyze_project()
    except Exception as e:
        pytest.fail(f"Second analyze_project run failed: {e}")

    # ===== 步骤4：比较跟踪器网格 / Step 4: Compare tracker grid =====
    tracker_path = get_mini_tracker_path(project_root, "src")
    if not tracker_path or not tracker_path.exists():
        pytest.fail(f"Tracker file missing after second run: {tracker_path}")

    # 读取修改后的跟踪器数据 / Read tracker data after modification
    tracker_data2 = read_tracker_file_compat(str(tracker_path))
    if not tracker_data2 or 'grid' not in tracker_data2 or 'keys' not in tracker_data2:
        pytest.fail("Could not read valid tracker data after modification.")
    grid2 = tracker_data2['grid']
    # 如果分析添加/删除文件，键可能会改变 / Keys might change if analysis adds/removes files
    keys2_map = tracker_data2['keys']

    # 重新查找键以防它们改变（这里不太可能但良好实践）
    # Re-find keys in case they changed (unlikely here but good practice)
    key_a_new = next((k for k, p in keys2_map.items() if path_utils.normalize_path(p) == module_a_norm_path), None)
    key_b_new = next((k for k, p in keys2_map.items() if path_utils.normalize_path(p) == module_b_norm_path), None)

    # 验证键仍然存在 / Verify keys still exist
    if not key_a_new or not key_b_new:
        pytest.fail(f"Could not find keys in second tracker. Keys: {keys2_map}")
    # 断言：键应该保持稳定 / Assertion: Keys should ideally be stable
    assert key_a_new == key_a
    assert key_b_new == key_b

    # 验证依赖字符已更改 / Verify the dependency character changed
    sorted_keys2 = sort_key_strings_hierarchically(list(keys2_map.keys()))
    final_dep_char = get_char_at_key(grid2, key_a, key_b, sorted_keys2)
    print(f"Final dependency char {key_a} -> {key_b}: '{final_dep_char}'")
    # 期望'<'（module_a依赖module_b，基于夹具定义）
    # Expect '<' (module_a depends on module_b, based on fixture definition)
    # 或'x'（如果检测到相互依赖） / or 'x' (if reciprocal detected)
    # 如果语义分析检测到而不是静态导入，允许's'或'S'
    # Allow 's' or 'S' if semantic analysis picks it up instead of static import
    assert final_dep_char in ('<', 'x', 's', 'S'), f"Expected dependency char '<', 'x', 's', or 'S', but got '{final_dep_char}'"
    # 断言：依赖字符在修改后必须改变 / Assertion: Dependency character must change after modification
    assert final_dep_char != initial_dep_char, "Dependency character did not change after modification"


def test_is02_config_file_exclusion(test_project, monkeypatch, clear_cache_fixture):
    """
    测试用例IS-02：验证配置文件修改（排除规则）后analyze_project移除键
    Test Case IS-02: Verify analyze_project removes keys for newly excluded files

    目的：测试配置文件的exclusion规则修改时，系统能否正确从跟踪器中移除被排除的文件
    Purpose: Test if system correctly removes excluded files from tracker when config exclusion rules are modified

    测试场景：
    1. 初始分析 - module_b.py在跟踪器中
    2. 修改配置文件排除module_b.py
    3. 再次分析 - 验证module_b.py的键已从跟踪器中移除

    Test scenarios:
    1. Initial analysis - module_b.py is in tracker
    2. Modify config to exclude module_b.py
    3. Run analysis again - verify module_b.py key removed from tracker

    涉及的缓存：
    - 配置文件缓存（基于mtime）
    - excluded_paths缓存
    - 文件扫描缓存

    Caches involved:
    - Config file cache (mtime-based)
    - excluded_paths cache
    - File scanning cache

    测试流程详解 / Detailed Test Flow:
    1. 初始配置：excluded_paths列表为空或不包含module_b.py
    2. 首次分析：module_b.py被扫描、分析并添加到跟踪器
    3. 修改配置：在excluded_paths中添加"src/module_b.py"
    4. 配置mtime更新：触发ConfigManager缓存失效
    5. 再次分析：系统重新读取配置，跳过被排除的文件
    6. 验证移除：跟踪器中不再包含module_b.py的键

    缓存失效链 / Cache Invalidation Chain:
    .clinerules.config.json mtime变化
    → ConfigManager.config_data缓存失效
    → get_excluded_paths缓存失效
    → is_valid_project_path缓存失效（对于被排除的路径）
    → 文件扫描跳过被排除的文件
    → 跟踪器不包含被排除文件的键
    """
    # 不需要为此测试模拟clear_all_caches
    # No need to mock clear_all_caches for this test.
    # 我们依赖analyze_project正确获取配置更改，
    # We rely on analyze_project picking up config changes correctly,
    # 隐式使用失效的配置依赖缓存
    # implicitly using invalidated config-dependent caches.

    # 获取项目根目录 / Get project root directory
    project_root = test_project
    # 获取src的mini-tracker路径 / Get mini-tracker path for src
    tracker_path = get_mini_tracker_path(project_root, "src")
    # 获取配置文件路径 / Get config file path
    config_path = project_root / ".clinerules.config.json"
    # 定义要排除的文件相对路径 / Define relative path of file to exclude
    file_to_exclude_rel = "src/module_b.py"
    # 获取要排除文件的规范化绝对路径 / Get normalized absolute path of file to exclude
    file_to_exclude_abs_norm = path_utils.normalize_path(str(project_root / file_to_exclude_rel))

    # 验证初始跟踪器文件存在 / Verify initial tracker file exists
    if not tracker_path or not tracker_path.exists():
        pytest.fail(f"Initial run did not create tracker file: {tracker_path}")

    # ===== 步骤1：读取初始跟踪器并验证module_b在其中 / Step 1: Read initial tracker and verify module_b is in it =====
    tracker_data1 = read_tracker_file_compat(str(tracker_path))
    if not tracker_data1 or 'keys' not in tracker_data1:
        pytest.fail("Could not read valid initial tracker data.")
    keys1_map = tracker_data1['keys']

    # 在初始跟踪器中查找module_b的键 / Find key for module_b in initial tracker
    key_b_initial = next((k for k, p in keys1_map.items() if path_utils.normalize_path(p) == file_to_exclude_abs_norm), None)
    # 断言：module_b的键必须存在 / Assertion: Key for module_b must exist
    assert key_b_initial is not None, f"Key for {file_to_exclude_rel} not found in initial tracker."
    print(f"Initial tracker contains key '{key_b_initial}' for {file_to_exclude_rel}.")

    # ===== 步骤2：修改配置文件以排除module_b.py / Step 2: Modify config file to exclude module_b.py =====
    print(f"Modifying {config_path} to exclude {file_to_exclude_rel}...")
    try:
        # 读取当前配置 / Read current config
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        # 确保excluded_paths列表存在 / Ensure excluded_paths list exists
        if 'excluded_paths' not in config_data:
            config_data['excluded_paths'] = []

        # 将相对路径添加到excluded_paths / Add relative path to excluded_paths
        config_data['excluded_paths'].append(file_to_exclude_rel)

        # 写入修改后的配置 / Write modified config
        config_path.write_text(json.dumps(config_data, indent=4))
        # 确保mtime变化 / Ensure mtime change
        time.sleep(0.1)
    except Exception as e:
        pytest.fail(f"Failed to modify config file: {e}")

    # 清除ConfigManager单例实例以强制重新加载
    # Clear ConfigManager singleton instance to force reload on next call
    monkeypatch.setattr(config_manager, '_instance', None, raising=False)

    # 显式使ConfigManager缓存失效以避免mtime分辨率问题
    # Explicitly invalidate ConfigManager caches to avoid mtime resolution issues
    # （文件系统mtime分辨率可能> 0.1s，导致过时的缓存命中）
    # (Filesystem mtime resolution might be > 0.1s, causing stale cache hits)
    from cline_utils.dependency_system.utils.cache_manager import cache_manager as cm
    cm.get_cache("config_data").invalidate(".*")
    cm.get_cache("excluded_paths").invalidate(".*")
    cm.get_cache("excluded_dirs").invalidate(".*")
    cm.get_cache("excluded_extensions").invalidate(".*")

    # ===== 步骤3：配置修改后再次运行分析 / Step 3: Run analysis again after config modification =====
    print("Running analyze_project (after config exclusion)...")
    try:
        # 依赖ConfigManager中的配置mtime检查和下游缓存失效
        # Rely on config mtime check in ConfigManager and downstream cache invalidation
        results2 = analyze_project()
    except Exception as e:
        pytest.fail(f"Second analyze_project run failed: {e}")

    # ===== 步骤4：验证键已从跟踪器中移除 / Step 4: Verify key removal from tracker =====
    tracker_path = get_mini_tracker_path(project_root, "src")
    if not tracker_path or not tracker_path.exists():
        pytest.fail(f"Tracker file missing after second run: {tracker_path}")

    # 读取修改后的跟踪器数据 / Read tracker data after modification
    tracker_data2 = read_tracker_file_compat(str(tracker_path))
    if not tracker_data2 or 'keys' not in tracker_data2:
        pytest.fail("Could not read valid tracker data after modification.")
    keys2_map = tracker_data2['keys']

    # 尝试在最终跟踪器中查找module_b的键 / Try to find key for module_b in final tracker
    key_b_final = next((k for k, p in keys2_map.items() if path_utils.normalize_path(p) == file_to_exclude_abs_norm), None)
    # 断言：被排除文件的键必须不存在 / Assertion: Key for excluded file must not exist
    assert key_b_final is None, f"Key for excluded file {file_to_exclude_rel} was found in final tracker (key: {key_b_final})."
    print(f"Verified: Key for excluded file {file_to_exclude_rel} correctly removed from tracker.")


def test_is03_clinerules_modification_roots(test_project):
    """
    测试用例IS-03：验证.clinerules修改（根目录）后analyze_project获取新根
    Test Case IS-03: Verify analyze_project picks up new roots from modified .clinerules

    目的：测试.clinerules文件中根目录配置修改时，系统能否正确扫描并跟踪新根目录下的文件
    Purpose: Test if system correctly scans and tracks files in new root directories when .clinerules root configuration is modified

    测试场景：
    1. 初始分析 - 只有'src'作为代码根
    2. 修改.clinerules添加'lib'作为代码根
    3. 再次分析 - 验证lib/helper.py的键已添加到跟踪器

    Test scenarios:
    1. Initial analysis - only 'src' as code root
    2. Modify .clinerules to add 'lib' as code root
    3. Run analysis again - verify lib/helper.py key added to tracker

    涉及的缓存：
    - .clinerules文件缓存（基于mtime）
    - code_roots缓存
    - 文件扫描缓存

    Caches involved:
    - .clinerules file cache (mtime-based)
    - code_roots cache
    - File scanning cache

    测试流程详解 / Detailed Test Flow:
    1. 初始.clinerules：[CODE_ROOT_DIRECTORIES]只包含"- src"
    2. 首次分析：只扫描src目录，lib/helper.py被忽略
    3. 修改.clinerules：在[CODE_ROOT_DIRECTORIES]添加"- lib"
    4. .clinerules mtime更新：触发根目录缓存失效
    5. 再次分析：系统重新读取根目录配置，扫描lib目录
    6. 验证新跟踪器：lib目录有自己的mini-tracker，包含helper.py

    关键设计点 / Key Design Points:
    - .clinerules是项目结构的权威来源
    - 根目录变化会影响整个项目的文件扫描范围
    - 每个根目录有独立的mini-tracker文件
    - ConfigManager监控.clinerules的mtime变化
    - 缓存失效确保新根目录被正确识别和处理
    """
    # 不需要为此测试模拟clear_all_caches
    # No need to mock clear_all_caches for this test.
    # 我们依赖analyze_project正确获取.clinerules更改，
    # We rely on analyze_project picking up .clinerules changes correctly,
    # 隐式使用失效的缓存（例如，用于根目录）
    # implicitly using invalidated caches (e.g., for root dirs).

    # 获取项目根目录 / Get project root directory
    project_root = test_project
    # 我们将查找'lib'的新跟踪器 / We will look for the NEW tracker for 'lib'
    # 获取.clinerules文件路径 / Get .clinerules file path
    clinerules_path = project_root / ".clinerules"
    # 定义新根目录相对路径 / Define new root directory relative path
    new_root_rel = "lib"
    # 定义新文件相对路径 / Define new file relative path
    new_file_rel = f"{new_root_rel}/helper.py"
    # 获取新文件的规范化绝对路径 / Get normalized absolute path of new file
    new_file_abs_norm = path_utils.normalize_path(str(project_root / new_file_rel))

    # 初始.clinerules内容现在在夹具中设置
    # Initial .clinerules content is now set up in the fixture

    # ===== 步骤1：初始分析运行（仅'src'作为代码根）/ Step 1: Initial analysis run (with only 'src' as code root) =====
    print("\nRunning analyze_project (initial run for IS-03)...")
    try:
        results1 = analyze_project(force_analysis=True)
    except Exception as e:
        pytest.fail(f"Initial analyze_project failed: {e}")

    # 初始运行只有src，因此lib跟踪器不应存在（或我们检查src跟踪器）
    # Initial run only has src, so lib tracker shouldn't exist (or we check src tracker)
    # 但我们想验证'helper.py'未被跟踪
    # But we want to verify 'helper.py' is NOT tracked.
    # 它不应该在src跟踪器中 / It shouldn't be in src tracker.
    tracker_path_src = get_mini_tracker_path(project_root, "src")
    if not tracker_path_src or not tracker_path_src.exists():
        pytest.fail("Initial run did not create src tracker.")

    # 读取初始跟踪器数据 / Read initial tracker data
    tracker_data1 = read_tracker_file_compat(str(tracker_path_src))
    if not tracker_data1 or 'keys' not in tracker_data1:
        pytest.fail("Could not read valid initial tracker data.")
    keys1_map = tracker_data1['keys']
    # 在初始跟踪器中查找helper.py的键 / Find key for helper.py in initial tracker
    key_helper_initial = next((k for k, p in keys1_map.items() if path_utils.normalize_path(p) == new_file_abs_norm), None)
    # 断言：helper.py不应在初始跟踪器中（因为'lib'不是根）
    # Assertion: helper.py should not be in initial tracker (as 'lib' was not a root)
    assert key_helper_initial is None, f"Key for {new_file_rel} found in initial tracker, but 'lib' was not a root."

    # ===== 步骤2：修改.clinerules添加'lib'作为代码根 / Step 2: Modify .clinerules to add 'lib' as code root =====
    print(f"Modifying {clinerules_path} to add '{new_root_rel}' to CODE_ROOT_DIRECTORIES...")
    try:
        # 读取当前内容 / Read current content
        current_content = clinerules_path.read_text()
        # 简单的字符串替换 - 可能比较脆弱 / Simple string replacement - might be fragile
        modified_content = current_content.replace(
            "[CODE_ROOT_DIRECTORIES]\n- src",
            f"[CODE_ROOT_DIRECTORIES]\n- src\n- {new_root_rel}"
        )
        # 如果模式不匹配则回退 / Fallback if pattern didn't match
        if modified_content == current_content:
            pytest.fail("Could not find '[CODE_ROOT_DIRECTORIES]\n- src' to modify in .clinerules")

        # 写入修改后的内容 / Write modified content
        clinerules_path.write_text(modified_content)
        # 确保mtime变化 / Ensure mtime change
        time.sleep(0.1)
    except Exception as e:
        pytest.fail(f"Failed to modify .clinerules file: {e}")

    # 依赖于.clinerules mtime的缓存应该失效
    # Caches depending on .clinerules mtime should invalidate.
    # 这包括ConfigManager读取根目录，可能还有path_utils.get_project_root
    # This includes ConfigManager reading roots, and potentially path_utils.get_project_root
    from cline_utils.dependency_system.utils.cache_manager import cache_manager as cm
    cm.get_cache("code_roots").invalidate(".*")
    cm.get_cache("doc_dirs").invalidate(".*")

    # ===== 步骤3：.clinerules修改后再次运行分析 / Step 3: Run analysis again after .clinerules modification =====
    print("Running analyze_project (after .clinerules modification)...")
    try:
        # ConfigManager应该由于其内部的mtime变化检查或其缓存装饰器而重新加载
        # ConfigManager should reload due to mtime change check within it or its cache decorator
        # analyze_project使用ConfigManager获取根目录
        # analyze_project uses ConfigManager to get roots
        results2 = analyze_project()
    except Exception as e:
        pytest.fail(f"Second analyze_project run failed: {e}")

    # ===== 步骤4：验证新键存在于跟踪器中 / Step 4: Verify new key exists in tracker =====
    # 现在检查lib跟踪器 / Now check for lib tracker
    tracker_path_lib = get_mini_tracker_path(project_root, "lib")
    if not tracker_path_lib or not tracker_path_lib.exists():
        pytest.fail(f"Tracker file for 'lib' missing after second run.")

    # 读取修改后的跟踪器数据 / Read tracker data after modification
    tracker_data2 = read_tracker_file_compat(str(tracker_path_lib))
    if not tracker_data2 or 'keys' not in tracker_data2:
        pytest.fail("Could not read valid tracker data after modification.")
    keys2_map = tracker_data2['keys']

    # 在最终跟踪器中查找helper.py的键 / Find key for helper.py in final tracker
    key_helper_final = next((k for k, p in keys2_map.items() if path_utils.normalize_path(p) == new_file_abs_norm), None)
    # 断言：新添加的根文件的键必须存在 / Assertion: Key for newly added root file must exist
    assert key_helper_final is not None, f"Key for newly added root file {new_file_rel} was NOT found in final tracker."
    print(f"Verified: Key '{key_helper_final}' for new root file {new_file_rel} correctly added to tracker.")


def test_is04_embedding_regeneration(test_project):
    """
    测试用例IS-04：验证--force-embeddings工作且相似度缓存更新
    Test Case IS-04: Verify --force-embeddings works and similarity cache updates

    目的：测试强制重新生成嵌入向量时，相似度计算缓存能否正确更新以使用新数据
    Purpose: Test if similarity calculation cache correctly updates to use new data when forcing embedding regeneration

    测试场景：
    1. 初始分析 - 生成嵌入并计算基线相似度
    2. 修改源文件内容
    3. 使用--force-embeddings运行分析
    4. 验证相似度分数已更改（证明缓存使用了新嵌入）

    Test scenarios:
    1. Initial analysis - generate embeddings and calculate baseline similarity
    2. Modify source file content
    3. Run analysis with --force-embeddings
    4. Verify similarity score changed (proving cache used new embeddings)

    涉及的缓存：
    - 嵌入文件缓存
    - 相似度计算缓存
    - 文件内容缓存

    Caches involved:
    - Embedding file cache
    - Similarity calculation cache
    - File content cache

    测试流程详解 / Detailed Test Flow:
    1. 初始分析：为module_a和module_b生成嵌入向量（.npy文件）
    2. 计算相似度：使用calculate_similarity获取基线分数
    3. 修改module_a：改变文件内容，影响嵌入向量
    4. 强制重新生成：force_embeddings=True删除旧嵌入并重新计算
    5. 新嵌入：基于新文件内容生成不同的向量
    6. 相似度变化：新向量导致不同的相似度分数
    7. 验证更新：分数变化证明缓存正确失效并使用新数据

    关键机制 / Key Mechanisms:
    - force_embeddings标志触发嵌入文件删除
    - 文件内容变化 → 嵌入向量变化 → 相似度变化
    - 相似度缓存键包含文件键，但不包含文件内容哈希
    - 强制重新生成确保缓存使用最新的嵌入数据
    - 这对于内容变化但文件结构不变的情况很重要

    注意事项 / Notes:
    - 使用确定性模拟嵌入模型（基于文本哈希）
    - 相同文本→相同嵌入，不同文本→不同嵌入
    - 避免下载真实的语言模型，加快测试速度
    """
    # 不需要模拟clear_all_caches或calculate_similarity
    # No mocking needed for clear_all_caches or calculate_similarity.
    # 我们想在强制嵌入重新生成后测试*真实*交互
    # We want to test the *real* interaction after forced embedding regeneration.

    # 获取项目根目录 / Get project root directory
    project_root = test_project
    # 获取src的mini-tracker路径 / Get mini-tracker path for src
    tracker_path = get_mini_tracker_path(project_root, "src")
    # 定义测试文件相对路径 / Define test file relative paths
    module_a_rel = "src/module_a.py"
    module_b_rel = "src/module_b.py"
    # 获取规范化的绝对路径 / Get normalized absolute paths
    module_a_abs_norm = path_utils.normalize_path(str(project_root / module_a_rel))
    module_b_abs_norm = path_utils.normalize_path(str(project_root / module_b_rel))

    # 如果需要，定义相似度缓存名称用于统计（这里可选）
    # Define cache name for similarity if needed for stats (optional here)
    cache_name_sim = 'calculate_similarity'

    # 确保嵌入目录存在以使calculate_similarity工作
    # Ensure embedding dir exists for calculate_similarity to work
    embedding_dir = project_root / "cache" / "embeddings"
    embedding_dir.mkdir(parents=True, exist_ok=True)
    # 测试环境中的ConfigManager应该指向这个'cache'目录
    # ConfigManager in the test environment should point to this 'cache' dir
    # 因为我们在夹具的base_config中设置了"cache_dir": "cache"
    # because we set "cache_dir": "cache" in the base_config fixture.
    # 我们通过检查目录是否存在来验证这个假设
    # We verify this assumption by checking if the dir exists.
    if not embedding_dir.exists():
        pytest.fail(f"Embedding directory {embedding_dir} was not created.")

    # ===== 步骤1：初始分析运行以建立基线键和嵌入 / Step 1: Initial analysis run to establish baseline keys and embeddings =====
    print("\nRunning analyze_project (initial run for IS-04)...")
    try:
        # 确保生成嵌入 / Ensure embeddings generated
        results1 = analyze_project(force_analysis=True)
    except Exception as e:
        pytest.fail(f"Initial analyze_project failed: {e}")

    # 验证跟踪器文件已创建 / Verify tracker file created
    tracker_path = get_mini_tracker_path(project_root, "src")
    if not tracker_path or not tracker_path.exists():
        pytest.fail("Tracker file not created.")

    # 读取跟踪器数据并获取键映射 / Read tracker data and get key map
    tracker_data1 = read_tracker_file_compat(str(tracker_path))
    keys_map = tracker_data1.get('keys', {})

    # 查找module_a和module_b的键 / Find keys for module_a and module_b
    key_a = next((k for k, p in keys_map.items() if path_utils.normalize_path(p) == module_a_abs_norm), None)
    key_b = next((k for k, p in keys_map.items() if path_utils.normalize_path(p) == module_b_abs_norm), None)
    if not key_a or not key_b:
        pytest.fail("Could not find keys for module_a or module_b.")

    # 为calculate_similarity构建path_to_key_info / Construct path_to_key_info for calculate_similarity
    path_to_key_info = {}
    for k, p in keys_map.items():
        norm_p = path_utils.normalize_path(p)
        parent = path_utils.normalize_path(os.path.dirname(p))
        path_to_key_info[norm_p] = KeyInfo(
            key_string=k,
            norm_path=norm_p,
            parent_path=parent,
            tier=1,  # 虚拟值 / Dummy
            is_directory=False  # 虚拟值 / Dummy
        )

    # 调用真实的相似度函数获取基线 / Call REAL similarity function to get baseline
    print(f"Calculating baseline similarity between {key_a} and {key_b}...")
    initial_sim = embedding_manager.calculate_similarity(
        key_a, key_b,
        str(embedding_dir),
        path_to_key_info,
        str(project_root),
        ["src"],  # code_roots / 代码根目录
        ["docs"]  # doc_roots / 文档根目录
    )
    print(f" -> Initial Similarity: {initial_sim}")
    # 断言：初始相似度应大于0 / Assertion: Initial similarity should be > 0
    assert initial_sim > 0, f"Initial similarity is 0.0, which implies mocking failed or empty embeddings. Sim: {initial_sim}"

    # ===== 步骤2：显著修改源文件 / Step 2: Modify source file significantly =====
    module_a_path_obj = project_root / module_a_rel
    print(f"Modifying {module_a_path_obj} significantly...")
    # 创建完全不同的内容哈希 / Create completely different content hash
    new_content_a = "class NewClass:\n def method(self):\n  pass\n# Completely different content hash"
    module_a_path_obj.write_text(new_content_a)
    # 等待确保mtime变化 / Wait to ensure mtime change
    time.sleep(0.1)

    # ===== 步骤3：使用force_embeddings=True和force_analysis=True运行分析以确保新的SES
    # Step 3: Run analysis with force_embeddings=True AND force_analysis=True to ensure fresh SES =====
    print("Running analyze_project --force-embeddings...")
    try:
        results2 = analyze_project(force_embeddings=True, force_analysis=True)
    except Exception as e:
        pytest.fail(f"analyze_project --force-embeddings run failed: {e}")

    # ===== 步骤4：在强制嵌入运行后手动调用相似度 / Step 4: Call similarity manually *after* forced embedding run =====
    print("Calling REAL similarity calculation *after* force-embeddings run...")
    # 确保键仍然有效（在此场景中它们不应改变） / Ensure keys are still valid (they shouldn't change in this scenario)
    tracker_data2 = read_tracker_file_compat(str(tracker_path))
    keys_map_after = tracker_data2.get('keys', {})
    key_a_after = next((k for k, p in keys_map_after.items() if path_utils.normalize_path(p) == module_a_abs_norm), None)
    key_b_after = next((k for k, p in keys_map_after.items() if path_utils.normalize_path(p) == module_b_abs_norm), None)
    # 断言：键不应意外改变 / Assertion: Keys should not change unexpectedly
    assert key_a_after == key_a, "Key for module_a changed unexpectedly."
    assert key_b_after == key_b, "Key for module_b changed unexpectedly."

    # 再次计算相似度 / Calculate similarity again
    print(f"Calculating final similarity between {key_a} and {key_b}...")
    final_sim = embedding_manager.calculate_similarity(
        key_a, key_b,
        str(embedding_dir),
        path_to_key_info,  # 键不应改变，因此这仍然有效 / Keys shouldn't have changed, so this is still valid
        str(project_root),
        ["src"],
        ["docs"]
    )
    print(f" -> Final Similarity: {final_sim}")

    # ===== 断言：验证相似度分数已更改 / Assertions: Verify similarity score changed =====
    # 检查相似度分数是否改变 / Check that the similarity score changed.
    # 我们使用基于文本哈希的确定性模拟嵌入模型
    # We use a deterministic mock embedding model based on text hash.
    # 由于文件内容显著改变，哈希改变，因此嵌入改变
    # Since the file content changed significantly, the hash changed, so the embedding changed.
    # 因此，相似度分数必须不同 / Therefore, the similarity score MUST be different.
    similarity_change = abs(final_sim - initial_sim)
    # 使用随机向量（randn），相似度通常很低（~0）
    # With random vectors (randn), similarity is usually low (~0).
    # 我们只需要验证分数改变了，证明缓存失效
    # We just need to verify that the score CHANGED, proving cache invalidation.
    # 如果两个分数都接近0，则期望小的变化
    # A small change is expected if both scores are near 0.
    assert similarity_change > 1e-6, f"Similarity score did not change significantly ({similarity_change:.6f}) after modifying file. Cache might not have updated."
    assert final_sim != initial_sim, f"Similarity score ({final_sim}) did not change after modifying file (initial: {initial_sim}). Cache might not have updated."

    print("Verified: Embedding regeneration appears to have triggered use of new data for similarity.")

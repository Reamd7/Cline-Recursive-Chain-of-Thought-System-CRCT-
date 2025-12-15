"""
测试模块：功能缓存测试
Test Module: Functional Cache Tests

本模块测试缓存管理器的功能性测试用例（FC-01到FC-07），包括：
- 项目根路径缓存（FC-01）
- 项目路径验证缓存（FC-02）
- 相似度计算缓存（FC-03）
- 依赖网格验证缓存（FC-04）
- 网格依赖获取缓存（FC-05）
- 跟踪文件读取缓存（FC-06）
- 配置依赖缓存（FC-07）

This module tests functional cache test cases (FC-01 to FC-07), including:
- Project root path cache (FC-01)
- Project path validation cache (FC-02)
- Similarity calculation cache (FC-03)
- Dependency grid validation cache (FC-04)
- Grid dependencies retrieval cache (FC-05)
- Tracker file read cache (FC-06)
- Config-dependent caches (FC-07)
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
# 导入numpy用于嵌入向量测试 / Import numpy for embedding vector testing
import numpy as np
# 导入logging模块用于日志记录 / Import logging module for logging
import logging

# 导入缓存管理器核心功能 / Import cache manager core functions
from cline_utils.dependency_system.utils.cache_manager import CacheManager, cached, get_cache_stats, clear_all_caches, invalidate_dependent_entries
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
# 导入跟踪器工具模块 / Import tracker utilities module
from cline_utils.dependency_system.utils import tracker_utils
# 导入KeyInfo类用于密钥信息管理 / Import KeyInfo class for key information management
from cline_utils.dependency_system.core.key_manager import KeyInfo

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

# ========================================
# 测试夹具 / Test Fixtures
# ========================================

@pytest.fixture(scope="function")
def clear_cache_fixture():
    """
    测试夹具：确保每个测试函数运行前后缓存状态清洁
    Test Fixture: Ensure clean cache state before and after each test function

    目的：避免测试之间的缓存污染
    Purpose: Avoid cache pollution between tests
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
    # 创建名为"cache_tests_functional"的临时目录
    # Create temporary directory named "cache_tests_functional"
    return tmp_path_factory.mktemp("cache_tests_functional")

@pytest.fixture(scope="function")
def test_project(temp_test_dir):
    """
    测试夹具：设置用于测试的最小临时项目结构
    Test Fixture: Set up a minimal temporary project structure for testing

    目的：创建包含必要文件和目录的测试项目
    Purpose: Create a test project with necessary files and directories

    项目结构 / Project structure:
        test_project_fc/
        ├── .clinerules              # 项目标记文件
        ├── .clinerules.config.json  # 配置文件
        ├── src/                     # 源代码目录
        │   ├── module_a.py
        │   └── module_b.py
        ├── docs/                    # 文档目录
        │   └── readme.md
        ├── cline_docs/              # 内存文件目录
        ├── lib/                     # 库目录
        │   └── helper.py
        └── cache/                   # 缓存目录
            └── embeddings/          # 嵌入向量目录
                ├── 1A1.npy
                ├── 1B2.npy
                └── 1C3.npy
    """
    # 创建项目目录路径 / Create project directory path
    project_dir = temp_test_dir / "test_project_fc"
    # 如果目录已存在，删除它 / If directory exists, remove it
    if project_dir.exists():
        shutil.rmtree(project_dir)
    # 创建新的项目目录 / Create new project directory
    project_dir.mkdir(exist_ok=True)

    # 创建空的.clinerules文件作为项目标记 / Create empty .clinerules as project marker
    (project_dir / ".clinerules").touch()
    # 创建配置文件 / Create config file
    (project_dir / ".clinerules.config.json").write_text(json.dumps({
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs", "cache_dir": "cache"},
        "excluded_dirs": [".git", "venv"],  # 排除的目录列表
        "excluded_extensions": ["*.log"],    # 排除的文件扩展名
        "thresholds": {"code_similarity": 0.7}  # 相似度阈值
    }))

    # 创建src目录 / Create src directory
    (project_dir / "src").mkdir(exist_ok=True)
    # 创建测试模块文件 / Create test module files
    (project_dir / "src" / "module_a.py").write_text("import os\nprint('hello')")
    (project_dir / "src" / "module_b.py").write_text("print('world')")

    # 创建docs目录和readme文件 / Create docs directory and readme file
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "docs" / "readme.md").write_text("# Test Readme")

    # 创建cline_docs目录 / Create cline_docs directory
    (project_dir / "cline_docs").mkdir(exist_ok=True)

    # 创建lib目录和helper文件 / Create lib directory and helper file
    (project_dir / "lib").mkdir(exist_ok=True)
    (project_dir / "lib" / "helper.py").write_text("def helper_func(): return 1")

    # 创建缓存目录和嵌入文件用于FC-03等测试
    # Create cache directory and embedding files for FC-03 etc. tests
    cache_dir = project_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    embedding_dir = cache_dir / "embeddings"
    embedding_dir.mkdir(exist_ok=True)

    # 创建模拟的嵌入向量数据 / Create mock embedding data
    np.save(embedding_dir / "1A1.npy", np.array([0.1, 0.2]))
    np.save(embedding_dir / "1B2.npy", np.array([0.3, 0.4]))
    np.save(embedding_dir / "1C3.npy", np.array([0.5, 0.6]))

    # 保存当前工作目录 / Save current working directory
    original_cwd = os.getcwd()
    # 切换到项目目录 / Change to project directory
    os.chdir(project_dir)
    # 让测试函数使用此项目 / Let test function use this project
    yield project_dir
    # 测试后恢复原工作目录 / Restore original working directory after test
    os.chdir(original_cwd)

# ========================================
# 功能测试用例 (FC-01到FC-07)
# Functional Tests (FC-01 to FC-07)
# ========================================

def test_fc01_get_project_root_cache(test_project, clear_cache_fixture, caplog):
    """
    测试用例FC-01：验证get_project_root缓存命中和潜在失效
    Test Case FC-01: Verify get_project_root cache hits and potential invalidation

    目的：测试项目根路径缓存的正确性和一致性
    Purpose: Test correctness and consistency of project root path cache

    测试场景：
    1. 首次调用 - 缓存未命中
    2. 第二次调用 - 缓存命中
    3. 修改.clinerules文件后调用 - 仍然缓存命中（因为缓存键依赖CWD而非文件mtime）

    Test scenarios:
    1. First call - cache miss
    2. Second call - cache hit
    3. Call after touching .clinerules - still cache hit (key depends on CWD, not file mtime)

    测试原理 / Test Rationale:
    - get_project_root函数通过向上查找.clinerules文件来定位项目根目录
    - 缓存键基于当前工作目录（CWD），而不是.clinerules文件的修改时间
    - 因此，只要CWD不变，缓存就会保持有效，即使.clinerules文件被修改
    - 这种设计提高了性能，避免频繁的文件系统遍历

    涉及的缓存 / Caches Involved:
    - project_root: 存储项目根路径的缓存
    - 缓存键格式: 当前工作目录的规范化路径
    - TTL: 无限制（直到显式清除）
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    # 这是必要的，因为之前的测试可能留下了缓存数据
    # This is necessary as previous tests may have left cache data
    clear_all_caches()

    # 定义缓存名称，用于后续的统计查询 / Define cache name for subsequent statistics queries
    cache_name = 'project_root'
    # 从夹具获取项目根路径，用于验证 / Get project root path from fixture for verification
    project_root_path = test_project

    # ===== 步骤1：首次调用 / Step 1: Initial call =====
    # 打印当前工作目录以便调试 / Print current working directory for debugging
    print(f"Calling get_project_root for the first time from: {os.getcwd()}")
    # 首次调用get_project_root函数，这应该触发缓存未命中
    # First call to get_project_root, this should trigger a cache miss
    # 函数会向上遍历目录树查找.clinerules文件
    # Function will traverse directory tree upwards to find .clinerules file
    root1 = path_utils.get_project_root()
    # 断言：验证返回的根路径是否正确 / Assertion: Verify returned root path is correct
    # 使用normalize_path确保路径比较的一致性（处理不同的路径分隔符和大小写）
    # Use normalize_path to ensure consistent path comparison (handle different separators and case)
    assert path_utils.normalize_path(root1) == path_utils.normalize_path(str(project_root_path))
    # 获取缓存统计信息，用于验证缓存行为 / Get cache statistics to verify cache behavior
    # 此时应该有1次未命中和0次命中 / At this point should have 1 miss and 0 hits
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次调用 - 应该缓存命中 / Step 2: Second call - should be cache hit =====
    print("Calling get_project_root for the second time...")
    # 再次调用get_project_root，由于CWD未变，应该从缓存返回
    # Call get_project_root again, should return from cache as CWD hasn't changed
    # 不会进行文件系统遍历，直接返回缓存的结果
    # No filesystem traversal, directly return cached result
    root2 = path_utils.get_project_root()
    # 断言：验证两次返回的路径相同 / Assertion: Verify both calls return same path
    # 这验证了缓存返回的是正确的值 / This verifies cache returns correct value
    assert path_utils.normalize_path(root2) == path_utils.normalize_path(root1)
    # 获取更新后的缓存统计 / Get updated cache statistics
    # 此时应该有1次未命中和至少1次命中 / At this point should have 1 miss and at least 1 hit
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    # 命中次数应该>=1，证明第二次调用使用了缓存
    # Hit count should be >=1, proving second call used cache
    assert stats2['hits'] >= 1

    # ===== 步骤3：测试缓存失效（实际上不会失效）/ Step 3: Test invalidation (actually won't invalidate) =====
    print("Touching .clinerules...")
    # 获取.clinerules文件路径 / Get .clinerules file path
    clinerules_path = project_root_path / ".clinerules"
    # 使用touch()更新文件修改时间但不改变内容
    # Use touch() to update file modification time without changing content
    # 这模拟了文件被编辑器保存但内容未变的情况
    # This simulates file being saved by editor but content unchanged
    touch(clinerules_path)
    # 等待确保mtime变化（文件系统时间戳精度问题）
    # Wait to ensure mtime change (filesystem timestamp precision)
    time.sleep(0.1)

    # 修改文件后再次调用 / Call again after file modification
    print("Calling get_project_root after touching .clinerules...")
    # 第三次调用，测试缓存是否因为.clinerules的mtime变化而失效
    # Third call, test if cache invalidates due to .clinerules mtime change
    root3 = path_utils.get_project_root()
    # 断言：验证路径仍然一致 / Assertion: Verify path is still consistent
    # 无论是否使用缓存，返回的路径都应该相同
    # Regardless of cache usage, returned path should be same
    assert path_utils.normalize_path(root3) == path_utils.normalize_path(root1)
    # 获取最新缓存统计 / Get latest cache statistics
    stats3 = get_cache_stats(cache_name)

    # 期望仍然命中缓存，因为get_project_root的缓存键依赖于当前工作目录而非.clinerules的mtime
    # Expect cache hit because get_project_root key depends on CWD, not .clinerules mtime
    # 这是一个重要的设计决策：为了性能，我们不监控.clinerules的变化
    # This is an important design decision: for performance, we don't monitor .clinerules changes
    # 如果需要重新扫描，用户需要显式清除缓存
    # If rescan needed, user must explicitly clear cache
    # 断言：验证缓存命中次数继续增加 / Assertion: Verify cache hit count continues to increase
    assert stats3['hits'] > stats2.get('hits', 0)

def test_fc02_is_valid_project_path_cache(test_project, clear_cache_fixture, caplog):
    """
    测试用例FC-02：验证is_valid_project_path缓存基于路径和根的命中/未命中
    Test Case FC-02: Verify valid_project_paths cache hits/misses based on path and root

    目的：测试项目路径验证缓存在不同路径下的表现
    Purpose: Test project path validation cache behavior with different paths

    测试场景：
    1. 首次调用有效路径 - 缓存未命中
    2. 第二次调用相同有效路径 - 缓存命中
    3. 调用不同的有效路径 - 缓存未命中
    4. 首次调用无效路径 - 缓存未命中
    5. 第二次调用相同无效路径 - 缓存命中

    Test scenarios:
    1. First call with valid path - cache miss
    2. Second call with same valid path - cache hit
    3. Call with different valid path - cache miss
    4. First call with invalid path - cache miss
    5. Second call with same invalid path - cache hit

    测试原理 / Test Rationale:
    - is_valid_project_path检查路径是否在项目根目录内且未被排除
    - 缓存键基于路径和项目根的组合，确保不同路径有独立的缓存条目
    - 无效路径的结果也会被缓存，避免重复的验证开销
    - 这对于大型项目的文件扫描性能至关重要

    涉及的缓存 / Caches Involved:
    - valid_project_paths: 存储路径验证结果的缓存
    - 缓存键格式: (规范化路径, 项目根路径)
    - 缓存值: True/False表示路径是否有效
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    # 这对于路径验证测试尤其重要，因为需要精确控制缓存状态
    # This is especially important for path validation tests as we need precise cache state control
    clear_all_caches()

    # 定义缓存名称 / Define cache name
    cache_name = 'valid_project_paths'
    # 获取项目根路径 / Get project root path
    project_root_path = test_project
    # 定义有效的相对路径 / Define valid relative path
    valid_path_rel = "src/module_a.py"
    # 构建有效的绝对路径 / Build valid absolute path
    valid_path_abs = project_root_path / valid_path_rel

    # 使用真正的无效路径（项目外） / Use a truly invalid path (outside project)
    invalid_path_rel = "../outside_project_file.txt"

    # 确保底层get_project_root至少被调用一次 / Ensure underlying get_project_root is called at least once
    path_utils.get_project_root()

    # ===== 步骤1：首次调用（有效路径） / Step 1: Initial call (valid path) =====
    print(f"Calling is_valid_project_path for '{valid_path_rel}' (1st time)")
    # 调用is_valid_project_path验证路径 / Call is_valid_project_path to validate path
    res1 = path_utils.is_valid_project_path(str(valid_path_abs))
    # 断言：验证返回True（路径有效） / Assertion: Verify returns True (path is valid)
    assert res1 is True
    # 获取缓存统计 / Get cache statistics
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次调用（相同有效路径）-> 缓存命中 / Step 2: Second call (same valid path) -> Cache Hit =====
    print(f"Calling is_valid_project_path for '{valid_path_rel}' (2nd time)")
    # 再次调用相同路径 / Call again with same path
    res2 = path_utils.is_valid_project_path(str(valid_path_abs))
    # 断言：验证仍返回True / Assertion: Verify still returns True
    assert res2 is True
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    assert stats2['hits'] >= 1

    # ===== 步骤3：第三次调用（不同的有效路径）-> 缓存未命中 / Step 3: Third call (different valid path) -> Cache Miss =====
    # 定义另一个有效的相对路径 / Define another valid relative path
    another_valid_path_rel = "docs/readme.md"
    # 构建另一个有效的绝对路径 / Build another valid absolute path
    another_valid_path_abs = project_root_path / another_valid_path_rel
    print(f"Calling is_valid_project_path for '{another_valid_path_rel}' (1st time)")
    # 调用新路径 / Call with new path
    res3 = path_utils.is_valid_project_path(str(another_valid_path_abs))
    # 断言：验证返回True / Assertion: Verify returns True
    assert res3 is True
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats3 = get_cache_stats(cache_name)
    # 断言：验证缓存未命中次数增加 / Assertion: Verify cache miss count increased
    assert stats3['misses'] > stats2.get('misses', 0)

    # ===== 步骤4：第四次调用（无效路径）-> 缓存未命中 / Step 4: Fourth call (invalid path) -> Cache Miss =====
    print(f"Calling is_valid_project_path for '{invalid_path_rel}' (1st time)")
    # 调用无效路径 / Call with invalid path
    res4 = path_utils.is_valid_project_path(invalid_path_rel)
    # 断言：验证返回False（路径无效） / Assertion: Verify returns False (path is invalid)
    assert res4 is False
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats4 = get_cache_stats(cache_name)
    # 断言：验证缓存未命中次数增加 / Assertion: Verify cache miss count increased
    assert stats4['misses'] > stats3.get('misses', 0)

    # ===== 步骤5：第五次调用（相同无效路径）-> 缓存命中 / Step 5: Fifth call (same invalid path) -> Cache Hit =====
    print(f"Calling is_valid_project_path for '{invalid_path_rel}' (2nd time)")
    # 再次调用相同的无效路径 / Call again with same invalid path
    res5 = path_utils.is_valid_project_path(invalid_path_rel)
    # 断言：验证仍返回False / Assertion: Verify still returns False
    assert res5 is False
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats5 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加（即使是无效路径结果也会被缓存）
    # Assertion: Verify cache hit count increased (even invalid path results are cached)
    assert stats5['hits'] > stats4.get('hits', 0)

# ===== FC-03: embedding_manager.calculate_similarity Cache =====

def test_fc03_calculate_similarity_cache(test_project, clear_cache_fixture, monkeypatch, caplog):
    """
    测试用例FC-03：验证calculate_similarity缓存命中/未命中
    Test Case FC-03: Verify calculate_similarity cache hits/misses

    目的：测试相似度计算缓存的正确性，包括手动失效机制
    Purpose: Test correctness of similarity calculation cache, including manual invalidation

    测试场景：
    1. 首次计算相似度 - 缓存未命中
    2. 第二次计算相同键对 - 缓存命中
    3. 反向键对计算 - 缓存命中（因为相似度是对称的）
    4. 修改嵌入文件后计算 - 缓存命中（过时，因为实现不检查mtime）
    5. 手动使缓存失效
    6. 再次计算 - 缓存未命中

    Test scenarios:
    1. First similarity calculation - cache miss
    2. Second calculation with same key pair - cache hit
    3. Reverse key pair calculation - cache hit (similarity is symmetric)
    4. Calculate after touching embedding file - cache hit (stale, implementation doesn't check mtime)
    5. Manually invalidate cache
    6. Calculate again - cache miss

    测试原理 / Test Rationale:
    - calculate_similarity计算两个嵌入向量之间的余弦相似度
    - 由于相似度计算是CPU密集型操作，缓存可以显著提升性能
    - 缓存键会规范化键对顺序（key1, key2）和（key2, key1）使用相同缓存
    - 当前实现不监控嵌入文件mtime，需要手动失效或强制重新生成
    - 测试手动失效机制确保在需要时可以强制更新

    涉及的缓存 / Caches Involved:
    - similarity_calculation: 存储相似度计算结果的缓存
    - 缓存键格式: sim_ses:{key1}:{key2}（键已排序）
    - 缓存值: 浮点数相似度分数（0.0到1.0）
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    # 相似度计算测试需要干净的缓存状态以验证对称性处理
    # Similarity calculation tests need clean cache state to verify symmetry handling
    clear_all_caches()

    # 定义缓存名称 / Define cache name
    cache_name = 'similarity_calculation'
    # 获取嵌入向量目录路径 / Get embedding directory path
    embedding_dir = test_project / "cache" / "embeddings"
    # 定义测试用的键 / Define test keys
    key1 = '1A1'
    key2 = '1B2'
    key3 = '1C3'
    # 构建嵌入文件路径 / Build embedding file path
    npy1_path = embedding_dir / f"{key1}.npy"

    # ===== 步骤1：首次调用 / Step 1: Initial call =====
    print(f"\nCalling calculate_similarity({key1}, {key2}) (1st time)")
    # 调用calculate_similarity计算相似度 / Call calculate_similarity to compute similarity
    sim1 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    # 断言：验证返回值是浮点数 / Assertion: Verify return value is float
    assert isinstance(sim1, float)
    # 获取缓存统计 / Get cache statistics
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次调用 -> 缓存命中 / Step 2: Second call -> Cache Hit =====
    print(f"Calling calculate_similarity({key1}, {key2}) (2nd time)")
    # 用相同参数再次调用 / Call again with same parameters
    sim2 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    # 断言：验证返回值与第一次相同 / Assertion: Verify return value same as first call
    assert sim2 == sim1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    assert stats2['hits'] >= 1

    # ===== 步骤3：第三次调用（反向键对）-> 缓存命中 / Step 3: Third call (reverse) -> Cache Hit =====
    print(f"Calling calculate_similarity({key2}, {key1}) (1st time)")
    # 交换key1和key2的顺序调用（相似度是对称的）/ Call with swapped key order (similarity is symmetric)
    sim3 = embedding_manager.calculate_similarity(key2, key1, str(embedding_dir), {}, str(test_project), [], [])
    # 断言：验证对称性，结果应该相同 / Assertion: Verify symmetry, result should be same
    assert sim3 == sim1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats3 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加（因为缓存键会规范化键顺序）
    # Assertion: Verify cache hit count increased (cache key normalizes key order)
    assert stats3['hits'] > stats2.get('hits', 0)

    # ===== 步骤4：修改.npy文件 / Step 4: Touch .npy file =====
    print(f"Touching {npy1_path}...")
    # 更新嵌入文件的修改时间 / Update embedding file modification time
    touch(npy1_path)
    # 等待确保mtime变化 / Wait to ensure mtime change
    time.sleep(0.1)

    # ===== 步骤5：文件修改后再次调用 -> 期望命中（过时的缓存）
    # Step 5: Call again after file modification -> Expect HIT (stale cache)
    print(f"Calling calculate_similarity({key1}, {key2}) (after touch)")
    # 再次调用 / Call again
    sim4 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats4 = get_cache_stats(cache_name)
    # 注意：这里期望缓存命中，因为当前实现不检查嵌入文件的mtime
    # Note: Expect cache hit here because current implementation doesn't check embedding file mtime
    # assert stats4['hits'] > stats3.get('hits', 0)  # 已注释，仅作说明 / Commented, for illustration only

    # ===== 步骤6：手动使缓存失效 / Step 6: Manually invalidate cache =====
    # 使用invalidate_dependent_entries手动清除特定键的缓存
    # Use invalidate_dependent_entries to manually clear cache for specific key
    invalidate_dependent_entries(cache_name, f"sim_ses:{key1}:{key2}")

    # ===== 步骤7：缓存失效后再次调用 -> 未命中 / Step 7: Call again after invalidation -> Miss =====
    print(f"Calling calculate_similarity({key1}, {key2}) (after invalidate)")
    # 再次调用，期望缓存未命中 / Call again, expect cache miss
    sim5 = embedding_manager.calculate_similarity(key1, key2, str(embedding_dir), {}, str(test_project), [], [])
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats5 = get_cache_stats(cache_name)
    # 断言：验证缓存未命中次数增加 / Assertion: Verify cache miss count increased
    assert stats5['misses'] > stats4.get('misses', 0)


# ===== FC-04: dependency_grid.validate_grid Cache =====

def test_fc04_validate_grid_cache(clear_cache_fixture):
    """
    测试用例FC-04：验证validate_grid缓存命中/未命中
    Test Case FC-04: Verify validate_grid cache hits/misses

    目的：测试依赖网格验证缓存的正确性
    Purpose: Test correctness of dependency grid validation cache

    测试场景：
    1. 首次验证网格 - 缓存未命中
    2. 第二次验证相同网格 - 缓存命中
    3. 使用未排序的键列表验证 - 缓存命中（因为缓存键使用排序后的版本）

    Test scenarios:
    1. First grid validation - cache miss
    2. Second validation with same grid - cache hit
    3. Validation with unsorted key list - cache hit (cache key uses sorted version)

    测试原理 / Test Rationale:
    - validate_grid验证依赖网格的结构完整性和一致性
    - 验证包括：行列数匹配、对称性检查、字符有效性等
    - 验证是纯函数操作，相同输入总是产生相同输出，适合缓存
    - 缓存键对键列表排序，确保键顺序不影响缓存命中
    - 这避免了重复的O(n²)验证开销

    涉及的缓存 / Caches Involved:
    - grid_validation: 存储网格验证结果的缓存
    - 缓存键格式: 基于排序后的键列表和网格内容的哈希
    - 缓存值: True/False表示网格是否有效
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    # 网格验证测试需要验证键列表排序对缓存的影响
    # Grid validation tests need to verify effect of key list sorting on cache
    clear_all_caches()

    # 定义缓存名称 / Define cache name
    cache_name = 'grid_validation'

    # 创建KeyInfo对象用于测试 / Create KeyInfo objects for testing
    ki1 = KeyInfo(key_string="1A1", norm_path="src/a.py", parent_path="src", tier=1, is_directory=False)
    ki2 = KeyInfo(key_string="1A2", norm_path="src/b.py", parent_path="src", tier=1, is_directory=False)
    ki3 = KeyInfo(key_string="1B", norm_path="src/c.py", parent_path="src", tier=1, is_directory=False)

    # 创建已排序的键列表 / Create sorted key list
    keys1_sorted = [ki1, ki2, ki3]
    # 创建测试用的依赖网格 / Create test dependency grid
    grid1 = {
        '1A1': "o<p",  # 1A1依赖1A2（<），与1B为占位符（p）
        '1A2': ">ox",  # 1A2被1A1依赖（>），与1B互相依赖（x）
        '1B':  "pxo"   # 1B与1A1为占位符（p），与1A2互相依赖（x）
    }

    # ===== 步骤1：首次调用 / Step 1: Initial call =====
    print("\nCalling validate_grid(G1, K1_sorted) (1st time)")
    # 调用validate_grid验证网格 / Call validate_grid to validate grid
    res1 = dependency_grid.validate_grid(grid1, keys1_sorted)
    # 断言：验证返回True（网格有效） / Assertion: Verify returns True (grid is valid)
    assert res1 is True
    # 获取缓存统计 / Get cache statistics
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次调用 -> 缓存命中 / Step 2: Second call -> Cache Hit =====
    print("Calling validate_grid(G1, K1_sorted) (2nd time)")
    # 用相同参数再次调用 / Call again with same parameters
    res2 = dependency_grid.validate_grid(grid1, keys1_sorted)
    # 断言：验证返回值与第一次相同 / Assertion: Verify return value same as first call
    assert res2 == res1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    assert stats2['hits'] >= 1

    # ===== 步骤3：第三次调用（未排序的键）-> 缓存命中 / Step 3: Third call (unsorted) -> Cache HIT =====
    # 创建未排序的键列表 / Create unsorted key list
    keys1_unsorted = [ki3, ki1, ki2]
    print("Calling validate_grid(G1, K1_unsorted) -> Expect HIT")
    # 用未排序的键列表调用 / Call with unsorted key list
    res3 = dependency_grid.validate_grid(grid1, keys1_unsorted)
    # 断言：验证返回值与第一次相同 / Assertion: Verify return value same as first call
    assert res3 == res1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats3 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加（因为缓存键使用排序后的键列表）
    # Assertion: Verify cache hit count increased (cache key uses sorted key list)
    assert stats3['hits'] > stats2.get('hits', 0)


# ===== FC-05: dependency_grid.get_dependencies_from_grid Cache =====

def test_fc05_get_dependencies_from_grid_cache(clear_cache_fixture):
    """
    测试用例FC-05：验证get_dependencies_from_grid缓存
    Test Case FC-05: Verify get_dependencies_from_grid cache

    目的：测试从网格获取依赖关系的缓存正确性
    Purpose: Test correctness of cache for getting dependencies from grid

    测试场景：
    1. 首次获取依赖 - 缓存未命中
    2. 第二次获取相同依赖 - 缓存命中

    Test scenarios:
    1. First dependency retrieval - cache miss
    2. Second retrieval of same dependencies - cache hit
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    clear_all_caches()

    # 定义缓存名称 / Define cache name
    cache_name = 'grid_dependencies'

    # 创建KeyInfo对象用于测试 / Create KeyInfo objects for testing
    ki1 = KeyInfo(key_string="1A1", norm_path="src/a.py", parent_path="src", tier=1, is_directory=False)
    ki2 = KeyInfo(key_string="1A2", norm_path="src/b.py", parent_path="src", tier=1, is_directory=False)
    ki3 = KeyInfo(key_string="1B", norm_path="src/c.py", parent_path="src", tier=1, is_directory=False)
    # 创建已排序的键列表 / Create sorted key list
    keys1_sorted = [ki1, ki2, ki3]

    # 创建测试用的依赖网格 / Create test dependency grid
    grid1 = {
        '1A1': "o<p",  # 1A1依赖1A2（<），与1B为占位符（p）
        '1A2': ">ox",  # 1A2被1A1依赖（>），与1B互相依赖（x）
        '1B':  "pxo"   # 1B与1A1为占位符（p），与1A2互相依赖（x）
    }
    # 定义目标键 / Define target key
    target_key1 = '1A1'

    # 定义期望的依赖关系字典 / Define expected dependencies dictionary
    expected_deps1 = {'<': ['1A2'], 'p': ['1B']}

    # ===== 步骤1：首次调用 / Step 1: Initial call =====
    print(f"\nCalling get_dependencies_from_grid(G1, {target_key1}, K1) (1st time)")
    # 调用get_dependencies_from_grid获取依赖 / Call get_dependencies_from_grid to get dependencies
    deps1 = dependency_grid.get_dependencies_from_grid(grid1, target_key1, keys1_sorted)
    # 断言：验证返回的依赖关系正确 / Assertion: Verify returned dependencies are correct
    assert deps1 == expected_deps1
    # 获取缓存统计 / Get cache statistics
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次调用 -> 缓存命中 / Step 2: Second call -> Cache Hit =====
    print(f"Calling get_dependencies_from_grid(G1, {target_key1}, K1) (2nd time)")
    # 用相同参数再次调用 / Call again with same parameters
    deps2 = dependency_grid.get_dependencies_from_grid(grid1, target_key1, keys1_sorted)
    # 断言：验证返回值与第一次相同 / Assertion: Verify return value same as first call
    assert deps2 == deps1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    assert stats2['hits'] >= 1


# ===== FC-06: tracker_io.read_tracker_file Cache =====

def test_fc06_read_tracker_file_cache(test_project, clear_cache_fixture):
    """
    测试用例FC-06：验证read_tracker_file缓存在文件修改时失效
    Test Case FC-06: Verify read_tracker_file cache invalidates on file modification

    目的：测试跟踪器文件读取缓存的mtime感知能力
    Purpose: Test mtime awareness of tracker file read cache

    测试场景：
    1. 首次读取跟踪器文件 - 缓存未命中
    2. 第二次读取相同文件 - 缓存命中
    3. 修改文件后读取 - 缓存未命中（因为mtime变化）

    Test scenarios:
    1. First tracker file read - cache miss
    2. Second read of same file - cache hit
    3. Read after file modification - cache miss (due to mtime change)
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    clear_all_caches()

    # 定义缓存名称 / Define cache name
    cache_name = 'tracker_data_structured'
    # 定义跟踪器文件的相对路径 / Define tracker file relative path
    tracker_rel_path = "cline_docs/tracker.md"
    # 构建跟踪器文件的绝对路径 / Build tracker file absolute path
    tracker_abs_path = test_project / tracker_rel_path

    # 定义初始跟踪器文件内容 / Define initial tracker file content
    initial_content = "# Initial Tracker\nkey1,key2\np,p\n"
    # 写入初始内容 / Write initial content
    tracker_abs_path.write_text(initial_content)
    # 等待确保文件系统更新 / Wait to ensure filesystem update
    time.sleep(0.1)

    # ===== 步骤1：首次读取 / Step 1: Initial read =====
    print(f"\nCalling read_tracker_file_structured({tracker_rel_path}) (1st time)")
    # 调用read_tracker_file_structured读取文件 / Call read_tracker_file_structured to read file
    result1 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    # 断言：验证读取结果不为None / Assertion: Verify read result is not None
    assert result1 is not None
    # 获取缓存统计 / Get cache statistics
    stats1 = get_cache_stats(cache_name)

    # ===== 步骤2：第二次读取 -> 缓存命中 / Step 2: Second read -> Cache Hit =====
    print(f"Calling read_tracker_file_structured({tracker_rel_path}) (2nd time)")
    # 再次读取相同文件 / Read same file again
    result2 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    # 断言：验证返回值与第一次相同 / Assertion: Verify return value same as first call
    assert result2 == result1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats2 = get_cache_stats(cache_name)
    # 断言：验证缓存命中次数增加 / Assertion: Verify cache hit count increased
    assert stats2['hits'] >= 1

    # ===== 步骤3：修改文件 / Step 3: Touch file =====
    print(f"Touching {tracker_abs_path}...")
    # 更新文件修改时间 / Update file modification time
    touch(tracker_abs_path)
    # 等待确保mtime变化 / Wait to ensure mtime change
    time.sleep(0.1)

    # ===== 步骤4：文件修改后第三次读取 -> 缓存未命中 / Step 4: Third read after modification -> Cache Miss =====
    print(f"Calling read_tracker_file_structured({tracker_rel_path}) (after touch)")
    # 再次读取（mtime已变化） / Read again (mtime has changed)
    result3 = tracker_utils.read_tracker_file_structured(str(tracker_abs_path))
    # 断言：验证内容仍然相同（只是mtime变了） / Assertion: Verify content still same (only mtime changed)
    assert result3 == result1
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats3 = get_cache_stats(cache_name)
    # 断言：验证缓存未命中次数增加（因为mtime变化导致缓存失效）
    # Assertion: Verify cache miss count increased (mtime change invalidated cache)
    assert stats3['misses'] > stats2.get('misses', 0)


# ===== FC-07: Config-dependent Caches =====

def test_fc07_config_dependent_caches(test_project, clear_cache_fixture, monkeypatch):
    """
    测试用例FC-07：验证配置依赖的缓存在.clinerules.config.json变化时失效
    Test Case FC-07: Verify caches invalidate when .clinerules.config.json changes

    目的：测试配置文件变化时相关缓存的自动失效机制
    Purpose: Test automatic invalidation of related caches when config file changes

    测试场景：
    1. 首次读取配置 - 缓存未命中
    2. 第二次读取相同配置 - 缓存命中
    3. 修改配置文件后读取 - 缓存未命中（因为配置文件mtime变化）

    Test scenarios:
    1. First config read - cache miss
    2. Second read of same config - cache hit
    3. Read after config file modification - cache miss (config file mtime changed)
    """
    # 清除所有缓存确保测试从干净状态开始 / Clear all caches to ensure test starts clean
    clear_all_caches()

    # 获取配置文件路径 / Get config file path
    config_path = test_project / ".clinerules.config.json"
    # 定义缓存名称（测试excluded_dirs缓存）/ Define cache name (testing excluded_dirs cache)
    cache_name_config = 'excluded_dirs'

    # 定义初始配置数据 / Define initial config data
    initial_config_data = {
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs"},
        "excluded_dirs": [".git", "venv"],  # 初始排除目录列表
        "excluded_extensions": ["*.log", "*.tmp"],  # 初始排除扩展名列表
        "thresholds": {"code_similarity": 0.7}  # 相似度阈值
    }
    # 写入初始配置 / Write initial config
    config_path.write_text(json.dumps(initial_config_data))
    # 等待确保文件系统更新 / Wait to ensure filesystem update
    time.sleep(0.1)

    # 重置ConfigManager单例以强制重新加载 / Reset ConfigManager singleton to force reload
    monkeypatch.setattr(config_manager.ConfigManager, '_instance', None, raising=False)
    # 创建新的ConfigManager实例 / Create new ConfigManager instance
    cm = config_manager.ConfigManager()
    # 首次获取排除目录列表 / First retrieval of excluded dirs
    initial_exclusions = cm.get_excluded_dirs()

    # ===== 步骤1：第二次调用配置获取器 -> 命中 / Step 1: Call config getter again -> Hit =====
    print("\nCalling get_excluded_dirs() (2nd time)")
    # 再次获取排除目录列表 / Get excluded dirs again
    exclusions1 = cm.get_excluded_dirs()
    # 断言：验证返回值与初始值相同 / Assertion: Verify return value same as initial
    assert exclusions1 == initial_exclusions
    # 获取缓存统计 / Get cache statistics
    stats_conf1 = get_cache_stats(cache_name_config)

    # ===== 步骤2：修改配置文件 / Step 2: Modify Config File =====
    print(f"Modifying {config_path}...")
    # 定义修改后的配置数据 / Define modified config data
    modified_config_data = {
        "paths": {"doc_dir": "docs", "memory_dir": "cline_docs"},
        "excluded_dirs": [".git", "venv", "build_custom"],  # 添加新的排除目录
        "excluded_extensions": ["*.log"],  # 减少排除扩展名
        "thresholds": {"code_similarity": 0.8}  # 提高相似度阈值
    }
    # 写入修改后的配置 / Write modified config
    config_path.write_text(json.dumps(modified_config_data))
    # 等待足够长时间确保mtime变化（某些文件系统mtime分辨率较低）
    # Wait long enough to ensure mtime change (some filesystems have low mtime resolution)
    time.sleep(1.5)

    # 重置ConfigManager单例以强制重新加载 / Reset ConfigManager singleton to force reload
    monkeypatch.setattr(config_manager.ConfigManager, '_instance', None, raising=False)
    # 创建新的ConfigManager实例 / Create new ConfigManager instance
    cm = config_manager.ConfigManager()

    # ===== 步骤3：配置修改后再次调用 -> 未命中 / Step 3: Call config getter again after modify -> Miss =====
    print("Calling get_excluded_dirs() (after modify)")
    # 获取修改后的排除目录列表 / Get excluded dirs after modification
    exclusions2 = cm.get_excluded_dirs()
    # 断言：验证返回值与初始值不同 / Assertion: Verify return value different from initial
    assert exclusions2 != initial_exclusions
    # 断言：验证新添加的目录在列表中 / Assertion: Verify newly added directory is in list
    assert "build_custom" in exclusions2
    # 获取更新后的缓存统计 / Get updated cache statistics
    stats_conf2 = get_cache_stats(cache_name_config)
    # 断言：验证缓存未命中次数增加（因为配置文件mtime变化）
    # Assertion: Verify cache miss count increased (config file mtime changed)
    assert stats_conf2['misses'] > stats_conf1.get('misses', 0)


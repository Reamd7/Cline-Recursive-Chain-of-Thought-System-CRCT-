"""
测试模块：手动工具缓存测试
Test Module: Manual Tooling Cache Tests

本模块提供了对缓存系统手动工具和管理功能的测试，包括：
- 缓存清除命令测试（MT-01）
- 缓存统计功能测试（MT-02）
- DEBUG日志输出测试（MT-03）

This module provides tests for cache system manual tools and management features, including:
- Cache clearing command tests (MT-01)
- Cache statistics functionality tests (MT-02)
- DEBUG logging output tests (MT-03)

测试编号说明 / Test ID Explanation:
MT = Manual/Tooling（手动/工具测试）
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入操作系统接口模块 / Import OS interface module
import os
# 导入时间模块，用于时间相关操作 / Import time module for time-related operations
import time
# 导入文件操作模块 / Import file operations module
import shutil
# 导入JSON处理模块 / Import JSON processing module
import json
# 导入Path类用于路径操作 / Import Path class for path operations
from pathlib import Path
# 导入numpy用于嵌入向量处理 / Import numpy for embedding vector processing
import numpy as np  # 由test_project fixture使用 / Still needed by test_project fixture
# 导入logging模块用于日志记录 / Import logging module for logging
import logging  # caplog需要 / Needed for caplog

# 导入缓存管理器相关函数 / Import cache manager related functions
from cline_utils.dependency_system.utils.cache_manager import get_cache_stats, clear_all_caches
# 导入路径工具 / Import path utils
from cline_utils.dependency_system.utils import path_utils
# 导入配置管理器 / Import config manager
from cline_utils.dependency_system.utils import config_manager
# 导入嵌入管理器（被test_project fixture需要） / Import embedding manager (needed by test_project fixture)
from cline_utils.dependency_system.analysis import embedding_manager
# 导入依赖网格模块（被test_project fixture需要） / Import dependency grid (needed by test_project fixture)
from cline_utils.dependency_system.core import dependency_grid
# 导入追踪器IO模块（MT-02和MT-03需要） / Import tracker IO (needed for MT-02 and MT-03)
from cline_utils.dependency_system.io import tracker_io
# 导入依赖分析器（MT-01需要） / Import dependency analyzer (needed for MT-01)
from cline_utils.dependency_system.analysis import dependency_analyzer
# 导入项目分析器（集成测试需要） / Import project analyzer (needed for integration tests)
from cline_utils.dependency_system.analysis.project_analyzer import analyze_project
# 导入命令处理器（MT-01需要） / Import command handler (needed for MT-01)
from cline_utils.dependency_system.dependency_processor import handle_clear_caches  # 使用特定的处理函数 / Use specific handler function

# 辅助函数 / Helper Functions

def touch(filepath):
    """
    辅助函数：更新文件的修改时间
    Helper Function: Update file modification time

    参数：
    - filepath: 文件路径（字符串或Path对象）

    Parameters:
    - filepath: File path (string or Path object)

    功能：
    使用Path.touch()方法更新文件的mtime（修改时间）

    Functionality:
    Use Path.touch() method to update file's mtime (modification time)
    """
    try:
        # 将文件路径转换为Path对象并调用touch()方法 / Convert file path to Path object and call touch() method
        Path(filepath).touch()
    except OSError as e:
        # 捕获并打印任何文件操作错误 / Catch and print any file operation errors
        print(f"Error touching file {filepath}: {e}")

# --- Fixtures（测试固件） ---

@pytest.fixture(scope="function")
def clear_cache_fixture():
    """
    测试fixture：在每个测试函数前后清空缓存
    Test fixture: Clear cache before and after each test function

    作用域：function（每个测试函数独立）
    Scope: function (independent for each test function)

    功能：
    1. 测试前：清空所有缓存
    2. 执行测试
    3. 测试后：清空所有缓存

    Functionality:
    1. Before test: Clear all caches
    2. Execute test
    3. After test: Clear all caches

    目的：
    确保每个测试函数都在干净的缓存状态下运行，避免测试间干扰

    Purpose:
    Ensure each test function runs with clean cache state, avoid inter-test interference
    """
    # 测试前清空所有缓存 / Clear all caches before test
    clear_all_caches()
    # 执行测试函数 / Execute test function
    yield
    # 测试后清空所有缓存 / Clear all caches after test
    clear_all_caches()

@pytest.fixture(scope="session")
def temp_test_dir(tmp_path_factory):
    """
    测试fixture：创建会话级临时测试目录
    Test fixture: Create session-level temporary test directory

    作用域：session（整个测试会话共享）
    Scope: session (shared across entire test session)

    参数：
    - tmp_path_factory: pytest提供的临时路径工厂

    Parameters:
    - tmp_path_factory: pytest provided temporary path factory

    返回：
    - 临时目录路径（Path对象）

    Returns:
    - Temporary directory path (Path object)
    """
    # 使用tmp_path_factory创建名为"cache_tests_manual"的临时目录 / Use tmp_path_factory to create temporary directory named "cache_tests_manual"
    return tmp_path_factory.mktemp("cache_tests_manual")  # 唯一名称 / Unique name

@pytest.fixture(scope="function")
def test_project(temp_test_dir):
    """
    测试fixture：设置最小化的临时项目结构
    Test fixture: Setup minimal temporary project structure

    作用域：function（每个测试函数独立）
    Scope: function (independent for each test function)

    功能：
    1. 创建临时项目目录
    2. 创建配置文件（.clinerules、.clinerules.config.json）
    3. 创建源代码文件
    4. 创建文档文件
    5. 创建内存目录（cline_docs）
    6. 创建追踪器文件
    7. 切换工作目录到项目根目录

    Features:
    1. Create temporary project directory
    2. Create config files (.clinerules, .clinerules.config.json)
    3. Create source code files
    4. Create documentation files
    5. Create memory directory (cline_docs)
    6. Create tracker files
    7. Change working directory to project root

    返回：
    - 项目根目录路径（Path对象）

    Returns:
    - Project root directory path (Path object)
    """
    # 创建临时项目目录（唯一名称） / Create temporary project directory (unique name)
    project_dir = temp_test_dir / "test_project_mt"  # Unique name
    project_dir.mkdir(exist_ok=True)
    # 创建.clinerules文件 / Create .clinerules file
    (project_dir / ".clinerules").touch()
    # 准备基础配置字典 / Prepare base config dict
    base_config = {
        "paths": {
            "doc_dir": "docs",  # 文档目录 / Documentation directory
            "memory_dir": "cline_docs",  # 内存目录 / Memory directory
            "cache_dir": "cache"  # 缓存目录 / Cache directory
        },
        "exclusions": {
            "dirs": [".git", "venv"],  # 排除的目录 / Excluded directories
            "files": ["*.log"]  # 排除的文件模式 / Excluded file patterns
        },
        "thresholds": {"code_similarity": 0.7}  # 代码相似度阈值 / Code similarity threshold
    }
    # 创建.clinerules.config.json文件 / Create .clinerules.config.json file
    (project_dir / ".clinerules.config.json").write_text(json.dumps(base_config))

    # 创建源代码文件（MT-01需要） / Create source code files (needed by MT-01)
    (project_dir / "src").mkdir(exist_ok=True)
    # 创建module_a.py，包含import语句 / Create module_a.py with import statement
    (project_dir / "src" / "module_a.py").write_text("import os\nprint('hello from module_a')")  # MT-01
    (project_dir / "src" / "module_b.py").write_text("print('hello from module_b')")
    # 创建文档文件（MT-02需要） / Create documentation files (needed by MT-02)
    (project_dir / "docs").mkdir(exist_ok=True)
    (project_dir / "docs" / "readme.md").write_text("# Test Readme")  # MT-02
    # 创建内存目录（追踪器路径需要） / Create memory directory (needed for tracker path)
    (project_dir / "cline_docs").mkdir(exist_ok=True)
    # 确保缓存目录存在 / Ensure cache directory exists
    (project_dir / "cache").mkdir(exist_ok=True)

    # 为MT-01、MT-02、MT-03创建初始追踪器文件 / Create initial tracker files for MT-01, MT-02, MT-03
    tracker_path = project_dir / "cline_docs" / "module_relationship_tracker.md"
    # 如果追踪器文件不存在，创建占位符内容 / If tracker file doesn't exist, create placeholder content
    if not tracker_path.exists():
        tracker_path.parent.mkdir(parents=True, exist_ok=True)
        tracker_path.write_text("# Placeholder Tracker\nkeyA,keyB\np,p\n")

    # 为MT-02创建tracker.md / Create tracker.md for MT-02
    tracker_path1 = project_dir / "cline_docs" / "tracker.md"
    tracker_path1.write_text("# Tracker 1\nA,B\np,p")
    # 为MT-03创建tracker_log_test.md / Create tracker_log_test.md for MT-03
    tracker_path_log = project_dir / "cline_docs" / "tracker_log_test.md"
    tracker_path_log.write_text("# Log Test Tracker\nLogKey1,LogKey2\np,p")

    # 保存原始工作目录 / Save original working directory
    original_cwd = os.getcwd()
    # 切换到项目目录 / Change to project directory
    os.chdir(project_dir)
    # 将项目目录提供给测试函数 / Yield project directory to test function
    yield project_dir
    # 测试后恢复原始工作目录 / Restore original working directory after test
    os.chdir(original_cwd)

# --- Manual/Tooling Tests（手动/工具测试，MT-01到MT-03） ---

def test_mt01_cache_clearing(test_project):
    """
    测试用例MT-01：验证缓存清除命令
    Test Case MT-01: Verify Cache Clearing Command

    目的：验证clear-caches命令处理器能有效清除缓存
    Purpose: Verify clear-caches command handler clears caches effectively

    测试步骤：
    1. 运行analyze_project填充缓存
    2. 调用可缓存函数并验证缓存命中
    3. 调用clear-caches处理器
    4. 再次调用可缓存函数并验证缓存未命中

    Test Steps:
    1. Run analyze_project to populate caches
    2. Call cacheable functions and verify cache hits
    3. Call clear-caches handler
    4. Call cacheable functions again and verify cache misses

    验证点：
    1. 清除前缓存命中计数 >= 1
    2. clear-caches返回退出码0
    3. 清除后缓存未命中计数 >= 1

    Verification Points:
    1. Cache hit count >= 1 before clearing
    2. clear-caches returns exit code 0
    3. Cache miss count >= 1 after clearing
    """
    # 使用可缓存函数，analyze_project可能会调用它们 / Use cacheable functions that analyze_project likely calls
    cache_name_read = 'tracker_data_structured'  # 追踪器读取缓存 / Tracker read cache
    cache_name_analyze = 'file_analysis'  # 文件分析缓存 / File analysis cache
    cache_name_config_get = 'excluded_dirs'  # 配置获取缓存（示例） / Config getter cache (example)

    # 定义测试用的路径 / Define paths for testing
    tracker_path = test_project / "cline_docs" / "module_relationship_tracker.md"
    file_to_analyze = test_project / "src" / "module_a.py"
    config_path = test_project / ".clinerules.config.json"  # 配置缓存需要 / Needed for config cache

    # 步骤1：运行analyze_project填充缓存 / Step 1: Run analyze_project to populate caches
    print("\nRunning analyze_project (to populate caches for MT-01)...")
    try:
        # 强制分析以确保文件被分析 / Force analysis to ensure files are analyzed
        results1 = analyze_project(force_analysis=True)
    except Exception as e:
        # 如果analyze_project失败，测试失败 / If analyze_project fails, test fails
        pytest.fail(f"analyze_project failed during cache population: {e}")

    # 确保追踪器存在，以便read_tracker_file可以有意义地调用 / Ensure tracker exists so read_tracker_file can be called meaningfully
    if not tracker_path.exists():
          # 如果analyze_project不保证创建追踪器，手动创建一个 / If analyze_project doesn't guarantee tracker creation, manually create one
          tracker_path.parent.mkdir(parents=True, exist_ok=True)
          tracker_path.write_text("# Placeholder Tracker\nkeyA,keyB\np,p\n")
          print("Warning: Tracker file not found, created placeholder for test.")

    # 步骤2：调用可缓存函数一次以确保它们已填充（如果analyze_project没有调用） / Step 2: Call cacheable functions once to ensure they are populated if not called by analyze_project
    # 然后再次调用以验证清除前发生缓存命中 / and then call again to verify a cache hit occurred before clearing
    print("Calling cached functions to confirm population and get initial hit...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path))  # 填充 / Populate
    _ = dependency_analyzer.analyze_file(str(file_to_analyze))  # 填充 / Populate
    _ = config_manager.ConfigManager().get_excluded_dirs()  # 填充 / Populate

    _ = tracker_io.read_tracker_file_structured(str(tracker_path))  # 命中? / Hit?
    stats_read1 = get_cache_stats(cache_name_read)
    # 断言：清除前缓存应有命中 / Assert: cache should have hits before clear
    assert stats_read1.get('hits', 0) >= 1, f"Cache '{cache_name_read}' should have hits before clear."

    _ = dependency_analyzer.analyze_file(str(file_to_analyze))  # 命中? / Hit?
    stats_analyze1 = get_cache_stats(cache_name_analyze)
    assert stats_analyze1.get('hits', 0) >= 1, f"Cache '{cache_name_analyze}' should have hits before clear."

    _ = config_manager.ConfigManager().get_excluded_dirs()  # 命中? / Hit?
    stats_config1 = get_cache_stats(cache_name_config_get)
    assert stats_config1.get('hits', 0) >= 1, f"Cache '{cache_name_config_get}' should have hits before clear."

    # 记录清除前的未命中计数（在初始填充/命中之后） / Record miss counts *before* clearing but *after* initial population/hits
    initial_read_misses = stats_read1.get('misses', 0)
    initial_analyze_misses = stats_analyze1.get('misses', 0)
    initial_config_misses = stats_config1.get('misses', 0)

    # 步骤3：调用clear-caches处理器 / Step 3: Call the clear-caches handler
    print("Calling handle_clear_caches...")
    # 处理器接受argparse Namespace对象，但不使用它。传递None / The handler takes argparse Namespace object, but doesn't use it. Pass None.
    exit_code = handle_clear_caches(None)
    # 断言：handle_clear_caches应返回退出码0 / Assert: handle_clear_caches should return exit code 0
    assert exit_code == 0, "handle_clear_caches returned non-zero exit code."

    # 步骤4：再次调用可缓存函数 -> 期望缓存未命中 / Step 4: Call cached functions again -> Expect Cache Misses
    print("Calling cached functions after clearing...")

    # a) read_tracker_file
    _ = tracker_io.read_tracker_file_structured(str(tracker_path))  # 应未命中 / Should miss
    stats_read2 = get_cache_stats(cache_name_read)
    print(f"Cache stats for {cache_name_read} after clear: {stats_read2}")
    # 注意：clear_all_caches()替换缓存实例，因此度量会重置 / Note: clear_all_caches() replaces the cache instances, so metrics are reset.
    assert stats_read2.get('misses', 0) >= 1, \
        f"Cache '{cache_name_read}' should have misses after clear (got {stats_read2.get('misses',0)})."

    # b) analyze_file
    _ = dependency_analyzer.analyze_file(str(file_to_analyze))  # 应未命中 / Should miss
    stats_analyze2 = get_cache_stats(cache_name_analyze)
    print(f"Cache stats for {cache_name_analyze} after clear: {stats_analyze2}")
    assert stats_analyze2.get('misses', 0) >= 1, \
        f"Cache '{cache_name_analyze}' should have misses after clear (got {stats_analyze2.get('misses',0)})."

    # c) ConfigManager getter
    _ = config_manager.ConfigManager().get_excluded_dirs()  # 应未命中 / Should miss
    stats_config2 = get_cache_stats(cache_name_config_get)
    print(f"Cache stats for {cache_name_config_get} after clear: {stats_config2}")
    assert stats_config2.get('misses', 0) >= 1, \
        f"Cache '{cache_name_config_get}' should have misses after clear (got {stats_config2.get('misses',0)})."

    print("Verified: Cache clearing appears functional.")

def test_mt02_cache_statistics(test_project, clear_cache_fixture):
    """
    测试用例MT-02：验证缓存统计功能
    Test Case MT-02: Verify Cache Statistics Functionality

    目的：验证get_cache_stats返回准确的命中/未命中计数
    Purpose: Verify get_cache_stats returns accurate hit/miss counts

    测试步骤：
    1. 清空缓存
    2. 调用可缓存函数多次，观察统计变化
    3. 修改文件并观察缓存失效
    4. 验证每次调用后的统计数据准确

    Test Steps:
    1. Clear caches
    2. Call cacheable function multiple times, observe statistics changes
    3. Modify file and observe cache invalidation
    4. Verify statistics data is accurate after each call

    验证点：
    1. 初始状态：0命中，0未命中
    2. 第一次调用：0命中，1未命中
    3. 第二次调用（相同参数）：1命中，1未命中
    4. 第三次调用（不同参数）：1命中，2未命中
    5. 第四次调用（第一个参数）：2命中，2未命中
    6. 第五次调用（第二个参数）：3命中，2未命中
    7. 修改文件后调用：3命中，3未命中
    8. 再次调用（重新缓存）：4命中，3未命中

    Verification Points:
    1. Initial state: 0 hits, 0 misses
    2. First call: 0 hits, 1 miss
    3. Second call (same args): 1 hit, 1 miss
    4. Third call (different args): 1 hit, 2 misses
    5. Fourth call (first args): 2 hits, 2 misses
    6. Fifth call (second args): 3 hits, 2 misses
    7. After file modification: 3 hits, 3 misses
    8. Call again (re-cached): 4 hits, 3 misses
    """
    # 测试开始时手动清空 / Manual clear at start
    clear_all_caches()
    # 使用简单的可缓存函数，如read_tracker_file / Use a simple cacheable function like read_tracker_file
    cache_name = 'tracker_data_structured'
    tracker_path1 = test_project / "cline_docs" / "tracker.md"  # 使用fixture设置的文件 / Use file from fixture setup
    tracker_path2 = test_project / "docs" / "readme.md"  # 使用另一个文件以增加多样性 / Use another file for variety

    # 文件存在于fixture设置中 / Files exist from fixture setup

    print(f"\nTesting cache statistics for '{cache_name}'...")

    # 初始状态应为0命中，0未命中（手动清除后） / Initial state should be 0 hits, 0 misses *after* manual clear
    stats_initial = get_cache_stats(cache_name)
    assert stats_initial.get('hits', 0) == 0, f"Initial hits should be 0 after clear, got {stats_initial}"
    assert stats_initial.get('misses', 0) == 0, f"Initial misses should be 0 after clear, got {stats_initial}"

    # 调用1（tracker1） -> 未命中1 / Call 1 (tracker1) -> Miss 1
    print("Call 1 (tracker1)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path1))
    stats1 = get_cache_stats(cache_name)
    assert stats1.get('hits', 0) == 0, f"Hits should be 0 after 1st call, got {stats1}"
    assert stats1.get('misses', 0) == 1, f"Misses should be 1 after 1st call, got {stats1}"

    # 调用2（tracker1再次） -> 命中1 / Call 2 (tracker1 again) -> Hit 1
    print("Call 2 (tracker1)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path1))
    stats2 = get_cache_stats(cache_name)
    assert stats2.get('hits', 0) == 1, "Hits should be 1 after 2nd call (same args)."
    assert stats2.get('misses', 0) == 1, "Misses should still be 1."

    # 调用3（tracker2） -> 未命中2 / Call 3 (tracker2) -> Miss 2
    print("Call 3 (tracker2)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path2))
    stats3 = get_cache_stats(cache_name)
    assert stats3.get('hits', 0) == 1, "Hits should still be 1."
    assert stats3.get('misses', 0) == 2, "Misses should be 2 after 3rd call (diff args)."

    # 调用4（tracker1再次） -> 命中2 / Call 4 (tracker1 again) -> Hit 2
    print("Call 4 (tracker1)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path1))
    stats4 = get_cache_stats(cache_name)
    assert stats4.get('hits', 0) == 2, "Hits should be 2 after 4th call."
    assert stats4.get('misses', 0) == 2, "Misses should still be 2."

    # 调用5（tracker2再次） -> 命中3 / Call 5 (tracker2 again) -> Hit 3
    print("Call 5 (tracker2)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path2))
    stats5 = get_cache_stats(cache_name)
    assert stats5.get('hits', 0) == 3, "Hits should be 3 after 5th call."
    assert stats5.get('misses', 0) == 2, "Misses should still be 2."

    # 调用6（touch tracker1，调用tracker1） -> 未命中3 / Call 6 (touch tracker1, call tracker1) -> Miss 3
    print("Call 6 (touch tracker1, call tracker1)...")
    touch(tracker_path1)
    time.sleep(0.1)
    _ = tracker_io.read_tracker_file_structured(str(tracker_path1))
    stats6 = get_cache_stats(cache_name)
    assert stats6.get('hits', 0) == 3, "Hits should still be 3."
    assert stats6.get('misses', 0) == 3, "Misses should be 3 after invalidation."

    # 调用7（tracker1再次） -> 命中4 / Call 7 (tracker1 again) -> Hit 4
    print("Call 7 (tracker1)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path1))
    stats7 = get_cache_stats(cache_name)
    assert stats7.get('hits', 0) == 4, "Hits should be 4 after re-cache."
    assert stats7.get('misses', 0) == 3, "Misses should still be 3."

    print(f"Final Stats for '{cache_name}': {stats7}")
    print("Verified: Cache statistics appear accurate.")

def test_mt03_debug_logging(test_project, clear_cache_fixture, caplog):
    """
    测试用例MT-03：验证DEBUG日志输出
    Test Case MT-03: Verify DEBUG Logging Output

    目的：验证缓存命中/未命中/失效消息出现在DEBUG日志中
    Purpose: Verify cache hit/miss/invalidation messages appear in DEBUG logs

    测试步骤：
    1. 清空缓存
    2. 设置日志级别为DEBUG
    3. 第一次调用 -> 检查未命中日志
    4. 第二次调用 -> 检查命中日志
    5. 修改文件 -> 第三次调用 -> 检查失效日志和未命中日志

    Test Steps:
    1. Clear caches
    2. Set log level to DEBUG
    3. First call -> Check miss log
    4. Second call -> Check hit log
    5. Modify file -> Third call -> Check invalidation and miss logs

    验证点：
    1. 第一次调用后日志包含"miss"
    2. 第二次调用后日志包含"hit"
    3. 文件修改后调用日志包含"miss"

    Verification Points:
    1. Log contains "miss" after first call
    2. Log contains "hit" after second call
    3. Log contains "miss" after file modification
    """
    # 测试开始时手动清空 / Manual clear at start
    clear_all_caches()
    # 再次使用简单的可缓存函数 / Use a simple cacheable function again
    cache_name = 'tracker_data_structured'
    tracker_path = test_project / "cline_docs" / "tracker_log_test.md"  # 使用唯一的文件 / Use a unique file

    # 文件存在于fixture设置中 / File exists from fixture setup

    # 设置日志级别为DEBUG以捕获缓存消息 / Set logging level to DEBUG to capture cache messages
    caplog.set_level(logging.DEBUG)
    # 可选：如果知道特定的缓存管理器日志记录器，则过滤它 / Optionally filter for the specific cache manager logger if known
    # logger_name = 'cline_utils.dependency_system.utils.cache_manager'
    # caplog.set_level(logging.DEBUG, logger=logger_name)

    print(f"\nTesting DEBUG logging for cache '{cache_name}'...")

    # 步骤1：初始调用 -> 期望缓存未命中日志 / Step 1: Initial call -> Expect Cache Miss log
    print("Call 1 (expect miss log)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path))
    # 检查特定日志消息（如果可用），否则进行通用检查 / Check for specific log message if available, otherwise generic check
    # 示例：assert f"Cache miss for cache '{cache_name}'" in caplog.text / Example: assert f"Cache miss for cache '{cache_name}'" in caplog.text
    assert "miss" in caplog.text.lower(), "Expected 'miss' message in log for initial call."
    print(" -> Miss log found (or expected pattern).")
    caplog.clear()  # 清除日志以进行下一步 / Clear logs for next step

    # 步骤2：第二次调用 -> 期望缓存命中日志 / Step 2: Second call -> Expect Cache Hit log
    print("Call 2 (expect hit log)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path))
    # assert f"Cache hit for cache '{cache_name}'" in caplog.text
    assert "hit" in caplog.text.lower(), "Expected 'hit' message in log for second call."
    print(" -> Hit log found.")
    caplog.clear()

    # 步骤3：touch文件 -> 期望失效日志（如果有失效日志）+ 下次调用时的未命中日志 / Step 3: Touch file -> Expect Invalidation log (if invalidation logs) + Miss log on next call
    print("Touch file (expect invalidation log if implemented)...")
    touch(tracker_path)
    time.sleep(0.1)
    # 注意：失效可能在*下次*调用的检查时隐式发生 / Note: Invalidation might happen implicitly on the *next* call's check,
    # 或者如果有单独的失效机制则显式发生 / or explicitly if there's a separate invalidation mechanism.
    # 日志消息可能会有所不同。让我们在下一次调用*后*检查日志 / The log message might vary. Let's check the logs *after* the next call.

    print("Call 3 (expect miss log after touch)...")
    _ = tracker_io.read_tracker_file_structured(str(tracker_path))
    log_text = caplog.text
    # 首先检查失效消息（如果期望） / Check for invalidation message *first* if expected
    # assert "Invalidating cache entry" in log_text # 调整期望的消息 / Adjust expected message
    # 然后再次检查未命中消息 / Then check for miss message again
    assert "miss" in log_text.lower(), "Expected 'miss' message after file touch."
    # 如果失效单独记录日志： / If invalidation logs separately:
    # invalidation_logged = "invalidating" in log_text.lower() # 检查特定消息 / Check for specific message
    # print(f" -> Invalidation logged: {invalidation_logged}")
    print(" -> Miss log found after invalidation.")

    print("Verified: DEBUG log messages appear as expected (basic check).")

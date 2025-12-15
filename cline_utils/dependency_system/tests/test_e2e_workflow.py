"""
测试模块：端到端工作流测试
Test Module: End-to-End Workflow Tests

本模块提供了对依赖系统完整工作流的端到端测试，包括：
- 新项目首次分析测试
- 缓存机制验证测试（幂等性）
- 强制重新分析测试（--force-analysis）
- 强制重新生成嵌入测试（--force-embeddings）
- 强制重新验证测试（--force-validate）

This module provides end-to-end tests for dependency system complete workflow, including:
- Fresh project analysis tests
- Cache mechanism verification tests (idempotency)
- Force re-analysis tests (--force-analysis)
- Force regenerate embeddings tests (--force-embeddings)
- Force revalidation tests (--force-validate)
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入操作系统接口模块 / Import OS interface module
import os
# 导入文件操作模块 / Import file operations module
import shutil
# 导入JSON处理模块 / Import JSON processing module
import json
# 导入argparse用于命令行参数模拟 / Import argparse for command-line argument simulation
import argparse
# 导入Path类用于路径操作 / Import Path class for path operations
from pathlib import Path
# 导入mock工具 / Import mock tools
from unittest.mock import MagicMock, patch

# 导入被测试的命令处理器和缓存管理器 / Import command handler and cache manager to be tested
from cline_utils.dependency_system.dependency_processor import command_handler_analyze_project
from cline_utils.dependency_system.utils.cache_manager import clear_all_caches
# 导入numpy用于嵌入向量模拟 / Import numpy for embedding vector simulation
import numpy as np

# --- Fixtures（测试固件） ---

@pytest.fixture(autouse=True)
def mock_embedding_manager():
    """
    自动使用的测试fixture：模拟嵌入管理器
    Auto-use test fixture: Mock Embedding Manager

    目的：避免下载实际的机器学习模型，提高测试速度
    Purpose: Avoid downloading actual ML models, improve test speed

    模拟的功能：
    1. 模拟模型加载（_load_model）
    2. 模拟文本编码（_encode_text）
    3. 模拟模型实例（MODEL_INSTANCE）
    4. 设置模拟的模型配置（SELECTED_MODEL_CONFIG）

    Mocked functionalities:
    1. Mock model loading (_load_model)
    2. Mock text encoding (_encode_text)
    3. Mock model instance (MODEL_INSTANCE)
    4. Set mocked model config (SELECTED_MODEL_CONFIG)
    """
    # 使用patch模拟_load_model函数 / Use patch to mock _load_model function
    with patch("cline_utils.dependency_system.analysis.embedding_manager._load_model") as mock_load, \
         # 模拟_encode_text函数 / Mock _encode_text function
         patch("cline_utils.dependency_system.analysis.embedding_manager._encode_text") as mock_encode, \
         # 模拟MODEL_INSTANCE全局变量 / Mock MODEL_INSTANCE global variable
         patch("cline_utils.dependency_system.analysis.embedding_manager.MODEL_INSTANCE", new_callable=MagicMock) as mock_instance, \
         # 设置模拟的模型配置 / Set mocked model config
         patch("cline_utils.dependency_system.analysis.embedding_manager.SELECTED_MODEL_CONFIG", {"type": "sentence-transformer", "name": "mock-model"}):

        # 配置mock_load返回模拟的模型实例 / Configure mock_load to return mocked model instance
        mock_load.return_value = mock_instance

        # 定义_load_model的副作用函数：设置全局MODEL_INSTANCE / Define side effect function for _load_model: set global MODEL_INSTANCE
        def side_effect_load(*args, **kwargs):
            # 导入embedding_manager模块 / Import embedding_manager module
            import cline_utils.dependency_system.analysis.embedding_manager as em
            # 设置全局MODEL_INSTANCE为模拟实例 / Set global MODEL_INSTANCE to mock instance
            em.MODEL_INSTANCE = mock_instance
            # 返回模拟实例 / Return mock instance
            return mock_instance

        # 设置mock_load的副作用 / Set side effect for mock_load
        mock_load.side_effect = side_effect_load

        # 定义_encode_text的副作用函数：返回随机向量 / Define side effect function for _encode_text: return random vector
        def side_effect_encode(text, model_config):
            # 返回384维的随机向量（float32类型） / Return random 384-dimensional vector (float32 type)
            return np.random.rand(384).astype(np.float32)

        # 设置mock_encode的副作用 / Set side effect for mock_encode
        mock_encode.side_effect = side_effect_encode

        # 模拟sentence-transformer的encode方法 / Mock sentence-transformer's encode method
        # 返回形状为(1, 384)的随机矩阵 / Return random matrix with shape (1, 384)
        mock_instance.encode.return_value = np.random.rand(1, 384).astype(np.float32)

        # 将模拟环境提供给测试函数 / Yield mocked environment to test function
        yield

@pytest.fixture(scope="function")
def test_project_e2e(tmp_path):
    """
    测试fixture：设置端到端测试的真实项目结构
    Test fixture: Setup realistic project structure for E2E testing

    功能：
    1. 创建临时项目目录
    2. 创建配置文件（.clinerules、.clinerules.config.json）
    3. 创建源代码文件
    4. 创建文档文件
    5. 创建内存目录

    Features:
    1. Create temporary project directory
    2. Create config files (.clinerules, .clinerules.config.json)
    3. Create source code files
    4. Create documentation files
    5. Create memory directory

    返回：
    - 项目根目录路径（Path对象）

    Returns:
    - Project root directory path (Path object)
    """
    # 创建临时项目目录 / Create temporary project directory
    project_dir = tmp_path / "test_project_e2e"
    project_dir.mkdir()

    # 创建.clinerules配置文件 / Create .clinerules config file
    # 定义代码根目录和文档目录 / Define code root directories and doc directories
    (project_dir / ".clinerules").write_text("[CODE_ROOT_DIRECTORIES]\n- src\n\n[DOC_DIRECTORIES]\n- docs")
    # 创建.clinerules.config.json配置文件 / Create .clinerules.config.json config file
    (project_dir / ".clinerules.config.json").write_text(json.dumps({
        "paths": {
            "doc_dir": "docs",  # 文档目录 / Documentation directory
            "memory_dir": "cline_docs",  # 内存目录 / Memory directory
            "cache_dir": "cache",  # 缓存目录 / Cache directory
            "embeddings_dir": "cline_docs/embeddings"  # 嵌入向量目录 / Embeddings directory
        },
        "excluded_dirs": [".git", "venv"],  # 排除目录列表 / Excluded directories list
        "embedding": {"model_selection": "mpnet"}  # 嵌入模型配置 / Embedding model config
    }))

    # 创建源代码目录和文件 / Create source code directory and files
    src_dir = project_dir / "src"
    src_dir.mkdir()
    # 创建main.py，导入utils模块 / Create main.py, imports utils module
    (src_dir / "main.py").write_text("import utils\nprint('Main running')")
    # 创建utils.py，定义helper函数 / Create utils.py, defines helper function
    (src_dir / "utils.py").write_text("def helper(): return True")

    # 创建文档目录和文件 / Create documentation directory and files
    docs_dir = project_dir / "docs"
    docs_dir.mkdir()
    # 创建readme.md，描述main.py / Create readme.md, describes main.py
    (docs_dir / "readme.md").write_text("# Project Readme\nDescribes main.py")

    # 创建内存目录（用于存储分析结果） / Create memory directory (for storing analysis results)
    memory_dir = project_dir / "cline_docs"
    memory_dir.mkdir()

    # 返回项目目录路径 / Return project directory path
    return project_dir

@pytest.fixture
def mock_args():
    """
    测试fixture：创建模拟的命令行参数对象
    Test fixture: Create mocked command-line arguments object

    功能：
    创建argparse.Namespace对象，包含默认参数值

    Features:
    Create argparse.Namespace object with default parameter values

    返回：
    - MagicMock对象，模拟argparse.Namespace

    Returns:
    - MagicMock object, simulates argparse.Namespace
    """
    # 创建MagicMock对象，指定spec为argparse.Namespace / Create MagicMock object with spec as argparse.Namespace
    args = MagicMock(spec=argparse.Namespace)
    # 设置默认的project_root参数为当前目录 / Set default project_root parameter to current directory
    args.project_root = "."
    # 设置默认的output参数为None（不指定输出文件） / Set default output parameter to None (no output file specified)
    args.output = None
    # 设置默认的force_analysis参数为False（不强制重新分析） / Set default force_analysis parameter to False (don't force re-analysis)
    args.force_analysis = False
    # 设置默认的force_embeddings参数为False（不强制重新生成嵌入） / Set default force_embeddings parameter to False (don't force regenerate embeddings)
    args.force_embeddings = False
    # 设置默认的force_validate参数为False（不强制重新验证） / Set default force_validate parameter to False (don't force revalidation)
    args.force_validate = False
    # 返回模拟的参数对象 / Return mocked arguments object
    return args

# --- Tests（测试用例） ---

def test_e2e_analyze_project_fresh(test_project_e2e, mock_args, capsys):
    """
    测试用例：测试新项目的首次分析
    Test Case: Test Fresh Analysis of New Project

    目的：验证analyze-project命令能正确处理全新项目
    Purpose: Verify analyze-project command correctly handles fresh project

    测试步骤：
    1. 清空所有缓存
    2. 设置项目根目录
    3. 运行分析命令
    4. 验证退出码为0（成功）
    5. 验证生成的文件存在
    6. 验证输出信息

    Test Steps:
    1. Clear all caches
    2. Set project root directory
    3. Run analysis command
    4. Verify exit code is 0 (success)
    5. Verify generated files exist
    6. Verify output messages

    验证点：
    1. 命令执行成功（exit_code == 0）
    2. 生成嵌入元数据文件（metadata.json）
    3. 生成依赖追踪文件（doc_tracker.md或tracker.md）
    4. 输出包含成功消息

    Verification Points:
    1. Command executes successfully (exit_code == 0)
    2. Embedding metadata file is generated (metadata.json)
    3. Dependency tracker file is generated (doc_tracker.md or tracker.md)
    4. Output contains success message
    """
    # 步骤1：清空所有缓存，确保是全新开始 / Step 1: Clear all caches to ensure fresh start
    clear_all_caches()
    # 步骤2：设置项目根目录为测试项目路径 / Step 2: Set project root to test project path
    mock_args.project_root = str(test_project_e2e)

    # 步骤3：运行分析命令 / Step 3: Run analysis command
    exit_code = command_handler_analyze_project(mock_args)

    # 步骤4：验证退出码为0（成功） / Step 4: Verify exit code is 0 (success)
    assert exit_code == 0

    # 步骤5：验证输出文件存在 / Step 5: Verify output files exist
    cline_docs = test_project_e2e / "cline_docs"
    # 验证嵌入元数据文件存在 / Verify embedding metadata file exists
    assert (cline_docs / "embeddings" / "metadata.json").exists()
    # 验证依赖追踪文件存在（可能是doc_tracker.md或tracker.md） / Verify dependency tracker file exists (may be doc_tracker.md or tracker.md)
    assert (cline_docs / "doc_tracker.md").exists() or (cline_docs / "tracker.md").exists()

    # 步骤6：验证捕获的输出包含成功消息 / Step 6: Verify captured output contains success message
    captured = capsys.readouterr()
    assert "Project analysis completed successfully" in captured.out

def test_e2e_analyze_project_cached(test_project_e2e, mock_args, capsys):
    """
    测试用例：测试第二次运行使用缓存数据（幂等性）
    Test Case: Test Second Run Uses Cached Data (Idempotency)

    目的：验证分析命令的幂等性，第二次运行应使用缓存
    Purpose: Verify idempotency of analysis command, second run should use cache

    测试步骤：
    1. 清空所有缓存
    2. 第一次运行分析（建立缓存）
    3. 第二次运行分析（应使用缓存）
    4. 验证两次运行都成功
    5. 验证输出文件仍然存在

    Test Steps:
    1. Clear all caches
    2. First run analysis (establish cache)
    3. Second run analysis (should use cache)
    4. Verify both runs succeed
    5. Verify output files still exist

    验证点：
    1. 第一次运行成功（exit_code1 == 0）
    2. 第二次运行成功（exit_code2 == 0）
    3. 输出文件在第二次运行后仍存在

    Verification Points:
    1. First run succeeds (exit_code1 == 0)
    2. Second run succeeds (exit_code2 == 0)
    3. Output files still exist after second run
    """
    # 步骤1：清空所有缓存 / Step 1: Clear all caches
    clear_all_caches()
    # 设置项目根目录 / Set project root directory
    mock_args.project_root = str(test_project_e2e)

    # 步骤2：第一次运行分析 / Step 2: First run analysis
    print("--- First Run ---")  # 输出分隔符 / Output separator
    exit_code1 = command_handler_analyze_project(mock_args)
    # 验证第一次运行成功 / Verify first run succeeds
    assert exit_code1 == 0

    # 步骤3：第二次运行分析 / Step 3: Second run analysis
    print("--- Second Run ---")  # 输出分隔符 / Output separator
    exit_code2 = command_handler_analyze_project(mock_args)
    # 验证第二次运行成功 / Verify second run succeeds
    assert exit_code2 == 0

    # 步骤4：验证输出文件仍然存在 / Step 4: Verify output files still exist
    cline_docs = test_project_e2e / "cline_docs"
    assert (cline_docs / "embeddings" / "metadata.json").exists()

def test_e2e_force_analysis(test_project_e2e, mock_args):
    """
    测试用例：测试--force-analysis触发重新分析
    Test Case: Test --force-analysis Triggers Re-analysis

    目的：验证--force-analysis参数能强制重新分析，忽略缓存
    Purpose: Verify --force-analysis parameter forces re-analysis, ignoring cache

    测试步骤：
    1. 清空所有缓存
    2. 设置force_analysis参数为True
    3. 运行分析命令
    4. 验证命令执行成功

    Test Steps:
    1. Clear all caches
    2. Set force_analysis parameter to True
    3. Run analysis command
    4. Verify command executes successfully

    验证点：
    1. 命令执行成功（exit_code == 0）

    Verification Points:
    1. Command executes successfully (exit_code == 0)
    """
    # 步骤1：清空所有缓存 / Step 1: Clear all caches
    clear_all_caches()
    # 设置项目根目录 / Set project root directory
    mock_args.project_root = str(test_project_e2e)
    # 步骤2：设置force_analysis为True / Step 2: Set force_analysis to True
    mock_args.force_analysis = True

    # 步骤3：运行分析命令 / Step 3: Run analysis command
    exit_code = command_handler_analyze_project(mock_args)
    # 步骤4：验证命令执行成功 / Step 4: Verify command executes successfully
    assert exit_code == 0

def test_e2e_force_embeddings(test_project_e2e, mock_args):
    """
    测试用例：测试--force-embeddings正常工作
    Test Case: Test --force-embeddings Works Correctly

    目的：验证--force-embeddings参数能强制重新生成嵌入向量
    Purpose: Verify --force-embeddings parameter forces regeneration of embeddings

    测试步骤：
    1. 清空所有缓存
    2. 设置force_embeddings参数为True
    3. 运行分析命令
    4. 验证命令执行成功

    Test Steps:
    1. Clear all caches
    2. Set force_embeddings parameter to True
    3. Run analysis command
    4. Verify command executes successfully

    验证点：
    1. 命令执行成功（exit_code == 0）

    Verification Points:
    1. Command executes successfully (exit_code == 0)
    """
    # 步骤1：清空所有缓存 / Step 1: Clear all caches
    clear_all_caches()
    # 设置项目根目录 / Set project root directory
    mock_args.project_root = str(test_project_e2e)
    # 步骤2：设置force_embeddings为True / Step 2: Set force_embeddings to True
    mock_args.force_embeddings = True

    # 步骤3：运行分析命令 / Step 3: Run analysis command
    exit_code = command_handler_analyze_project(mock_args)
    # 步骤4：验证命令执行成功 / Step 4: Verify command executes successfully
    assert exit_code == 0

def test_e2e_force_validate(test_project_e2e, mock_args, caplog):
    """
    测试用例：测试--force-validate清除验证缓存
    Test Case: Test --force-validate Clears Validation Cache

    目的：验证--force-validate参数能清除验证缓存并重新验证
    Purpose: Verify --force-validate parameter clears validation cache and revalidates

    测试步骤：
    1. 清空所有缓存
    2. 设置force_validate参数为True
    3. 配置日志捕获（INFO级别）
    4. 运行分析命令
    5. 验证命令执行成功
    6. 验证日志包含清除验证缓存的消息

    Test Steps:
    1. Clear all caches
    2. Set force_validate parameter to True
    3. Configure log capture (INFO level)
    4. Run analysis command
    5. Verify command executes successfully
    6. Verify log contains validation cache clearing message

    验证点：
    1. 命令执行成功（exit_code == 0）
    2. 日志中包含"Cleared validation cache"消息

    Verification Points:
    1. Command executes successfully (exit_code == 0)
    2. Log contains "Cleared validation cache" message
    """
    # 步骤1：清空所有缓存 / Step 1: Clear all caches
    clear_all_caches()
    # 设置项目根目录 / Set project root directory
    mock_args.project_root = str(test_project_e2e)
    # 步骤2：设置force_validate为True / Step 2: Set force_validate to True
    mock_args.force_validate = True

    # 步骤3：配置日志捕获级别为INFO / Step 3: Configure log capture level to INFO
    # 使用caplog.at_level上下文管理器 / Use caplog.at_level context manager
    with caplog.at_level("INFO"):
        # 步骤4：运行分析命令 / Step 4: Run analysis command
        exit_code = command_handler_analyze_project(mock_args)

    # 步骤5：验证命令执行成功 / Step 5: Verify command executes successfully
    assert exit_code == 0
    # 步骤6：验证日志中包含清除验证缓存的消息 / Step 6: Verify log contains validation cache clearing message
    assert "Cleared validation cache" in caplog.text

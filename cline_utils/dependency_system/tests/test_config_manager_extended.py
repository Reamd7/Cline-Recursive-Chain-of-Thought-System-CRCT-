"""
测试模块：配置管理器扩展测试
Test Module: Config Manager Extended Tests

本模块提供了对ConfigManager类的全面测试，包括：
- 单例模式验证
- 默认配置值测试
- 环境变量覆盖测试
- 资源自适应调整测试
- 优化建议生成测试

This module provides comprehensive tests for the ConfigManager class, including:
- Singleton pattern validation
- Default configuration value tests
- Environment variable override tests
- Resource adaptive adjustment tests
- Optimization recommendation generation tests
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入操作系统接口模块，用于环境变量操作 / Import OS interface module for environment variable operations
import os
# 导入JSON处理模块 / Import JSON processing module
import json
# 导入unittest.mock的模拟工具，用于创建模拟对象和打补丁 / Import mock tools from unittest.mock
from unittest.mock import MagicMock, patch, mock_open

# 导入被测试的ConfigManager类和默认配置 / Import ConfigManager class and default config to be tested
from cline_utils.dependency_system.utils.config_manager import (
    ConfigManager,
    DEFAULT_CONFIG
)

@pytest.fixture(autouse=True)
def mock_cached():
    """
    自动使用的fixture：模拟缓存装饰器
    Auto-use fixture: Mock cache decorator

    目的：禁用缓存装饰器，确保每次调用都执行实际逻辑
    Purpose: Disable cache decorator to ensure actual logic is executed on each call
    """
    # 定义一个无操作的缓存装饰器 / Define a no-op cache decorator
    def no_op_cached(*args, **kwargs):
        # 装饰器函数，直接返回原始函数，不添加任何缓存逻辑 / Decorator function that returns original function without caching
        def decorator(func):
            return func
        return decorator

    # 使用patch替换cache_manager中的cached装饰器 / Use patch to replace cached decorator in cache_manager
    # side_effect使得每次调用都返回no_op_cached / side_effect makes each call return no_op_cached
    with patch("cline_utils.dependency_system.utils.cache_manager.cached", side_effect=no_op_cached):
        yield

@pytest.fixture
def clean_config_manager():
    """
    测试fixture：提供干净的ConfigManager实例
    Test fixture: Provide clean ConfigManager instance

    功能：
    1. 重置单例实例
    2. 模拟文件I/O操作
    3. 测试后清理

    Features:
    1. Reset singleton instance
    2. Mock file I/O operations
    3. Cleanup after test
    """
    # 重置单例实例为None，确保测试开始时是全新状态 / Reset singleton instance to None for fresh state
    ConfigManager._instance = None
    # 打补丁：模拟加载用户配置文件方法，避免实际文件读取 / Patch: Mock loading user config file to avoid actual file I/O
    with patch.object(ConfigManager, '_load_user_config_file', return_value=None):
        # 打补丁：模拟保存配置方法，避免实际文件写入 / Patch: Mock saving config to avoid actual file writing
        with patch.object(ConfigManager, '_save_config', return_value=True):
            # 创建ConfigManager实例 / Create ConfigManager instance
            manager = ConfigManager()
            # 将实例提供给测试函数 / Yield instance to test function
            yield manager
    # 测试结束后，再次重置单例实例 / After test, reset singleton instance again
    ConfigManager._instance = None

class TestConfigManagerExtended:
    """
    测试类：ConfigManager扩展功能测试
    Test Class: ConfigManager Extended Functionality Tests

    测试ConfigManager的各种高级功能，包括单例模式、配置更新、
    环境变量覆盖、资源自适应调整等。
    """

    def test_singleton(self, clean_config_manager):
        """
        测试用例：验证单例模式
        Test Case: Verify Singleton Pattern

        目的：确保ConfigManager遵循单例模式，多次创建返回同一实例
        Purpose: Ensure ConfigManager follows singleton pattern
        """
        # 第一次调用ConfigManager()获取实例 / First call to get ConfigManager instance
        manager1 = ConfigManager()
        # 第二次调用ConfigManager()获取实例 / Second call to get ConfigManager instance
        manager2 = ConfigManager()
        # 断言：两次获取的实例是同一个对象（使用is检查对象身份）
        # Assertion: Both instances are the same object (using 'is' to check object identity)
        assert manager1 is manager2

    def test_default_values(self, clean_config_manager):
        """
        测试用例：验证默认配置值
        Test Case: Verify Default Configuration Values

        目的：确保ConfigManager正确加载默认配置值
        Purpose: Ensure ConfigManager loads default configuration values correctly
        """
        # 断言：验证性能配置中的默认批处理大小为32
        # Assertion: Verify default batch size in performance config is 32
        assert clean_config_manager.config["performance"]["default_batch_size"] == 32
        # 断言：验证资源配置中的最小内存要求为512MB
        # Assertion: Verify minimum memory requirement in resources config is 512MB
        assert clean_config_manager.config["resources"]["min_memory_mb"] == 512

    def test_deep_update(self, clean_config_manager):
        """
        测试用例：验证深度字典更新
        Test Case: Verify Deep Dictionary Update

        目的：测试_deep_update方法能否正确地递归合并嵌套字典
        Purpose: Test if _deep_update method correctly merges nested dictionaries recursively
        """
        # 创建原始字典，包含嵌套结构 / Create original dictionary with nested structure
        original = {"a": 1, "b": {"c": 2}}
        # 创建更新字典，包含新键和嵌套更新 / Create update dictionary with new keys and nested updates
        updates = {"b": {"d": 3}, "e": 4}
        # 调用_deep_update方法进行深度合并 / Call _deep_update method for deep merge
        clean_config_manager._deep_update(original, updates)
        # 断言：验证合并后的结果
        # - 保留了原有的"a": 1
        # - 合并了"b"的嵌套字典，保留"c": 2，添加"d": 3
        # - 添加了新的顶层键"e": 4
        # Assertion: Verify merged result preserves, merges, and adds keys correctly
        assert original == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    def test_environment_overrides(self):
        """
        测试用例：环境变量覆盖配置
        Test Case: Environment Variable Override Configuration

        目的：验证环境变量能够正确覆盖默认配置值
        Purpose: Verify environment variables can correctly override default config values
        """
        # 重置单例实例，确保测试隔离 / Reset singleton instance for test isolation
        ConfigManager._instance = None

        # 使用patch.dict临时设置环境变量 / Use patch.dict to temporarily set environment variables
        with patch.dict(os.environ, {
            "ANALYZER_BATCH_SIZE": "64",      # 设置批处理大小为64 / Set batch size to 64
            "ANALYZER_LOG_LEVEL": "DEBUG",    # 设置日志级别为DEBUG / Set log level to DEBUG
            "ANALYZER_USE_STREAMING": "false" # 禁用流式分析 / Disable streaming analysis
        }):
            # 模拟文件加载和保存操作 / Mock file loading and saving operations
            with patch.object(ConfigManager, '_load_user_config_file', return_value=None):
                with patch.object(ConfigManager, '_save_config', return_value=True):
                    # 创建ConfigManager实例，此时会读取环境变量 / Create ConfigManager, it will read env vars
                    manager = ConfigManager()

                    # 断言：验证批处理大小被环境变量覆盖为64 / Assertion: Verify batch size overridden to 64
                    assert manager.get_performance_setting("default_batch_size") == 64
                    # 断言：验证日志级别被环境变量覆盖为DEBUG / Assertion: Verify log level overridden to DEBUG
                    assert manager.get_output_setting("log_level") == "DEBUG"
                    # 断言：验证流式分析被环境变量禁用 / Assertion: Verify streaming analysis disabled
                    assert manager.get_performance_setting("use_streaming_analysis") is False

    def test_resource_adjustments_low_memory(self, clean_config_manager):
        """
        测试用例：低内存环境下的资源调整
        Test Case: Resource Adjustments Under Low Memory

        目的：验证系统在低内存环境下能够自动调整配置参数
        Purpose: Verify system can automatically adjust config parameters under low memory
        """
        # 创建模拟的ResourceValidator实例 / Create mock ResourceValidator instance
        mock_validator = MagicMock()
        # 设置模拟的系统资源验证结果：低内存（512MB）
        # Set mock system resource validation result: low memory (512MB)
        mock_validator.validate_system_resources.return_value = {
            "valid": True,                                      # 系统资源验证通过 / System resource validation passed
            "resource_check": {
                "memory": {"available_mb": 512},                # 可用内存仅512MB / Only 512MB available memory
                "cpu": {"cores": 4},                            # CPU核心数为4 / 4 CPU cores
                "disk_space": {"free_space_mb": 10000}          # 磁盘空间充足 / Sufficient disk space
            }
        }

        # 使用patch替换ResourceValidator，使其返回我们的模拟对象
        # Use patch to replace ResourceValidator to return our mock object
        with patch("cline_utils.dependency_system.utils.config_manager.ResourceValidator", return_value=mock_validator):
            # 调用资源调整方法 / Call resource adjustment method
            clean_config_manager._apply_resource_adjustments()

            # === 验证资源调整的效果 === / === Verify resource adjustment effects ===
            # 断言：批处理大小应降低到16或更小 / Assertion: Batch size should be reduced to 16 or less
            assert clean_config_manager.get_performance_setting("default_batch_size") <= 16
            # 断言：嵌入批处理大小应降低到8或更小 / Assertion: Embedding batch size should be reduced to 8 or less
            assert clean_config_manager.get_performance_setting("embedding_batch_size") <= 8
            # 断言：工作线程数应降低到1 / Assertion: Worker count should be reduced to 1
            assert clean_config_manager.get_performance_setting("max_workers") == 1
            # 断言：应启用流式分析以减少内存占用 / Assertion: Streaming analysis should be enabled
            assert clean_config_manager.get_performance_setting("use_streaming_analysis") is True

    def test_resource_adjustments_low_disk(self, clean_config_manager):
        """
        测试用例：低磁盘空间环境下的资源调整
        Test Case: Resource Adjustments Under Low Disk Space

        目的：验证系统在低磁盘空间环境下能够自动调整配置参数
        Purpose: Verify system can automatically adjust config parameters under low disk space
        """
        # 创建模拟的ResourceValidator实例 / Create mock ResourceValidator instance
        mock_validator = MagicMock()
        # 设置模拟的系统资源验证结果：低磁盘空间（100MB）
        # Set mock system resource validation result: low disk space (100MB)
        mock_validator.validate_system_resources.return_value = {
            "valid": True,                                      # 系统资源验证通过 / System resource validation passed
            "resource_check": {
                "memory": {"available_mb": 4096},               # 内存充足 / Sufficient memory
                "cpu": {"cores": 4},                            # CPU核心数为4 / 4 CPU cores
                "disk_space": {"free_space_mb": 100}            # 磁盘空间仅100MB / Only 100MB disk space
            }
        }

        # 使用patch替换ResourceValidator / Use patch to replace ResourceValidator
        with patch("cline_utils.dependency_system.utils.config_manager.ResourceValidator", return_value=mock_validator):
            # 调用资源调整方法 / Call resource adjustment method
            clean_config_manager._apply_resource_adjustments()

            # === 验证资源调整的效果 === / === Verify resource adjustment effects ===
            # 断言：缓存大小限制应降低到1000或更小 / Assertion: Cache size limit reduced to 1000 or less
            assert clean_config_manager.get_performance_setting("cache_size_limit") <= 1000
            # 断言：应禁用自动生成图表以节省磁盘空间 / Assertion: Auto-generate diagrams disabled to save disk
            assert clean_config_manager.get_output_setting("auto_generate_diagrams") is False

    def test_get_analysis_settings(self, clean_config_manager):
        """
        测试用例：获取分析设置
        Test Case: Get Analysis Settings

        目的：验证get_analysis_settings方法返回正确的分析配置
        Purpose: Verify get_analysis_settings method returns correct analysis configuration
        """
        # 调用获取分析设置的方法 / Call method to get analysis settings
        settings = clean_config_manager.get_analysis_settings()

        # === 验证返回的设置包含所有必需的键 === / === Verify returned settings contain all required keys ===
        # 断言：包含流式分析开关 / Assertion: Contains streaming analysis switch
        assert "use_streaming" in settings
        # 断言：包含批处理大小配置 / Assertion: Contains batch size configuration
        assert "batch_size" in settings
        # 断言：包含内存限制配置 / Assertion: Contains memory limit configuration
        assert "memory_limit_mb" in settings
        # 断言：默认批处理大小应为32 / Assertion: Default batch size should be 32
        assert settings["batch_size"] == 32

    def test_get_optimization_recommendations(self, clean_config_manager):
        """
        测试用例：获取优化建议
        Test Case: Get Optimization Recommendations

        目的：验证系统能够根据资源状况生成合理的优化建议
        Purpose: Verify system can generate reasonable optimization recommendations based on resource status
        """
        # 手动设置验证结果，模拟资源受限的环境 / Manually set validation results to simulate resource-constrained environment
        clean_config_manager._resource_validation_results = {
            "resource_check": {
                "memory": {"available_mb": 512},    # 低内存：512MB / Low memory: 512MB
                "cpu": {"cores": 1},                 # 单核CPU / Single core CPU
                "disk_space": {"free_space_mb": 100} # 低磁盘空间：100MB / Low disk: 100MB
            }
        }

        # 调用获取优化建议的方法 / Call method to get optimization recommendations
        recommendations = clean_config_manager.get_optimization_recommendations()

        # === 验证优化建议的内容 === / === Verify optimization recommendation content ===
        # 断言：应包含启用流式分析的建议 / Assertion: Should contain recommendation to enable streaming
        assert any("streaming analysis" in r for r in recommendations)
        # 断言：应包含关于CPU受限的建议 / Assertion: Should contain recommendation about limited CPU
        assert any("limited CPU" in r for r in recommendations)
        # 断言：应包含释放磁盘空间的建议 / Assertion: Should contain recommendation to free disk space
        assert any("freeing up disk space" in r for r in recommendations)

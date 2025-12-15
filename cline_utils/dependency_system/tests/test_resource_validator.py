"""
测试模块：资源验证器测试
Test Module: Resource Validator Tests

本模块提供了对ResourceValidator类的全面测试，包括：
- 缓存机制测试（保存、加载、有效性验证）
- 内存资源验证测试
- 磁盘空间验证测试
- 系统资源综合验证测试

This module provides comprehensive tests for the ResourceValidator class, including:
- Cache mechanism tests (save, load, validity verification)
- Memory resource validation tests
- Disk space validation tests
- System resource integration tests
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入操作系统接口模块 / Import OS interface module
import os
# 导入JSON处理模块 / Import JSON processing module
import json
# 导入日期时间处理模块 / Import datetime processing module
import datetime
# 导入文件操作模块 / Import file operations module
import shutil
# 导入mock工具，用于模拟对象和打补丁 / Import mock tools for creating mock objects and patching
from unittest.mock import MagicMock, patch, mock_open
# 导入Path类，用于路径操作 / Import Path class for path operations
from pathlib import Path

# 导入被测试的资源验证器及相关函数 / Import resource validator and related functions to be tested
from cline_utils.dependency_system.utils.resource_validator import (
    ResourceValidator,  # 资源验证器主类 / Main resource validator class
    _get_cache_path,  # 获取缓存路径函数 / Get cache path function
    _load_validation_cache,  # 加载验证缓存函数 / Load validation cache function
    _save_validation_cache,  # 保存验证缓存函数 / Save validation cache function
    _is_cache_valid,  # 验证缓存有效性函数 / Verify cache validity function
    validate_and_get_optimal_settings,  # 验证并获取最优设置函数 / Validate and get optimal settings function
    MemoryLimitError,  # 内存限制错误异常 / Memory limit error exception
    DiskSpaceError  # 磁盘空间错误异常 / Disk space error exception
)

# Mock数据常量 / Mock data constants
# 模拟的项目路径 / Mock project path
MOCK_PROJECT_PATH = "/path/to/project"
# 模拟的缓存文件路径 / Mock cache file path
MOCK_CACHE_PATH = "/path/to/cache/validation_cache.json"

@pytest.fixture
def validator():
    """
    测试fixture：提供ResourceValidator实例
    Test fixture: Provide ResourceValidator instance

    返回：
    - ResourceValidator实例，非严格模式（strict_mode=False）

    Returns:
    - ResourceValidator instance in non-strict mode (strict_mode=False)
    """
    # 创建非严格模式的验证器实例 / Create validator instance in non-strict mode
    return ResourceValidator(strict_mode=False)

@pytest.fixture
def mock_psutil():
    """
    测试fixture：提供模拟的psutil模块
    Test fixture: Provide mocked psutil module

    目的：模拟系统资源监控库，避免依赖实际系统状态
    Purpose: Mock system resource monitoring library to avoid dependency on actual system state

    返回：
    - 模拟的psutil模块对象

    Returns:
    - Mocked psutil module object
    """
    # 创建MagicMock对象模拟psutil模块 / Create MagicMock object to mock psutil module
    mock = MagicMock()
    # 使用patch.dict将模拟对象注入sys.modules / Use patch.dict to inject mock object into sys.modules
    with patch.dict("sys.modules", {"psutil": mock}):
        # 将模拟对象提供给测试函数 / Yield mock object to test function
        yield mock

@pytest.fixture
def mock_shutil():
    """
    测试fixture：提供模拟的shutil模块
    Test fixture: Provide mocked shutil module

    目的：模拟文件操作库，避免实际磁盘操作
    Purpose: Mock file operations library to avoid actual disk operations

    返回：
    - 模拟的shutil模块对象

    Returns:
    - Mocked shutil module object
    """
    # 使用patch模拟resource_validator中的shutil / Use patch to mock shutil in resource_validator
    with patch("cline_utils.dependency_system.utils.resource_validator.shutil") as mock:
        # 将模拟对象提供给测试函数 / Yield mock object to test function
        yield mock

@pytest.fixture
def mock_fs():
    """
    测试fixture：提供模拟的文件系统操作
    Test fixture: Provide mocked file system operations

    目的：模拟文件打开、路径检查、目录创建等操作
    Purpose: Mock file opening, path checking, directory creation operations

    返回：
    - (mock_file, mock_exists, mock_makedirs) 三元组

    Returns:
    - (mock_file, mock_exists, mock_makedirs) tuple
    """
    # 模拟内置的open函数 / Mock built-in open function
    with patch("builtins.open", mock_open()) as mock_file:
        # 模拟os.path.exists函数 / Mock os.path.exists function
        with patch("os.path.exists") as mock_exists:
            # 模拟os.makedirs函数 / Mock os.makedirs function
            with patch("os.makedirs") as mock_makedirs:
                # 将所有模拟对象作为三元组提供给测试函数 / Yield all mock objects as tuple to test function
                yield mock_file, mock_exists, mock_makedirs

class TestResourceValidatorCache:
    """
    测试类：资源验证器缓存机制测试
    Test Class: Resource Validator Cache Mechanism Tests

    测试ResourceValidator的缓存相关功能，包括：
    - 缓存路径获取
    - 缓存保存和加载
    - 缓存有效性验证（版本、路径、时间、错误状态）

    Tests cache-related functionality of ResourceValidator, including:
    - Cache path retrieval
    - Cache saving and loading
    - Cache validity verification (version, path, time, error state)
    """

    def test_get_cache_path(self):
        """
        测试用例：验证缓存路径获取
        Test Case: Verify Cache Path Retrieval

        目的：确保_get_cache_path()返回正确的缓存文件路径
        Purpose: Ensure _get_cache_path() returns correct cache file path

        验证点：
        1. 路径以"validation_cache.json"结尾

        Verification Points:
        1. Path ends with "validation_cache.json"
        """
        # 调用函数获取缓存路径 / Call function to get cache path
        path = _get_cache_path()
        # 断言：路径应以"validation_cache.json"结尾 / Assert: path should end with "validation_cache.json"
        assert path.endswith("validation_cache.json")

    def test_save_validation_cache(self, mock_fs):
        """
        测试用例：验证缓存保存功能
        Test Case: Verify Cache Saving Functionality

        目的：确保_save_validation_cache()正确保存缓存数据到文件
        Purpose: Ensure _save_validation_cache() correctly saves cache data to file

        验证点：
        1. makedirs被调用以创建缓存目录
        2. 文件以正确路径和模式打开
        3. 数据被写入文件

        Verification Points:
        1. makedirs is called to create cache directory
        2. File is opened with correct path and mode
        3. Data is written to file
        """
        # 解包模拟的文件系统对象 / Unpack mocked file system objects
        mock_file, mock_exists, mock_makedirs = mock_fs
        # 准备测试用的缓存结果数据 / Prepare test cache result data
        results = {"valid": True, "errors": []}

        # 使用patch模拟_get_cache_path返回值 / Use patch to mock _get_cache_path return value
        with patch("cline_utils.dependency_system.utils.resource_validator._get_cache_path", return_value=MOCK_CACHE_PATH):
            # 调用保存缓存函数 / Call save cache function
            _save_validation_cache(MOCK_PROJECT_PATH, results)

            # 断言：makedirs应被调用一次（创建缓存目录） / Assert: makedirs should be called once (create cache directory)
            mock_makedirs.assert_called_once()
            # 断言：文件应以写模式和UTF-8编码打开 / Assert: file should be opened in write mode with UTF-8 encoding
            mock_file.assert_called_with(MOCK_CACHE_PATH, 'w', encoding='utf-8')
            # 获取文件句柄 / Get file handle
            handle = mock_file()
            # 断言：文件写入操作应被调用（验证json.dump被执行） / Assert: file write operation should be called (verify json.dump was executed)
            assert handle.write.called

    def test_load_validation_cache_exists(self, mock_fs):
        """
        测试用例：验证缓存加载功能（缓存存在时）
        Test Case: Verify Cache Loading Functionality (When Cache Exists)

        目的：确保_load_validation_cache()能正确加载已存在的缓存文件
        Purpose: Ensure _load_validation_cache() correctly loads existing cache file

        验证点：
        1. 正确解析JSON缓存数据
        2. 返回的数据与预期一致

        Verification Points:
        1. JSON cache data is correctly parsed
        2. Returned data matches expectation
        """
        # 解包模拟的文件系统对象 / Unpack mocked file system objects
        mock_file, mock_exists, _ = mock_fs
        # 设置mock_exists返回True（模拟文件存在） / Set mock_exists to return True (simulate file exists)
        mock_exists.return_value = True

        # 准备测试用的缓存数据 / Prepare test cache data
        cache_data = {
            "version": "1.0",  # 缓存版本 / Cache version
            "project_path": MOCK_PROJECT_PATH,  # 项目路径 / Project path
            "results": {"valid": True}  # 验证结果 / Validation results
        }

        # 设置mock_file的read方法返回JSON字符串 / Set mock_file's read method to return JSON string
        mock_file.return_value.read.return_value = json.dumps(cache_data)

        # 使用patch模拟_get_cache_path返回值 / Use patch to mock _get_cache_path return value
        with patch("cline_utils.dependency_system.utils.resource_validator._get_cache_path", return_value=MOCK_CACHE_PATH):
            # 调用加载缓存函数 / Call load cache function
            loaded_data = _load_validation_cache()
            # 断言：加载的数据应与原始数据一致 / Assert: loaded data should match original data
            assert loaded_data == cache_data

    def test_load_validation_cache_not_exists(self, mock_fs):
        """
        测试用例：验证缓存加载功能（缓存不存在时）
        Test Case: Verify Cache Loading Functionality (When Cache Does Not Exist)

        目的：确保_load_validation_cache()在缓存文件不存在时返回None
        Purpose: Ensure _load_validation_cache() returns None when cache file does not exist

        验证点：
        1. 文件不存在时返回None

        Verification Points:
        1. Returns None when file does not exist
        """
        # 解包模拟的文件系统对象 / Unpack mocked file system objects
        _, mock_exists, _ = mock_fs
        # 设置mock_exists返回False（模拟文件不存在） / Set mock_exists to return False (simulate file does not exist)
        mock_exists.return_value = False

        # 使用patch模拟_get_cache_path返回值 / Use patch to mock _get_cache_path return value
        with patch("cline_utils.dependency_system.utils.resource_validator._get_cache_path", return_value=MOCK_CACHE_PATH):
            # 调用加载缓存函数 / Call load cache function
            loaded_data = _load_validation_cache()
            # 断言：加载的数据应为None / Assert: loaded data should be None
            assert loaded_data is None

    def test_is_cache_valid_success(self):
        """
        测试用例：验证缓存有效性检查（有效缓存）
        Test Case: Verify Cache Validity Check (Valid Cache)

        目的：确保_is_cache_valid()对有效缓存返回True
        Purpose: Ensure _is_cache_valid() returns True for valid cache

        验证点：
        1. 版本正确
        2. 项目路径匹配
        3. 未过期（7天内）
        4. 无错误记录

        Verification Points:
        1. Correct version
        2. Project path matches
        3. Not expired (within 7 days)
        4. No errors recorded
        """
        # 准备有效的缓存数据 / Prepare valid cache data
        cache_data = {
            "version": "1.0",  # 正确的版本号 / Correct version number
            "project_path": MOCK_PROJECT_PATH,  # 匹配的项目路径 / Matching project path
            "last_validated": datetime.datetime.now().isoformat(),  # 当前时间（未过期） / Current time (not expired)
            "results": {"valid": True, "errors": [], "warnings": []}  # 有效结果，无错误 / Valid results, no errors
        }
        # 断言：缓存应被判定为有效 / Assert: cache should be determined as valid
        assert _is_cache_valid(cache_data, MOCK_PROJECT_PATH) is True

    def test_is_cache_valid_version_mismatch(self):
        """
        测试用例：验证缓存有效性检查（版本不匹配）
        Test Case: Verify Cache Validity Check (Version Mismatch)

        目的：确保版本不匹配的缓存被判定为无效
        Purpose: Ensure cache with version mismatch is determined as invalid

        验证点：
        1. 旧版本缓存返回False

        Verification Points:
        1. Old version cache returns False
        """
        # 准备版本不匹配的缓存数据 / Prepare cache data with version mismatch
        cache_data = {
            "version": "0.9",  # 旧版本号 / Old version number
            "project_path": MOCK_PROJECT_PATH,
            "last_validated": datetime.datetime.now().isoformat(),
            "results": {"valid": True}
        }
        # 断言：缓存应被判定为无效 / Assert: cache should be determined as invalid
        assert _is_cache_valid(cache_data, MOCK_PROJECT_PATH) is False

    def test_is_cache_valid_path_mismatch(self):
        """
        测试用例：验证缓存有效性检查（路径不匹配）
        Test Case: Verify Cache Validity Check (Path Mismatch)

        目的：确保项目路径不匹配的缓存被判定为无效
        Purpose: Ensure cache with project path mismatch is determined as invalid

        验证点：
        1. 不同项目路径的缓存返回False

        Verification Points:
        1. Cache with different project path returns False
        """
        # 准备路径不匹配的缓存数据 / Prepare cache data with path mismatch
        cache_data = {
            "version": "1.0",
            "project_path": "/other/path",  # 不同的项目路径 / Different project path
            "last_validated": datetime.datetime.now().isoformat(),
            "results": {"valid": True}
        }
        # 断言：缓存应被判定为无效 / Assert: cache should be determined as invalid
        assert _is_cache_valid(cache_data, MOCK_PROJECT_PATH) is False

    def test_is_cache_valid_expired(self):
        """
        测试用例：验证缓存有效性检查（缓存过期）
        Test Case: Verify Cache Validity Check (Cache Expired)

        目的：确保过期缓存（超过7天）被判定为无效
        Purpose: Ensure expired cache (over 7 days) is determined as invalid

        验证点：
        1. 8天前的缓存返回False

        Verification Points:
        1. Cache from 8 days ago returns False
        """
        # 计算8天前的日期时间 / Calculate datetime 8 days ago
        old_date = (datetime.datetime.now() - datetime.timedelta(days=8)).isoformat()
        # 准备过期的缓存数据 / Prepare expired cache data
        cache_data = {
            "version": "1.0",
            "project_path": MOCK_PROJECT_PATH,
            "last_validated": old_date,  # 8天前（已过期） / 8 days ago (expired)
            "results": {"valid": True}
        }
        # 断言：缓存应被判定为无效 / Assert: cache should be determined as invalid
        assert _is_cache_valid(cache_data, MOCK_PROJECT_PATH) is False

    def test_is_cache_valid_previous_errors(self):
        """
        测试用例：验证缓存有效性检查（存在历史错误）
        Test Case: Verify Cache Validity Check (Previous Errors Exist)

        目的：确保包含错误的缓存被判定为无效
        Purpose: Ensure cache containing errors is determined as invalid

        验证点：
        1. 有错误记录的缓存返回False

        Verification Points:
        1. Cache with error records returns False
        """
        # 准备包含错误的缓存数据 / Prepare cache data with errors
        cache_data = {
            "version": "1.0",
            "project_path": MOCK_PROJECT_PATH,
            "last_validated": datetime.datetime.now().isoformat(),
            "results": {"valid": False, "errors": ["Some error"]}  # 包含错误 / Contains errors
        }
        # 断言：缓存应被判定为无效 / Assert: cache should be determined as invalid
        assert _is_cache_valid(cache_data, MOCK_PROJECT_PATH) is False

class TestResourceValidatorMemory:
    """
    测试类：资源验证器内存验证测试
    Test Class: Resource Validator Memory Validation Tests

    测试ResourceValidator的内存验证功能，包括：
    - 充足内存验证
    - 临界内存验证（触发异常）
    - 无psutil时的降级处理

    Tests memory validation functionality of ResourceValidator, including:
    - Sufficient memory validation
    - Critical memory validation (trigger exception)
    - Fallback handling when psutil is unavailable
    """

    def test_validate_memory_sufficient(self, validator, mock_psutil):
        """
        测试用例：验证内存充足情况
        Test Case: Verify Sufficient Memory Situation

        目的：确保在内存充足时验证通过
        Purpose: Ensure validation passes when memory is sufficient

        测试场景：
        - 总内存：16GB
        - 可用内存：8GB
        - 使用率：50%

        Test Scenario:
        - Total memory: 16GB
        - Available memory: 8GB
        - Usage: 50%

        验证点：
        1. sufficient为True
        2. critical为False
        3. available_mb为8192.0

        Verification Points:
        1. sufficient is True
        2. critical is False
        3. available_mb is 8192.0
        """
        # 创建内存信息模拟对象 / Create memory info mock object
        memory_mock = MagicMock()
        # 设置总内存为16GB（字节） / Set total memory to 16GB (bytes)
        memory_mock.total = 16 * 1024 * 1024 * 1024
        # 设置可用内存为8GB（字节） / Set available memory to 8GB (bytes)
        memory_mock.available = 8 * 1024 * 1024 * 1024
        # 设置使用率为50% / Set usage to 50%
        memory_mock.percent = 50.0
        # 配置mock_psutil的virtual_memory方法返回内存模拟对象 / Configure mock_psutil's virtual_memory method to return memory mock object
        mock_psutil.virtual_memory.return_value = memory_mock

        # 调用验证器的内存验证方法 / Call validator's memory validation method
        result = validator._validate_memory()
        # 断言：内存应充足 / Assert: memory should be sufficient
        assert result["sufficient"] is True
        # 断言：不应处于临界状态 / Assert: should not be in critical state
        assert result["critical"] is False
        # 断言：可用内存应为8192MB / Assert: available memory should be 8192MB
        assert result["available_mb"] == 8192.0

    def test_validate_memory_critical(self, validator, mock_psutil):
        """
        测试用例：验证内存临界情况
        Test Case: Verify Critical Memory Situation

        目的：确保在内存极度不足时抛出MemoryLimitError异常
        Purpose: Ensure MemoryLimitError exception is raised when memory is critically low

        测试场景：
        - 总内存：16GB
        - 可用内存：100MB（低于最小要求512MB）
        - 使用率：99%

        Test Scenario:
        - Total memory: 16GB
        - Available memory: 100MB (below minimum 512MB)
        - Usage: 99%

        验证点：
        1. 应抛出MemoryLimitError异常

        Verification Points:
        1. Should raise MemoryLimitError exception
        """
        # 创建内存信息模拟对象 / Create memory info mock object
        memory_mock = MagicMock()
        # 设置总内存为16GB / Set total memory to 16GB
        memory_mock.total = 16 * 1024 * 1024 * 1024
        # 设置可用内存为100MB（低于最小要求） / Set available memory to 100MB (below minimum)
        memory_mock.available = 100 * 1024 * 1024
        # 设置使用率为99% / Set usage to 99%
        memory_mock.percent = 99.0
        # 配置mock_psutil的virtual_memory方法返回内存模拟对象 / Configure mock_psutil's virtual_memory method to return memory mock object
        mock_psutil.virtual_memory.return_value = memory_mock

        # 使用pytest.raises断言应抛出MemoryLimitError异常 / Use pytest.raises to assert MemoryLimitError should be raised
        with pytest.raises(MemoryLimitError):
            # 调用验证器的内存验证方法 / Call validator's memory validation method
            validator._validate_memory()

    def test_validate_memory_fallback(self, validator):
        """
        测试用例：验证内存验证降级处理
        Test Case: Verify Memory Validation Fallback

        目的：确保在psutil不可用时使用降级方案
        Purpose: Ensure fallback solution is used when psutil is unavailable

        测试场景：
        - psutil模块不可用
        - 非Windows平台

        Test Scenario:
        - psutil module unavailable
        - Non-Windows platform

        验证点：
        1. fallback为True
        2. sufficient为True（降级方案默认通过）

        Verification Points:
        1. fallback is True
        2. sufficient is True (fallback solution passes by default)
        """
        # 使用patch.dict强制psutil为None（模拟ImportError） / Use patch.dict to force psutil to None (simulate ImportError)
        with patch.dict("sys.modules", {"psutil": None}):
             # 模拟sys.platform为linux（非win32） / Mock sys.platform as linux (not win32)
            with patch("sys.platform", "linux"):
                # 调用验证器的内存验证方法 / Call validator's memory validation method
                result = validator._validate_memory()
                # 断言：应使用降级方案 / Assert: should use fallback solution
                assert result["fallback"] is True
                # 断言：降级方案默认判定为充足 / Assert: fallback solution defaults to sufficient
                assert result["sufficient"] is True

class TestResourceValidatorDisk:
    """
    测试类：资源验证器磁盘空间验证测试
    Test Class: Resource Validator Disk Space Validation Tests

    测试ResourceValidator的磁盘空间验证功能，包括：
    - 充足磁盘空间验证
    - 不足磁盘空间验证

    Tests disk space validation functionality of ResourceValidator, including:
    - Sufficient disk space validation
    - Insufficient disk space validation
    """

    def test_validate_disk_space_sufficient(self, validator, mock_shutil):
        """
        测试用例：验证磁盘空间充足情况
        Test Case: Verify Sufficient Disk Space Situation

        目的：确保在磁盘空间充足时验证通过
        Purpose: Ensure validation passes when disk space is sufficient

        测试场景：
        - 总空间：100GB
        - 已用空间：50GB
        - 剩余空间：50GB
        - 需求空间：500MB

        Test Scenario:
        - Total space: 100GB
        - Used space: 50GB
        - Free space: 50GB
        - Required space: 500MB

        验证点：
        1. sufficient为True
        2. free_space_mb为51200（50GB）

        Verification Points:
        1. sufficient is True
        2. free_space_mb is 51200 (50GB)
        """
        # 配置mock_shutil的disk_usage返回值（总、已用、剩余，单位：字节） / Configure mock_shutil's disk_usage return value (total, used, free in bytes)
        mock_shutil.disk_usage.return_value = (100*1024**3, 50*1024**3, 50*1024**3)

        # 使用patch模拟Path.exists返回True（路径存在） / Use patch to mock Path.exists returning True (path exists)
        with patch("pathlib.Path.exists", return_value=True):
             # 使用patch.object模拟_estimate_required_disk_space返回500MB / Use patch.object to mock _estimate_required_disk_space returning 500MB
            with patch.object(validator, "_estimate_required_disk_space", return_value=500):
                # 调用验证器的磁盘空间验证方法 / Call validator's disk space validation method
                result = validator._validate_disk_space(MOCK_PROJECT_PATH)
                # 断言：磁盘空间应充足 / Assert: disk space should be sufficient
                assert result["sufficient"] is True
                # 断言：剩余空间应为51200MB（50GB） / Assert: free space should be 51200MB (50GB)
                assert result["free_space_mb"] == 50 * 1024

    def test_validate_disk_space_insufficient(self, validator, mock_shutil):
        """
        测试用例：验证磁盘空间不足情况
        Test Case: Verify Insufficient Disk Space Situation

        目的：确保在磁盘空间不足时验证失败
        Purpose: Ensure validation fails when disk space is insufficient

        测试场景：
        - 总空间：100GB
        - 已用空间：99.99GB
        - 剩余空间：10MB
        - 需求空间：500MB

        Test Scenario:
        - Total space: 100GB
        - Used space: 99.99GB
        - Free space: 10MB
        - Required space: 500MB

        验证点：
        1. sufficient为False
        2. error字段存在

        Verification Points:
        1. sufficient is False
        2. error field exists
        """
        # 配置mock_shutil的disk_usage返回值（剩余空间仅10MB） / Configure mock_shutil's disk_usage return value (only 10MB free)
        mock_shutil.disk_usage.return_value = (100*1024**3, 99.99*1024**3, 10*1024**2)

        # 使用patch模拟Path.exists返回True / Use patch to mock Path.exists returning True
        with patch("pathlib.Path.exists", return_value=True):
            # 使用patch.object模拟需求空间为500MB / Use patch.object to mock required space as 500MB
            with patch.object(validator, "_estimate_required_disk_space", return_value=500):
                # 调用验证器的磁盘空间验证方法 / Call validator's disk space validation method
                # 注意：该方法会抑制错误并返回包含sufficient=False的降级结果 / Note: method suppresses error and returns fallback with sufficient=False
                result = validator._validate_disk_space(MOCK_PROJECT_PATH)
                # 断言：磁盘空间应不足 / Assert: disk space should be insufficient
                assert result["sufficient"] is False
                # 断言：结果中应包含错误信息 / Assert: result should contain error information
                assert "error" in result

class TestResourceValidatorIntegration:
    """
    测试类：资源验证器集成测试
    Test Class: Resource Validator Integration Tests

    测试ResourceValidator的完整验证流程，包括：
    - 系统资源综合验证（内存、磁盘、CPU、临时空间、项目特定检查）
    - 最优设置获取（根据系统资源自动调整参数）

    Tests complete validation workflow of ResourceValidator, including:
    - System resource comprehensive validation (memory, disk, CPU, temp space, project-specific checks)
    - Optimal settings retrieval (auto-adjust parameters based on system resources)
    """

    def test_validate_system_resources_success(self, validator):
        """
        测试用例：验证系统资源综合验证成功
        Test Case: Verify System Resource Comprehensive Validation Success

        目的：确保所有资源检查通过时验证成功
        Purpose: Ensure validation succeeds when all resource checks pass

        测试场景：
        - 内存充足（2048MB可用）
        - 磁盘空间充足（5000MB可用）
        - 临时空间充足（5000MB可用）
        - CPU充足（4核心）
        - 项目特定检查通过

        Test Scenario:
        - Sufficient memory (2048MB available)
        - Sufficient disk space (5000MB available)
        - Sufficient temp space (5000MB available)
        - Sufficient CPU (4 cores)
        - Project-specific checks pass

        验证点：
        1. valid为True
        2. errors列表为空
        3. 缓存保存函数被调用

        Verification Points:
        1. valid is True
        2. errors list is empty
        3. Cache save function is called
        """
        # 使用patch.object模拟内存验证通过 / Use patch.object to mock memory validation passing
        with patch.object(validator, "_validate_memory", return_value={"sufficient": True, "critical": False, "available_mb": 2048}):
            # 模拟磁盘空间验证通过 / Mock disk space validation passing
            with patch.object(validator, "_validate_disk_space", return_value={"sufficient": True, "free_space_mb": 5000}):
                # 模拟临时空间验证通过 / Mock temp space validation passing
                with patch.object(validator, "_validate_temporary_space", return_value={"sufficient": True, "free_space_mb": 5000}):
                    # 模拟CPU验证通过 / Mock CPU validation passing
                    with patch.object(validator, "_validate_cpu", return_value={"sufficient": True, "cores": 4}):
                        # 模拟项目特定验证通过 / Mock project-specific validation passing
                        with patch.object(validator, "_validate_project_specific", return_value={"sufficient": True}):
                            # 使用patch模拟缓存保存函数 / Use patch to mock cache save function
                            with patch("cline_utils.dependency_system.utils.resource_validator._save_validation_cache") as mock_save:
                                # 调用系统资源验证方法 / Call system resource validation method
                                results = validator.validate_system_resources(MOCK_PROJECT_PATH)
                                # 断言：验证应成功 / Assert: validation should succeed
                                assert results["valid"] is True
                                # 断言：错误列表应为空 / Assert: errors list should be empty
                                assert len(results["errors"]) == 0
                                # 断言：缓存保存函数应被调用 / Assert: cache save function should be called
                                mock_save.assert_called()

    def test_validate_and_get_optimal_settings(self):
        """
        测试用例：验证并获取最优设置
        Test Case: Verify and Get Optimal Settings

        目的：确保根据系统资源自动调整最优参数
        Purpose: Ensure optimal parameters are auto-adjusted based on system resources

        测试场景1（高资源）：
        - 可用内存：4096MB
        - CPU核心数：8

        预期结果：
        - batch_size：32
        - enable_parallel：True

        Test Scenario 1 (High Resources):
        - Available memory: 4096MB
        - CPU cores: 8

        Expected Results:
        - batch_size: 32
        - enable_parallel: True

        测试场景2（低资源）：
        - 可用内存：512MB
        - CPU核心数：1

        预期结果：
        - batch_size：16
        - memory_efficient：True
        - enable_parallel：False

        Test Scenario 2 (Low Resources):
        - Available memory: 512MB
        - CPU cores: 1

        Expected Results:
        - batch_size: 16
        - memory_efficient: True
        - enable_parallel: False

        验证点：
        1. 高资源时批处理大小为32，并行开启
        2. 低资源时批处理大小为16，内存优化开启，并行关闭

        Verification Points:
        1. High resources: batch size 32, parallel enabled
        2. Low resources: batch size 16, memory efficient enabled, parallel disabled
        """
        # 使用patch模拟validate_system_resources方法 / Use patch to mock validate_system_resources method
        with patch("cline_utils.dependency_system.utils.resource_validator.ResourceValidator.validate_system_resources") as mock_validate:
            # 场景1：模拟高资源配置 / Scenario 1: Mock high resources configuration
            mock_validate.return_value = {
                "valid": True,  # 验证通过 / Validation passed
                "resource_check": {
                    "memory": {"available_mb": 4096},  # 4GB可用内存 / 4GB available memory
                    "cpu": {"cores": 8}  # 8核心CPU / 8-core CPU
                }
            }
            # 调用获取最优设置函数 / Call get optimal settings function
            settings = validate_and_get_optimal_settings(MOCK_PROJECT_PATH)
            # 断言：批处理大小应为32 / Assert: batch size should be 32
            assert settings["batch_size"] == 32
            # 断言：并行处理应开启 / Assert: parallel processing should be enabled
            assert settings["enable_parallel"] is True

            # 场景2：模拟低资源配置 / Scenario 2: Mock low resources configuration
            mock_validate.return_value = {
                "valid": True,  # 验证通过 / Validation passed
                "resource_check": {
                    "memory": {"available_mb": 512},  # 512MB可用内存 / 512MB available memory
                    "cpu": {"cores": 1}  # 单核心CPU / Single-core CPU
                }
            }
            # 调用获取最优设置函数 / Call get optimal settings function
            settings = validate_and_get_optimal_settings(MOCK_PROJECT_PATH)
            # 断言：批处理大小应为16 / Assert: batch size should be 16
            assert settings["batch_size"] == 16
            # 断言：内存优化模式应开启 / Assert: memory efficient mode should be enabled
            assert settings["memory_efficient"] is True
            # 断言：并行处理应关闭 / Assert: parallel processing should be disabled
            assert settings["enable_parallel"] is False

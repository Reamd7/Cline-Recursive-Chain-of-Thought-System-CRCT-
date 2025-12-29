# Testing Guide

# 测试指南 | Testing Guide

> [!NOTE]
> This guide covers the comprehensive testing infrastructure in v8.0, including how to run tests, write new tests, and interpret results.
>
> 本指南涵盖了 v8.0 中全面的测试基础设施,包括如何运行测试、编写新测试以及解释结果。

## Overview

## 概述 | Overview

Version 8.0 includes a **production-ready test suite** with **53+ test cases** across **9 test files**:

v8.0 版本包含一个**生产就绪的测试套件**,在 **9 个测试文件**中包含 **53+ 个测试用例**:

- **Cache functionality** - Compression, eviction, metrics, invalidation
- **缓存功能** - 压缩、驱逐、指标、失效

- **Integration tests** - Multi-component workflows and file modification
- **集成测试** - 多组件工作流和文件修改

- **End-to-End tests** - Complete CLI workflow verification
- **端到端测试** - 完整的 CLI 工作流验证

- **Component tests** - Config management, resource validation, progress tracking
- **组件测试** - 配置管理、资源验证、进度跟踪

- **Runtime analysis** - Symbol extraction and inspection
- **运行时分析** - 符号提取和检查

- **Regression prevention** - Ensure stability across versions
- **回归预防** - 确保跨版本的稳定性

**Test Location**: `cline_utils/dependency_system/tests/`
**测试位置**: `cline_utils/dependency_system/tests/`

**Total Test Code**: ~168 KB
**总测试代码**: ~168 KB

**Coverage Target**: 70%+ for all modules
**覆盖率目标**: 所有模块 70%+

---

## Running Tests

## 运行测试 | Running Tests

### All Tests

### 所有测试 | All Tests

```bash
# Run full test suite
# 运行完整测试套件
pytest cline_utils/dependency_system/tests/

# With coverage
# 使用覆盖率
pytest --cov=cline_utils cline_utils/dependency_system/tests/

# Verbose output
# 详细输出
pytest -v cline_utils/dependency_system/tests/
```

### Specific Test Files

### 特定测试文件 | Specific Test Files

```bash
# Cache tests only
# 仅缓存测试
pytest cline_utils/dependency_system/tests/test_functional_cache.py

# Integration tests
# 集成测试
pytest cline_utils/dependency_system/tests/test_integration_cache.py

# Manual tooling tests
# 手动工具测试
pytest cline_utils/dependency_system/tests/test_manual_tooling_cache.py

# Reranker verification
# 重排序器验证
pytest cline_utils/dependency_system/tests/verify_rerank_caching.py
```

### By Test Function

### 按测试函数 | By Test Function

```bash
# Run single test
# 运行单个测试
pytest cline_utils/dependency_system/tests/test_functional_cache.py::test_cache_compression

# Run tests matching pattern
# 运行匹配模式的测试
pytest -k "compression" cline_utils/dependency_system/tests/
```

---

## Test Suite Structure

## 测试套件结构 | Test Suite Structure

### 1. Functional Cache Tests (`test_functional_cache.py`)

### 1. 功能缓存测试 (`test_functional_cache.py`) | 1. Functional Cache Tests

**Purpose**: Verify cache_manager functionality
**目的**: 验证 cache_manager 功能

**Size**: ~35KB, comprehensive coverage
**大小**: ~35KB,全面覆盖

**Coverage**:
**覆盖范围**:

- ✅ Basic cache operations (get/set)
- ✅ 基本缓存操作(获取/设置)

- ✅ TTL expiration
- ✅ TTL 过期

- ✅ LRU eviction
- ✅ LRU 驱逐

- ✅ Compression with threshold
- ✅ 阈值压缩

- ✅ Dependency invalidation
- ✅ 依赖失效

- ✅ File modification tracking
- ✅ 文件修改跟踪

- ✅ Metrics and hit rates
- ✅ 指标和命中率

**Example**:
**示例**:

```python
def test_cache_compression():
    cache = Cache("test", enable_compression=True)
    large_data = "x" * 2000  # >1KB

    cache.set("key", large_data)
    assert cache._data["key"]["compressed"] == True
    assert cache.get("key") == large_data
```

### 2. Integration Tests (`test_integration_cache.py`)

### 2. 集成测试 (`test_integration_cache.py`) | 2. Integration Tests

**Purpose**: Test multi-component workflows
**目的**: 测试多组件工作流

**Size**: ~23KB
**大小**: ~23KB

**Coverage**:
**覆盖范围**:

- ✅ Cache + file analysis
- ✅ 缓存 + 文件分析

- ✅ Cache + embedding generation
- ✅ 缓存 + 嵌入生成

- ✅ Cache persistence and loading
- ✅ 缓存持久化和加载

- ✅ Multi-cache coordination
- ✅ 多缓存协调

- ✅ Error recovery
- ✅ 错误恢复

**Example**:
**示例**:

```python
def test_end_to_end_analysis_with_caching():
    # Analyze project
    # 分析项目
    result1 = analyze_project()

    # Analyze again (should use cache)
    # 再次分析(应使用缓存)
    result2 = analyze_project()

    assert cache_manager.get_cache("analysis").metrics.hits > 0
    assert result1 == result2
```

### 3. Manual Tooling Tests (`test_manual_tooling_cache.py`)

### 3. 手动工具测试 (`test_manual_tooling_cache.py`) | 3. Manual Tooling Tests

**Purpose**: Verify command-line tools
**目的**: 验证命令行工具

**Size**: ~15KB
**大小**: ~15KB

**Coverage**:
**覆盖范围**:

- ✅ `analyze-project` with caching
- ✅ 带缓存的 `analyze-project`

- ✅ `show-dependencies` performance
- ✅ `show-dependencies` 性能

- ✅ `visualize-dependencies` caching
- ✅ `visualize-dependencies` 缓存

- ✅ Cache invalidation on file changes
- ✅ 文件更改时的缓存失效

**Example**:
**示例**:

```python
def test_analyze_project_caching():
    # First run
    # 首次运行
    start = time.time()
    run_command("analyze-project")
    first_time = time.time() - start

    # Second run (cached)
    # 第二次运行(缓存)
    start = time.time()
    run_command("analyze-project")
    second_time = time.time() - start

    assert second_time < first_time * 0.5  # 50%+ faster
                                        # 快 50% 以上
```

### 4. Reranker Verification (`verify_rerank_caching.py`)

### 4. 重排序器验证 (`verify_rerank_caching.py`) | 4. Reranker Verification

**Purpose**: Validate reranker performance
**目的**: 验证重排序器性能

**Size**: ~4KB
**大小**: ~4KB

**Coverage**:
**覆盖范围**:

- ✅ Score consistency
- ✅ 分数一致性

- ✅ Cache hit rates
- ✅ 缓存命中率

- ✅ Performance benchmarks
- ✅ 性能基准

- ✅ Memory usage
- ✅ 内存使用

**Example**:
**示例**:

```python
def test_reranker_score_caching():
    # First call
    # 首次调用
    score1 = score_pair_with_reranker(doc_a, doc_b)

    # Second call (cached)
    # 第二次调用(缓存)
    score2 = score_pair_with_reranker(doc_a, doc_b)

    assert score1 == score2
    assert reranker_cache.metrics.hits == 1
```

### 5. Configuration Manager Tests (`test_config_manager_extended.py`)

### 5. 配置管理器测试 (`test_config_manager_extended.py`) | 5. Configuration Manager Tests

**Purpose**: Verify configuration management and resource adjustments
**目的**: 验证配置管理和资源调整

**Size**: ~5.5 KB, 8 test cases
**大小**: ~5.5 KB,8 个测试用例

**Coverage**:
**覆盖范围**:

- ✅ Singleton pattern enforcement
- ✅ 单例模式强制

- ✅ Default value validation
- ✅ 默认值验证

- ✅ Deep configuration updates
- ✅ 深度配置更新

- ✅ Environment variable overrides
- ✅ 环境变量覆盖

- ✅ Resource-based adjustments (low memory/disk)
- ✅ 基于资源的调整(低内存/磁盘)

- ✅ Analysis settings retrieval
- ✅ 分析设置检索

- ✅ Optimization recommendations
- ✅ 优化建议

**Example**:
**示例**:

```python
def test_environment_overrides():
    with patch.dict(os.environ, {
        "ANALYZER_BATCH_SIZE": "64",
        "ANALYZER_LOG_LEVEL": "DEBUG"
    }):
        manager = ConfigManager()
        assert manager.get_performance_setting("default_batch_size") == 64
        assert manager.get_output_setting("log_level") == "DEBUG"
```

### 6. Resource Validator Tests (`test_resource_validator.py`)

### 6. 资源验证器测试 (`test_resource_validator.py`) | 6. Resource Validator Tests

**Purpose**: Test system resource validation and caching
**目的**: 测试系统资源验证和缓存

**Size**: ~10 KB, 8 test cases
**大小**: ~10 KB,8 个测试用例

**Coverage**:
**覆盖范围**:

- ✅ Cache path generation
- ✅ 缓存路径生成

- ✅ Validation cache save/load
- ✅ 验证缓存保存/加载

- ✅ Cache validity checks (version, path, expiration)
- ✅ 缓存有效性检查(版本、路径、过期)

- ✅ Memory validation (sufficient/critical/fallback)
- ✅ 内存验证(充足/严重/回退)

- ✅ Disk space validation
- ✅ 磁盘空间验证

- ✅ Full system resource validation
- ✅ 完整系统资源验证

- ✅ Optimal settings generation
- ✅ 最佳设置生成

**Example**:
**示例**:

```python
def test_resource_adjustments_low_memory():
    mock_validator = MagicMock()
    mock_validator.validate_system_resources.return_value = {
        "resource_check": {"memory": {"available_mb": 512}}
    }

    config.apply_resource_adjustments()

    # Should have adjusted for low memory
    # 应针对低内存进行调整
    assert config.get_performance_setting("default_batch_size") <= 16
    assert config.get_performance_setting("use_streaming_analysis") is True
```

### 7. Phase Tracker Tests (`test_phase_tracker.py`)

### 7. 阶段跟踪器测试 (`test_phase_tracker.py`) | 7. Phase Tracker Tests

**Purpose**: Verify progress tracking and UX feedback
**目的**: 验证进度跟踪和 UX 反馈

**Size**: ~4.3 KB, 9 test cases
**大小**: ~4.3 KB,9 个测试用例

**Coverage**:
**覆盖范围**:

- ✅ Initialization and defaults
- ✅ 初始化和默认值

- ✅ Time formatting (seconds, minutes:seconds, hours:minutes:seconds)
- ✅ 时间格式化(秒、分:秒、时:分:秒)

- ✅ Context manager usage
- ✅ 上下文管理器使用

- ✅ Progress updates
- ✅ 进度更新

- ✅ Description changes
- ✅ 描述更改

- ✅ Total adjustments
- ✅ 总数调整

- ✅ TTY vs non-TTY output
- ✅ TTY 与非 TTY 输出

- ✅ ETA calculation
- ✅ ETA 计算

**Example**:
**示例**:

```python
def test_eta_calculation():
    tracker = PhaseTracker(100)
    tracker.start_time = time.time() - 10  # 10 seconds elapsed
                                     # 已经过 10 秒
    tracker.current = 50  # 50% done
                   # 完成 50%

    tracker._print_progress()
    # ETA should be approximately 10 seconds (50% remaining)
    # ETA 应约为 10 秒(剩余 50%)
```

### 8. Runtime Inspector Tests (`test_runtime_inspector.py`)

### 8. 运行时检查器测试 (`test_runtime_inspector.py`) | 8. Runtime Inspector Tests

**Purpose**: Test runtime symbol extraction from Python modules
**目的**: 测试从 Python 模块运行时提取符号

**Size**: ~4.4 KB, 8 test cases
**大小**: ~4.4 KB,8 个测试用例

**Coverage**:
**覆盖范围**:

- ✅ Type annotation extraction
- ✅ 类型注解提取

- ✅ Source context retrieval (within code roots)
- ✅ 源上下文检索(在代码根目录内)

- ✅ Module exports identification
- ✅ 模块导出识别

- ✅ Inheritance hierarchy detection
- ✅ 继承层次检测

- ✅ Closure dependency analysis
- ✅ 闭包依赖分析

- ✅ Scope references (globals/nonlocals)
- ✅ 作用域引用(全局/非局部)

- ✅ Attribute access detection
- ✅ 属性访问检测

**Example**:
**示例**:

```python
def test_get_type_annotations():
    def sample(a: int, b: str) -> bool:
        return True

    annotations = get_type_annotations(sample)
    assert annotations['parameters']['a'] == "<class 'int'>"
    assert annotations['return_type'] == "<class 'bool'>"
```

### 9. End-to-End Workflow Tests (`test_e2e_workflow.py`)

### 9. 端到端工作流测试 (`test_e2e_workflow.py`) | 9. End-to-End Workflow Tests

**Purpose**: Simulate complete CLI workflows
**目的**: 模拟完整的 CLI 工作流

**Size**: ~6 KB, 5 test cases
**大小**: ~6 KB,5 个测试用例

**Coverage**:
**覆盖范围**:

- ✅ Fresh project analysis
- ✅ 新项目分析

- ✅ Cached re-analysis (idempotency)
- ✅ 缓存重新分析(幂等性)

- ✅ `--force-analysis` flag
- ✅ `--force-analysis` 标志

- ✅ `--force-embeddings` flag
- ✅ `--force-embeddings` 标志

- ✅ `--force-validate` flag
- ✅ `--force-validate` 标志

**Example**:
**示例**:

```python
def test_e2e_analyze_project_cached():
    # First run
    # 首次运行
    exit_code1 = command_handler_analyze_project(args)
    assert exit_code1 == 0

    # Second run (should use cache)
    # 第二次运行(应使用缓存)
    exit_code2 = command_handler_analyze_project(args)
    assert exit_code2 == 0

    # Verify output files still exist
    # 验证输出文件仍然存在
    assert (cline_docs / "embeddings" / "metadata.json").exists()
```

---

## Writing New Tests

## 编写新测试 | Writing New Tests

### Test Template

### 测试模板 | Test Template

```python
import pytest
from cline_utils.dependency_system.utils.cache_manager import Cache

class TestNewFeature:
    def setup_method(self):
        """Setup before each test."""
        """每个测试前的设置。"""
        self.cache = Cache("test_cache", ttl=300)

    def teardown_method(self):
        """Cleanup after each test."""
        """每个测试后的清理。"""
        self.cache.clear()

    def test_basic_functionality(self):
        """Test description."""
        """测试描述。"""
        # Arrange
        # 准备
        key = "test_key"
        value = "test_value"

        # Act
        # 执行
        self.cache.set(key, value)
        result = self.cache.get(key)

        # Assert
        # 断言
        assert result == value

    def test_edge_case(self):
        """Test edge case description."""
        """测试边缘情况描述。"""
        # Test edge case...
        # 测试边缘情况...
        pass
```

### Best Practices

### 最佳实践 | Best Practices

1. **Use Descriptive Names**
   **使用描述性名称**

   ```python
   # ✅ Good
   # ✅ 良好
   def test_cache_evicts_lru_when_full():
       ...

   # ❌ Bad
   # ❌ 不良
   def test_cache_1():
       ...
   ```

2. **Test One Thing Per Test**
   **每个测试只测试一件事**

   ```python
   # ✅ Good
   # ✅ 良好
   def test_compression_enabled():
       ...

   def test_compression_disabled():
       ...

   # ❌ Bad
   # ❌ 不良
   def test_compression_and_eviction_and_ttl():
       ...
   ```

3. **Use Fixtures for Common Setup**
   **使用夹具进行通用设置**

   ```python
   @pytest.fixture
   def cache():
       c = Cache("test", max_size=100)
       yield c
       c.clear()

   def test_something(cache):
       cache.set("key", "value")
       ...
   ```

4. **Test Edge Cases**
   **测试边缘情况**

   ```python
   def test_cache_with_empty_key():
       with pytest.raises(ValueError):
           cache.set("", "value")
   ```

---

## Coverage Analysis

## 覆盖率分析 | Coverage Analysis

### Generate Coverage Report

### 生成覆盖率报告 | Generate Coverage Report

```bash
# HTML report
# HTML 报告
pytest --cov=cline_utils --cov-report=html cline_utils/dependency_system/tests/
open htmlcov/index.html

# Terminal report
# 终端报告
pytest --cov=cline_utils --cov-report=term-missing cline_utils/dependency_system/tests/

# XML for CI/CD
# CI/CD 的 XML
pytest --cov=cline_utils --cov-report=xml cline_utils/dependency_system/tests/
```

### Current Coverage (v8.0)

### 当前覆盖率 (v8.0) | Current Coverage (v8.0)

| Module | Coverage | Status |
|--------|----------|--------|
| **模块** | **覆盖率** | **状态** |
| `cache_manager.py` | 92% | ✅ Excellent / 优秀 |
| `config_manager.py` | 85% | ✅ Excellent / 优秀 |
| `resource_validator.py` | 88% | ✅ Excellent / 优秀 |
| `phase_tracker.py` | 95% | ✅ Excellent / 优秀 |
| `embedding_manager.py` | 65% | ⚠️ Needs improvement / 需要改进 |
| `dependency_analyzer.py` | 71% | ✅ Good / 良好 |
| `dependency_suggester.py` | 58% | ⚠️ Needs improvement / 需要改进 |
| `runtime_inspector.py` | 82% | ✅ Excellent / 优秀 |

### Test Suite Statistics

### 测试套件统计 | Test Suite Statistics

**Total Test Files**: 9 active test files
**总测试文件**: 9 个活动测试文件

**Total Test Cases**: 53+
**总测试用例**: 53+

**Total Test Code**: ~168 KB
**总测试代码**: ~168 KB

**Test Distribution**:
**测试分布**:

- Functional: 20 tests (caching, low-level operations)
- 功能性: 20 个测试(缓存、低级操作)

- Integration: 4 tests (workflow integration)
- 集成: 4 个测试(工作流集成)

- Manual/Tooling: 3 tests (cache management)
- 手动/工具: 3 个测试(缓存管理)

- End-to-End: 5 tests (CLI workflows)
- 端到端: 5 个测试(CLI 工作流)

- Component-Specific: 21+ tests (config, resources, phase tracker, runtime)
- 组件特定: 21+ 个测试(配置、资源、阶段跟踪器、运行时)

---

## Continuous Integration

## 持续集成 | Continuous Integration

### GitHub Actions Example

### GitHub Actions 示例 | GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: pytest --cov=cline_utils cline_utils/dependency_system/tests/

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Troubleshooting

## 故障排除 | Troubleshooting

### Issue: Tests fail with import errors

### 问题: 测试失败并显示导入错误 | Issue: Tests fail with import errors

**Cause**: Missing dependencies
**原因**: 缺少依赖

**Solution**:
**解决方案**:

```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Issue: Cache tests fail intermittently

### 问题: 缓存测试间歇性失败 | Issue: Cache tests fail intermittently

**Cause**: Timing issues with TTL
**原因**: TTL 计时问题

**Solution**: Increase TTL margin in tests:
**解决方案**: 在测试中增加 TTL 边距:

```python
# Instead of
# 代替
assert cache.is_expired() == True  # Might fail on slow systems
                               # 可能在慢系统上失败

# Use
# 使用
time.sleep(ttl + 0.5)  # Add safety margin
                  # 添加安全边距
assert cache.is_expired() == True
```

### Issue: Integration tests timeout

### 问题: 集成测试超时 | Issue: Integration tests timeout

**Cause**: Large project analysis
**原因**: 大型项目分析

**Solution**: Use smaller test fixtures:
**解决方案**: 使用较小的测试夹具:

```python
@pytest.fixture
def small_project():
    """Create minimal test project."""
    """创建最小的测试项目。"""
    return create_test_project(num_files=10)
```

---

## Performance Benchmarks

## 性能基准 | Performance Benchmarks

### Benchmark Template

### 基准模板 | Benchmark Template

```python
import time
import statistics

def benchmark_cache_operations(iterations=1000):
    cache = Cache("bench", max_size=10000)
    times = []

    for i in range(iterations):
        start = time.perf_counter()
        cache.set(f"key_{i}", f"value_{i}")
        cache.get(f"key_{i}")
        times.append(time.perf_counter() - start)

    print(f"Avg: {statistics.mean(times)*1000:.2f}ms")
    print(f"P95: {statistics.quantiles(times, n=20)[18]*1000:.2f}ms")
```

### Expected Performance

### 预期性能 | Expected Performance

| Operation | Time | Memory |
|-----------|------|--------|
| **操作** | **时间** | **内存** |
| cache.set() | <0.1ms | ~500 bytes/item |
| cache.get() (hit) | <0.05ms | 0 |
| cache.get() (miss) | <0.05ms | 0 |
| Compression | ~1ms | -30% size |
| Eviction | ~0.5ms | Frees memory |

---

## Testing Checklist

## 测试检查清单 | Testing Checklist

Before each release:

每次发布前:

- [ ] All unit tests pass
- [ ] 所有单元测试通过

- [ ] Integration tests pass
- [ ] 集成测试通过

- [ ] Coverage >70% for new code
- [ ] 新代码覆盖率 >70%

- [ ] Performance benchmarks within expected ranges
- [ ] 性能基准在预期范围内

- [ ] Manual verification tests completed
- [ ] 手动验证测试完成

- [ ] No regressions from previous version
- [ ] 无来自以前版本的回归

- [ ] Documentation tests (if applicable)
- [ ] 文档测试(如适用)

---

## Future Testing Enhancements

## 未来测试增强 | Future Testing Enhancements

Planned improvements:

计划改进:

1. **Property-based testing** - Use Hypothesis for edge case discovery
   **基于属性的测试** - 使用 Hypothesis 发现边缘情况

2. **Load testing** - Simulate large-scale projects
   **负载测试** - 模拟大型项目

3. **Mutation testing** - Verify test quality
   **变异测试** - 验证测试质量

4. **Visual regression** - Test diagram generation
   **视觉回归** - 测试图表生成

5. **E2E tests** - Full workflow automation
   **端到端测试** - 完整的工作流自动化

---

## References

## 参考 | References

- [Test Suite Directory](cline_utils/dependency_system/tests/)
- [测试套件目录](cline_utils/dependency_system/tests/)

- [pytest Documentation](https://docs.pytest.org/)
- [pytest 文档](https://docs.pytest.org/)

- [Coverage.py Guide](https://coverage.readthedocs.io/)
- [Coverage.py 指南](https://coverage.readthedocs.io/)

---

**Testing is critical for maintaining quality as CRCT evolves.** The v8.0 test suite provides a solid foundation for regression detection and quality assurance.
**测试对于 CRCT 发展过程中的质量维护至关重要。**v8.0 测试套件为回归检测和质量保证提供了坚实的基础。

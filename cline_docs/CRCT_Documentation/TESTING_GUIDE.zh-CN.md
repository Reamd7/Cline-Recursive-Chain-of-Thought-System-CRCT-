# 测试指南

> [!NOTE]
> 本指南涵盖v8.0中的全面测试基础设施，包括如何运行测试、编写新测试以及解释结果。

## 概述

版本8.0包括**生产就绪的测试套件**，跨**9个测试文件**包含**53+个测试用例**：
- **缓存功能** - 压缩、驱逐、指标、失效
- **集成测试** - 多组件工作流和文件修改
- **端到端测试** - 完整的CLI工作流验证
- **组件测试** - 配置管理、资源验证、进度跟踪
- **运行时分析** - 符号提取和检查
- **回归预防** - 确保跨版本的稳定性

**测试位置**：`cline_utils/dependency_system/tests/`
**总测试代码**：约168 KB
**覆盖目标**：所有模块70%+

---

## 运行测试

### 所有测试

```bash
# 运行完整测试套件
pytest cline_utils/dependency_system/tests/

# 带覆盖率
pytest --cov=cline_utils cline_utils/dependency_system/tests/

# 详细输出
pytest -v cline_utils/dependency_system/tests/
```

### 特定测试文件

```bash
# 仅缓存测试
pytest cline_utils/dependency_system/tests/test_functional_cache.py

# 集成测试
pytest cline_utils/dependency_system/tests/test_integration_cache.py

# 手动工具测试
pytest cline_utils/dependency_system/tests/test_manual_tooling_cache.py

# 重排序器验证
pytest cline_utils/dependency_system/tests/verify_rerank_caching.py
```

### 按测试函数

```bash
# 运行单个测试
pytest cline_utils/dependency_system/tests/test_functional_cache.py::test_cache_compression

# 运行匹配模式的测试
pytest -k "compression" cline_utils/dependency_system/tests/
```

---

## 测试套件结构

### 1. 功能缓存测试（`test_functional_cache.py`）

**目的**：验证cache_manager功能
**大小**：约35KB，全面覆盖

**覆盖范围**：
- ✅ 基本缓存操作（get/set）
- ✅ TTL过期
- ✅ LRU驱逐
- ✅ 带阈值的压缩
- ✅ 依赖失效
- ✅ 文件修改跟踪
- ✅ 指标和命中率

**示例**：
```python
def test_cache_compression():
    cache = Cache("test", enable_compression=True)
    large_data = "x" * 2000  # >1KB

    cache.set("key", large_data)
    assert cache._data["key"]["compressed"] == True
    assert cache.get("key") == large_data
```

### 2. 集成测试（`test_integration_cache.py`）

**目的**：测试多组件工作流
**大小**：约23KB

**覆盖范围**：
- ✅ 缓存 + 文件分析
- ✅ 缓存 + 嵌入生成
- ✅ 缓存持久化和加载
- ✅ 多缓存协调
- ✅ 错误恢复

**示例**：
```python
def test_end_to_end_analysis_with_caching():
    # 分析项目
    result1 = analyze_project()

    # 再次分析（应使用缓存）
    result2 = analyze_project()

    assert cache_manager.get_cache("analysis").metrics.hits > 0
    assert result1 == result2
```

### 3. 手动工具测试（`test_manual_tooling_cache.py`）

**目的**：验证命令行工具
**大小**：约15KB

**覆盖范围**：
- ✅ 带缓存的`analyze-project`
- ✅ `show-dependencies`性能
- ✅ `visualize-dependencies`缓存
- ✅ 文件更改时的缓存失效

**示例**：
```python
def test_analyze_project_caching():
    # 首次运行
    start = time.time()
    run_command("analyze-project")
    first_time = time.time() - start

    # 第二次运行（缓存）
    start = time.time()
    run_command("analyze-project")
    second_time = time.time() - start

    assert second_time < first_time * 0.5  # 快50%+
```

### 4. 重排序器验证（`verify_rerank_caching.py`）

**目的**：验证重排序器性能
**大小**：约4KB

**覆盖范围**：
- ✅ 分数一致性
- ✅ 缓存命中率
- ✅ 性能基准
- ✅ 内存使用

**示例**：
```python
def test_reranker_score_caching():
    # 首次调用
    score1 = score_pair_with_reranker(doc_a, doc_b)

    # 第二次调用（缓存）
    score2 = score_pair_with_reranker(doc_a, doc_b)

    assert score1 == score2
    assert reranker_cache.metrics.hits == 1
```

### 5. 配置管理器测试（`test_config_manager_extended.py`）

**目的**：验证配置管理和资源调整
**大小**：约5.5 KB，8个测试用例

**覆盖范围**：
- ✅ 单例模式强制执行
- ✅ 默认值验证
- ✅ 深度配置更新
- ✅ 环境变量覆盖
- ✅ 基于资源的调整（低内存/磁盘）
- ✅ 分析设置检索
- ✅ 优化建议

**示例**：
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

### 6. 资源验证器测试（`test_resource_validator.py`）

**目的**：测试系统资源验证和缓存
**大小**：约10 KB，8个测试用例

**覆盖范围**：
- ✅ 缓存路径生成
- ✅ 验证缓存保存/加载
- ✅ 缓存有效性检查（版本、路径、过期）
- ✅ 内存验证（充足/临界/回退）
- ✅ 磁盘空间验证
- ✅ 完整系统资源验证
- ✅ 最优设置生成

**示例**：
```python
def test_resource_adjustments_low_memory():
    mock_validator = MagicMock()
    mock_validator.validate_system_resources.return_value = {
        "resource_check": {"memory": {"available_mb": 512}}
    }

    config.apply_resource_adjustments()

    # 应该已针对低内存进行调整
    assert config.get_performance_setting("default_batch_size") <= 16
    assert config.get_performance_setting("use_streaming_analysis") is True
```

### 7. 阶段跟踪器测试（`test_phase_tracker.py`）

**目的**：验证进度跟踪和用户体验反馈
**大小**：约4.3 KB，9个测试用例

**覆盖范围**：
- ✅ 初始化和默认值
- ✅ 时间格式化（秒、分钟:秒、小时:分钟:秒）
- ✅ 上下文管理器使用
- ✅ 进度更新
- ✅ 描述更改
- ✅ 总计调整
- ✅ TTY vs 非TTY输出
- ✅ 预计完成时间计算

**示例**：
```python
def test_eta_calculation():
    tracker = PhaseTracker(100)
    tracker.start_time = time.time() - 10  # 已过10秒
    tracker.current = 50  # 完成50%

    tracker._print_progress()
    # 预计完成时间应该大约是10秒（剩余50%）
```

### 8. 运行时检查器测试（`test_runtime_inspector.py`）

**目的**：测试从Python模块提取运行时符号
**大小**：约4.4 KB，8个测试用例

**覆盖范围**：
- ✅ 类型注解提取
- ✅ 源上下文检索（在代码根目录内）
- ✅ 模块导出识别
- ✅ 继承层次检测
- ✅ 闭包依赖分析
- ✅ 作用域引用（全局/非本地）
- ✅ 属性访问检测

**示例**：
```python
def test_get_type_annotations():
    def sample(a: int, b: str) -> bool:
        return True

    annotations = get_type_annotations(sample)
    assert annotations['parameters']['a'] == "<class 'int'>"
    assert annotations['return_type'] == "<class 'bool'>"
```

### 9. 端到端工作流测试（`test_e2e_workflow.py`）

**目的**：模拟完整的CLI工作流
**大小**：约6 KB，5个测试用例

**覆盖范围**：
- ✅ 新项目分析
- ✅ 缓存重新分析（幂等性）
- ✅ `--force-analysis`标志
- ✅ `--force-embeddings`标志
- ✅ `--force-validate`标志

**示例**：
```python
def test_e2e_analyze_project_cached():
    # 首次运行
    exit_code1 = command_handler_analyze_project(args)
    assert exit_code1 == 0

    # 第二次运行（应使用缓存）
    exit_code2 = command_handler_analyze_project(args)
    assert exit_code2 == 0

    # 验证输出文件仍然存在
    assert (cline_docs / "embeddings" / "metadata.json").exists()
```

---

## 编写新测试

### 测试模板

```python
import pytest
from cline_utils.dependency_system.utils.cache_manager import Cache

class TestNewFeature:
    def setup_method(self):
        """每个测试前的设置。"""
        self.cache = Cache("test_cache", ttl=300)

    def teardown_method(self):
        """每个测试后的清理。"""
        self.cache.clear()

    def test_basic_functionality(self):
        """测试描述。"""
        # 安排
        key = "test_key"
        value = "test_value"

        # 执行
        self.cache.set(key, value)
        result = self.cache.get(key)

        # 断言
        assert result == value

    def test_edge_case(self):
        """测试边缘情况描述。"""
        # 测试边缘情况...
        pass
```

### 最佳实践

1. **使用描述性名称**
   ```python
   # ✅ 好
   def test_cache_evicts_lru_when_full():
       ...

   # ❌ 差
   def test_cache_1():
       ...
   ```

2. **每个测试测试一件事**
   ```python
   # ✅ 好
   def test_compression_enabled():
       ...

   def test_compression_disabled():
       ...

   # ❌ 差
   def test_compression_and_eviction_and_ttl():
       ...
   ```

3. **使用Fixture进行通用设置**
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

4. **测试边缘情况**
   ```python
   def test_cache_with_empty_key():
       with pytest.raises(ValueError):
           cache.set("", "value")
   ```

---

## 覆盖率分析

### 生成覆盖率报告

```bash
# HTML报告
pytest --cov=cline_utils --cov-report=html cline_utils/dependency_system/tests/
open htmlcov/index.html

# 终端报告
pytest --cov=cline_utils --cov-report=term-missing cline_utils/dependency_system/tests/

# CI/CD的XML
pytest --cov=cline_utils --cov-report=xml cline_utils/dependency_system/tests/
```

### 当前覆盖率（v8.0）

| 模块 | 覆盖率 | 状态 |
|--------|----------|--------|
| `cache_manager.py` | 92% | ✅ 优秀 |
| `config_manager.py` | 85% | ✅ 优秀 |
| `resource_validator.py` | 88% | ✅ 优秀 |
| `phase_tracker.py` | 95% | ✅ 优秀 |
| `embedding_manager.py` | 65% | ⚠️ 需要改进 |
| `dependency_analyzer.py` | 71% | ✅ 良好 |
| `dependency_suggester.py` | 58% | ⚠️ 需要改进 |
| `runtime_inspector.py` | 82% | ✅ 优秀 |

### 测试套件统计

**总测试文件**：9个活动测试文件
**总测试用例**：53+
**总测试代码**：约168 KB

**测试分布**：
- 功能性：20个测试（缓存、低级操作）
- 集成：4个测试（工作流集成）
- 手动/工具：3个测试（缓存管理）
- 端到端：5个测试（CLI工作流）
- 组件特定：21+个测试（配置、资源、阶段跟踪器、运行时）

---

## 持续集成

### GitHub Actions示例

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

## 故障排除

### 问题：测试失败并出现导入错误

**原因**：缺少依赖

**解决方案**：
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### 问题：缓存测试间歇性失败

**原因**：TTL的时间问题

**解决方案**：在测试中增加TTL边距：
```python
# 而不是
assert cache.is_expired() == True  # 在慢系统上可能失败

# 使用
time.sleep(ttl + 0.5)  # 添加安全边距
assert cache.is_expired() == True
```

### 问题：集成测试超时

**原因**：大型项目分析

**解决方案**：使用更小的测试fixture：
```python
@pytest.fixture
def small_project():
    """创建最小测试项目。"""
    return create_test_project(num_files=10)
```

---

## 性能基准

### 基准模板

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

    print(f"平均: {statistics.mean(times)*1000:.2f}ms")
    print(f"P95: {statistics.quantiles(times, n=20)[18]*1000:.2f}ms")
```

### 预期性能

| 操作 | 时间 | 内存 |
|-----------|------|--------|
| cache.set() | <0.1ms | 每项约500字节 |
| cache.get()（命中） | <0.05ms | 0 |
| cache.get()（未命中） | <0.05ms | 0 |
| 压缩 | 约1ms | -30%大小 |
| 驱逐 | 约0.5ms | 释放内存 |

---

## 测试清单

每次发布前：

- [ ] 所有单元测试通过
- [ ] 集成测试通过
- [ ] 新代码覆盖率>70%
- [ ] 性能基准在预期范围内
- [ ] 手动验证测试完成
- [ ] 无先前版本的回归
- [ ] 文档测试（如适用）

---

## 未来测试增强

计划的改进：

1. **基于属性的测试** - 使用Hypothesis进行边缘情况发现
2. **负载测试** - 模拟大规模项目
3. **变异测试** - 验证测试质量
4. **视觉回归** - 测试图表生成
5. **端到端测试** - 完整工作流自动化

---

## 参考资料

- [测试套件目录](cline_utils/dependency_system/tests/)
- [pytest文档](https://docs.pytest.org/)
- [Coverage.py指南](https://coverage.readthedocs.io/)

---

**测试对于随着CRCT演进保持质量至关重要。** v8.0测试套件为回归检测和质量保证提供了坚实的基础。

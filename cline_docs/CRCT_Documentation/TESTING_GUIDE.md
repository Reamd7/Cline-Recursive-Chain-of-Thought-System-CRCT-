# Testing Guide

> [!NOTE]
> This guide covers the comprehensive testing infrastructure in v8.0, including how to run tests, write new tests, and interpret results.

## Overview

Version 8.0 includes a **production-ready test suite** with **53+ test cases** across **9 test files**:
- **Cache functionality** - Compression, eviction, metrics, invalidation
- **Integration tests** - Multi-component workflows and file modification
- **End-to-End tests** - Complete CLI workflow verification
- **Component tests** - Config management, resource validation, progress tracking
- **Runtime analysis** - Symbol extraction and inspection
- **Regression prevention** - Ensure stability across versions

**Test Location**: `cline_utils/dependency_system/tests/`  
**Total Test Code**: ~168 KB  
**Coverage Target**: 70%+ for all modules

---

## Running Tests

### All Tests

```bash
# Run full test suite
pytest cline_utils/dependency_system/tests/

# With coverage
pytest --cov=cline_utils cline_utils/dependency_system/tests/

# Verbose output
pytest -v cline_utils/dependency_system/tests/
```

### Specific Test Files

```bash
# Cache tests only
pytest cline_utils/dependency_system/tests/test_functional_cache.py

# Integration tests
pytest cline_utils/dependency_system/tests/test_integration_cache.py

# Manual tooling tests
pytest cline_utils/dependency_system/tests/test_manual_tooling_cache.py

# Reranker verification
pytest cline_utils/dependency_system/tests/verify_rerank_caching.py
```

### By Test Function

```bash
# Run single test
pytest cline_utils/dependency_system/tests/test_functional_cache.py::test_cache_compression

# Run tests matching pattern
pytest -k "compression" cline_utils/dependency_system/tests/
```

---

## Test Suite Structure

### 1. Functional Cache Tests (`test_functional_cache.py`)

**Purpose**: Verify cache_manager functionality  
**Size**: ~35KB, comprehensive coverage

**Coverage**:
- ✅ Basic cache operations (get/set)
- ✅ TTL expiration
- ✅ LRU eviction
- ✅ Compression with threshold
- ✅ Dependency invalidation
- ✅ File modification tracking
- ✅ Metrics and hit rates

**Example**:
```python
def test_cache_compression():
    cache = Cache("test", enable_compression=True)
    large_data = "x" * 2000  # >1KB
    
    cache.set("key", large_data)
    assert cache._data["key"]["compressed"] == True
    assert cache.get("key") == large_data
```

### 2. Integration Tests (`test_integration_cache.py`)

**Purpose**: Test multi-component workflows  
**Size**: ~23KB

**Coverage**:
- ✅ Cache + file analysis
- ✅ Cache + embedding generation
- ✅ Cache persistence and loading
- ✅ Multi-cache coordination
- ✅ Error recovery

**Example**:
```python
def test_end_to_end_analysis_with_caching():
    # Analyze project
    result1 = analyze_project()
    
    # Analyze again (should use cache)
    result2 = analyze_project()
    
    assert cache_manager.get_cache("analysis").metrics.hits > 0
    assert result1 == result2
```

### 3. Manual Tooling Tests (`test_manual_tooling_cache.py`)

**Purpose**: Verify command-line tools  
**Size**: ~15KB

**Coverage**:
- ✅ `analyze-project` with caching
- ✅ `show-dependencies` performance
- ✅ `visualize-dependencies` caching
- ✅ Cache invalidation on file changes

**Example**:
```python
def test_analyze_project_caching():
    # First run
    start = time.time()
    run_command("analyze-project")
    first_time = time.time() - start
    
    # Second run (cached)
    start = time.time()
    run_command("analyze-project")
    second_time = time.time() - start
    
    assert second_time < first_time * 0.5  # 50%+ faster
```

### 4. Reranker Verification (`verify_rerank_caching.py`)

**Purpose**: Validate reranker performance  
**Size**: ~4KB

**Coverage**:
- ✅ Score consistency
- ✅ Cache hit rates
- ✅ Performance benchmarks
- ✅ Memory usage

**Example**:
```python
def test_reranker_score_caching():
    # First call
    score1 = score_pair_with_reranker(doc_a, doc_b)
    
    # Second call (cached)
    score2 = score_pair_with_reranker(doc_a, doc_b)
    
    assert score1 == score2
    assert reranker_cache.metrics.hits == 1
```

### 5. Configuration Manager Tests (`test_config_manager_extended.py`)

**Purpose**: Verify configuration management and resource adjustments  
**Size**: ~5.5 KB, 8 test cases

**Coverage**:
- ✅ Singleton pattern enforcement
- ✅ Default value validation
- ✅ Deep configuration updates
- ✅ Environment variable overrides
- ✅ Resource-based adjustments (low memory/disk)
- ✅ Analysis settings retrieval
- ✅ Optimization recommendations

**Example**:
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

**Purpose**: Test system resource validation and caching  
**Size**: ~10 KB, 8 test cases

**Coverage**:
- ✅ Cache path generation
- ✅ Validation cache save/load
- ✅ Cache validity checks (version, path, expiration)
- ✅ Memory validation (sufficient/critical/fallback)
- ✅ Disk space validation
- ✅ Full system resource validation
- ✅ Optimal settings generation

**Example**:
```python
def test_resource_adjustments_low_memory():
    mock_validator = MagicMock()
    mock_validator.validate_system_resources.return_value = {
        "resource_check": {"memory": {"available_mb": 512}}
    }
    
    config.apply_resource_adjustments()
    
    # Should have adjusted for low memory
    assert config.get_performance_setting("default_batch_size") <= 16
    assert config.get_performance_setting("use_streaming_analysis") is True
```

### 7. Phase Tracker Tests (`test_phase_tracker.py`)

**Purpose**: Verify progress tracking and UX feedback  
**Size**: ~4.3 KB, 9 test cases

**Coverage**:
- ✅ Initialization and defaults
- ✅ Time formatting (seconds, minutes:seconds, hours:minutes:seconds)
- ✅ Context manager usage
- ✅ Progress updates
- ✅ Description changes
-  ✅ Total adjustments
- ✅ TTY vs non-TTY output
- ✅ ETA calculation

**Example**:
```python
def test_eta_calculation():
    tracker = PhaseTracker(100)
    tracker.start_time = time.time() - 10  # 10 seconds elapsed
    tracker.current = 50  # 50% done
    
    tracker._print_progress()
    # ETA should be approximately 10 seconds (50% remaining)
```

### 8. Runtime Inspector Tests (`test_runtime_inspector.py`)

**Purpose**: Test runtime symbol extraction from Python modules  
**Size**: ~4.4 KB, 8 test cases

**Coverage**:
- ✅ Type annotation extraction
- ✅ Source context retrieval (within code roots)
- ✅ Module exports identification
- ✅ Inheritance hierarchy detection
- ✅ Closure dependency analysis
- ✅ Scope references (globals/nonlocals)
- ✅ Attribute access detection

**Example**:
```python
def test_get_type_annotations():
    def sample(a: int, b: str) -> bool:
        return True
    
    annotations = get_type_annotations(sample)
    assert annotations['parameters']['a'] == "<class 'int'>"
    assert annotations['return_type'] == "<class 'bool'>"
```

### 9. End-to-End Workflow Tests (`test_e2e_workflow.py`)

**Purpose**: Simulate complete CLI workflows  
**Size**: ~6 KB, 5 test cases

**Coverage**:
- ✅ Fresh project analysis
- ✅ Cached re-analysis (idempotency)
- ✅ `--force-analysis` flag
- ✅ `--force-embeddings` flag
- ✅ `--force-validate` flag

**Example**:
```python
def test_e2e_analyze_project_cached():
    # First run
    exit_code1 = command_handler_analyze_project(args)
    assert exit_code1 == 0
    
    # Second run (should use cache)
    exit_code2 = command_handler_analyze_project(args)
    assert exit_code2 == 0
    
    # Verify output files still exist
    assert (cline_docs / "embeddings" / "metadata.json").exists()
```

---

## Writing New Tests

### Test Template

```python
import pytest
from cline_utils.dependency_system.utils.cache_manager import Cache

class TestNewFeature:
    def setup_method(self):
        """Setup before each test."""
        self.cache = Cache("test_cache", ttl=300)
    
    def teardown_method(self):
        """Cleanup after each test."""
        self.cache.clear()
    
    def test_basic_functionality(self):
        """Test description."""
        # Arrange
        key = "test_key"
        value = "test_value"
        
        # Act
        self.cache.set(key, value)
        result = self.cache.get(key)
        
        # Assert
        assert result == value
    
    def test_edge_case(self):
        """Test edge case description."""
        # Test edge case...
        pass
```

### Best Practices

1. **Use Descriptive Names**
   ```python
   # ✅ Good
   def test_cache_evicts_lru_when_full():
       ...
   
   # ❌ Bad
   def test_cache_1():
       ...
   ```

2. **Test One Thing Per Test**
   ```python
   # ✅ Good
   def test_compression_enabled():
       ...
   
   def test_compression_disabled():
       ...
   
   # ❌ Bad
   def test_compression_and_eviction_and_ttl():
       ...
   ```

3. **Use Fixtures for Common Setup**
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
   ```python
   def test_cache_with_empty_key():
       with pytest.raises(ValueError):
           cache.set("", "value")
   ```

---

## Coverage Analysis

### Generate Coverage Report

```bash
# HTML report
pytest --cov=cline_utils --cov-report=html cline_utils/dependency_system/tests/
open htmlcov/index.html

# Terminal report
pytest --cov=cline_utils --cov-report=term-missing cline_utils/dependency_system/tests/

# XML for CI/CD
pytest --cov=cline_utils --cov-report=xml cline_utils/dependency_system/tests/
```

### Current Coverage (v8.0)

| Module | Coverage | Status |
|--------|----------|--------|
| `cache_manager.py` | 92% | ✅ Excellent |
| `config_manager.py` | 85% | ✅ Excellent |
| `resource_validator.py` | 88% | ✅ Excellent |
| `phase_tracker.py` | 95% | ✅ Excellent |
| `embedding_manager.py` | 65% | ⚠️ Needs improvement |
| `dependency_analyzer.py` | 71% | ✅ Good |
| `dependency_suggester.py` | 58% | ⚠️ Needs improvement |
| `runtime_inspector.py` | 82% | ✅ Excellent |

### Test Suite Statistics

**Total Test Files**: 9 active test files  
**Total Test Cases**: 53+  
**Total Test Code**: ~168 KB  

**Test Distribution**:
- Functional: 20 tests (caching, low-level operations)
- Integration: 4 tests (workflow integration)
- Manual/Tooling: 3 tests (cache management)
- End-to-End: 5 tests (CLI workflows)
- Component-Specific: 21+ tests (config, resources, phase tracker, runtime)

---

## Continuous Integration

### GitHub Actions Example

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

### Issue: Tests fail with import errors

**Cause**: Missing dependencies

**Solution**:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Issue: Cache tests fail intermittently

**Cause**: Timing issues with TTL

**Solution**: Increase TTL margin in tests:
```python
# Instead of
assert cache.is_expired() == True  # Might fail on slow systems

# Use
time.sleep(ttl + 0.5)  # Add safety margin
assert cache.is_expired() == True
```

### Issue: Integration tests timeout

**Cause**: Large project analysis

**Solution**: Use smaller test fixtures:
```python
@pytest.fixture
def small_project():
    """Create minimal test project."""
    return create_test_project(num_files=10)
```

---

## Performance Benchmarks

### Benchmark Template

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

| Operation | Time | Memory |
|-----------|------|--------|
| cache.set() | <0.1ms | ~500 bytes/item |
| cache.get() (hit) | <0.05ms | 0 |
| cache.get() (miss) | <0.05ms | 0 |
| Compression | ~1ms | -30% size |
| Eviction | ~0.5ms | Frees memory |

---

## Testing Checklist

Before each release:

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Coverage >70% for new code
- [ ] Performance benchmarks within expected ranges
- [ ] Manual verification tests completed
- [ ] No regressions from previous version
- [ ] Documentation tests (if applicable)

---

## Future Testing Enhancements

Planned improvements:

1. **Property-based testing** - Use Hypothesis for edge case discovery
2. **Load testing** - Simulate large-scale projects
3. **Mutation testing** - Verify test quality
4. **Visual regression** - Test diagram generation
5. **E2E tests** - Full workflow automation

---

## References

- [Test Suite Directory](cline_utils/dependency_system/tests/)
- [pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Guide](https://coverage.readthedocs.io/)

---

**Testing is critical for maintaining quality as CRCT evolves.** The v8.0 test suite provides a solid foundation for regression detection and quality assurance.

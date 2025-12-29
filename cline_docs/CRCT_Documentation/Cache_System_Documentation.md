# Cache System Documentation (v7.5)

# 缓存系统文档 (v7.5) | Cache System Documentation

## Overview

## 概述 | Overview

The CRCT cache system is designed to boost performance by storing the results of potentially costly function calls (like file analysis or embedding lookups) and reusing them when the same inputs occur again. It's a dynamic system based on Time-To-Live (TTL) expiration and automatic cleanup.

CRCT 缓存系统旨在通过存储可能昂贵的函数调用结果(如文件分析或嵌入查找)并在相同输入再次出现时重用它们来提高性能。这是一个基于生存时间 (TTL) 过期和自动清理的动态系统。

#### Core Components:

#### 核心组件 | Core Components

1.  **`Cache` Class**: A single cache instance holding data (`key -> value`), access times, and optional dependency information. It manages TTL expiration and LRU (Least Recently Used) eviction when size limits are reached.

1.  **`Cache` 类**: 单个缓存实例,保存数据 (`key -> value`)、访问时间和可选的依赖信息。当达到大小限制时,它管理 TTL 过期和 LRU (最近最少使用) 驱逐。

2.  **`CacheManager` Class**: Oversees all active `Cache` instances. It creates caches on-demand when they are first requested (e.g., via the `@cached` decorator) and handles the cleanup of expired caches to free up memory.

2.  **`CacheManager` 类**: 监督所有活动的 `Cache` 实例。它在首次请求时按需创建缓存(例如,通过 `@cached` 装饰器),并处理过期缓存的清理以释放内存。

3.  **`@cached` Decorator`: The primary way to enable caching for a function.

3.  **`@cached` 装饰器`: 为函数启用缓存的主要方式。

#### Key Features:

#### 主要特性 | Key Features

-   **Dynamic Cache Creation**: Caches are created automatically the first time a specific `cache_name` is used with the `@cached` decorator. There's no need to predefine caches.

-   **动态缓存创建**: 当首次使用特定的 `cache_name` 与 `@cached` 装饰器时,缓存会自动创建。无需预先定义缓存。

-   **Automatic Expiration (TTL)**: Each cache instance has a default TTL. If a cache is not accessed within its TTL, it becomes eligible for removal by the `CacheManager`. Individual cached items within a cache also respect TTL settings.

-   **自动过期 (TTL)**: 每个缓存实例都有默认的 TTL。如果缓存在其 TTL 内未被访问,则有资格被 `CacheManager` 移除。缓存中的单个缓存项也遵循 TTL 设置。

-   **LRU Eviction**: When an individual cache instance reaches its maximum size limit, it removes the least recently used item to make space.

-   **LRU 驱逐**: 当单个缓存实例达到其最大大小限制时,它会移除最近最少使用的项以腾出空间。

-   **Targeted Invalidation**: Functions are provided to clear specific cache entries based on key patterns (supports regex) or automatically when dependent files are modified.

-   **定向失效**: 提供了基于键模式(支持正则表达式)清除特定缓存条目的功能,或在依赖文件被修改时自动清除。

-   **Optional Persistence**: The system includes code to save/load caches to disk, although this feature is **disabled by default** in the current version.

-   **可选持久化**: 系统包含将缓存保存/加载到磁盘的代码,尽管此功能在当前版本中**默认禁用**。

-   **Isolation**: Each cache (identified by its unique `cache_name`) operates independently. Clearing one cache does not affect others.

-   **隔离性**: 每个缓存(通过其唯一的 `cache_name` 标识)独立运行。清除一个缓存不会影响其他缓存。

For most interactions with the CRCT system via the LLM, the cache operates transparently in the background. This guide provides details for users interested in understanding the mechanism or potentially leveraging it in custom scripts.

对于大多数通过 LLM 与 CRCT 系统的交互,缓存在后台透明地运行。本指南为有兴趣了解其机制或可能希望在自定义脚本中利用它的用户提供详细信息。

---

## How to Use the Cache System

## 如何使用缓存系统 | How to Use the Cache System

The primary interface for enabling caching is the `@cached` decorator.

启用缓存的主要接口是 `@cached` 装饰器。

#### Basic Usage

#### 基本用法 | Basic Usage

To cache a function's results, decorate it with `@cached`, providing a unique `cache_name` and typically a `key_func` to generate a unique string key based on the function's arguments.

要缓存函数的结果,请使用 `@cached` 装饰它,提供唯一的 `cache_name`,通常还需要提供 `key_func` 以根据函数的参数生成唯一的字符串键。

```python
# Example within cline_utils/dependency_system/utils/cache_manager.py
from cline_utils.dependency_system.utils.cache_manager import cached

# Define a function to generate a key based on input 'x'
def create_cache_key(x):
    return f"my_function_key:{x}"

@cached(cache_name="my_function_cache", key_func=create_cache_key)
def potentially_slow_function(x):
    # Simulate an expensive computation
    print(f"Executing potentially_slow_function({x})...")
    time.sleep(1)
    return x * x

# First call: executes the function, result stored in "my_function_cache" with key "my_function_key:5"
result1 = potentially_slow_function(5)
print(f"Result 1: {result1}")

# Second call with same input: returns cached result instantly
result2 = potentially_slow_function(5)
print(f"Result 2: {result2}")

# Call with different input: executes function, new result cached
result3 = potentially_slow_function(10)
print(f"Result 3: {result3}")
```

代码说明:

```python
# cline_utils/dependency_system/utils/cache_manager.py 中的示例
from cline_utils.dependency_system.utils.cache_manager import cached

# 定义基于输入 'x' 生成键的函数
def create_cache_key(x):
    return f"my_function_key:{x}"

@cached(cache_name="my_function_cache", key_func=create_cache_key)
def potentially_slow_function(x):
    # 模拟昂贵的计算
    print(f"Executing potentially_slow_function({x})...")
    time.sleep(1)
    return x * x

# 第一次调用: 执行函数,结果存储在 "my_function_cache" 中,键为 "my_function_key:5"
result1 = potentially_slow_function(5)
print(f"Result 1: {result1}")

# 第二次调用使用相同输入: 立即返回缓存的结果
result2 = potentially_slow_function(5)
print(f"Result 2: {result2}")

# 使用不同输入调用: 执行函数,新结果被缓存
result3 = potentially_slow_function(10)
print(f"Result 3: {result3}")
```

-   `"my_function_cache"`: This name identifies the specific cache instance used for this function. A new `Cache` object is created dynamically by the `CacheManager` the first time this name is encountered.

-   `"my_function_cache"`: 此名称标识用于此函数的特定缓存实例。`CacheManager` 会在首次遇到此名称时动态创建新的 `Cache` 对象。

-   `key_func=create_cache_key`: This function takes the arguments passed to `potentially_slow_function` and generates a unique string identifier for the cache entry.

-   `key_func=create_cache_key`: 此函数接受传递给 `potentially_slow_function` 的参数,并为缓存条目生成唯一的字符串标识符。

#### Advanced Usage: TTL and Dependencies

#### 高级用法: TTL 和依赖 | Advanced Usage: TTL and Dependencies

You can customize the Time-To-Live for a specific cache or define dependencies.

您可以自定义特定缓存的生存时间或定义依赖关系。

**Custom TTL:**

**自定义 TTL:** (Custom TTL)

```python
# Set a 5-minute TTL for this specific cache instance
@cached(cache_name="short_lived_cache", key_func=lambda arg: f"slc:{arg}", ttl=300)
def function_with_short_ttl(arg):
    # ... function logic ...
    return arg
```

代码说明:

```python
# 为此特定缓存实例设置 5 分钟的 TTL
@cached(cache_name="short_lived_cache", key_func=lambda arg: f"slc:{arg}", ttl=300)
def function_with_short_ttl(arg):
    # ... 函数逻辑 ...
    return arg
```

**Dynamic Dependencies:**

**动态依赖:** (Dynamic Dependencies)

If a cached result depends on other data (e.g., a file), you can return the dependencies along with the result. The cache system implicitly creates dependencies based on file paths used in certain cached functions (like `analyze_file`).

如果缓存结果依赖于其他数据(例如文件),您可以将依赖关系与结果一起返回。缓存系统基于某些缓存函数中使用的文件路径(如 `analyze_file`)隐式创建依赖关系。

```python
@cached(cache_name="dependent_cache", key_func=lambda file_id: f"dep_cache:{file_id}")
def process_file_data(file_id):
    file_path = f"/path/to/data/{file_id}.json"
    # ... process file_path ...
    result = {"data": "processed_data"}
    # Implicit dependency on file_path might be handled by internal functions,
    # but you could return explicit dependencies if needed:
    # dependencies = [f"file:{normalize_path(file_path)}"]
    # return result, dependencies
    return result # Example without explicit dependency return
```

代码说明:

```python
@cached(cache_name="dependent_cache", key_func=lambda file_id: f"dep_cache:{file_id}")
def process_file_data(file_id):
    file_path = f"/path/to/data/{file_id}.json"
    # ... 处理 file_path ...
    result = {"data": "processed_data"}
    # 对 file_path 的隐式依赖可能由内部函数处理,
    # 但如果需要,您可以返回显式依赖:
    # dependencies = [f"file:{normalize_path(file_path)}"]
    # return result, dependencies
    return result # 无显式依赖返回的示例
```

If the underlying file changes, functions like `check_file_modified` can trigger invalidation for caches linked to that file path.

如果基础文件发生变化,`check_file_modified` 等函数可以触发与该文件路径链接的缓存失效。

#### Manual Invalidation

#### 手动失效 | Manual Invalidation

While the system often handles invalidation automatically (e.g., based on file modification), you can manually clear entries using `invalidate_dependent_entries` or clear entire caches using the CLI command.

虽然系统通常会自动处理失效(例如,基于文件修改),但您可以使用 `invalidate_dependent_entries` 手动清除条目,或使用 CLI 命令清除整个缓存。

```python
from cline_utils.dependency_system.utils.cache_manager import invalidate_dependent_entries

# Invalidate specific entry in "my_function_cache"
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:5")

# Invalidate all entries in "my_function_cache"
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:.*")
```

代码说明:

```python
from cline_utils.dependency_system.utils.cache_manager import invalidate_dependent_entries

# 使 "my_function_cache" 中的特定条目失效
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:5")

# 使 "my_function_cache" 中的所有条目失效
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:.*")
```

**Clearing All Caches:**

**清除所有缓存:** (Clearing All Caches)

The most straightforward way for a user to clear all caches is via the `dependency_processor.py` command:

用户清除所有缓存的最直接方法是通过 `dependency_processor.py` 命令:

```bash
python -m cline_utils.dependency_system.dependency_processor clear-caches
```

The LLM can execute this command if you suspect caching issues are causing problems.

如果您怀疑缓存问题导致问题,LLM 可以执行此命令。

---

## Cache Management Details

## 缓存管理详情 | Cache Management Details

-   **On-Demand Creation & Cleanup**: Caches are created by the `CacheManager` when first requested via `@cached(cache_name=...)`. The manager periodically cleans up `Cache` instances that haven't been accessed within their TTL, conserving memory.

-   **按需创建和清理**: 缓存由 `CacheManager` 在首次通过 `@cached(cache_name=...)` 请求时创建。管理器定期清理在其 TTL 内未被访问的 `Cache` 实例,以节省内存。

-   **LRU Eviction**: Individual `Cache` instances have size limits. When full, the least recently used entry is removed.

-   **LRU 驱逐**: 单个 `Cache` 实例有大小限制。当满时,最近最少使用的条目将被移除。

-   **Dependency Tracking**: The system can link cache entries to dependencies (like file paths). Modifying a file triggers `check_file_modified`, which uses `invalidate_dependent_entries` to clear relevant cached data (e.g., analysis results for that file).

-   **依赖跟踪**: 系统可以将缓存条目链接到依赖项(如文件路径)。修改文件会触发 `check_file_modified`,该函数使用 `invalidate_dependent_entries` 清除相关的缓存数据(例如该文件的分析结果)。

---

## Configuration

## 配置 | Configuration

Cache behavior can be tuned by modifying constants directly within `cline_utils/dependency_system/utils/cache_manager.py`:

可以通过直接修改 `cline_utils/dependency_system/utils/cache_manager.py` 中的常量来调整缓存行为:

-   `DEFAULT_TTL` (seconds): Default expiration time for cache instances and entries (currently 600 seconds / 10 minutes).

-   `DEFAULT_TTL` (秒): 缓存实例和条目的默认过期时间(当前为 600 秒 / 10 分钟)。

-   `DEFAULT_MAX_SIZE`: Default maximum number of items per cache instance (currently 1000).

-   `DEFAULT_MAX_SIZE`: 每个缓存实例的默认最大项数(当前为 1000)。

-   `CACHE_SIZES` (dictionary): Allows setting different `max_size` values for specific `cache_name`s (e.g., `{"embeddings_generation": 100, "key_generation": 5000}`).

-   `CACHE_SIZES` (字典): 允许为特定的 `cache_name` 设置不同的 `max_size` 值(例如, `{"embeddings_generation": 100, "key_generation": 5000}`)。

*Note: Modifying these requires directly editing the Python file.*

*注意: 修改这些需要直接编辑 Python 文件。*

---

## Persistence

## 持久化 | Persistence

The `CacheManager` can be initialized with `persist=True` to save/load cache contents to/from JSON files within the `CACHE_DIR` (a `cache` subdirectory within `cline_utils/dependency_system/utils/`).

`CacheManager` 可以使用 `persist=True` 初始化,以将缓存内容保存/加载到 `CACHE_DIR` (位于 `cline_utils/dependency_system/utils/` 中的 `cache` 子目录)中的 JSON 文件。

**This feature is currently DISABLED (`persist=False`) by default.** Enabling it would preserve caches between runs but might lead to loading stale data if not managed carefully.

**此功能当前默认禁用 (`persist=False`)。** 启用它会在运行之间保留缓存,但如果管理不当可能会导致加载过时数据。

---

## Cache Statistics

## 缓存统计 | Cache Statistics

For debugging or performance analysis, you can retrieve statistics for a specific cache:

对于调试或性能分析,您可以检索特定缓存的统计信息:

```python
from cline_utils.dependency_system.utils.cache_manager import get_cache_stats

stats = get_cache_stats("my_function_cache") # Use the actual cache_name
print(f"Cache 'my_function_cache' Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Current Size: {stats['size']}")
```

代码说明:

```python
from cline_utils.dependency_system.utils.cache_manager import get_cache_stats

stats = get_cache_stats("my_function_cache") # 使用实际的 cache_name
print(f"缓存 'my_function_cache' 统计 - 命中: {stats['hits']}, 未命中: {stats['misses']}, 当前大小: {stats['size']}")
```

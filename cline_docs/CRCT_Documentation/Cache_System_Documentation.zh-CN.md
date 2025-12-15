# 缓存系统文档 (v7.5)

## 概述

CRCT 缓存系统（Cache System）旨在通过存储潜在昂贵函数调用的结果（如文件分析或嵌入查找）并在相同输入再次出现时重用它们来提升性能。这是一个基于生存时间（Time-To-Live, TTL）过期和自动清理的动态系统。

#### 核心组件：

1.  **`Cache` 类**：单个缓存实例，持有数据（`key -> value`）、访问时间和可选的依赖信息。它管理 TTL 过期和当达到大小限制时的 LRU（Least Recently Used，最近最少使用）驱逐。
2.  **`CacheManager` 类**：监管所有活动的 `Cache` 实例。它在首次请求时按需创建缓存（例如，通过 `@cached` 装饰器），并处理过期缓存的清理以释放内存。
3.  **`@cached` 装饰器**：为函数启用缓存的主要方式。

#### 主要特性：

-   **动态缓存创建**：当首次使用特定的 `cache_name` 与 `@cached` 装饰器时，缓存会自动创建。无需预定义缓存。
-   **自动过期 (TTL)**：每个缓存实例都有一个默认 TTL。如果缓存在其 TTL 内未被访问，它将有资格被 `CacheManager` 移除。缓存内的单个缓存项也遵循 TTL 设置。
-   **LRU 驱逐**：当单个缓存实例达到其最大大小限制时，它会移除最近最少使用的项以腾出空间。
-   **定向失效**：提供了基于键模式（支持正则表达式）清除特定缓存条目的函数，或在依赖文件被修改时自动清除。
-   **可选持久化**：系统包含将缓存保存/加载到磁盘的代码，尽管此功能在当前版本中**默认禁用**。
-   **隔离**：每个缓存（由其唯一的 `cache_name` 标识）独立运行。清除一个缓存不会影响其他缓存。

对于通过 LLM 与 CRCT 系统的大多数交互，缓存在后台透明地运行。本指南为对理解机制或可能在自定义脚本中利用它感兴趣的用户提供详细信息。

---

## 如何使用缓存系统

启用缓存的主要接口是 `@cached` 装饰器。

#### 基本用法

要缓存函数的结果，使用 `@cached` 装饰它，提供唯一的 `cache_name` 并通常提供一个 `key_func` 来基于函数的参数生成唯一的字符串键。

```python
# 示例位于 cline_utils/dependency_system/utils/cache_manager.py
from cline_utils.dependency_system.utils.cache_manager import cached

# 定义一个函数来基于输入 'x' 生成键
def create_cache_key(x):
    return f"my_function_key:{x}"

@cached(cache_name="my_function_cache", key_func=create_cache_key)
def potentially_slow_function(x):
    # 模拟一个昂贵的计算
    print(f"Executing potentially_slow_function({x})...")
    time.sleep(1)
    return x * x

# 第一次调用：执行函数，结果存储在 "my_function_cache" 中，键为 "my_function_key:5"
result1 = potentially_slow_function(5)
print(f"Result 1: {result1}")

# 使用相同输入的第二次调用：立即返回缓存结果
result2 = potentially_slow_function(5)
print(f"Result 2: {result2}")

# 使用不同输入的调用：执行函数，新结果被缓存
result3 = potentially_slow_function(10)
print(f"Result 3: {result3}")
```

-   `"my_function_cache"`：此名称标识用于此函数的特定缓存实例。当首次遇到此名称时，`CacheManager` 会动态创建一个新的 `Cache` 对象。
-   `key_func=create_cache_key`：此函数接受传递给 `potentially_slow_function` 的参数，并为缓存条目生成唯一的字符串标识符。

#### 高级用法：TTL 和依赖

您可以为特定缓存自定义生存时间或定义依赖。

**自定义 TTL：**

```python
# 为这个特定的缓存实例设置 5 分钟 TTL
@cached(cache_name="short_lived_cache", key_func=lambda arg: f"slc:{arg}", ttl=300)
def function_with_short_ttl(arg):
    # ... 函数逻辑 ...
    return arg
```

**动态依赖：**

如果缓存结果依赖于其他数据（例如，文件），您可以将依赖与结果一起返回。缓存系统根据某些缓存函数（如 `analyze_file`）中使用的文件路径隐式创建依赖。

```python
@cached(cache_name="dependent_cache", key_func=lambda file_id: f"dep_cache:{file_id}")
def process_file_data(file_id):
    file_path = f"/path/to/data/{file_id}.json"
    # ... 处理 file_path ...
    result = {"data": "processed_data"}
    # file_path 上的隐式依赖可能由内部函数处理，
    # 但如果需要，您可以返回显式依赖：
    # dependencies = [f"file:{normalize_path(file_path)}"]
    # return result, dependencies
    return result # 不返回显式依赖的示例
```

如果底层文件发生更改，像 `check_file_modified` 这样的函数可以触发链接到该文件路径的缓存的失效。

#### 手动失效

虽然系统通常自动处理失效（例如，基于文件修改），但您可以使用 `invalidate_dependent_entries` 手动清除条目或使用 CLI 命令清除整个缓存。

```python
from cline_utils.dependency_system.utils.cache_manager import invalidate_dependent_entries

# 使 "my_function_cache" 中的特定条目失效
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:5")

# 使 "my_function_cache" 中的所有条目失效
invalidate_dependent_entries(cache_name="my_function_cache", key_pattern="my_function_key:.*")
```

**清除所有缓存：**

用户清除所有缓存的最直接方式是通过 `dependency_processor.py` 命令：

```bash
python -m cline_utils.dependency_system.dependency_processor clear-caches
```

如果您怀疑缓存问题导致问题，LLM 可以执行此命令。

---

## 缓存管理详情

-   **按需创建与清理**：缓存在首次通过 `@cached(cache_name=...)` 请求时由 `CacheManager` 创建。管理器定期清理在其 TTL 内未被访问的 `Cache` 实例，节省内存。
-   **LRU 驱逐**：单个 `Cache` 实例有大小限制。当满时，最近最少使用的条目被移除。
-   **依赖跟踪**：系统可以将缓存条目链接到依赖（如文件路径）。修改文件触发 `check_file_modified`，它使用 `invalidate_dependent_entries` 清除相关的缓存数据（例如，该文件的分析结果）。

---

## 配置

可以通过直接修改 `cline_utils/dependency_system/utils/cache_manager.py` 中的常量来调整缓存行为：

-   `DEFAULT_TTL`（秒）：缓存实例和条目的默认过期时间（当前为 600 秒 / 10 分钟）。
-   `DEFAULT_MAX_SIZE`：每个缓存实例的默认最大项目数（当前为 1000）。
-   `CACHE_SIZES`（字典）：允许为特定的 `cache_name` 设置不同的 `max_size` 值（例如，`{"embeddings_generation": 100, "key_generation": 5000}`）。

*注意：修改这些需要直接编辑 Python 文件。*

---

## 持久化

`CacheManager` 可以使用 `persist=True` 初始化，以将缓存内容保存/加载到 `CACHE_DIR`（`cline_utils/dependency_system/utils/` 中的 `cache` 子目录）中的 JSON 文件。

**此功能目前默认禁用（`persist=False`）。**启用它会在运行之间保留缓存，但如果不仔细管理，可能会导致加载陈旧数据。

---

## 缓存统计

对于调试或性能分析，您可以检索特定缓存的统计信息：

```python
from cline_utils.dependency_system.utils.cache_manager import get_cache_stats

stats = get_cache_stats("my_function_cache") # 使用实际的 cache_name
print(f"Cache 'my_function_cache' Stats - Hits: {stats['hits']}, Misses: {stats['misses']}, Current Size: {stats['size']}")
```

这对于理解缓存效率和识别性能瓶颈很有用。

---

## 最佳实践

1.  **使用描述性缓存名称**：选择清楚描述缓存目的的名称（例如，`"file_analysis_cache"` 而不是 `"cache1"`）。
2.  **设计好的键函数**：确保您的 `key_func` 为不同的输入生成唯一的键，以避免冲突。
3.  **考虑 TTL**：为经常更改的数据设置较短的 TTL，为稳定数据设置较长的 TTL。
4.  **监控缓存大小**：定期检查缓存统计以确保它们不会无限增长。
5.  **在开发期间清除缓存**：当您修改缓存函数或怀疑陈旧数据时，清除缓存以避免混淆。

---

## 故障排除

-   **缓存未被使用**：确保您在函数上使用 `@cached` 装饰器，并且 `cache_name` 和 `key_func` 正确设置。
-   **陈旧数据**：如果您看到旧结果，使用 CLI 命令清除缓存或减少 TTL。
-   **内存问题**：如果缓存消耗过多内存，减少 `DEFAULT_MAX_SIZE` 或为特定缓存调整 `CACHE_SIZES`。
-   **性能慢**：检查缓存统计。低命中率可能表示 `key_func` 没有有效地重用结果。

---

缓存系统是 CRCT 高性能的关键组成部分。理解如何使用和配置它可以帮助您优化项目的分析速度。

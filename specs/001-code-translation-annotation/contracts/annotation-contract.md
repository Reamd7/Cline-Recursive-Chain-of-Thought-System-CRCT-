# Annotation Contract: 代码注释规范

**Feature**: 项目代码与文档多语言支持 | **Date**: 2025-12-29
**Version**: 1.0

## 概述 | Overview

本文档定义了代码注释的契约和规范,确保所有代码注释遵循统一的标准和格式。

---

## 注释风格规范 | Annotation Style Specification

### Python 代码注释风格

遵循 **Google Python Style Guide** 和 **PEP 257** 规范。

#### 1. 模块级注释 (Module Docstring)

```python
"""
This module provides report generation functionality for code analysis.

该模块提供代码分析的报告生成功能。

Main features:
    - Generate HTML reports from analysis results
    - Support custom templates
    - Export to multiple formats

主要功能:
    - 从分析结果生成 HTML 报告
    - 支持自定义模板
    - 导出为多种格式
"""
```

#### 2. 函数注释 (Function Docstring)

**完整示例**:
```python
def process_chunk(chunk: str, max_tokens: int = 1000) -> List[str]:
    """
    处理文本块并生成思维链步骤。

    Process text chunks and generate Chain-of-Thought steps.

    这个函数通过递归分解来处理大型文本块,
    确保每个步骤都在模型的上下文窗口大小内。

    This function processes large text chunks through recursive decomposition,
    ensuring each step fits within the model's context window size.

    Args:
        chunk: 要处理的文本块 | The text chunk to process
        max_tokens: 最大词元数量,默认 1000 | Maximum number of tokens, default 1000

    Returns:
        思维链步骤列表,每个步骤包含推理过程 | List of Chain-of-Thought steps, each containing reasoning process

    Raises:
        ValueError: 如果文本块为空或格式无效 | If the text chunk is empty or has invalid format
        TokenLimitExceededError: 如果单个步骤超出词元限制 | If a single step exceeds token limit

    Example:
        >>> steps = process_chunk("Analyze this text.", max_tokens=500)
        >>> print(len(steps))
        3
    """
    # Implementation here
    pass
```

**简化示例** (适用于简单函数):
```python
def get_config_path() -> str:
    """返回配置文件的绝对路径。| Return absolute path to config file."""
    return os.path.abspath("config.yaml")
```

#### 3. 类注释 (Class Docstring)

```python
class ReportGenerator:
    """
    代码分析报告生成器。

    Code analysis report generator.

    这个类负责从分析结果生成各种格式的报告,
    支持 HTML、PDF 和 Markdown 输出。

    This class is responsible for generating reports in various formats
    from analysis results, supporting HTML, PDF, and Markdown output.

    Attributes:
        template_dir: 模板目录路径 | Template directory path
        output_dir: 输出目录路径 | Output directory path
        format: 输出格式 (html/pdf/markdown) | Output format
    """

    def __init__(self, template_dir: str, output_dir: str, format: str = "html"):
        """初始化报告生成器。| Initialize the report generator."""
        self.template_dir = template_dir
        self.output_dir = output_dir
        self.format = format
```

#### 4. 行内注释 (Inline Comments)

```python
def process_chunk(chunk: str, max_tokens: int = 1000) -> List[str]:
    """
    处理文本块并生成思维链步骤。
    """
    # 递归终止条件: 如果块足够小,直接处理
    # Recursive termination: if chunk is small enough, process directly
    if len(chunk) <= max_tokens:
        return [self._analyze(chunk)]

    # 否则,分解为更小的块并递归处理
    # Otherwise, split into smaller chunks and process recursively
    sub_chunks = self._split_chunk(chunk)

    results = []
    for sub in sub_chunks:
        # 对每个子块进行递归处理并收集结果
        # Recursively process each sub-chunk and collect results
        results.extend(self.process_chunk(sub))

    return results
```

---

## 注释内容规范 | Annotation Content Guidelines

### 必须包含的内容

1. **功能描述**:
   - 解释函数或类"做什么"
   - 简洁明确,一句话概括

2. **参数说明** (Args):
   - 每个参数的类型和用途
   - 约束条件 (如范围、默认值)

3. **返回值说明** (Returns):
   - 返回值的类型和含义
   - 特殊情况下的返回值

4. **异常说明** (Raises,如适用):
   - 可能抛出的异常
   - 异常抛出的条件

### 可选内容

1. **示例** (Examples):
   - 对于复杂的公共 API,提供使用示例
   - 示例应覆盖常见用法

2. **注意事项** (Notes):
   - 重要的使用注意事项
   - 性能考虑或限制

3. **"为什么"的解释**:
   - 为什么选择特定的算法或设计
   - 为什么有特定的约束或假设

---

## 特殊场景处理 | Special Scenarios

### 1. 已有注释的代码

**规则**: 保留原文注释,添加中文翻译

```python
def process_data(data: List[str]) -> Dict[str, int]:
    """
    Process input data and generate statistics.

    处理输入数据并生成统计信息。

    Args:
        data: List of input strings | 输入字符串列表

    Returns:
        Dictionary with statistics | 包含统计信息的字典
    """
    # Filter out empty strings
    # 过滤空字符串
    filtered = [s for s in data if s]

    # Count occurrences
    # 统计出现次数
    counts = Counter(filtered)

    return dict(counts)
```

### 2. 简单函数 (Getter/Setter)

**规则**: 使用一行简洁注释

```python
def get_name(self) -> str:
    """获取用户名称。| Get user name."""
    return self._name

def set_name(self, name: str) -> None:
    """设置用户名称。| Set user name."""
    self._name = name
```

### 3. 复杂算法

**规则**: 添加详细的"为什么"解释

```python
def choose_algorithm(self, data_size: int) -> Algorithm:
    """
    根据数据大小选择最合适的排序算法。

    Choose the most appropriate sorting algorithm based on data size.

    为什么选择快速排序而非归并排序:
    - 快速排序的平均时间复杂度为 O(n log n)
    - 对于中等规模数据,快速排序的常数因子更小
    - 归并排序需要额外的 O(n) 空间,而快速排序是原地排序

    Why Quick Sort over Merge Sort:
    - Quick Sort has average time complexity of O(n log n)
    - For medium-sized data, Quick Sort has smaller constant factors
    - Merge Sort requires O(n) extra space, while Quick Sort is in-place
    """
    if data_size < 100:
        return Algorithm.INSERTION_SORT
    elif data_size < 10000:
        return Algorithm.QUICK_SORT
    else:
        return Algorithm.MERGE_SORT
```

### 4. 技术术语

**规则**: 首次出现时使用双语格式

```python
def compute_embeddings(self, texts: List[str]) -> np.ndarray:
    """
    计算文本的向量嵌入 (Embeddings)。

    Compute vector embeddings for texts.

    使用 Transformer 模型将文本转换为高维向量表示,
    这些向量可以用于语义搜索和相似度计算。

    Use Transformer model to convert text to high-dimensional vector representations,
    which can be used for semantic search and similarity calculation.

    Args:
        texts: 输入文本列表 | List of input texts

    Returns:
        向量矩阵,形状为 (len(texts), embedding_dim) | Vector matrix with shape (len(texts), embedding_dim)
    """
    pass
```

---

## 验收标准 | Acceptance Criteria

### 函数级别检查
每个函数必须满足:

1. **注释完整性**:
   - [ ] 有清晰的 docstring
   - [ ] 包含功能描述 (中英双语)
   - [ ] 包含参数说明 (Args)
   - [ ] 包含返回值说明 (Returns)
   - [ ] 如适用,包含异常说明 (Raises)

2. **注释质量**:
   - [ ] 解释"为什么"而非仅仅"是什么"
   - [ ] 技术术语使用一致
   - [ ] 语言简洁明确

3. **格式正确性**:
   - [ ] 遵循 Google 风格
   - [ ] 缩进和空行使用正确

### 文件级别检查
每个代码文件必须满足:

1. **模块级注释**:
   - [ ] 文件顶部有模块 docstring
   - [ ] 说明模块的主要功能和用途

2. **注释覆盖率**:
   - [ ] ≥ 95% 的函数有中文注释
   - [ ] 所有公共 API 有完整注释

3. **一致性**:
   - [ ] 所有注释风格一致
   - [ ] 术语翻译一致

---

## 禁止行为 | Prohibited Actions

1. **禁止注释代码**:
   - 不要使用注释来禁用代码,应该直接删除或使用版本控制

2. **禁止无意义注释**:
   ```python
   # Bad example
   i = i + 1  # Increment i by one

   # Good example
   # Move to next chunk (skip header)
   i = i + 1
   ```

3. **禁止过时的注释**:
   - 代码修改时必须同步更新注释

4. **禁止仅翻译变量名**:
   ```python
   # Bad
   # 用户名称变量
   user_name = "Alice"

   # Good
   # 用户名称,用于日志记录
   user_name = "Alice"
   ```

---

## 其他编程语言 | Other Programming Languages

### JavaScript/TypeScript

```javascript
/**
 * 处理用户输入并生成响应。
 * Process user input and generate response.
 *
 * @param input - 用户输入的文本 | User input text
 * @param options - 配置选项 | Configuration options
 * @returns 生成的响应 | Generated response
 * @throws {ValidationError} 如果输入格式无效 | If input format is invalid
 *
 * @example
 * ```javascript
 * const response = processUserInput("Hello", { language: "en" });
 * console.log(response);
 * ```
 */
function processUserInput(input, options = {}) {
  // Implementation
}
```

### Java

```java
/**
 * 处理用户输入并生成响应。
 * Process user input and generate response.
 *
 * @param input 用户输入的文本 | User input text
 * @param options 配置选项 | Configuration options
 * @return 生成的响应 | Generated response
 * @throws ValidationError 如果输入格式无效 | If input format is invalid
 *
 * @since 1.0
 */
public Response processUserInput(String input, Options options) {
  // Implementation
}
```

---

## 参考资源 | Reference Resources
- [PEP 257 -- Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Docstring Conventions](https://numpydoc.readthedocs.io/en/latest/format.html)

---

**文档版本**: 1.0 | **最后更新**: 2025-12-29

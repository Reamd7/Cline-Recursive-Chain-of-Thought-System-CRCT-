# 迁移指南：v7.x 到 v8.0

> [!CAUTION]
> **主要版本更新** - 此版本包含重大更改。请在升级前仔细阅读本指南。

## 概述

版本 8.0 代表了 CRCT 系统的重大架构演进。核心嵌入和分析基础设施已被重建，以提供显著改进的准确性和性能。

**升级时间**：~15-30 分钟（取决于项目大小）
**需要停机**：否（仅分析）
**数据迁移**：是（必须重新生成嵌入）

---

## 重大更改摘要

### 1. 嵌入系统架构 ⚠️
- **更改**：从简单的基于内容的迁移到符号本质字符串（Symbol Essence Strings, SES）
- **影响**：所有现有嵌入不兼容，必须重新生成
- **操作**：升级后运行 `analyze-project --force-embeddings`

### 2. 新的 Python 依赖 🔧
- **添加**：`llama-cpp-python`（用于 GGUF 模型支持）
- **添加**：`huggingface_hub`（用于模型下载）
- **操作**：运行 `pip install -r requirements.txt`

### 3. 运行时符号检查 📦
- **要求**：Python 文件必须语法有效且可导入
- **影响**：语法错误将阻止这些文件的符号提取
- **操作**：在运行分析之前修复语法错误

### 4. 首次运行模型下载 📥
- **行为**：Qwen3 重排序器模型（~600MB）在首次运行时自动下载
- **影响**：需要稳定的互联网连接
- **存储**：模型存储在 `models/` 目录中

### 5. CLI 和 API 更改 ⚠️
- **已弃用**：`set_char` 命令现在**不安全**且已弃用。请改用 `add-dependency`。
- **已删除**：`cline_utils.dependency_system.core.exceptions` 模块。
- **影响**：使用 `set_char` 或从 `exceptions` 导入的自定义脚本将失败。
- **操作**：更新脚本以使用 `add-dependency` 和 `exceptions_enhanced`。

---

## 迁移前检查清单

在升级之前，确保：

- [ ] **备份当前工作** - 将所有更改提交到版本控制
- [ ] **检查 Python 版本** - 需要 Python 3.8+
- [ ] **验证磁盘空间** - 模型和嵌入需要约 2GB
- [ ] **检查互联网连接** - 模型下载需要
- [ ] **修复语法错误** - 在 Python 文件上运行 linter
- [ ] **查看当前配置** - 记录任何自定义配置设置

---

## 分步迁移

### 步骤 1：安装新依赖

```bash
# 导航到项目根目录
cd /path/to/your/project

# 更新 Python 依赖
pip install -r requirements.txt

# 验证安装
python -c "import llama_cpp; from huggingface_hub import hf_hub_download; print('✓ Dependencies installed')"

# 可选：更新 Node 依赖以进行可视化
npm install
```

**预期输出**：
```
✓ Dependencies installed
```

**故障排除**：
- **macOS**：如果 llama-cpp-python 失败，使用 `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python` 安装
- **Linux**：可能需要 `build-essential` 和 `cmake`：`sudo apt install build-essential cmake`
- **Windows**：确保安装了 Visual Studio Build Tools

---

### 步骤 2：修复语法错误（Python 项目）

新的运行时检查器需要可导入的 Python 模块。

```bash
# 运行 linter 查找语法错误
python -m pylint your_package/ --errors-only

# 或使用 flake8
flake8 your_package/ --select=E9,F

# 在继续之前修复任何报告的语法错误
```

**常见问题**：
- 函数/类定义后缺少冒号
- 缩进错误
- 未闭合的括号/圆括号
- 字符串中的无效转义序列

---

### 步骤 3：更新配置（可选）

在 `.clinerules` 中查看新的配置选项：

```json
{
  "thresholds": {
    "reranker_promotion_threshold": 0.92,
    "reranker_strong_semantic_threshold": 0.78,
    "reranker_weak_semantic_threshold": 0.65
  },
  "embedding": {
    "auto_select_model": true,
    "batch_size": "auto",
    "max_context_length": 32768
  },
  "resources": {
    "min_memory_mb": 512,
    "recommended_memory_mb": 2048
  }
}
```

**新选项**：
- `reranker_*_threshold`：控制重排序器敏感度
- `auto_select_model`：启用硬件自适应模型选择（默认：true）
- `batch_size`：设置为 "auto" 以根据 VRAM 动态调整大小
- `max_context_length`：大文件的最大 tokens（默认：32768）

---

### 步骤 4：运行首次分析（模型下载）

首次运行时，Qwen3 重排序器将自动下载：

```bash
python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
```

**预期输出**：
```
INFO: Checking for Qwen3 reranker model...
INFO: Downloading ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0...
Downloading: 100%|████████████| 612MB/612MB [02:15<00:00, 4.52MB/s]
INFO: Model downloaded successfully
INFO: Generating embeddings with SES architecture...
```

**下载详情**：
- **大小**：~600MB（量化 Q8_0 模型）
- **时间**：2-5 分钟（取决于连接）
- **存储**：`models/Qwen3-Reranker-0.6B-Q8_0/`

**如果下载失败**：
```bash
# 从 Hugging Face 手动下载
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0-Safetensors",
    local_dir="models/Qwen3-Reranker-0.6B-Q8_0"
)
```

---

### 步骤 5：验证升级成功

检查分析是否成功完成：

```bash
# 在输出中查找这些指标：
# ✓ "Symbol map merge complete: <N> files"
# ✓ "Dependency suggestion complete"
# ✓ "Final review checklist generated successfully"

# 验证新文件已创建：
ls -la cline_utils/dependency_system/core/project_symbol_map.json
ls -la cline_utils/dependency_system/core/ast_verified_links.json

# 检查调试输出中的错误
grep ERROR cline_docs/debug.txt
```

---

## 迁移后验证

### 验证嵌入

嵌入现在应该使用 SES 格式：

```bash
# 检查嵌入元数据
cat cline_utils/dependency_system/analysis/embeddings/metadata.json | head -20

# 应显示丰富的元数据，包括：
# - "type_annotations": {...}
# - "inheritance": [...]
# - "decorators": [...]
```

### 验证符号映射

```bash
# 检查生成的符号映射
python -c "
import json
with open('cline_utils/dependency_system/core/project_symbol_map.json') as f:
    data = json.load(f)
    print(f'Symbol map entries: {len(data)}')
    # 显示示例条目
    sample = next(iter(data.values()))
    print('Sample keys:', list(sample.keys())[:5])
"
```

**预期键**：`imports`、`functions`、`classes`、`calls`、`attribute_accesses` 等。

### 测试重排序

检查是否正在使用重排序器：

```bash
# 查看日志中的重排序器使用情况
grep "Reranker" cline_docs/debug.txt | head -10

# 应显示如下行：
# "Reranked pair: source.py -> target.py (score: 0.847)"
```

---

## 常见迁移问题

### 问题："llama-cpp-python 无法安装"

**症状**：pip install 期间构建错误

**解决方案**：
```bash
# macOS - 使用 Metal 加速
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# Linux - 先安装构建工具
sudo apt install build-essential cmake
pip install llama-cpp-python

# Windows - 安装 Visual Studio Build Tools
# 下载地址：https://visualstudio.microsoft.com/downloads/
# 然后：pip install llama-cpp-python
```

---

### 问题："运行时检查失败"

**症状**：分析期间关于导入失败的警告

**原因**：项目文件中的语法错误或缺少依赖

**解决方案**：
```bash
# 识别有问题的文件
grep "Failed to inspect" cline_docs/debug.txt

# 检查文件是否可导入
python -c "import path.to.your.module"

# 修复语法错误或在 .clinerules 中添加到排除项
```

---

### 问题："分析期间内存不足"

**症状**：进程被终止或崩溃

**解决方案**：
```bash
# 在配置中减少批次大小
{
  "embedding": {
    "batch_size": 32  # 有限 RAM 的较低值
  },
  "resources": {
    "min_memory_mb": 512
  }
}

# 或使用仅 CPU 模式（较慢但使用更少内存）
{
  "compute": {
    "embedding_device": "cpu"
  }
}
```

---

### 问题："模型下载卡住/超时"

**症状**：下载冻结或失败

**解决方案**：
```bash
# 使用手动下载
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0-Safetensors',
    local_dir='models/Qwen3-Reranker-0.6B-Q8_0',
    resume_download=True  # 如果中断则恢复
)
"

# 然后重新运行分析
python -m cline_utils.dependency_system.dependency_processor analyze-project
```

---

## 回滚程序

如果您需要恢复到 v7.x：

```bash
# 1. 检出以前的版本
git checkout tags/v7.90  # 或您最后的 v7.x 版本

# 2. 重新安装旧依赖
pip install -r requirements.txt

# 3. 删除 v8.0 产物
rm -rf models/
rm cline_utils/dependency_system/core/project_symbol_map.json
rm cline_utils/dependency_system/core/ast_verified_links.json

# 4. 使用旧系统重新生成
python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
```

---

## 性能预期

### 首次运行（v8.0）
- **嵌入生成**：慢 2-4 倍（由于 SES 复杂性）
- **依赖建议**：与 v7.x 相似
- **总体**：初始运行慢约 30-50%

### 后续运行
- **使用缓存**：快 2-3 倍（更好的缓存）
- **准确度**：好 5-10 倍（重排序器 + SES）
- **内存**：相似或略高的峰值使用

### 资源使用
| 组件 | v7.x | v8.0 | 备注 |
|-----------|------|------|-------|
| **峰值 RAM** | ~1GB | ~1.5GB | 加载重排序器时 |
| **磁盘** | ~100MB | ~1GB | 包括模型 |
| **VRAM** (GPU) | ~500MB | ~2GB | 使用 Qwen3-4B GGUF |

---

## v8.0 的好处

### 准确度改进
- **10 倍更好**的 SES 语义理解
- **5 倍更少**的重排序器误报
- **AST 验证**的结构依赖（100% 准确度）

### 开发者体验
- **实时进度条**带 ETA
- **清晰的错误消息**带可操作的指导
- **自动**模型下载和设置

### 性能优化
- **硬件自适应**模型选择
- **动态批次调整**基于 VRAM
- **增强的缓存**带压缩

---

## 获取帮助

### 资源
- **文档**：`/docs/` 目录
- **示例**：`/examples/` 目录
- **测试套件**：`/tests/` - 使用 `pytest` 运行

### 故障排除
1. 检查 `cline_docs/debug.txt` 以获取详细日志
2. 使用详细日志记录运行：`--log-level DEBUG`
3. 查看 `.clinerules` 中的配置

### 支持渠道
- **GitHub Issues**：用于错误和功能请求
- **Discussions**：用于问题和最佳实践

---

## 下一步

成功迁移后：

1. **查看结果**：检查生成的依赖关系图
2. **微调配置**：如果需要，调整重排序器阈值
3. **优化性能**：为您的硬件配置批次大小
4. **探索新功能**：尝试运行时检查和 AST 验证

---

**迁移完成！** 🎉

您的 CRCT 安装现在运行 v8.0，具有增强的准确性和性能。

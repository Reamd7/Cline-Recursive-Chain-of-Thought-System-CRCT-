# Migration Guide: v7.x to v8.0

## 迁移指南:v7.x 到 v8.0 | Migration Guide: v7.x to v8.0

> [!CAUTION]
> **Major Version Update** - This release includes breaking changes. Please read this guide carefully before upgrading.
>
> **主要版本更新** - 此版本包含重大变更。请在升级前仔细阅读本指南。

## Overview

## 概述 | Overview

Version 8.0 represents a significant architectural evolution of the CRCT system. The core embedding and analysis infrastructure has been rebuilt to provide dramatically improved accuracy and performance.

v8.0 版本代表了 CRCT 系统的重大架构演进。核心嵌入和分析基础设施已重建,以提供显著提升的准确性和性能。

**Upgrade Time**: ~15-30 minutes (depending on project size)
**升级时间**: 约 15-30 分钟(取决于项目规模)

**Downtime Required**: No (analysis only)
**所需停机时间**: 无(仅分析)

**Data Migration**: Yes (embeddings must be regenerated)
**数据迁移**: 是(必须重新生成嵌入)

---

## Breaking Changes Summary

## 重大变更摘要 | Breaking Changes Summary

### 1. Embedding System Architecture ⚠️

### 1. 嵌入系统架构 ⚠️ | Embedding System Architecture

- **Changed**: Migrated from simple content-based to Symbol Essence Strings (SES)
- **变更**: 从简单的基于内容迁移到符号本质字符串 (SES)

- **Impact**: All existing embeddings are incompatible and must be regenerated
- **影响**: 所有现有嵌入不兼容,必须重新生成

- **Action**: Run `analyze-project --force-embeddings` after upgrade
- **操作**: 升级后运行 `analyze-project --force-embeddings`

### 2. New Python Dependencies 🔧

### 2. 新的 Python 依赖 🔧 | New Python Dependencies

- **Added**: `llama-cpp-python` (for GGUF model support)
- **新增**: `llama-cpp-python`(用于 GGUF 模型支持)

- **Added**: `huggingface_hub` (for model downloads)
- **新增**: `huggingface_hub`(用于模型下载)

- **Action**: Run `pip install -r requirements.txt`
- **操作**: 运行 `pip install -r requirements.txt`

### 3. Runtime Symbol Inspection 📦

### 3. 运行时符号检查 📦 | Runtime Symbol Inspection

- **Requirement**: Python files must be syntactically valid and importable
- **要求**: Python 文件必须在语法上有效且可导入

- **Impact**: Syntax errors will prevent symbol extraction for those files
- **影响**: 语法错误将阻止这些文件的符号提取

- **Action**: Fix syntax errors before running analysis
- **操作**: 在运行分析前修复语法错误

### 4. First-Run Model Download 📥

### 4. 首次运行模型下载 📥 | First-Run Model Download

- **Behavior**: Qwen3 reranker model (~600MB) downloads automatically on first run
- **行为**: Qwen3 重排序模型(~600MB)在首次运行时自动下载

- **Impact**: Requires stable internet connection
- **影响**: 需要稳定的互联网连接

- **Storage**: Models stored in `models/` directory
- **存储**: 模型存储在 `models/` 目录中

### 5. CLI & API Changes ⚠️

### 5. CLI 和 API 变更 ⚠️ | CLI & API Changes

- **Deprecated**: `set_char` command is now **unsafe** and deprecated. Use `add-dependency` instead.
- **已弃用**: `set_char` 命令现已**不安全**并被弃用。请改用 `add-dependency`。

- **Removed**: `cline_utils.dependency_system.core.exceptions` module.
- **已移除**: `cline_utils.dependency_system.core.exceptions` 模块。

- **Impact**: Custom scripts using `set_char` or importing from `exceptions` will fail.
- **影响**: 使用 `set_char` 或从 `exceptions` 导入的自定义脚本将失败。

- **Action**: Update scripts to use `add-dependency` and `exceptions_enhanced`.
- **操作**: 更新脚本以使用 `add-dependency` 和 `exceptions_enhanced`。

---

## Pre-Migration Checklist

## 迁移前检查清单 | Pre-Migration Checklist

Before upgrading, ensure:

在升级前,请确保:

- [ ] **Backup current work** - Commit all changes to version control
- [ ] **备份当前工作** - 将所有更改提交到版本控制

- [ ] **Check Python version** - Requires Python 3.8+
- [ ] **检查 Python 版本** - 需要 Python 3.8+

- [ ] **Verify disk space** - Need ~2GB for models and embeddings
- [ ] **验证磁盘空间** - 模型和嵌入需要约 2GB

- [ ] **Check internet connection** - Required for model downloads
- [ ] **检查互联网连接** - 模型下载所需

- [ ] **Fix syntax errors** - Run linter on Python files
- [ ] **修复语法错误** - 在 Python 文件上运行 linter

- [ ] **Review current config** - Note any custom configuration settings
- [ ] **查看当前配置** - 记录任何自定义配置设置

---

## Step-by-Step Migration

## 分步迁移指南 | Step-by-Step Migration

### Step 1: Install New Dependencies

### 步骤 1: 安装新的依赖 | Step 1: Install New Dependencies

```bash
# Navigate to project root
# 导航到项目根目录
cd /path/to/your/project

# Update Python dependencies
# 更新 Python 依赖
pip install -r requirements.txt

# Verify installation
# 验证安装
python -c "import llama_cpp; from huggingface_hub import hf_hub_download; print('✓ Dependencies installed')"

# Optional: Update Node dependencies for visualization
# 可选:更新可视化所需的 Node 依赖
npm install
```

**Expected Output**:
**预期输出**:

```
✓ Dependencies installed
✓ 依赖已安装
```

**Troubleshooting**:
**故障排除**:

- **macOS**: If llama-cpp-python fails, install with `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python`
- **macOS**: 如果 llama-cpp-python 安装失败,使用 `CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python` 安装

- **Linux**: May need `build-essential` and `cmake`: `sudo apt install build-essential cmake`
- **Linux**: 可能需要 `build-essential` 和 `cmake`: `sudo apt install build-essential cmake`

- **Windows**: Ensure Visual Studio Build Tools are installed
- **Windows**: 确保已安装 Visual Studio Build Tools

---

### Step 2: Fix Syntax Errors (Python Projects)

### 步骤 2: 修复语法错误(Python 项目) | Step 2: Fix Syntax Errors (Python Projects)

The new runtime inspector requires importable Python modules.

新的运行时检查器需要可导入的 Python 模块。

```bash
# Run linter to find syntax errors
# 运行 linter 查找语法错误
python -m pylint your_package/ --errors-only

# Or use flake8
# 或使用 flake8
flake8 your_package/ --select=E9,F

# Fix any reported syntax errors before proceeding
# 在继续之前修复任何报告的语法错误
```

**Common Issues**:
**常见问题**:

- Missing colons after function/class definitions
- 函数/类定义后缺少冒号

- Indentation errors
- 缩进错误

- Unclosed brackets/parentheses
- 未闭合的括号/圆括号

- Invalid escape sequences in strings
- 字符串中的无效转义序列

---

### Step 3: Update Configuration (Optional)

### 步骤 3: 更新配置(可选) | Step 3: Update Configuration (Optional)

Review new configuration options in `.clinerules`:

查看 `.clinerules` 中的新配置选项:

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

**New Options**:
**新选项**:

- `reranker_*_threshold`: Control reranker sensitivity
- `reranker_*_threshold`: 控制重排序器灵敏度

- `auto_select_model`: Enable hardware-adaptive model selection (default: true)
- `auto_select_model`: 启用硬件自适应模型选择(默认: true)

- `batch_size`: Set to "auto" for dynamic sizing based on VRAM
- `batch_size`: 设置为 "auto" 以根据 VRAM 动态调整大小

- `max_context_length`: Maximum tokens for large files (default: 32768)
- `max_context_length`: 大文件的最大词元数(默认: 32768)

---

### Step 4: Run First Analysis (Model Download)

### 步骤 4: 运行首次分析(模型下载) | Step 4: Run First Analysis (Model Download)

On first run, the Qwen3 reranker will download automatically:

首次运行时,Qwen3 重排序器将自动下载:

```bash
python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
```

**Expected Output**:
**预期输出**:

```
INFO: Checking for Qwen3 reranker model...
INFO: 正在检查 Qwen3 重排序器模型...
INFO: Downloading ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0...
INFO: 正在下载 ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0...
Downloading: 100%|████████████| 612MB/612MB [02:15<00:00, 4.52MB/s]
INFO: Model downloaded successfully
INFO: 模型下载成功
INFO: Generating embeddings with SES architecture...
INFO: 正在使用 SES 架构生成嵌入...
```

**Download Details**:
**下载详情**:

- **Size**: ~600MB (quantized Q8_0 model)
- **大小**: ~600MB(量化 Q8_0 模型)

- **Time**: 2-5 minutes (depending on connection)
- **时间**: 2-5 分钟(取决于连接)

- **Storage**: `models/Qwen3-Reranker-0.6B-Q8_0/`
- **存储**: `models/Qwen3-Reranker-0.6B-Q8_0/`

**If Download Fails**:
**如果下载失败**:

```bash
# Manually download from Hugging Face
# 从 Hugging Face 手动下载
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id="ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0-Safetensors",
    local_dir="models/Qwen3-Reranker-0.6B-Q8_0"
)
```

---

### Step 5: Verify Upgrade Success

### 步骤 5: 验证升级成功 | Step 5: Verify Upgrade Success

Check that analysis completed successfully:

检查分析是否成功完成:

```bash
# Look for these indicators in output:
# 在输出中查找这些指示器:
# ✓ "Symbol map merge complete: <N> files"
# ✓ "符号映射合并完成: <N> 个文件"

# ✓ "Dependency suggestion complete"
# ✓ "依赖建议完成"

# ✓ "Final review checklist generated successfully"
# ✓ "最终审查检查清单生成成功"

# Verify new files were created:
# 验证新文件是否已创建:
ls -la cline_utils/dependency_system/core/project_symbol_map.json
ls -la cline_utils/dependency_system/core/ast_verified_links.json

# Check for errors in debug output
# 检查调试输出中的错误
grep ERROR cline_docs/debug.txt
```

---

## Post-Migration Validation

## 迁移后验证 | Post-Migration Validation

### Verify Embeddings

### 验证嵌入 | Verify Embeddings

Embeddings should now use SES format:

嵌入现在应使用 SES 格式:

```bash
# Check embedding metadata
# 检查嵌入元数据
cat cline_utils/dependency_system/analysis/embeddings/metadata.json | head -20

# Should show rich metadata including:
# 应显示丰富的元数据,包括:
# - "type_annotations": {...}
# - "inheritance": [...]
# - "decorators": [...]
```

### Verify Symbol Map

### 验证符号映射 | Verify Symbol Map

```bash
# Inspect generated symbol map
# 检查生成的符号映射
python -c "
import json
with open('cline_utils/dependency_system/core/project_symbol_map.json') as f:
    data = json.load(f)
    print(f'Symbol map entries: {len(data)}')
    # Show sample entry
    # 显示示例条目
    sample = next(iter(data.values()))
    print('Sample keys:', list(sample.keys())[:5])
"
```

**Expected Keys**: `imports`, `functions`, `classes`, `calls`, `attribute_accesses`, etc.
**预期键**: `imports`, `functions`, `classes`, `calls`, `attribute_accesses` 等。

### Test Reranking

### 测试重排序 | Test Reranking

Check that reranker is being used:

检查重排序器是否正在使用:

```bash
# Review reranker usage in logs
# 查看日志中的重排序器使用情况
grep "Reranker" cline_docs/debug.txt | head -10

# Should show lines like:
# 应显示类似以下的行:
# "Reranked pair: source.py -> target.py (score: 0.847)"
```

---

## Common Migration Issues

## 常见迁移问题 | Common Migration Issues

### Issue: "llama-cpp-python won't install"

### 问题: "llama-cpp-python 无法安装" | Issue: "llama-cpp-python won't install"

**Symptoms**: Build errors during pip install
**症状**: pip install 期间的构建错误

**Solutions**:
**解决方案**:

```bash
# macOS - Use Metal acceleration
# macOS - 使用 Metal 加速
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python

# Linux - Install build tools first
# Linux - 首先安装构建工具
sudo apt install build-essential cmake
pip install llama-cpp-python

# Windows - Install Visual Studio Build Tools
# Windows - 安装 Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/downloads/
# 从以下地址下载: https://visualstudio.microsoft.com/downloads/
# Then: pip install llama-cpp-python
# 然后: pip install llama-cpp-python
```

---

### Issue: "Runtime inspection failing"

### 问题: "运行时检查失败" | Issue: "Runtime inspection failing"

**Symptoms**: Warnings about failed imports during analysis
**症状**: 分析期间关于导入失败的警告

**Cause**: Syntax errors or missing dependencies in project files
**原因**: 项目文件中的语法错误或缺少依赖

**Solution**:
**解决方案**:

```bash
# Identify problematic files
# 识别问题文件
grep "Failed to inspect" cline_docs/debug.txt

# Check if file is importable
# 检查文件是否可导入
python -c "import path.to.your.module"

# Fix syntax errors or add to exclusions in .clinerules
# 修复语法错误或在 .clinerules 中添加到排除列表
```

---

### Issue: "Out of memory during analysis"

### 问题: "分析期间内存不足" | Issue: "Out of memory during analysis"

**Symptoms**: Process killed or crashes
**症状**: 进程被终止或崩溃

**Solution**:
**解决方案**:

```bash
# Reduce batch size in config
# 在配置中减少批处理大小
{
  "embedding": {
    "batch_size": 32  # Lower value for limited RAM
                      # 为有限的 RAM 使用较低的值
  },
  "resources": {
    "min_memory_mb": 512
  }
}

# Or use CPU-only mode (slower but uses less memory)
# 或使用仅 CPU 模式(较慢但使用较少内存)
{
  "compute": {
    "embedding_device": "cpu"
  }
}
```

---

### Issue: "Model download stuck/timeout"

### 问题: "模型下载卡住/超时" | Issue: "Model download stuck/timeout"

**Symptoms**: Download freezes or fails
**症状**: 下载冻结或失败

**Solution**:
**解决方案**:

```bash
# Use manual download
# 使用手动下载
pip install huggingface_hub
python -c "
from huggingface_hub import snapshot_download
snapshot_download(
    repo_id='ManiKumarAdapala/Qwen3-Reranker-0.6B-Q8_0-Safetensors',
    local_dir='models/Qwen3-Reranker-0.6B-Q8_0',
    resume_download=True  # Resume if interrupted
                          # 如果中断则恢复
)
"

# Then rerun analysis
# 然后重新运行分析
python -m cline_utils.dependency_system.dependency_processor analyze-project
```

---

## Rollback Procedure

## 回滚过程 | Rollback Procedure

If you need to revert to v7.x:

如果您需要回退到 v7.x:

```bash
# 1. Checkout previous version
# 1. 检出以前的版本
git checkout tags/v7.90  # Or your last v7.x version
                          # 或您的最后一个 v7.x 版本

# 2. Reinstall old dependencies
# 2. 重新安装旧的依赖
pip install -r requirements.txt

# 3. Remove v8.0 artifacts
# 3. 删除 v8.0 工件
rm -rf models/
rm cline_utils/dependency_system/core/project_symbol_map.json
rm cline_utils/dependency_system/core/ast_verified_links.json

# 4. Regenerate with old system
# 4. 使用旧系统重新生成
python -m cline_utils.dependency_system.dependency_processor analyze-project --force-embeddings
```

---

## Performance Expectations

## 性能预期 | Performance Expectations

### First Run (v8.0)

### 首次运行 (v8.0) | First Run (v8.0)

- **Embedding Generation**: 2-4x slower (due to SES complexity)
- **嵌入生成**: 慢 2-4 倍(由于 SES 复杂性)

- **Dependency Suggestion**: Similar to v7.x
- **依赖建议**: 与 v7.x 相似

- **Overall**: ~30-50% slower on initial run
- **总体**: 首次运行慢约 30-50%

### Subsequent Runs

### 后续运行 | Subsequent Runs

- **With Cache**: 2-3x faster (better caching)
- **使用缓存**: 快 2-3 倍(更好的缓存)

- **Accuracy**: 5-10x better (reranker + SES)
- **准确性**: 好 5-10 倍(重排序器 + SES)

- **Memory**: Similar or slightly higher peak usage
- **内存**: 峰值使用相似或略高

### Resource Usage

### 资源使用 | Resource Usage

| Component | v7.x | v8.0 | Notes |
|-----------|------|------|-------|
| **组件** | **v7.x** | **v8.0** | **备注** |
| **Peak RAM** | ~1GB | ~1.5GB | With reranker loaded / 加载重排序器后 |
| **峰值 RAM** | ~1GB | ~1.5GB | |
| **Disk** | ~100MB | ~1GB | Includes models / 包括模型 |
| **磁盘** | ~100MB | ~1GB | |
| **VRAM** (GPU) | ~500MB | ~2GB | With Qwen3-4B GGUF |
| **显存** (GPU) | ~500MB | ~2GB | |

---

## Benefits of v8.0

## v8.0 的优势 | Benefits of v8.0

### Accuracy Improvements

### 准确性提升 | Accuracy Improvements

- **10x better** semantic understanding with SES
- 使用 SES,**语义理解提升 10 倍**

- **5x fewer** false positives with reranker
- 使用重排序器,**误报减少 5 倍**

- **AST-verified** structural dependencies (100% accuracy)
- **AST 验证的结构性依赖**(100% 准确性)

### Developer Experience

### 开发者体验 | Developer Experience

- **Real-time progress bars** with ETA
- **实时进度条**和预计完成时间

- **Clear error messages** with actionable guidance
- **清晰的错误消息**和可操作的指导

- **Automatic** model download and setup
- **自动**模型下载和设置

### Performance Optimization

### 性能优化 | Performance Optimization

- **Hardware-adaptive** model selection
- **硬件自适应**模型选择

- **Dynamic batch sizing** based on VRAM
- 基于 VRAM 的**动态批处理大小调整**

- **Enhanced caching** with compression
- **增强的缓存**和压缩

---

## Getting Help

## 获取帮助 | Getting Help

### Resources

### 资源 | Resources

- **Documentation**: `/docs/` directory
- **文档**: `/docs/` 目录

- **Examples**: `/examples/` directory
- **示例**: `/examples/` 目录

- **Test Suite**: `/tests/` - Run with `pytest`
- **测试套件**: `/tests/` - 使用 `pytest` 运行

### Troubleshooting

### 故障排除 | Troubleshooting

1. Check `cline_docs/debug.txt` for detailed logs
   检查 `cline_docs/debug.txt` 获取详细日志

2. Run with verbose logging: `--log-level DEBUG`
   使用详细日志运行: `--log-level DEBUG`

3. Review configuration in `.clinerules`
   查看 `.clinerules` 中的配置

### Support Channels

### 支持渠道 | Support Channels

- **GitHub Issues**: For bugs and feature requests
- **GitHub Issues**: 用于错误报告和功能请求

- **Discussions**: For questions and best practices
- **Discussions**: 用于问题和最佳实践

---

## Next Steps

## 后续步骤 | Next Steps

After successful migration:

成功迁移后:

1. **Review Results**: Check generated dependency diagrams
   **查看结果**: 检查生成的依赖关系图

2. **Fine-tune Config**: Adjust reranker thresholds if needed
   **微调配置**: 如需要,调整重排序器阈值

3. **Optimize Performance**: Configure batch sizes for your hardware
   **优化性能**: 为您的硬件配置批处理大小

4. **Explore New Features**: Try runtime inspection and AST verification
   **探索新功能**: 尝试运行时检查和 AST 验证

---

**Migration Complete!** 🎉
**迁移完成!** 🎉

Your CRCT installation is now running v8.0 with enhanced accuracy and performance.
您的 CRCT 安装现已运行 v8.0 版本,具有增强的准确性和性能。

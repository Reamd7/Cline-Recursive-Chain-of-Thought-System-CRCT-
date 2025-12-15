# CRCT 依赖系统测试套件

本目录包含 CRCT 依赖系统的综合测试套件。

## 结构

- **`test_functional_cache.py`**：缓存机制的功能测试（低级别）。
- **`test_integration_cache.py`**：完整分析工作流的集成测试，包括嵌入生成和源修改。
- **`test_manual_tooling_cache.py`**：手动缓存管理工具的测试。
- **`test_e2e_workflow.py`**：模拟 CLI 使用的端到端测试。
- **`test_resource_validator.py`**：系统资源验证和优化的测试。
- **`test_phase_tracker.py`**：进度跟踪和 UI 反馈的测试。
- **`test_config_manager_extended.py`**：配置管理、环境覆盖和资源调整的测试。
- **`test_runtime_inspector.py`**：运行时符号提取和分析的测试。

## 运行测试

### 前置条件
确保您已安装开发依赖项：
```bash
pip install -r requirements-dev.txt
```

### 基本用法
运行所有测试：
```bash
pytest cline_utils/dependency_system/tests/
```

运行并显示详细输出：
```bash
pytest -v cline_utils/dependency_system/tests/
```

### 运行特定测试
运行特定测试文件：
```bash
pytest cline_utils/dependency_system/tests/test_integration_cache.py
```

运行特定测试用例：
```bash
pytest cline_utils/dependency_system/tests/test_integration_cache.py::test_is04_embedding_regeneration
```

### 覆盖率
生成覆盖率报告：
```bash
pytest --cov=cline_utils.dependency_system --cov-report=html cline_utils/dependency_system/tests/
```
报告将在 `htmlcov/index.html` 中生成。

## 添加新测试

1.  **确定组件**：确定您正在测试的组件（例如 `project_analyzer`、`embedding_manager`）。
2.  **选择级别**：
    *   **单元/功能**：使用 `test_functional_*.py` 或创建新的 `test_<component>.py`。
    *   **集成**：如果涉及多个组件或文件 I/O，使用 `test_integration_*.py`。
    *   **端到端**：使用 `test_e2e_workflow.py` 进行完整工作流验证。
3.  **使用固定装置**：利用 `conftest.py` 中的现有固定装置（如果可用）或在本地定义它们。常见的固定装置包括 `test_project`（创建临时项目结构）和 `mock_embedding_model`。
4.  **模拟外部调用**：通过模拟 `embedding_manager` 或 `transformers` 避免实际的网络请求（例如模型下载）。

## 故障排除

-   **嵌入模型下载**：如果测试由于网络问题而缓慢或失败，请确保正在使用 `MockEmbeddingModel` 或您已在本地缓存了模型。
-   **路径问题**：使用 `pathlib` 实现跨操作系统的健壮路径处理。
-   **缓存干扰**：测试通常应该孤立运行。确保调用了 `clear_all_caches()` 或测试使用唯一的临时目录。

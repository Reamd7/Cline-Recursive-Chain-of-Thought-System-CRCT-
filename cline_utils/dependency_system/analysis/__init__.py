"""
============================================================================
分析模块包初始化 (Analysis Package Initialization)
============================================================================

这是依赖追踪系统的分析模块包，包含了所有与代码分析、依赖分析相关的核心功能。

模块列表:
---------
- dependency_analyzer.py: 依赖分析器，解析和分析代码依赖关系
- dependency_suggester.py: 依赖建议器，为代码提供智能依赖建议
- embedding_manager.py: 嵌入管理器 (v8.0)，管理 Symbol Essence Strings (SES)
- project_analyzer.py: 项目分析器，执行全项目级别的依赖分析
- reranker_history_tracker.py: 重排序历史追踪器 (v8.0)，追踪 Qwen3 重排序历史
- runtime_inspector.py: 运行时检查器 (v8.0)，提取运行时符号元数据
- symbol_map_merger.py: 符号映射合并器 (v8.0)，合并多个符号映射

主要特性 (v8.0):
----------------
- Symbol Essence Strings (SES): 革命性的嵌入架构
- Qwen3 重排序器: AI 驱动的语义依赖评分
- 运行时符号检查: 深度元数据提取（类型、继承、装饰器等）
- 硬件自适应: 根据可用资源选择 GGUF (Qwen3-4B) 或 SentenceTransformer

版本: v8.0
作者: CRCT 项目组
============================================================================
"""

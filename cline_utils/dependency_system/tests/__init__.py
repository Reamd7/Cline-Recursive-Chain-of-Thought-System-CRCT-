"""
============================================================================
测试模块包初始化 (Tests Package Initialization)
============================================================================

这是依赖追踪系统的测试模块包，包含了所有单元测试和集成测试。

测试文件列表:
-------------
- test_config_manager_extended.py: 配置管理器扩展测试
- test_e2e_workflow.py: 端到端工作流测试
- test_functional_cache.py: 功能性缓存测试
- test_integration_cache.py: 集成缓存测试
- test_manual_tooling_cache.py: 手动工具缓存测试
- test_phase_tracker.py: 阶段追踪器测试 (v8.0)
- test_resource_validator.py: 资源验证器测试 (v8.0)
- test_runtime_inspector.py: 运行时检查器测试 (v8.0)
- verify_rerank_caching.py: 重排序缓存验证 (v8.0)

测试覆盖范围:
-------------
- 缓存系统: 功能性、集成、手动工具缓存的全面测试
- 配置管理: 配置加载、验证、更新等测试
- 工作流: 端到端的依赖分析工作流测试
- v8.0 新功能: 阶段追踪、资源验证、运行时检查、重排序缓存

运行测试:
---------
使用 pytest 运行所有测试:
    pytest cline_utils/dependency_system/tests/

运行特定测试:
    pytest cline_utils/dependency_system/tests/test_cache_manager.py

版本: v8.0
作者: CRCT 项目组
============================================================================
"""
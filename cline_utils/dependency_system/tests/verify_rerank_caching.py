"""
测试模块：重排序缓存验证
Test Module: Rerank Caching Verification

本模块验证Qwen3重排序模型的缓存功能，确保：
- 缓存命中和未命中统计准确
- 相同输入使用缓存结果
- 不同输入触发新的计算
- 缓存清理功能正常

This module verifies Qwen3 reranker model caching functionality, ensuring:
- Cache hit and miss statistics are accurate
- Same inputs use cached results
- Different inputs trigger new calculations
- Cache clearing works properly
"""

# 导入系统模块 / Import system module
import sys
# 导入操作系统接口模块 / Import OS interface module
import os
# 导入unittest测试框架 / Import unittest testing framework
import unittest
# 导入unittest.mock模拟工具 / Import unittest.mock tools
from unittest.mock import MagicMock, patch
# 导入PyTorch张量库 / Import PyTorch tensor library
import torch

# 添加项目根目录到路径 / Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# 导入embedding_manager模块（包含重排序功能）/ Import embedding_manager (contains reranking functionality)
from cline_utils.dependency_system.analysis import embedding_manager
# 导入缓存管理器 / Import cache manager
from cline_utils.dependency_system.utils.cache_manager import cache_manager

class TestRerankCaching(unittest.TestCase):
    """
    测试类：重排序缓存功能测试
    Test Class: Rerank Caching Functionality Tests

    验证重排序模型的缓存机制，确保缓存能够有效减少重复计算
    """

    def setUp(self):
        """
        测试设置：每个测试前清理缓存
        Test Setup: Clear caches before each test

        目的：确保每个测试从干净状态开始
        Purpose: Ensure each test starts from clean state
        """
        # 清理所有缓存 / Clear all caches
        cache_manager.clear_all()

    @patch('cline_utils.dependency_system.analysis.embedding_manager._load_reranker_model')
    @patch('cline_utils.dependency_system.analysis.embedding_manager._get_available_vram')
    @patch('cline_utils.dependency_system.analysis.embedding_manager._get_available_ram')
    def test_reranking_cache(self, mock_get_ram, mock_get_vram, mock_load_model):
        """
        测试用例：验证重排序缓存
        Test Case: Verify Reranking Cache

        目的：验证重排序缓存的命中/未命中机制
        Purpose: Verify reranking cache hit/miss mechanism

        测试流程：
        1. 第一次调用 -> 缓存未命中
        2. 第二次调用（相同输入）-> 缓存命中
        3. 第三次调用（不同输入）-> 缓存未命中

        Test flow:
        1. First call -> cache miss
        2. Second call (same inputs) -> cache hit
        3. Third call (different inputs) -> cache miss
        """
        # === 设置模拟对象 === / === Setup mock objects ===

        # 模拟可用RAM为16GB / Mock available RAM as 16GB
        mock_get_ram.return_value = 16.0
        # 模拟可用VRAM为0（强制使用CPU路径）/ Mock available VRAM as 0 (force CPU path)
        mock_get_vram.return_value = 0.0

        # 创建模拟的tokenizer和模型 / Create mock tokenizer and model
        mock_tokenizer = MagicMock()
        mock_model = MagicMock()

        # === 模拟tokenizer行为 === / === Mock tokenizer behavior ===

        # 模拟pad方法返回张量 / Mock pad method to return tensors
        mock_tokenizer.pad.return_value = {
            'input_ids': torch.tensor([[1, 2, 3]]),
            'attention_mask': torch.tensor([[1, 1, 1]])
        }
        # 模拟token到ID的转换 / Mock token to ID conversion
        mock_tokenizer.convert_tokens_to_ids.side_effect = lambda x: 1 if x == 'no' else (2 if x == 'yes' else 0)
        # 模拟编码方法 / Mock encode method
        mock_tokenizer.encode.return_value = [1, 2, 3]

        # 模拟tokenizer批量编码调用 / Mock tokenizer batch encoding call
        def tokenizer_side_effect(texts, **kwargs):
            # 返回包含input_ids的字典，每个文本对应一个ID列表
            # Return dict with input_ids, one ID list per text
            return {'input_ids': [[1, 2, 3]] * len(texts)}
        mock_tokenizer.side_effect = tokenizer_side_effect

        # === 模拟模型行为 === / === Mock model behavior ===

        # 模拟模型返回logits（形状：[batch_size, seq_len, vocab_size]）
        # Mock model to return logits (shape: [batch_size, seq_len, vocab_size])
        # vocab_size需要>=3以覆盖ID 0, 1, 2 / vocab_size needs to be >=3 to cover IDs 0, 1, 2
        mock_logits = torch.randn(1, 3, 10)
        mock_model.return_value.logits = mock_logits
        # 使用side_effect每次返回新的迭代器 / Use side_effect to return new iterator each time
        mock_model.parameters.side_effect = lambda: iter([MagicMock(device=MagicMock(type='cpu'))])

        # 设置加载模型的返回值 / Set load_model return value
        mock_load_model.return_value = (mock_tokenizer, mock_model)

        # === 注入预计算的token ID === / === Inject pre-computed token IDs ===
        # 因为我们模拟了加载函数，需要手动设置这些全局变量
        # Since we mocked load function, need to manually set these globals
        embedding_manager.RERANKER_FALSE_ID = 1
        embedding_manager.RERANKER_TRUE_ID = 2

        # === 准备测试数据 === / === Prepare test data ===
        query = "test query"  # 查询文本 / Query text
        candidates = ["doc1", "doc2"]  # 候选文档 / Candidate documents

        # === 第一次调用：应该未命中缓存 === / === First call: should miss cache ===
        print("First call to rerank...")
        results1 = embedding_manager.rerank_candidates_with_qwen3(query, candidates)

        # 获取缓存统计信息 / Get cache statistics
        cache = cache_manager.get_cache("reranking")
        print(f"Cache hits after first call: {cache.metrics.hits}")
        print(f"Cache misses after first call: {cache.metrics.misses}")

        # 断言：第一次调用应该没有命中 / Assertion: First call should have 0 hits
        self.assertEqual(cache.metrics.hits, 0)
        # 断言：第一次调用应该有1次未命中 / Assertion: First call should have 1 miss
        self.assertEqual(cache.metrics.misses, 1)

        # === 第二次调用：相同输入，应该命中缓存 === / === Second call: same inputs, should hit cache ===
        print("Second call to rerank (same inputs)...")
        results2 = embedding_manager.rerank_candidates_with_qwen3(query, candidates)

        print(f"Cache hits after second call: {cache.metrics.hits}")
        print(f"Cache misses after second call: {cache.metrics.misses}")

        # 断言：第二次调用应该有1次命中 / Assertion: Second call should have 1 hit
        self.assertEqual(cache.metrics.hits, 1)
        # 断言：未命中次数保持为1 / Assertion: Misses should remain 1
        self.assertEqual(cache.metrics.misses, 1)
        # 断言：两次结果应该相同 / Assertion: Both results should be identical
        self.assertEqual(results1, results2)

        # === 第三次调用：不同输入，应该未命中缓存 === / === Third call: different inputs, should miss cache ===
        print("Third call to rerank (different inputs)...")
        results3 = embedding_manager.rerank_candidates_with_qwen3(query, ["doc3"])

        print(f"Cache hits after third call: {cache.metrics.hits}")
        print(f"Cache misses after third call: {cache.metrics.misses}")

        # 断言：命中次数保持为1 / Assertion: Hits should remain 1
        self.assertEqual(cache.metrics.hits, 1)
        # 断言：未命中次数应该增加到2 / Assertion: Misses should increase to 2
        self.assertEqual(cache.metrics.misses, 2)

if __name__ == '__main__':
    # 运行单元测试 / Run unit tests
    unittest.main()

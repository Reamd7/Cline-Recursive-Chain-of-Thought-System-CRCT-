# utils/batch_processor.py
# 批处理器工具模块 - Batch Processor Utility Module

"""
Utility module for parallel batch processing.
Provides efficient parallel execution of tasks with adaptive batch sizing.

批量并行处理的实用工具模块
提供具有自适应批量大小的高效并行任务执行
"""

# ==================== 导入依赖模块 - Import Dependencies ====================
import functools  # 函数工具库，用于传递关键字参数 - Function tools for passing kwargs
import logging  # 日志记录模块 - Logging module
import os  # 操作系统接口模块 - OS interface module
import time  # 时间处理模块 - Time handling module
from concurrent.futures import ThreadPoolExecutor, as_completed  # 线程池执行器和任务完成迭代器 - Thread pool executor and task completion iterator
from typing import Any, Callable, Dict, List, Optional, TypeVar  # 类型提示 - Type hints

# 注释：移除了缓存导入，因为缓存批处理本身很复杂且通常不需要
# Removed cache import as caching batch processing itself is complex and often not desired
# from cline_utils.dependency_system.utils.cache_manager import cached

from cline_utils.dependency_system.utils.phase_tracker import PhaseTracker  # 阶段进度跟踪器 - Phase progress tracker

# ==================== 日志和类型变量配置 - Logger and Type Variable Configuration ====================
logger = logging.getLogger(__name__)  # 获取当前模块的日志记录器 - Get logger for current module

# 类型变量 - Type variables for generic typing
T = TypeVar("T")  # 输入项目的泛型类型 - Generic type for input items
R = TypeVar("R")  # 处理结果的泛型类型 - Generic type for processing results


# ==================== BatchProcessor 批处理器类 ====================
class BatchProcessor:
    """
    Generic batch processor for parallel execution of tasks.
    通用批处理器，用于并行执行任务
    """

    def __init__(
        self,
        max_workers: Optional[int] = None,  # 最大工作线程数 - Maximum worker threads
        batch_size: Optional[int] = None,  # 批次大小 - Batch size
        show_progress: bool = True,  # 是否显示进度 - Whether to show progress
        phase_name: str = "Processing",  # 阶段名称 - Phase name
    ):
        """
        Initialize the batch processor.
        初始化批处理器

        Args:
            max_workers: Maximum number of worker threads (defaults to CPU count * 4, capped at 64)
                        最大工作线程数（默认为CPU数*4，上限64）
            batch_size: Size of batches to process (defaults to adaptive sizing)
                       批次处理大小（默认为自适应大小）
            show_progress: Whether to show progress information (prints to stdout)
                          是否显示进度信息（输出到标准输出）
            phase_name: Name of the phase for the progress tracker
                       进度跟踪器的阶段名称
        """
        # ========== 步骤1: 计算CPU核心数 - Calculate CPU Core Count ==========
        cpu_count = os.cpu_count() or 8  # 获取CPU核心数，如果失败则默认为8 - Get CPU count, default to 8 if fails

        # ========== 步骤2: 计算默认工作线程数 - Calculate Default Worker Count ==========
        # 增加并行度：默认使用4倍CPU数，上限为48以避免线程失控
        # Increase parallelism: use 4x CPUs by default, cap at 48 to avoid runaway threads
        default_workers = min(4, (cpu_count * 4))  # 默认工作线程数 = min(4, CPU数*4) - Default workers = min(4, CPU*4)

        # ========== 步骤3: 设置最大工作线程数（确保至少为1）- Set max_workers (ensure at least 1) ==========
        self.max_workers = max(1, max_workers or default_workers)  # 确保max_workers至少为1 - Ensure max_workers is at least 1

        # ========== 步骤4: 初始化实例变量 - Initialize Instance Variables ==========
        self.batch_size = batch_size  # 批次大小（可选，None表示自适应） - Batch size (optional, None means adaptive)
        self.show_progress = show_progress  # 是否显示进度 - Whether to show progress
        self.phase_name = phase_name  # 阶段名称 - Phase name
        self.total_items = 0  # 总项目数 - Total items count
        self.processed_items = 0  # 已处理项目数 - Processed items count
        self.start_time = 0.0  # 开始时间戳 - Start time timestamp

    # <<< MODIFIED: Accept **kwargs >>>
    def process_items(
        self, items: List[T], processor_func: Callable[..., R], **kwargs: Any
    ) -> List[Optional[R]]:
        """
        Process a list of items in parallel batches.
        Extra keyword arguments (**kwargs) are passed directly to the processor_func.

        Args:
            items: List of items to process
            processor_func: Function to process each item (can accept kwargs)
            **kwargs: Additional keyword arguments to pass to processor_func
        Returns:
            List of results from processing each item (order matches input items)
        """
        if not callable(processor_func):
            logger.error("processor_func must be callable")
            raise TypeError("processor_func must be a callable")  # Use TypeError

        self.total_items = len(items)
        if not self.total_items:
            logger.info("No items to process")
            return []

        self.processed_items = 0
        self.start_time = time.time()

        actual_batch_size = self._determine_batch_size()
        logger.debug(
            f"Processing {self.total_items} items with batch size: {actual_batch_size}, workers: {self.max_workers}"
        )

        # Create a results list pre-filled with None to maintain order
        results: List[Optional[R]] = [None] * self.total_items
        items_processed_in_batches = 0

        # Use PhaseTracker if progress is enabled
        self.tracker = None
        context_manager = PhaseTracker(total=self.total_items, phase_name=self.phase_name) if self.show_progress else None
        
        if context_manager:
            with context_manager as tracker:
                self.tracker = tracker
                for i in range(0, self.total_items, actual_batch_size):
                    batch_indices = range(i, min(i + actual_batch_size, self.total_items))
                    batch_items = [items[idx] for idx in batch_indices]

                    if not batch_items:
                        continue

                    # Pass kwargs to the batch processing function
                    batch_results_map = self._process_batch(
                        batch_items, processor_func, **kwargs
                    )

                    # Place results back into the main list using original indices
                    for original_idx, result_value in batch_results_map.items():
                        global_index = i + original_idx
                        if 0 <= global_index < self.total_items:
                            results[global_index] = result_value
                        else:
                            logger.error(
                                f"Calculated invalid global index {global_index} from batch index {original_idx} (batch start {i})"
                            )

                    items_processed_in_batches += len(batch_items)
                    self.processed_items = items_processed_in_batches
                    tracker.update(len(batch_items))
        else:
             # No progress bar logic
             for i in range(0, self.total_items, actual_batch_size):
                batch_indices = range(i, min(i + actual_batch_size, self.total_items))
                batch_items = [items[idx] for idx in batch_indices]

                if not batch_items:
                    continue

                batch_results_map = self._process_batch(
                    batch_items, processor_func, **kwargs
                )

                for original_idx, result_value in batch_results_map.items():
                    global_index = i + original_idx
                    if 0 <= global_index < self.total_items:
                        results[global_index] = result_value
                    else:
                        logger.error(
                            f"Calculated invalid global index {global_index} from batch index {original_idx} (batch start {i})"
                        )
                
                items_processed_in_batches += len(batch_items)
                self.processed_items = items_processed_in_batches

        final_time = time.time() - self.start_time
        logger.debug(f"Processed {self.total_items} items in {final_time:.2f} seconds")
        
        # Filter out potential None values if errors occurred and weren't replaced
        # Or raise an error if None is found, depending on desired strictness
        final_results = [res for res in results if res is not None]
        if len(results) != self.total_items:
            logger.critical(
                f"Result list length ({len(results)}) does not match total items ({self.total_items}). This is an internal error."
            )

        if any(res is None for res in results):
            logger.warning(
                f"Some items failed processing ({len(results) - len(final_results)} errors). Results list contains only successful items."
            )

        # Make sure final newline is printed after progress bar
        if self.show_progress and self.total_items > 0:
            print()

        # Cast is needed because we pre-filled with None, but logic aims to replace all Nones
        return results

    # <<< MODIFIED: Accept **kwargs >>>
    def process_with_collector(
        self,
        items: List[T],
        processor_func: Callable[..., R],
        collector_func: Callable[[List[R]], Any],
        **kwargs: Any,
    ) -> Any:
        """
        Process items in batches and collect results with a collector function.
        Extra keyword arguments (**kwargs) are passed directly to the processor_func.

        Args:
            items: List of items to process
            processor_func: Function to process each item (can accept kwargs)
            collector_func: Function to collect and process ALL results at the end
            **kwargs: Additional keyword arguments to pass to processor_func
        Returns:
            Result from the collector function
        """
        # Use the modified process_items to get all results first
        all_results = self.process_items(items, processor_func, **kwargs)
        # Then pass the complete list of results to the collector
        logger.info("Calling collector function with all results...")
        return collector_func(all_results)

    def _determine_batch_size(self) -> int:
        """Determine adaptive batch size based on total items and workers."""
        if self.batch_size is not None:
            # If batch_size is explicitly set, use it (but ensure it's at least 1)
            return max(8, self.batch_size)

        # --- Adaptive sizing (more aggressive parallelism) ---
        if self.total_items == 0:
            return 8  # Handle edge case

        effective_workers = max(1, self.max_workers)

        # Favor smaller batches to keep more threads busy; minimum per worker now 8
        min_sensible_batch = 8
        if self.total_items < effective_workers * min_sensible_batch:
            min_batch = max(1, self.total_items // effective_workers)
        else:
            min_batch = min_sensible_batch

        # Increase target concurrency; aim for ~10-16 batches per worker
        target_batches_per_worker = 12
        denominator = max(4, effective_workers * target_batches_per_worker)
        calculated_batch_size = max(4, self.total_items // denominator)

        # Allow larger caps but still finite to avoid memory spikes
        max_sensible_batch = 256
        max_batch = min(self.total_items, max_sensible_batch)

        # Final batch size leaning smaller to increase utilization
        final_batch_size = min(max_batch, max(min_batch, calculated_batch_size))
        final_batch_size = max(16, final_batch_size)

        num_batches = (self.total_items + final_batch_size - 1) // final_batch_size
        logger.debug(
            f"Adaptive batch size: Total={self.total_items}, Workers={effective_workers}, "
            f"TargetBatches/Worker={target_batches_per_worker} => Calculated={calculated_batch_size}, "
            f"Min={min_batch}, Max={max_batch} -> Final={final_batch_size}, Batches={num_batches}"
        )
        return final_batch_size

    # <<< MODIFIED: Accept **kwargs and return Dict >>>
    def _process_batch(
        self, batch: List[T], processor_func: Callable[..., R], **kwargs: Any
    ) -> Dict[int, R]:
        """
        Process a single batch of items in parallel. Returns a dictionary mapping
        batch index to result to handle potential errors and maintain order linkage.

        Args:
            batch: Batch of items to process
            processor_func: Function to process each item (can accept kwargs)
            **kwargs: Additional keyword arguments to pass to processor_func
        Returns:
            Dictionary mapping batch index (0-based) to the result for that item.
            Items that failed processing will be missing from the dictionary.
        """
        if not batch:
            return {}

        batch_results_map: Dict[int, R] = {}
        # Wrap the processor_func to include kwargs using functools.partial
        # The executor will call partial_func(item)
        partial_func = functools.partial(processor_func, **kwargs)

        # Keep executor saturated; use full pool size (bounded by batch length)
        with ThreadPoolExecutor(
            max_workers=min(self.max_workers, max(1, len(batch)))
        ) as executor:
            # Map future to the index within the current batch
            future_to_idx = {
                executor.submit(partial_func, item): i for i, item in enumerate(batch)
            }

            for future in as_completed(future_to_idx):
                idx_in_batch = future_to_idx[future]
                item_info = batch[idx_in_batch]  # For logging errors
                try:
                    result = future.result()
                    batch_results_map[idx_in_batch] = result
                except Exception as e:
                    # Log the specific item that failed if possible
                    item_repr = repr(item_info)
                    if len(item_repr) > 100:
                        item_repr = item_repr[:100] + "..."
                    logger.error(
                        f"Error processing item (batch index {idx_in_batch}): {item_repr} -> {e}",
                        exc_info=True,
                    )  # Log with traceback
                    # Do not add to batch_results_map, indicating failure

        return batch_results_map

    def _show_progress(self) -> None:
        """Show progress information to stdout."""
        elapsed_time = time.time() - self.start_time
        if elapsed_time < 0.01:
            elapsed_time = 0.01  # Avoid division by zero

        items_per_second = self.processed_items / elapsed_time
        percent_complete = (
            self.processed_items / max(1, self.total_items)
        ) * 100  # Avoid division by zero total_items
        remaining_items = self.total_items - self.processed_items
        eta_seconds = remaining_items / items_per_second if items_per_second > 0 else 0

        # Format ETA nicely
        if eta_seconds > 3600:
            eta_str = f"{eta_seconds/3600:.1f}h"
        elif eta_seconds > 60:
            eta_str = f"{eta_seconds/60:.1f}m"
        else:
            eta_str = f"{eta_seconds:.1f}s"

        # Use a fixed width for progress numbers to prevent line jitter
        progress_str = (
            f"{self.processed_items:>{len(str(self.total_items))}}/{self.total_items}"
        )

        print(
            f"Progress: {progress_str} ({percent_complete:6.1f}%) | "
            f"{items_per_second:6.1f} items/s | "
            f"ETA: {eta_str:<6}",  # Left align ETA string in a fixed width
            end="\r",
            flush=True,  # Ensure it updates immediately
        )
        # No newline here, handled after the loop finishes


# --- Convenience Functions ---

# Caching these convenience functions is generally not recommended
# as the 'items' list can be large and hashing it is expensive/unreliable.


# <<< MODIFIED: Accept **kwargs >>>
def process_items(
    items: List[T],
    processor_func: Callable[..., R],
    max_workers: Optional[int] = None,
    batch_size: Optional[int] = None,
    show_progress: bool = True,
    phase_name: str = "Processing",
    **kwargs: Any,
) -> List[R]:
    """
    Convenience function to process items in parallel using BatchProcessor.
    Extra keyword arguments (**kwargs) are passed directly to the processor_func.
    """
    processor = BatchProcessor(max_workers, batch_size, show_progress, phase_name=phase_name)
    return processor.process_items(items, processor_func, **kwargs)


# <<< MODIFIED: Accept **kwargs >>>
def process_with_collector(
    items: List[T],
    processor_func: Callable[..., R],
    collector_func: Callable[[List[R]], Any],
    max_workers: Optional[int] = None,
    batch_size: Optional[int] = None,
    show_progress: bool = True,
    **kwargs: Any,
) -> Any:
    """
    Convenience function to process items and collect results using BatchProcessor.
    Extra keyword arguments (**kwargs) are passed directly to the processor_func.
    """
    processor = BatchProcessor(max_workers, batch_size, show_progress)
    # Note: process_items used internally will handle passing kwargs to processor_func
    return processor.process_with_collector(
        items, processor_func, collector_func, **kwargs
    )


# --- End of batch_processor.py ---

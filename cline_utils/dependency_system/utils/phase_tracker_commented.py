# cline_utils/dependency_system/utils/phase_tracker.py
# 阶段进度跟踪器模块 - Phase Progress Tracker Module

"""
A simple progress tracker that displays a progress bar, current task description,
and ETA in the terminal. Designed to be used as a context manager.

简单的进度跟踪器，在终端中显示进度条、当前任务描述和预计完成时间
设计为上下文管理器使用
"""

# ==================== 导入依赖模块 - Import Dependencies ====================
import sys  # 系统特定参数和函数 - System-specific parameters and functions
import time  # 时间访问和转换 - Time access and conversions
import shutil  # 高级文件操作 - High-level file operations
from typing import Optional  # 可选类型提示 - Optional type hint


# ==================== PhaseTracker 阶段跟踪器类 ====================
class PhaseTracker:
    """
    A simple progress tracker that displays a progress bar, current task description,
    and ETA in the terminal. Designed to be used as a context manager.

    简单的进度跟踪器，在终端中显示进度条、当前任务描述和预计完成时间（ETA）
    设计为上下文管理器使用

    使用示例 - Usage Example:
        with PhaseTracker(total=100, phase_name="Processing") as tracker:
            for item in items:
                tracker.update(1, description=f"Processing {item}")
    """

    def __init__(self, total: int, phase_name: str = "Processing", unit: str = "items"):
        """
        初始化阶段跟踪器 - Initialize phase tracker

        Args:
            total: 总项目数 - Total number of items to process
            phase_name: 阶段名称 - Name of the processing phase
            unit: 计数单位 - Unit of measurement for items
        """
        # ========== 步骤1: 保存基本配置参数 - Save Basic Configuration Parameters ==========
        self.total = total  # 总项目数 - Total items
        self.phase_name = phase_name  # 阶段名称（例如"Processing"） - Phase name (e.g., "Processing")
        self.unit = unit  # 项目单位（例如"items", "files"） - Unit of items (e.g., "items", "files")

        # ========== 步骤2: 初始化进度跟踪变量 - Initialize Progress Tracking Variables ==========
        self.current = 0  # 当前已完成项目数 - Current number of completed items
        self.start_time = 0.0  # 开始时间戳（秒） - Start time timestamp (seconds)
        self.last_update_time = 0.0  # 上次更新时间戳 - Last update time timestamp
        self.description = ""  # 当前任务描述 - Current task description

        # ========== 步骤3: 检查终端环境 - Check Terminal Environment ==========
        self._check_tty()  # 检查是否在TTY终端中运行 - Check if running in a TTY terminal

    def _check_tty(self):
        """
        检查是否在TTY终端中运行 - Check if we are running in a TTY

        TTY（TeleTYpewriter）：交互式终端
        非TTY环境（如文件重定向或管道）不支持动态进度条
        """
        # ========== 步骤1: 检测TTY状态 - Detect TTY Status ==========
        self.is_tty = sys.stdout.isatty()  # 检查标准输出是否连接到终端 - Check if stdout is connected to a terminal

        # ========== 步骤2: 设置默认终端宽度 - Set Default Terminal Width ==========
        self.term_width = 80  # 默认终端宽度（字符数） - Default terminal width (characters)

        # ========== 步骤3: 获取实际终端宽度（如果在TTY中）- Get Actual Terminal Width (if in TTY) ==========
        if self.is_tty:
            try:
                # 尝试获取实际终端尺寸 - Try to get actual terminal size
                # get_terminal_size返回(columns, lines)元组 - Returns (columns, lines) tuple
                self.term_width = shutil.get_terminal_size((80, 20)).columns  # 获取列数，默认(80列, 20行) - Get columns, default (80 cols, 20 rows)
            except Exception:
                # 如果获取失败，使用默认值 - If fails, use default value
                pass  # 保持默认值80 - Keep default value 80

    def __enter__(self):
        """
        上下文管理器入口方法 - Context manager entry method

        在'with'语句开始时调用 - Called at the start of 'with' statement

        Returns:
            self: 返回自身以便在with块中使用 - Return self for use in with block
        """
        # ========== 步骤1: 记录开始时间 - Record Start Time ==========
        self.start_time = time.time()  # 记录当前时间戳作为开始时间 - Record current timestamp as start time
        self.last_update_time = self.start_time  # 初始化上次更新时间 - Initialize last update time

        # ========== 步骤2: 打印初始进度 - Print Initial Progress ==========
        self._print_progress()  # 显示初始进度状态（0%） - Show initial progress state (0%)

        # ========== 步骤3: 返回自身 - Return Self ==========
        return self  # 返回tracker对象供with块使用 - Return tracker object for use in with block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        上下文管理器退出方法 - Context manager exit method

        在'with'语句结束时调用 - Called at the end of 'with' statement

        Args:
            exc_type: 异常类型（如果有） - Exception type (if any)
            exc_val: 异常值（如果有） - Exception value (if any)
            exc_tb: 异常回溯（如果有） - Exception traceback (if any)
        """
        # ========== 步骤1: 确保打印最终换行符 - Ensure Final Newline is Printed ==========
        if self.is_tty:
            # 打印换行符，使光标移到下一行 - Print newline to move cursor to next line
            sys.stdout.write("\n")  # 写入换行符 - Write newline character
            sys.stdout.flush()  # 刷新输出缓冲区 - Flush output buffer

        # ========== 步骤2: 处理异常（如果有）- Handle Exception (if any) ==========
        if exc_type:
            # 如果发生异常，可以在这里记录日志或处理 - If exception occurred, can log or handle here
            pass  # 让异常正常传播 - Let exception propagate normally

    def update(self, n: int = 1, description: Optional[str] = None):
        """
        更新进度 - Update progress

        Args:
            n: 增加的项目数（默认1） - Number of items to increment (default 1)
            description: 可选的任务描述 - Optional task description
        """
        # ========== 步骤1: 增加当前计数 - Increment Current Count ==========
        self.current += n  # 增加已完成项目数 - Increment completed items count

        # ========== 步骤2: 更新描述（如果提供）- Update Description (if provided) ==========
        if description is not None:
            self.description = description  # 更新当前任务描述 - Update current task description

        # ========== 步骤3: 刷新进度显示 - Refresh Progress Display ==========
        self._print_progress()  # 重新渲染进度条 - Re-render progress bar

    def set_description(self, description: str):
        """
        更新任务描述而不增加进度 - Update task description without incrementing progress

        Args:
            description: 新的任务描述 - New task description
        """
        # ========== 步骤1: 更新描述 - Update Description ==========
        self.description = description  # 设置新的描述文本 - Set new description text

        # ========== 步骤2: 刷新显示 - Refresh Display ==========
        self._print_progress()  # 重新渲染进度条以显示新描述 - Re-render progress bar to show new description

    def set_total(self, total: int):
        """
        更新总项目数 - Update total count

        当总数在处理过程中动态变化时使用 - Use when total changes dynamically during processing

        Args:
            total: 新的总项目数 - New total count
        """
        # ========== 步骤1: 更新总数 - Update Total ==========
        self.total = total  # 设置新的总项目数 - Set new total count

        # ========== 步骤2: 刷新显示 - Refresh Display ==========
        self._print_progress()  # 重新渲染进度条以反映新总数 - Re-render progress bar to reflect new total

    def _format_time(self, seconds: float) -> str:
        """
        格式化时间为可读格式 - Format seconds into readable format

        转换规则 - Conversion Rules:
        - < 60秒: 显示为"Xs" - Display as "Xs"
        - 60秒-1小时: 显示为"MM:SS" - Display as "MM:SS"
        - >= 1小时: 显示为"HH:MM:SS" - Display as "HH:MM:SS"

        Args:
            seconds: 秒数（浮点数） - Number of seconds (float)

        Returns:
            str: 格式化的时间字符串 - Formatted time string
        """
        # ========== 情况1: 小于60秒 - Case 1: Less than 60 seconds ==========
        if seconds < 60:
            return f"{int(seconds)}s"  # 返回"Xs"格式 - Return "Xs" format

        # ========== 情况2: 60秒到1小时 - Case 2: 60 seconds to 1 hour ==========
        minutes = int(seconds // 60)  # 计算完整分钟数 - Calculate complete minutes
        seconds = int(seconds % 60)  # 计算剩余秒数 - Calculate remaining seconds

        if minutes < 60:
            return f"{minutes:02d}:{seconds:02d}"  # 返回"MM:SS"格式 - Return "MM:SS" format

        # ========== 情况3: 1小时或更多 - Case 3: 1 hour or more ==========
        hours = int(minutes // 60)  # 计算小时数 - Calculate hours
        minutes = int(minutes % 60)  # 重新计算剩余分钟数 - Recalculate remaining minutes
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"  # 返回"HH:MM:SS"格式 - Return "HH:MM:SS" format

    def _print_progress(self):
        """
        将进度条渲染到标准输出 - Render the progress bar to stdout

        处理两种模式 - Handles two modes:
        1. TTY模式: 动态进度条 - Dynamic progress bar
        2. 非TTY模式: 定期日志输出 - Periodic log output
        """
        # ==================== 非TTY模式处理 - Non-TTY Mode Handling ====================
        if not self.is_tty:
            # 在非TTY环境（如文件重定向）中，定期打印进度日志
            # In non-TTY environment (like file redirection), periodically print progress logs
            if self.total > 0:
                # 计算完成百分比 - Calculate completion percentage
                percent = (self.current / self.total) * 100  # 百分比 = (当前/总数) * 100

                # 只在特定间隔打印（避免输出过多） - Only print at specific intervals (avoid too much output)
                # 打印条件: 完成 或 每20%打印一次 - Print conditions: completed or every 20%
                if self.current == self.total or self.current % max(1, self.total // 5) == 0:
                     print(f"[{self.phase_name}] {self.current}/{self.total} ({percent:.1f}%) - {self.description}")
            return  # 非TTY模式处理完毕，直接返回 - Non-TTY mode done, return

        # ==================== TTY模式动态进度条 - TTY Mode Dynamic Progress Bar ====================

        # ========== 步骤1: 计算时间相关信息 - Calculate Time-related Information ==========
        now = time.time()  # 当前时间戳 - Current timestamp
        elapsed = now - self.start_time  # 已经过时间（秒） - Elapsed time (seconds)

        # ========== 步骤2: 计算完成百分比 - Calculate Completion Percentage ==========
        percent = 0.0  # 初始化百分比 - Initialize percentage
        if self.total > 0:
            # 计算百分比，并确保不超过100% - Calculate percentage, ensure not over 100%
            percent = min(100.0, (self.current / self.total) * 100.0)

        # ========== 步骤3: 计算预计剩余时间（ETA）- Calculate Estimated Time of Arrival (ETA) ==========
        eta_str = "??"  # 默认ETA字符串（未知） - Default ETA string (unknown)
        if self.current > 0 and self.total > 0:
            # 计算处理速率（项目/秒） - Calculate processing rate (items/second)
            rate = self.current / elapsed if elapsed > 0 else 0  # 速率 = 已完成项目数 / 已用时间

            if rate > 0:
                # 计算剩余项目数 - Calculate remaining items
                remaining_items = self.total - self.current  # 剩余项目 = 总数 - 当前数

                # 计算预计剩余秒数 - Calculate estimated remaining seconds
                eta_seconds = remaining_items / rate  # ETA(秒) = 剩余项目 / 速率

                # 格式化ETA字符串 - Format ETA string
                eta_str = self._format_time(eta_seconds)  # 使用时间格式化函数 - Use time formatting function

        # ========== 步骤4: 构建进度条组件 - Build Progress Bar Components ==========
        # 前缀: [阶段名称] - Prefix: [Phase Name]
        prefix = f"[{self.phase_name}] "  # 例如: "[Processing] " - e.g., "[Processing] "

        # 后缀: 百分比 | ETA - Suffix: Percentage | ETA
        suffix = f" {percent:5.1f}% | ETA: {eta_str}"  # 例如: " 75.3% | ETA: 02:15" - e.g., " 75.3% | ETA: 02:15"

        # ========== 步骤5: 处理描述文本（截断过长文本）- Handle Description Text (Truncate if too long) ==========
        # 预留空间计算 - Reserved space calculation
        reserved_width = len(prefix) + len(suffix) + 15  # +15 用于进度条和间隔 - +15 for progress bar and spacing

        # 可用于描述的空间 - Available space for description
        available_for_desc = max(10, self.term_width - reserved_width - 20)  # -20 用于进度条长度 - -20 for bar length

        # 构建描述字符串 - Build description string
        desc_str = ""  # 初始化描述字符串 - Initialize description string
        if self.description:
            desc_str = f" | {self.description}"  # 添加描述前缀 - Add description prefix

            # 如果描述过长，截断并添加省略号 - If description too long, truncate and add ellipsis
            if len(desc_str) > available_for_desc:
                desc_str = desc_str[:available_for_desc-3] + "..."  # 截断并添加"..." - Truncate and add "..."

        # ========== 步骤6: 计算进度条宽度 - Calculate Progress Bar Width ==========
        # 进度条宽度 = 终端宽度 - 前缀 - 后缀 - 描述 - 3(用于括号和空格)
        # Bar width = Terminal width - Prefix - Suffix - Description - 3(for brackets and spaces)
        bar_width = self.term_width - len(prefix) - len(suffix) - len(desc_str) - 3
        bar_width = max(5, bar_width)  # 确保进度条至少5个字符宽 - Ensure bar is at least 5 characters wide

        # ========== 步骤7: 生成进度条可视化 - Generate Progress Bar Visualization ==========
        # 计算填充长度 - Calculate filled length
        filled_length = int(bar_width * percent / 100.0)  # 填充长度 = 进度条宽度 * 百分比 / 100

        # 生成进度条字符串 - Generate progress bar string
        # 格式: "========----" (=表示完成，-表示未完成) - Format: "========----" (= for completed, - for incomplete)
        bar = "=" * filled_length + "-" * (bar_width - filled_length)

        # ========== 步骤8: 组装完整的进度行 - Assemble Complete Progress Line ==========
        # 格式: \r[Phase] [========----] 75.3% | ETA: 02:15 | Current task...
        line = f"\r{prefix}[{bar}]{suffix}{desc_str}"  # \r: 回车符，覆盖当前行 - \r: Carriage return, overwrite current line

        # ========== 步骤9: 填充空格以覆盖之前的输出 - Pad with Spaces to Overwrite Previous Output ==========
        if len(line) < self.term_width:
            # 如果新行比之前短，用空格填充以清除旧内容 - If new line is shorter, pad with spaces to clear old content
            line += " " * (self.term_width - len(line))

        # ========== 步骤10: 输出进度行到终端 - Output Progress Line to Terminal ==========
        sys.stdout.write(line)  # 写入进度行 - Write progress line
        sys.stdout.flush()  # 立即刷新输出（不等待换行） - Immediately flush output (don't wait for newline)

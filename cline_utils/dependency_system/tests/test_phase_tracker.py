"""
测试模块：阶段跟踪器测试
Test Module: Phase Tracker Tests

本模块测试PhaseTracker类的功能，包括：
- 初始化和属性设置
- 进度更新和显示
- 上下文管理器功能
- 时间格式化
- TTY和非TTY环境下的输出
- ETA（预计完成时间）计算

This module tests PhaseTracker class functionality, including:
- Initialization and attribute setting
- Progress update and display
- Context manager functionality
- Time formatting
- Output in TTY and non-TTY environments
- ETA (Estimated Time of Arrival) calculation
"""

# 导入pytest测试框架 / Import pytest testing framework
import pytest
# 导入系统模块用于访问sys.stdout / Import sys module for sys.stdout access
import sys
# 导入时间模块用于时间操作 / Import time module for time operations
import time
# 导入操作系统模块（用于terminal_size） / Import os module (for terminal_size)
import os
# 导入unittest.mock模拟工具 / Import unittest.mock tools
from unittest.mock import MagicMock, patch
# 导入StringIO用于捕获标准输出 / Import StringIO to capture stdout
from io import StringIO

# 导入被测试的PhaseTracker类 / Import PhaseTracker class to be tested
from cline_utils.dependency_system.utils.phase_tracker import PhaseTracker

class TestPhaseTracker:
    """
    测试类：PhaseTracker功能测试
    Test Class: PhaseTracker Functionality Tests

    测试进度跟踪器的各种功能，包括进度显示、时间估算、
    上下文管理等。
    """

    def test_init(self):
        """
        测试用例：验证初始化
        Test Case: Verify Initialization

        目的：确保PhaseTracker正确初始化所有属性
        Purpose: Ensure PhaseTracker correctly initializes all attributes
        """
        # 创建PhaseTracker实例，总数为100，阶段名称为"TestPhase"
        # Create PhaseTracker instance with total=100, phase_name="TestPhase"
        tracker = PhaseTracker(total=100, phase_name="TestPhase")

        # 断言：验证总数正确设置 / Assertion: Verify total is set correctly
        assert tracker.total == 100
        # 断言：验证阶段名称正确设置 / Assertion: Verify phase name is set correctly
        assert tracker.phase_name == "TestPhase"
        # 断言：验证当前进度初始化为0 / Assertion: Verify current progress initialized to 0
        assert tracker.current == 0
        # 断言：验证描述初始化为空字符串 / Assertion: Verify description initialized to empty string
        assert tracker.description == ""

    def test_format_time(self):
        """
        测试用例：验证时间格式化
        Test Case: Verify Time Formatting

        目的：测试_format_time方法能否正确格式化秒数为可读时间
        Purpose: Test if _format_time method correctly formats seconds to readable time
        """
        # 创建PhaseTracker实例 / Create PhaseTracker instance
        tracker = PhaseTracker(100)

        # 测试秒数格式化（30秒 -> "30s"）/ Test seconds formatting (30s -> "30s")
        assert tracker._format_time(30) == "30s"
        # 测试分秒格式化（65秒 -> "01:05"）/ Test minutes:seconds formatting (65s -> "01:05")
        assert tracker._format_time(65) == "01:05"
        # 测试时分秒格式化（3665秒 -> "01:01:05"）/ Test hours:minutes:seconds formatting
        assert tracker._format_time(3665) == "01:01:05"

    def test_context_manager(self):
        """
        测试用例：验证上下文管理器
        Test Case: Verify Context Manager

        目的：测试PhaseTracker作为上下文管理器的功能
        Purpose: Test PhaseTracker functionality as context manager
        """
        # 模拟sys.stdout以捕获输出 / Mock sys.stdout to capture output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # 使用with语句创建PhaseTracker上下文 / Use with statement to create PhaseTracker context
            with PhaseTracker(100) as tracker:
                # 断言：验证开始时间已设置（大于0）/ Assertion: Verify start_time is set (> 0)
                assert tracker.start_time > 0
                # 断言：验证最后更新时间等于开始时间 / Assertion: Verify last update time equals start time
                assert tracker.last_update_time == tracker.start_time

            # 注意：退出时会打印换行符（在TTY模式下）
            # Note: Newline is printed on exit (in TTY mode)
            # StringIO.isatty()默认返回False，需要打补丁来测试TTY行为
            # StringIO.isatty() returns False by default, patching needed to test TTY behavior

    def test_update(self):
        """
        测试用例：验证进度更新
        Test Case: Verify Progress Update

        目的：测试update方法能否正确更新进度和描述
        Purpose: Test if update method correctly updates progress and description
        """
        # 创建PhaseTracker实例 / Create PhaseTracker instance
        tracker = PhaseTracker(100)
        # 模拟_print_progress方法 / Mock _print_progress method
        tracker._print_progress = MagicMock()

        # 调用update方法，将进度更新到10，描述为"Processing items"
        # Call update method, update progress to 10, description to "Processing items"
        tracker.update(10, "Processing items")

        # 断言：验证当前进度更新为10 / Assertion: Verify current progress updated to 10
        assert tracker.current == 10
        # 断言：验证描述更新为"Processing items" / Assertion: Verify description updated
        assert tracker.description == "Processing items"
        # 断言：验证_print_progress被调用 / Assertion: Verify _print_progress was called
        tracker._print_progress.assert_called()

    def test_set_description(self):
        """
        测试用例：验证设置描述
        Test Case: Verify Set Description

        目的：测试set_description方法能否正确更新描述并触发输出
        Purpose: Test if set_description correctly updates description and triggers output
        """
        # 创建PhaseTracker实例 / Create PhaseTracker instance
        tracker = PhaseTracker(100)
        # 模拟_print_progress方法 / Mock _print_progress method
        tracker._print_progress = MagicMock()

        # 调用set_description方法 / Call set_description method
        tracker.set_description("New description")

        # 断言：验证描述已更新 / Assertion: Verify description is updated
        assert tracker.description == "New description"
        # 断言：验证_print_progress被调用 / Assertion: Verify _print_progress was called
        tracker._print_progress.assert_called()

    def test_set_total(self):
        """
        测试用例：验证设置总数
        Test Case: Verify Set Total

        目的：测试set_total方法能否正确更新总数并触发输出
        Purpose: Test if set_total correctly updates total and triggers output
        """
        # 创建PhaseTracker实例 / Create PhaseTracker instance
        tracker = PhaseTracker(100)
        # 模拟_print_progress方法 / Mock _print_progress method
        tracker._print_progress = MagicMock()

        # 调用set_total方法，将总数更新为200 / Call set_total, update total to 200
        tracker.set_total(200)

        # 断言：验证总数已更新为200 / Assertion: Verify total is updated to 200
        assert tracker.total == 200
        # 断言：验证_print_progress被调用 / Assertion: Verify _print_progress was called
        tracker._print_progress.assert_called()

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_progress_non_tty(self, mock_stdout):
        """
        测试用例：验证非TTY环境下的进度打印
        Test Case: Verify Progress Printing in Non-TTY Environment

        目的：测试在非终端环境下进度信息的输出格式
        Purpose: Test progress output format in non-terminal environment
        """
        # 模拟isatty返回False（非终端环境）/ Mock isatty to return False (non-terminal)
        with patch("sys.stdout.isatty", return_value=False):
            # 创建PhaseTracker实例 / Create PhaseTracker instance
            tracker = PhaseTracker(100, phase_name="Test")
            # 显式设置is_tty为False / Explicitly set is_tty to False
            tracker.is_tty = False

            # 更新进度到20，描述为"Step 1" / Update progress to 20, description "Step 1"
            tracker.update(20, "Step 1")

            # 获取捕获的输出 / Get captured output
            output = mock_stdout.getvalue()
            # 断言：验证输出包含正确的进度信息格式
            # Assertion: Verify output contains correct progress format
            assert "[Test] 20/100 (20.0%) - Step 1" in output

    @patch("sys.stdout", new_callable=StringIO)
    def test_print_progress_tty(self, mock_stdout):
        """
        测试用例：验证TTY环境下的进度打印
        Test Case: Verify Progress Printing in TTY Environment

        目的：测试在终端环境下进度信息的输出格式和ETA显示
        Purpose: Test progress output format and ETA display in terminal environment
        """
        # 模拟isatty返回True（终端环境）/ Mock isatty to return True (terminal)
        with patch("sys.stdout.isatty", return_value=True):
            # 模拟终端大小为100列x20行 / Mock terminal size to 100 columns x 20 rows
            with patch("shutil.get_terminal_size", return_value=os.terminal_size((100, 20))):
                # 创建PhaseTracker实例 / Create PhaseTracker instance
                tracker = PhaseTracker(100, phase_name="Test")
                # 设置is_tty为True / Set is_tty to True
                tracker.is_tty = True
                # 设置开始时间为10秒前（模拟已运行10秒）
                # Set start time to 10 seconds ago (simulate 10 seconds elapsed)
                tracker.start_time = time.time() - 10

                # 更新进度到50（一半），描述为"Halfway"
                # Update progress to 50 (halfway), description "Halfway"
                tracker.update(50, "Halfway")

                # 获取捕获的输出 / Get captured output
                output = mock_stdout.getvalue()

                # === 验证输出包含关键组件 === / === Verify output contains key components ===
                # 断言：包含回车符和阶段名称 / Assertion: Contains carriage return and phase name
                assert "\r[Test]" in output
                # 断言：包含百分比（50.0%）/ Assertion: Contains percentage (50.0%)
                assert "50.0%" in output
                # 断言：包含描述信息 / Assertion: Contains description
                assert "Halfway" in output
                # 断言：包含ETA（预计完成时间）/ Assertion: Contains ETA
                assert "ETA:" in output

    def test_eta_calculation(self):
        """
        测试用例：验证ETA计算
        Test Case: Verify ETA Calculation

        目的：测试预计完成时间（ETA）的计算是否准确
        Purpose: Test if Estimated Time of Arrival (ETA) calculation is accurate

        测试逻辑：
        - 已运行10秒，完成50个项目
        - 速率 = 5项/秒
        - 剩余50个项目
        - 预计还需10秒

        Test logic:
        - 10 seconds elapsed, 50 items done
        - Rate = 5 items/sec
        - 50 items remaining
        - ETA should be 10 seconds
        """
        # 创建PhaseTracker实例 / Create PhaseTracker instance
        tracker = PhaseTracker(100)
        # 设置开始时间为10秒前 / Set start time to 10 seconds ago
        tracker.start_time = time.time() - 10
        # 设置当前进度为50（已完成一半）/ Set current progress to 50 (halfway done)
        tracker.current = 50

        # 注意：无法直接访问内部变量eta_str，需要通过捕获输出来验证
        # Note: Can't directly access internal variable eta_str, need to verify via output

        # 捕获标准输出 / Capture stdout
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            # 设置为TTY模式以显示ETA / Set to TTY mode to display ETA
            tracker.is_tty = True
            # 设置终端宽度 / Set terminal width
            tracker.term_width = 100
            # 调用_print_progress触发ETA计算和显示 / Call _print_progress to trigger ETA calculation
            tracker._print_progress()

            # 获取输出 / Get output
            output = mock_stdout.getvalue()
            # 断言：验证输出包含ETA约为10秒（允许轻微的时间偏移）
            # Assertion: Verify output contains ETA of about 10 seconds (allow slight drift)
            assert "ETA: 10s" in output or "ETA: 09s" in output or "ETA: 11s" in output

# ========================================
# 代码分析报告生成器 (Code Analysis Report Generator)
# ========================================
"""
代码质量分析工具 - 检测未完成和不当的实现

该脚本会扫描代码库，识别以下问题：
1. 未完成的实现（TODO、FIXME、pass语句、NotImplementedError等）
2. 不当的实现（空函数、空类等）
3. 未使用的代码项（通过pyright分析）

使用Tree-sitter进行精确的AST分析，回退到正则表达式作为备选方案。
"""

# ========================================
# 标准库导入
# ========================================
import json  # JSON数据处理
import os  # 操作系统接口
import re  # 正则表达式
import subprocess  # 子进程管理（运行pyright）
import sys  # 系统参数和函数
from pathlib import Path  # 面向对象的文件路径处理

# ========================================
# 步骤1: 配置Python导入路径
# ========================================
# 将项目根目录添加到sys.path，以便导入cline_utils模块
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # 获取项目根目录
if project_root not in sys.path:  # 检查是否已在路径中
    sys.path.insert(0, project_root)  # 插入到路径开头

# ========================================
# 内部模块导入
# ========================================
from cline_utils.dependency_system.utils import path_utils  # 路径工具函数
from cline_utils.dependency_system.utils.config_manager import ConfigManager  # 配置管理器

# ========================================
# 步骤2: 尝试导入Tree-sitter（AST解析器）
# ========================================
# Tree-sitter是一个增量解析库，可以为代码构建精确的语法树
try:
    import tree_sitter_javascript  # JavaScript解析器
    import tree_sitter_python  # Python解析器
    import tree_sitter_typescript  # TypeScript解析器
    from tree_sitter import Language, Parser  # 核心解析器类

    TREE_SITTER_AVAILABLE = True  # 标记tree-sitter可用
except ImportError:
    # 如果tree-sitter不可用，回退到正则表达式分析
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not available. Falling back to regex-based analysis.")

# ========================================
# 步骤3: 初始化配置管理器
# ========================================
config = ConfigManager()  # 创建配置管理器实例，用于读取项目配置

# ========================================
# 配置常量 (Configuration Constants)
# ========================================

# 要扫描的文件扩展名集合
EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".md", ".txt"}

# 正则表达式模式字典 - 用于检测代码中的问题标记
PATTERNS = {
    "TODO": re.compile(r"TODO", re.IGNORECASE),  # TODO标记（不区分大小写）
    "FIXME": re.compile(r"FIXME", re.IGNORECASE),  # FIXME标记（不区分大小写）
    "pass": re.compile(r"^\s*pass\s*$", re.MULTILINE),  # 独立的pass语句（更严格的检查）
    "NotImplementedError": re.compile(r"NotImplementedError"),  # 未实现错误
    "in a real": re.compile(r"in a real", re.IGNORECASE),  # 临时实现标记
    "for now": re.compile(r"for now", re.IGNORECASE),  # 临时实现标记
    "simplified": re.compile(r"simplified", re.IGNORECASE),  # 简化实现标记
    "placeholder": re.compile(r"placeholder", re.IGNORECASE),  # 占位符标记
}

# 输出文件路径
OUTPUT_FILE = "code_analysis/issues_report.md"  # 主报告文件
PYRIGHT_OUTPUT = "pyright_output.json"  # Pyright类型检查器的输出文件


# ========================================
# 核心函数 (Core Functions)
# ========================================

def get_parser(lang_name):
    """
    Get a tree-sitter parser for the specified language.

    获取指定语言的tree-sitter解析器。

    Tree-sitter是一个通用的解析器生成器工具和增量解析库。
    它可以为多种编程语言构建语法树（AST），用于精确的代码分析。

    Args:
        lang_name (str): 语言名称，可选值：
            - "python": Python语言
            - "javascript": JavaScript语言
            - "typescript": TypeScript语言
            - "tsx": TypeScript/JSX语言

    Returns:
        Parser | None: 配置好的解析器对象，如果失败则返回None
    """
    # 检查tree-sitter是否可用
    if not TREE_SITTER_AVAILABLE:
        return None  # tree-sitter不可用，返回None

    try:
        # ========================================
        # 步骤1: 创建解析器实例
        # ========================================
        parser = Parser()  # 创建通用解析器对象

        # ========================================
        # 步骤2: 根据语言名称配置对应的语言解析器
        # ========================================
        if lang_name == "python":
            # 设置Python语言解析器
            parser.language = Language(tree_sitter_python.language())
        elif lang_name == "javascript":
            # 设置JavaScript语言解析器
            parser.language = Language(tree_sitter_javascript.language())
        elif lang_name == "typescript":
            # 设置TypeScript语言解析器
            parser.language = Language(tree_sitter_typescript.language_typescript())
        elif lang_name == "tsx":
            # 设置TSX（TypeScript + JSX）语言解析器
            parser.language = Language(tree_sitter_typescript.language_tsx())
        else:
            # 不支持的语言
            return None

        return parser  # 返回配置好的解析器

    except Exception as e:
        # 捕获初始化过程中的任何异常
        print(f"Error initializing parser for {lang_name}: {e}")
        return None  # 初始化失败，返回None


def analyze_node(node, issues, filepath, source_code):
    """
    Recursively analyze tree-sitter nodes.

    递归分析tree-sitter节点，检测代码质量问题。

    该函数遍历抽象语法树（AST），检测以下问题：
    1. 空函数或仅包含pass/docstring的函数
    2. 抛出NotImplementedError的函数（未完成的实现）
    3. 空类或仅包含pass/docstring的类
    4. JavaScript/TypeScript中的空函数和类

    Args:
        node: Tree-sitter节点对象
        issues (list): 问题列表，用于收集发现的问题
        filepath: 文件路径
        source_code: 源代码字节串
    """

    # ========================================
    # Python语言检查
    # ========================================
    if node.type in ("function_definition", "async_function_definition"):
        # 检测函数定义（包括同步和异步函数）
        # ========================================
        # 步骤1: 获取函数体节点
        # ========================================
        body_node = node.child_by_field_name("body")  # 获取函数体
        if body_node:
            has_raise_not_implemented = False  # 标记是否有NotImplementedError

            # ========================================
            # 步骤2: 过滤掉琐碎的子节点
            # ========================================
            # 琐碎节点包括：注释、pass语句、文档字符串
            non_trivial_children = []  # 非琐碎子节点列表

            # 遍历函数体的所有子节点
            for child in body_node.children:
                # 跳过注释
                if child.type == "comment":
                    continue

                # 跳过pass语句
                if child.type == "pass_statement":
                    continue

                # 检查是否为文档字符串
                if child.type == "expression_statement":
                    # 文档字符串是一个只包含字符串字面量的表达式语句
                    if child.child_count == 1 and child.children[0].type == "string":
                        continue  # 跳过文档字符串

                # 检查是否为raise NotImplementedError语句
                if child.type == "raise_statement":
                    # 检查是否抛出NotImplementedError
                    if "NotImplementedError" in child.text.decode("utf8"):
                        has_raise_not_implemented = True  # 标记找到NotImplementedError
                        # 将此视为"琐碎"节点以查找其他实际代码
                        # 但稍后会特别标记此情况
                        continue

                # 这是一个非琐碎的子节点
                non_trivial_children.append(child)

            # ========================================
            # 步骤3: 检查是否有实质性代码
            # ========================================
            if not non_trivial_children:
                # 函数体中没有非琐碎的代码
                if has_raise_not_implemented:
                    # 函数只抛出NotImplementedError - 未完成的实现
                    issues.append(
                        {
                            "type": "Incomplete Implementation",  # 问题类型：未完成的实现
                            "subtype": "NotImplementedError",  # 子类型
                            "file": str(filepath),  # 文件路径
                            "line": node.start_point[0] + 1,  # 行号（从1开始）
                            "content": node.text.decode("utf8").split("\n")[0] + "...",  # 代码内容（第一行）
                        }
                    )
                else:
                    # 函数体为空或只有pass/docstring - 不当的实现
                    issues.append(
                        {
                            "type": "Improper Implementation",  # 问题类型：不当的实现
                            "subtype": "Empty/Stub Function",  # 子类型：空/桩函数
                            "file": str(filepath),
                            "line": node.start_point[0] + 1,
                            "content": node.text.decode("utf8").split("\n")[0] + "...",
                        }
                    )

    # ========================================
    # Python类定义检查
    # ========================================
    elif node.type == "class_definition":
        # 检测类定义
        # ========================================
        # 步骤1: 获取类体节点
        # ========================================
        body_node = node.child_by_field_name("body")  # 获取类体
        if body_node:
            # ========================================
            # 步骤2: 过滤掉琐碎的子节点
            # ========================================
            non_trivial_children = []  # 非琐碎子节点列表
            for child in body_node.children:
                # 跳过注释
                if child.type == "comment":
                    continue
                # 跳过pass语句
                if child.type == "pass_statement":
                    continue
                # 检查是否为文档字符串
                if child.type == "expression_statement":
                    # 文档字符串是一个只包含字符串字面量的表达式语句
                    if child.child_count == 1 and child.children[0].type == "string":
                        continue
                # 这是一个非琐碎的子节点
                non_trivial_children.append(child)

            # ========================================
            # 步骤3: 检查类是否为空
            # ========================================
            if not non_trivial_children:
                # 类体为空或只有pass/docstring
                issues.append(
                    {
                        "type": "Improper Implementation",  # 问题类型：不当的实现
                        "subtype": "Empty/Stub Class",  # 子类型：空/桩类
                        "file": str(filepath),
                        "line": node.start_point[0] + 1,
                        "content": node.text.decode("utf8").split("\n")[0] + "...",
                    }
                )

    # ========================================
    # JavaScript/TypeScript检查
    # ========================================
    elif node.type in (
        "function_declaration",  # 函数声明
        "method_definition",  # 方法定义
        "arrow_function",  # 箭头函数
        "class_declaration",  # 类声明
    ):
        # 获取函数或类的body节点
        body_node = node.child_by_field_name("body")
        if body_node and body_node.type == "statement_block":
            # ========================================
            # 检查语句块是否为空或只包含注释
            # ========================================
            # 过滤掉注释和花括号
            non_comment_children = [
                c for c in body_node.children if c.type not in ("comment", "{", "}")
            ]
            if not non_comment_children:
                # 代码块为空
                issues.append(
                    {
                        "type": "Improper Implementation",  # 问题类型：不当的实现
                        "subtype": "Empty/Stub Function/Class",  # 子类型：空函数/类
                        "file": str(filepath),
                        "line": node.start_point[0] + 1,
                        "content": node.text.decode("utf8").split("\n")[0] + "...",
                    }
                )

    # ========================================
    # 递归处理所有子节点
    # ========================================
    # 遍历当前节点的所有子节点，递归调用analyze_node
    for child in node.children:
        analyze_node(child, issues, filepath, source_code)


def scan_file(filepath):
    """
    Scan a single file for code quality issues.

    扫描单个文件以查找代码质量问题。

    该函数结合使用正则表达式和tree-sitter AST分析来检测：
    - TODO/FIXME标记
    - 空函数和类
    - 未实现的功能
    - 其他代码异味

    Args:
        filepath: 要扫描的文件路径

    Returns:
        list: 发现的问题列表，每个问题是一个字典，包含：
            - type: 问题类型
            - subtype: 子类型
            - file: 文件路径
            - line: 行号
            - content: 问题代码片段
    """
    issues = []  # 初始化问题列表

    try:
        # ========================================
        # 步骤1: 读取文件内容（二进制模式，用于tree-sitter）
        # ========================================
        with open(filepath, "rb") as f:  # 以二进制模式读取（tree-sitter需要）
            content = f.read()  # 读取文件内容

        # ========================================
        # 步骤2: 正则表达式扫描（始终运行）
        # ========================================
        # 用于检测注释和代码中的模式（TODO、FIXME等）
        try:
            # 将二进制内容解码为文本
            text_content = content.decode("utf-8", errors="ignore")  # 忽略解码错误
            lines = text_content.splitlines()  # 按行分割

            # 遍历每一行
            for i, line in enumerate(lines):
                # 检查每个预定义的模式
                for label, pattern in PATTERNS.items():
                    # ========================================
                    # 决定是否跳过某些模式
                    # ========================================
                    # 如果tree-sitter可用于此文件，跳过'pass'和'NotImplementedError'的正则检查
                    # （因为tree-sitter会更准确地处理这些情况）
                    ext = Path(filepath).suffix  # 获取文件扩展名
                    is_parsed = TREE_SITTER_AVAILABLE and ext in (
                        ".py",
                        ".js",
                        ".ts",
                        ".jsx",
                        ".tsx",
                    )

                    # 如果tree-sitter将处理此文件，跳过这些模式的正则检查
                    if is_parsed and label in ("pass", "NotImplementedError"):
                        continue

                    # 在当前行中搜索模式
                    if pattern.search(line):
                        # 找到匹配，记录问题
                        issues.append(
                            {
                                "type": "Incomplete/Improper",  # 问题类型
                                "subtype": label,  # 具体模式（如TODO、FIXME）
                                "file": str(filepath),  # 文件路径
                                "line": i + 1,  # 行号（从1开始）
                                "content": line.strip(),  # 去除空白的行内容
                            }
                        )

                # ========================================
                # 回退检查（当tree-sitter不可用时）
                # ========================================
                # 简单检测单行的函数桩（例如：def foo(): pass）
                if not TREE_SITTER_AVAILABLE and "def " in line and "pass" in line:
                    issues.append(
                        {
                            "type": "Improper Implementation",
                            "subtype": "One-line stub",  # 单行桩函数
                            "file": str(filepath),
                            "line": i + 1,
                            "content": line.strip(),
                        }
                    )

        except Exception as e:
            # 捕获正则扫描中的错误
            print(f"Error doing regex scan on {filepath}: {e}")

        # ========================================
        # 步骤3: Tree-sitter AST扫描（更精确）
        # ========================================
        if TREE_SITTER_AVAILABLE:
            # 根据文件扩展名确定语言
            ext = Path(filepath).suffix  # 获取文件扩展名
            lang = None  # 初始化语言变量

            # 映射扩展名到语言名称
            if ext == ".py":
                lang = "python"
            elif ext == ".js":
                lang = "javascript"
            elif ext == ".ts":
                lang = "typescript"
            elif ext in (".jsx", ".tsx"):
                lang = "tsx"  # 简化处理（将jsx和tsx都视为tsx）

            # 如果确定了语言，进行AST分析
            if lang:
                parser = get_parser(lang)  # 获取对应语言的解析器
                if parser:
                    tree = parser.parse(content)  # 解析内容，生成语法树
                    # 递归分析语法树的根节点
                    analyze_node(tree.root_node, issues, filepath, content)

    except Exception as e:
        # 捕获文件读取或处理中的任何错误
        print(f"Error reading {filepath}: {e}")

    return issues  # 返回收集到的所有问题


def get_unused_items():
    """
    Get unused code items from pyright analysis.

    从pyright分析结果中获取未使用的代码项。

    Pyright是一个Python静态类型检查器，它可以检测未被访问的变量、
    函数、类等代码项。这个函数解析pyright的JSON输出来提取这些信息。

    Returns:
        list: 未使用项的列表，每个项包含：
            - type: "Unused Item"
            - subtype: "Pyright Diagnostic"
            - file: 文件路径
            - line: 行号
            - content: 诊断消息
    """
    unused = []  # 初始化未使用项列表

    # ========================================
    # 检查pyright输出文件是否存在
    # ========================================
    if os.path.exists(PYRIGHT_OUTPUT):
        try:
            # ========================================
            # 步骤1: 读取并解析JSON文件
            # ========================================
            with open(PYRIGHT_OUTPUT, "r", encoding="utf-8") as f:
                data = json.load(f)  # 加载JSON数据

                # ========================================
                # 步骤2: 提取通用诊断信息
                # ========================================
                # Pyright输出结构可能有所不同，这里假设标准JSON输出
                # 我们查找包含"is not accessed"消息的诊断信息
                if "generalDiagnostics" in data:
                    for diag in data["generalDiagnostics"]:
                        # 检查诊断消息是否包含"is not accessed"
                        if "is not accessed" in diag.get("message", ""):
                            # 提取诊断信息并添加到列表
                            unused.append(
                                {
                                    "type": "Unused Item",  # 类型：未使用项
                                    "subtype": "Pyright Diagnostic",  # 子类型
                                    "file": diag.get("file", "unknown"),  # 文件路径
                                    "line": diag.get("range", {})  # 获取行号
                                    .get("start", {})
                                    .get("line", 0)
                                    + 1,  # pyright从0开始计数，所以+1
                                    "content": diag.get("message", ""),  # 诊断消息
                                }
                            )
        except Exception as e:
            # 捕获JSON解析错误
            print(f"Error parsing pyright output: {e}")
    else:
        # pyright输出文件不存在
        print(f"Warning: {PYRIGHT_OUTPUT} not found. Skipping unused item analysis.")

    return unused  # 返回未使用项列表


def generate_report(issues, unused):
    """
    Generate a Markdown report of code quality issues.

    生成代码质量问题的Markdown报告。

    该函数将所有发现的问题（未完成的实现、不当的实现、未使用的代码）
    格式化为易读的Markdown文档。

    Args:
        issues (list): 问题列表（来自scan_file）
        unused (list): 未使用项列表（来自get_unused_items）
    """
    # ========================================
    # 步骤1: 打开输出文件
    # ========================================
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        # 写入报告标题
        f.write("# Code Analysis Issues Report\n\n")

        # ========================================
        # 步骤2: 写入未完成和不当实现部分
        # ========================================
        f.write("## Incomplete & Improper Items\n")
        if issues:
            # ========================================
            # 步骤2a: 按文件和行号排序问题
            # ========================================
            issues.sort(key=lambda x: (x["file"], x["line"]))

            # ========================================
            # 步骤2b: 遍历并写入每个问题
            # ========================================
            for issue in issues:
                # 写入问题的子类型、文件路径和行号
                f.write(
                    f"- **{issue['subtype']}** in `{issue['file']}:{issue['line']}`\n"
                )
                # 写入问题的代码内容（使用代码块格式）
                f.write(f"  ```\n  {issue['content']}\n  ```\n")
        else:
            # 没有发现问题
            f.write("No incomplete items found.\n")

        # ========================================
        # 步骤3: 写入未使用项部分
        # ========================================
        f.write("\n## Unused Items\n")
        if unused:
            # 遍历并写入每个未使用项
            for item in unused:
                # 写入项的子类型、文件路径和行号
                f.write(f"- **{item['subtype']}** in `{item['file']}:{item['line']}`\n")
                # 写入诊断消息（使用引用格式）
                f.write(f"  > {item['content']}\n")
        else:
            # 没有发现未使用项（或pyright输出缺失）
            f.write("No unused items found (or pyright output missing).\n")


def main():
    """
    Main entry point for the code analysis report generator.

    代码分析报告生成器的主入口点。

    执行流程：
    1. 从配置中获取代码根目录和排除路径
    2. 运行pyright进行静态类型检查
    3. 遍历所有代码文件进行扫描
    4. 收集未使用的代码项
    5. 生成Markdown格式的报告
    """
    all_issues = []  # 初始化所有问题的列表

    # ========================================
    # 步骤1: 从配置管理器获取配置
    # ========================================
    code_roots = config.get_code_root_directories()  # 获取代码根目录列表
    excluded_paths = config.get_excluded_paths()  # 获取要排除的路径列表

    # ========================================
    # 步骤2: 运行pyright进行未使用项分析
    # ========================================
    try:
        print("Running pyright for unused item analysis...")  # 提示用户
        # 将pyright的输出重定向到文件
        with open(PYRIGHT_OUTPUT, "w") as f:
            result = subprocess.run(
                ["pyright", "--outputjson"],  # 以JSON格式输出
                stdout=f,  # 标准输出重定向到文件
                stderr=subprocess.STDOUT,  # 标准错误也重定向到文件
                cwd=project_root,  # 在项目根目录运行
            )
        # 检查pyright的退出代码
        if result.returncode == 0:
            print("Pyright analysis completed successfully.")
        else:
            print(
                f"Pyright completed with warnings/errors (exit code {result.returncode}). Output file generated."
            )
    except Exception as e:
        # 捕获运行pyright时的任何异常
        print(f"Warning: Unexpected error running pyright: {e}")

    # ========================================
    # 步骤3: 遍历代码根目录并扫描文件
    # ========================================
    print(f"Scanning code roots: {code_roots}")  # 显示将要扫描的目录

    # 遍历每个代码根目录
    for root_dir in code_roots:
        # ========================================
        # 步骤3a: 处理相对和绝对路径
        # ========================================
        # 解析root_dir（如果需要的话，相对于项目根目录）
        # ConfigManager通常返回相对于项目根目录的标准化路径或绝对路径

        # 我们需要处理code_roots是相对路径还是绝对路径的情况
        # ConfigManager.get_code_root_directories()返回标准化路径，
        # 如果在.clinerules中定义为相对路径，可能是相对于项目根目录

        # 假设从项目根目录运行
        start_dir = root_dir
        if not os.path.exists(start_dir):
            print(f"Warning: Code root {start_dir} does not exist. Skipping.")
            continue  # 跳过不存在的目录

        # ========================================
        # 步骤3b: 遍历目录树
        # ========================================
        for root, dirs, files in os.walk(start_dir):
            # ========================================
            # 步骤3c: 过滤要排除的目录
            # ========================================
            # 就地修改dirs列表以跳过排除的目录
            # 这样os.walk就不会进入这些目录
            dirs[:] = [
                d
                for d in dirs
                if not path_utils.is_path_excluded(
                    os.path.join(root, d), excluded_paths
                )
            ]

            # ========================================
            # 步骤3d: 处理每个文件
            # ========================================
            for file in files:
                filepath = os.path.join(root, file)  # 构建完整文件路径

                # 检查文件路径是否在排除列表中
                if path_utils.is_path_excluded(filepath, excluded_paths):
                    continue  # 跳过排除的文件

                # 检查文件扩展名是否在支持的扩展名集合中
                ext = Path(file).suffix  # 获取文件扩展名
                if ext not in EXTENSIONS:
                    continue  # 跳过不支持的文件类型

                # ========================================
                # 步骤3e: 扫描文件并收集问题
                # ========================================
                all_issues.extend(scan_file(filepath))  # 扫描文件并添加问题到列表

    # ========================================
    # 步骤4: 获取未使用的代码项
    # ========================================
    unused_items = get_unused_items()  # 从pyright输出中提取未使用项

    # ========================================
    # 步骤5: 生成报告
    # ========================================
    generate_report(all_issues, unused_items)  # 生成Markdown报告
    print(f"Report generated at {OUTPUT_FILE}")  # 通知用户报告已生成


# ========================================
# 程序入口点
# ========================================
if __name__ == "__main__":
    main()  # 如果直接运行此脚本，调用main函数

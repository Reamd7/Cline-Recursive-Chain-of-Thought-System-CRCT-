# cline_utils/dependency_system/utils/tracker_utils.py
# 跟踪器工具模块（第2部分）- Tracker Utilities Module (Part 2)

"""
Continuation of tracker utilities.
Contains functions for finding tracker files and aggregating dependencies.

跟踪器工具的继续部分
包含查找跟踪文件和聚合依赖的函数
"""

# 此文件是tracker_utils.py的第2部分
# This file is part 2 of tracker_utils.py


# ==================== 查找所有跟踪文件函数 - Find All Tracker Files Function ====================
def find_all_tracker_paths(config: ConfigManager, project_root: str) -> Set[str]:
    """
    Finds all main, doc, and mini tracker files in the project.
    查找项目中所有主跟踪器、文档跟踪器和迷你跟踪器文件

    跟踪器类型 - Tracker Types:
    1. Main Tracker: module_relationship_tracker.md - 主跟踪器（模块关系）
    2. Doc Tracker: doc_tracker.md - 文档跟踪器
    3. Mini Trackers: *_module.md - 迷你跟踪器（各模块）

    Args:
        config: 配置管理器实例 - ConfigManager instance
        project_root: 项目根目录路径 - Project root directory path

    Returns:
        Set[str]: 所有跟踪文件的标准化路径集合 - Set of all tracker file normalized paths
    """
    # ========== 步骤1: 初始化结果集合 - Initialize Result Set ==========
    all_tracker_paths = set()  # 使用集合避免重复 - Use set to avoid duplicates

    # ========== 步骤2: 获取内存目录配置 - Get Memory Directory Configuration ==========
    memory_dir_rel = config.get_path("memory_dir")  # 获取相对路径 - Get relative path
    if not memory_dir_rel:
        # 内存目录未配置 - Memory directory not configured
        logger.warning("memory_dir not configured. Cannot find main/doc trackers.")  # 记录警告 - Log warning
        memory_dir_abs = None  # 设置为None - Set to None
    else:
        # ========== 步骤2.1: 计算绝对路径 - Calculate Absolute Path ==========
        memory_dir_abs = normalize_path(os.path.join(project_root, memory_dir_rel))  # 标准化绝对路径 - Normalize absolute path
        logger.debug(
            f"Path Components: project_root='{project_root}', "
            f"memory_dir_rel='{memory_dir_rel}', "
            f"calculated memory_dir_abs='{memory_dir_abs}'"
        )  # 记录路径组件 - Log path components

        # ========== 步骤2.2: 查找主跟踪器 - Find Main Tracker ==========
        main_tracker_abs = config.get_path(
            "main_tracker_filename",  # 配置键 - Config key
            os.path.join(memory_dir_abs, "module_relationship_tracker.md"),  # 默认值 - Default value
        )
        logger.debug(
            f"Using main_tracker_abs from config (or default): '{main_tracker_abs}'"
        )  # 记录主跟踪器路径 - Log main tracker path

        if os.path.exists(main_tracker_abs):
            # 主跟踪器存在 - Main tracker exists
            all_tracker_paths.add(main_tracker_abs)  # 添加到结果集 - Add to result set
        else:
            # 主跟踪器不存在 - Main tracker doesn't exist
            logger.debug(f"Main tracker not found at: {main_tracker_abs}")  # 记录调试信息 - Log debug info

        # ========== 步骤2.3: 查找文档跟踪器 - Find Doc Tracker ==========
        doc_tracker_abs = config.get_path(
            "doc_tracker_filename",  # 配置键 - Config key
            os.path.join(memory_dir_abs, "doc_tracker.md"),  # 默认值 - Default value
        )
        logger.debug(
            f"Using doc_tracker_abs from config (or default): '{doc_tracker_abs}'"
        )  # 记录文档跟踪器路径 - Log doc tracker path

        if os.path.exists(doc_tracker_abs):
            # 文档跟踪器存在 - Doc tracker exists
            all_tracker_paths.add(doc_tracker_abs)  # 添加到结果集 - Add to result set
        else:
            # 文档跟踪器不存在 - Doc tracker doesn't exist
            logger.debug(f"Doc tracker not found at: {doc_tracker_abs}")  # 记录调试信息 - Log debug info

    # ========== 步骤3: 查找迷你跟踪器 - Find Mini Trackers ==========
    code_roots_rel = config.get_code_root_directories()  # 获取代码根目录列表 - Get code root directories list
    if not code_roots_rel:
        # 未配置代码根目录 - No code root directories configured
        logger.warning(
            "No code_root_directories configured. Cannot find mini trackers."
        )  # 记录警告 - Log warning
    else:
        # ========== 步骤3.1: 遍历每个代码根目录 - Iterate Through Each Code Root Directory ==========
        for code_root_rel in code_roots_rel:
            # 计算代码根目录的绝对路径 - Calculate absolute path of code root directory
            code_root_abs = normalize_path(os.path.join(project_root, code_root_rel))

            # ========== 步骤3.2: 构建迷你跟踪器搜索模式 - Build Mini Tracker Search Pattern ==========
            mini_tracker_pattern = os.path.join(code_root_abs, "**", "*_module.md")
            # 模式：代码根目录/**/*_module.md - Pattern: code_root/**/*_module.md
            # **: 递归匹配所有子目录 - Recursively matches all subdirectories

            # ========== 步骤3.3: 使用glob查找匹配的文件 - Use glob to Find Matching Files ==========
            try:
                found_mini_trackers = glob.glob(
                    mini_tracker_pattern, recursive=True
                )  # 递归搜索 - Recursive search
                # glob.glob: 返回匹配模式的文件路径列表 - Returns list of file paths matching pattern

                # ========== 步骤3.4: 标准化路径并添加到结果集 - Normalize Paths and Add to Result Set ==========
                normalized_mini_paths = {
                    normalize_path(mt_path) for mt_path in found_mini_trackers
                }  # 集合推导式标准化路径 - Set comprehension to normalize paths

                all_tracker_paths.update(normalized_mini_paths)  # 更新结果集 - Update result set

                logger.debug(
                    f"Found {len(normalized_mini_paths)} mini trackers under '{code_root_rel}'."
                )  # 记录找到的迷你跟踪器数量 - Log number of mini trackers found

            # ========== 步骤3.5: 异常处理 - Exception Handling ==========
            except Exception as e:
                # glob搜索失败 - glob search failed
                logger.error(
                    f"Error during glob search for mini trackers under '{code_root_abs}': {e}"
                )  # 记录错误 - Log error

    # ========== 步骤4: 返回结果 - Return Result ==========
    logger.debug(f"Found {len(all_tracker_paths)} total tracker files.")  # 记录总数 - Log total count
    return all_tracker_paths  # 返回所有跟踪文件路径集合 - Return set of all tracker file paths


# ==================== 全局映射缓存键生成函数 - Global Map Cache Key Generation Function ====================
def get_global_map_cache_key_part(global_map: Dict[str, Any]) -> str:
    """
    Creates a stable hashable key part from a dictionary.
    从字典创建稳定的可哈希键部分

    使用场景 - Use Case:
    - 为缓存键创建唯一标识 - Create unique identifier for cache keys
    - 基于全局映射的内容生成哈希 - Generate hash based on global map content

    Args:
        global_map: 全局映射字典 - Global map dictionary

    Returns:
        str: 哈希值字符串 - Hash value string
    """
    # ========== 步骤1: 空映射处理 - Empty Map Handling ==========
    if not global_map:
        return "empty"  # 空映射返回"empty" - Return "empty" for empty map

    # ========== 步骤2: 生成哈希 - Generate Hash ==========
    # 对排序后的键进行哈希以保持稳定性 - Hash sorted keys for stability
    # 这避免了对不可哈希值进行哈希 - This avoids hashing unhashable values
    # 假设路径集合是最重要的变化因素 - Assumes the set of paths is the most important changing factor
    hash_input = "".join(sorted(global_map.keys()))  # 连接排序后的键 - Join sorted keys
    hash_output = hashlib.sha256(hash_input.encode()).hexdigest()  # SHA256哈希 - SHA256 hash
    # sha256: 生成256位哈希值 - Generates 256-bit hash
    # hexdigest: 返回十六进制字符串 - Returns hexadecimal string

    return hash_output  # 返回哈希值 - Return hash value


# ==================== 依赖聚合函数 - Dependency Aggregation Function ====================
@cached(
    "aggregation_v2_gi",  # 缓存名称 - Cache name
    # key_func: show_progress不影响缓存，所以接受但不包含在键中 - show_progress doesn't affect cache, accepted but not included in key
    key_func=lambda paths, pmi, cgptki, show_progress=True: f"agg_v2_gi:{':'.join(sorted(list(paths)))}:{hash(tuple(sorted(pmi.items())))}:{get_global_map_cache_key_part(cgptki)}",
    ttl=300,  # 缓存生存时间300秒 - Cache TTL 300 seconds
)
def aggregate_all_dependencies(
    tracker_paths: Set[str],
    path_migration_info: PathMigrationInfo,
    current_global_path_to_key_info: Dict[str, KeyInfo],  # 新参数 - New parameter
    show_progress: bool = True,
) -> Dict[Tuple[str, str], Tuple[str, Set[str]]]:
    """
    Aggregates dependencies from tracker files, resolving paths to current global KeyInfo objects
    and then to their KEY#global_instance strings for instance-specific aggregation.

    从跟踪文件聚合依赖，将路径解析为当前全局KeyInfo对象
    然后解析为它们的KEY#global_instance字符串以进行实例特定的聚合

    聚合策略 - Aggregation Strategy:
    1. 读取所有跟踪文件 - Read all tracker files
    2. 将文件中的路径映射到全局KeyInfo - Map paths from files to global KeyInfo
    3. 解析为KEY#GI字符串 - Resolve to KEY#GI strings
    4. 按优先级聚合依赖 - Aggregate dependencies by priority
    5. 追踪依赖来源 - Track dependency origins

    Args:
        tracker_paths: 跟踪文件路径集合 - Set of tracker file paths
        path_migration_info: 路径迁移信息 - Path migration info
        current_global_path_to_key_info: 当前全局路径到KeyInfo的映射 - Current global path to KeyInfo mapping
        show_progress: 是否显示进度 - Whether to show progress

    Returns:
        Dict[Tuple[str, str], Tuple[str, Set[str]]]:
            键: (源KEY#GI, 目标KEY#GI) - Key: (source KEY#GI, target KEY#GI)
            值: (依赖字符, 来源跟踪文件集合) - Value: (dependency char, set of origin tracker files)
    """
    # ========== 步骤1: 初始化聚合结果 - Initialize Aggregation Result ==========
    aggregated_links: Dict[Tuple[str, str], Tuple[str, Set[str]]] = {}
    # 键: (src_KEY#GI, tgt_KEY#GI) - Key: (src_KEY#GI, tgt_KEY#GI)
    # 值: (依赖字符, 来源集合) - Value: (dependency char, origins set)

    # ========== 步骤2: 获取配置和优先级函数 - Get Config and Priority Function ==========
    config = ConfigManager()  # 创建配置管理器实例 - Create ConfigManager instance
    get_priority_from_char = config.get_char_priority  # 获取字符优先级函数 - Get char priority function

    logger.debug(
        f"Aggregating dependencies (outputting KEY#global_instance) from {len(tracker_paths)} trackers..."
    )  # 记录开始聚合 - Log start of aggregation

    # ========== 步骤3: 准备并行处理 - Prepare Parallel Processing ==========
    from cline_utils.dependency_system.utils.batch_processor import BatchProcessor

    # ========== 步骤3.1: 定义单个跟踪器聚合函数 - Define Single Tracker Aggregation Function ==========
    def _aggregate_single_tracker(
        tracker_file_path: str,
    ) -> Dict[Tuple[str, str], Tuple[str, Set[str]]]:
        """
        处理单个跟踪文件的聚合 - Process aggregation for a single tracker file

        Args:
            tracker_file_path: 跟踪文件路径 - Tracker file path

        Returns:
            Dict: 该跟踪器的依赖链接 - Dependency links from this tracker
        """
        # ========== 步骤3.1.1: 初始化本地链接字典 - Initialize Local Links Dictionary ==========
        local_links: Dict[Tuple[str, str], Tuple[str, Set[str]]] = {}  # 本地依赖链接 - Local dependency links

        logger.debug(
            f"Aggregation: Processing tracker {os.path.basename(tracker_file_path)}"
        )  # 记录处理的跟踪器 - Log tracker being processed

        # ========== 步骤3.1.2: 读取跟踪器数据 - Read Tracker Data ==========
        tracker_data = read_tracker_file_structured(tracker_file_path)  # 读取结构化数据 - Read structured data

        definitions_ordered_from_file = tracker_data[
            "definitions_ordered"
        ]  # 从文件读取的有序定义 - Ordered definitions from file
        grid_headers_from_file = tracker_data[
            "grid_headers_ordered"
        ]  # 从文件读取的网格头 - Grid headers from file
        grid_rows_from_file = tracker_data[
            "grid_rows_ordered"
        ]  # 从文件读取的网格行 - Grid rows from file

        # ========== 步骤3.1.3: 检查数据完整性 - Check Data Completeness ==========
        if not definitions_ordered_from_file or not grid_rows_from_file:
            # 数据为空或不完整 - Data empty or incomplete
            logger.debug(
                f"Aggregation: Skipping empty/incomplete data in: {os.path.basename(tracker_file_path)}"
            )  # 记录跳过 - Log skip
            return local_links  # 返回空链接字典 - Return empty links dict

        # ========== 步骤3.1.4: 构建此跟踪器的有效KeyInfo列表 - Build Effective KeyInfo List for This Tracker ==========
        effective_ki_list_for_this_tracker: List[Optional[KeyInfo]] = []  # 有效的KeyInfo列表 - Effective KeyInfo list

        # 遍历每个定义条目 - Iterate through each definition entry
        for _key_in_file, path_in_file in definitions_ordered_from_file:
            # ========== 步骤3.1.5: 解析路径到当前KeyInfo - Resolve Path to Current KeyInfo ==========
            mig_info = path_migration_info.get(path_in_file)  # 获取迁移信息 - Get migration info
            resolved_ki_for_this_def_entry: Optional[KeyInfo] = None  # 初始化解析结果 - Initialize resolved result

            if mig_info and mig_info[1]:  # 有当前全局基础键 - Has current global base key
                new_global_base_key = mig_info[1]  # 获取新的全局基础键 - Get new global base key

                # ========== 步骤3.1.6: 在全局映射中查找KeyInfo - Find KeyInfo in Global Map ==========
                # 首选：路径和键都匹配 - Prefer: both path and key match
                resolved_ki_for_this_def_entry = next(
                    (
                        ki
                        for ki in current_global_path_to_key_info.values()
                        if ki.key_string == new_global_base_key
                        and ki.norm_path == path_in_file
                    ),
                    None,
                ) or next(
                    # 备选：只匹配键 - Alternative: only key matches
                    (
                        ki
                        for ki in current_global_path_to_key_info.values()
                        if ki.key_string == new_global_base_key
                    ),
                    None,
                )

            effective_ki_list_for_this_tracker.append(
                resolved_ki_for_this_def_entry
            )  # 添加到有效列表 - Add to effective list

        # ========== 步骤3.1.7: 验证结构一致性 - Verify Structure Consistency ==========
        if not (
            len(effective_ki_list_for_this_tracker) == len(grid_headers_from_file)
            and len(effective_ki_list_for_this_tracker) == len(grid_rows_from_file)
        ):
            # 结构不一致 - Structure inconsistent
            logger.warning(
                f"Aggregation: Tracker '{os.path.basename(tracker_file_path)}' has inconsistent structure after global validation. "
                f"Effective KIs: {len(effective_ki_list_for_this_tracker)}, File Headers: {len(grid_headers_from_file)}, File Rows: {len(grid_rows_from_file)}. "
                "Skipping this tracker."
            )  # 记录警告 - Log warning
            return local_links  # 返回空链接 - Return empty links

        # ========== 步骤3.1.8: 处理每一行（源依赖）- Process Each Row (Source Dependencies) ==========
        for row_idx, (_row_label_in_file, compressed_row_str) in enumerate(
            grid_rows_from_file
        ):
            # 获取源KeyInfo - Get source KeyInfo
            source_ki_global = effective_ki_list_for_this_tracker[row_idx]
            if not source_ki_global:
                continue  # 源KeyInfo无效，跳过 - Source KeyInfo invalid, skip

            # ========== 步骤3.1.9: 获取源的全局实例字符串 - Get Source Global Instance String ==========
            source_key_gi_str = get_key_global_instance_string(
                source_ki_global, current_global_path_to_key_info
            )
            if not source_key_gi_str:
                # 无法获取全局实例字符串 - Cannot get global instance string
                logger.warning(
                    f"Aggregation: Could not get global instance for source path {source_ki_global.norm_path} from {os.path.basename(tracker_file_path)}. Skipping row."
                )  # 记录警告 - Log warning
                continue  # 跳过此行 - Skip this row

            # ========== 步骤3.1.10: 解压缩行数据 - Decompress Row Data ==========
            try:
                decompressed_row_chars = decompress(
                    compressed_row_str
                )  # 解压缩字符串 - Decompress string

                # 验证长度 - Verify length
                if len(decompressed_row_chars) != len(
                    effective_ki_list_for_this_tracker
                ):
                    # 长度不匹配 - Length mismatch
                    logger.warning(
                        f"Aggregation: Row {row_idx} (source KI: {source_key_gi_str}) in {os.path.basename(tracker_file_path)} "
                        f"has decompressed length {len(decompressed_row_chars)}, expected {len(effective_ki_list_for_this_tracker)}. Skipping row."
                    )  # 记录警告 - Log warning
                    continue  # 跳过此行 - Skip this row

                # ========== 步骤3.1.11: 处理每个单元格（目标依赖）- Process Each Cell (Target Dependencies) ==========
                for col_idx, dep_char_val in enumerate(decompressed_row_chars):
                    # 跳过对角线和空字符 - Skip diagonal and empty characters
                    if dep_char_val == DIAGONAL_CHAR or dep_char_val == EMPTY_CHAR:
                        continue  # 跳过 - Skip

                    # 获取目标KeyInfo - Get target KeyInfo
                    target_ki_global = effective_ki_list_for_this_tracker[col_idx]
                    if not target_ki_global:
                        continue  # 目标KeyInfo无效，跳过 - Target KeyInfo invalid, skip

                    # 跳过自依赖 - Skip self-dependency
                    if source_ki_global.norm_path == target_ki_global.norm_path:
                        continue  # 跳过自依赖 - Skip self-dependency

                    # ========== 步骤3.1.12: 获取目标的全局实例字符串 - Get Target Global Instance String ==========
                    target_key_gi_str = get_key_global_instance_string(
                        target_ki_global, current_global_path_to_key_info
                    )
                    if not target_key_gi_str:
                        # 无法获取目标全局实例字符串 - Cannot get target global instance string
                        logger.warning(
                            f"Aggregation: Could not get global instance for target path {target_ki_global.norm_path} from {os.path.basename(tracker_file_path)}. Skipping cell."
                        )  # 记录警告 - Log warning
                        continue  # 跳过此单元格 - Skip this cell

                    # ========== 步骤3.1.13: 创建依赖链接 - Create Dependency Link ==========
                    link = (source_key_gi_str, target_key_gi_str)  # 创建链接元组 - Create link tuple
                    existing_char, existing_origins = local_links.get(
                        link, (None, set())
                    )  # 获取现有条目 - Get existing entry

                    # ========== 步骤3.1.14: 计算优先级 - Calculate Priorities ==========
                    try:
                        current_priority = get_priority_from_char(
                            dep_char_val
                        )  # 当前字符优先级 - Current char priority
                        existing_priority = (
                            get_priority_from_char(existing_char)
                            if existing_char
                            else -1  # 现有字符优先级或-1 - Existing char priority or -1
                        )
                    except KeyError:
                        # 无效的依赖字符 - Invalid dependency char
                        logger.warning(
                            f"Aggregation: Invalid dep char '{dep_char_val}' in {os.path.basename(tracker_file_path)}. Skipping {link}."
                        )  # 记录警告 - Log warning
                        continue  # 跳过 - Skip

                    # ========== 步骤3.1.15: 根据优先级更新链接 - Update Link Based on Priority ==========
                    if current_priority > existing_priority:
                        # 当前优先级更高，替换 - Current priority higher, replace
                        local_links[link] = (str(dep_char_val), {tracker_file_path})
                    elif current_priority == existing_priority:
                        # 优先级相同，合并来源 - Same priority, merge origins
                        if existing_char is not None and dep_char_val == existing_char:
                            existing_origins.add(tracker_file_path)  # 添加来源 - Add origin
                            local_links[link] = (
                                str(existing_char),
                                set(existing_origins),
                            )  # 更新条目 - Update entry
                        elif existing_char == "n":
                            pass  # 保持现有的'n' - Keep existing 'n'
                        elif dep_char_val == "n":
                            local_links[link] = (
                                "n",
                                {tracker_file_path},
                            )  # 设置为'n' - Set to 'n'
                        else:
                            # 冲突，用新值覆盖 - Conflict, overwrite with new value
                            local_links[link] = (str(dep_char_val), {tracker_file_path})
                            logger.debug(
                                f"Aggregation conflict (same priority): {link} was '{existing_char}', overwritten by '{dep_char_val}' from {os.path.basename(tracker_file_path)}."
                            )  # 记录冲突 - Log conflict

            # ========== 步骤3.1.16: 行处理异常捕获 - Row Processing Exception Handling ==========
            except Exception as e_agg_row:
                # 处理行时发生异常 - Exception during row processing
                logger.warning(
                    f"Aggregation: Error processing row {row_idx} for source KI {source_key_gi_str} in {os.path.basename(tracker_file_path)}: {e_agg_row}",
                    exc_info=False,
                )  # 记录警告 - Log warning

        # ========== 步骤3.1.17: 返回本地链接 - Return Local Links ==========
        return local_links  # 返回此跟踪器的依赖链接 - Return dependency links from this tracker

    # ========== 步骤4: 并行处理所有跟踪器 - Process All Trackers in Parallel ==========
    tracker_list = list(tracker_paths)  # 转换为列表 - Convert to list
    processor = BatchProcessor(
        show_progress=show_progress, phase_name="Aggregating Dependencies"
    )  # 创建批处理器 - Create batch processor
    per_tracker_results = processor.process_items(
        tracker_list, _aggregate_single_tracker
    )  # 并行处理 - Process in parallel

    # ========== 步骤5: 合并所有跟踪器的结果 - Merge Results from All Trackers ==========
    for local_links in per_tracker_results:
        # 遍历每个跟踪器的结果 - Iterate through each tracker's results
        for link, (char_val, origins) in local_links.items():
            # 遍历每个依赖链接 - Iterate through each dependency link

            # ========== 步骤5.1: 规范化现有条目类型 - Normalize Existing Entry Types ==========
            existing_entry = aggregated_links.get(link)  # 获取现有条目 - Get existing entry

            # 当前字符始终是来自local_links的具体字符串 - Current char is always concrete string from local_links
            current_char: str = str(char_val)

            if existing_entry is None:
                # 没有现有条目 - No existing entry
                existing_char_str: str = ""  # 标记为"无现有" - Sentinel for "no existing"
                existing_origins: Set[str] = set()  # 空来源集合 - Empty origins set
                existing_priority = -1  # 优先级-1 - Priority -1
            else:
                # 有现有条目 - Has existing entry
                e_char, e_origins = existing_entry  # 解包现有条目 - Unpack existing entry
                existing_char_str = e_char  # 现有字符 - Existing char
                existing_origins = set(e_origins)  # 现有来源集合 - Existing origins set
                try:
                    existing_priority = get_priority_from_char(
                        existing_char_str
                    )  # 计算现有优先级 - Calculate existing priority
                except KeyError:
                    existing_priority = -1  # 无效字符，优先级-1 - Invalid char, priority -1

            # ========== 步骤5.2: 计算当前优先级 - Calculate Current Priority ==========
            try:
                current_priority = get_priority_from_char(
                    current_char
                )  # 计算当前优先级 - Calculate current priority
            except KeyError:
                continue  # 无效字符，跳过 - Invalid char, skip

            # ========== 步骤5.3: 根据优先级合并 - Merge Based on Priority ==========
            if current_priority > existing_priority:
                # 当前优先级更高，替换 - Current priority higher, replace
                aggregated_links[link] = (str(current_char), set(origins))
            elif current_priority == existing_priority:
                # 优先级相同 - Same priority
                if existing_char_str != "" and existing_char_str == current_char:
                    # 字符相同，合并来源 - Same char, merge origins
                    merged: Set[str] = existing_origins.union(set(origins))
                    aggregated_links[link] = (str(current_char), merged)
                elif existing_char_str == "n":
                    pass  # 保持现有的'n' - Keep existing 'n'
                elif current_char == "n":
                    aggregated_links[link] = ("n", set(origins))  # 设置为'n' - Set to 'n'
                else:
                    # 冲突，用新值覆盖 - Conflict, overwrite with new value
                    aggregated_links[link] = (str(current_char), set(origins))

    # ========== 步骤6: 记录完成并返回 - Log Completion and Return ==========
    logger.debug(
        f"Aggregation complete. Found {len(aggregated_links)} unique KEY#global_instance directed links."
    )  # 记录完成 - Log completion
    return aggregated_links  # 返回聚合的依赖链接 - Return aggregated dependency links


# ==================== 文件结束标记 - End of File Marker (Part 2) ====================
# --- End of tracker_utils.py ---

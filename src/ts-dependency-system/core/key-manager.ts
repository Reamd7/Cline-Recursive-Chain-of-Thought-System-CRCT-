/**
 * Core module for key management.
 * Handles key generation, validation, and sorting based on a hierarchical,
 * contextual model with tier promotion for nested subdirectories.
 */

import * as fs from 'fs';
import * as path from 'path';
import { KeyGenerationError } from './exceptions';

// 尝试导入工具模块，如果不可用则提供基本实现
let getProjectRoot: () => string;
let normalizePath: (p: string) => string;
let ConfigManager: any;

try {
  // 这些导入将在工具模块实现后更新
  // 从工具模块导入
  getProjectRoot = () => process.cwd();
  normalizePath = (p: string) => path.normalize(p).replace(/\\/g, '/');
  ConfigManager = class {
    getExcludedDirs() { return new Set<string>(); }
    getExcludedExtensions() { return new Set<string>(); }
    getExcludedPaths() { return []; }
  };
} catch (error) {
  // 提供基本实现
  console.warn("Warning: Potential import errors. Ensure utils module is implemented.");
  getProjectRoot = () => process.cwd();
  normalizePath = (p: string) => path.normalize(p).replace(/\\/g, '/');
  ConfigManager = class {
    getExcludedDirs() { return new Set<string>(); }
    getExcludedExtensions() { return new Set<string>(); }
    getExcludedPaths() { return []; }
  };
}

// 常量
const ASCII_A_UPPER = 65;  // ASCII值 'A'
const ASCII_A_LOWER = 97;  // ASCII值 'a'
const ASCII_Z_LOWER = 122; // ASCII值 'z'

// 层次化键模式，允许多位数的层级和文件编号
// 结构：层级 + 目录 + [子目录 + [文件] | 文件]
const HIERARCHICAL_KEY_PATTERN = /^[1-9]\d*[A-Z](?:[a-z](?:[1-9]\d*)?|[1-9]\d*)?$/;
// 用于将键拆分为可排序部分的模式（数字和非数字）
const KEY_PATTERN = /\d+|\D+/g;

/**
 * 存储生成的键的信息
 */
export interface KeyInfo {
  keyString: string;         // 生成的键字符串（例如 "1A", "1Aa", "2Ab"）
  normPath: string;          // 此键表示的规范化绝对路径
  parentPath: string | null; // 包含此项目的父目录的规范化路径
  tier: number;              // 此键字符串中使用的层级编号
  isDirectory: boolean;      // 如果键表示目录则为true
}

/**
 * 根据文件扩展名确定文件类型
 * @param filePath 文件路径
 * @returns 文件类型字符串（例如 "py", "js", "md", "generic"）
 */
export function getFileTypeForKey(filePath: string): string {
  const ext = path.extname(filePath).toLowerCase();

  if (ext === ".py") {
    return "py";
  } else if ([".js", ".ts", ".jsx", ".tsx"].includes(ext)) {
    return "js";
  } else if ([".md", ".rst"].includes(ext)) {
    return "md";
  } else if ([".html", ".htm"].includes(ext)) {
    return "html";
  } else if (ext === ".css") {
    return "css";
  } else {
    return "generic";
  }
}

/**
 * 为文件和目录生成层次化、上下文相关的键
 * 为嵌套子目录实现层级提升
 * 
 * @param rootPaths 要处理的根目录路径列表
 * @param excludedDirs 可选的要排除的目录名称集合
 * @param excludedExtensions 可选的要排除的文件扩展名集合
 * @param precomputedExcludedPaths 可选的预计算的要排除的绝对路径集合
 * @returns 包含以下内容的元组：
 *          - 将规范化路径映射到KeyInfo对象的字典
 *          - 新生成的KeyInfo对象列表（唯一）
 * @throws FileNotFoundError 如果根路径不存在
 * @throws KeyGenerationError 如果违反键生成规则（例如，>26个子目录）
 */
export function generateKeys(
  rootPaths: string | string[],
  excludedDirs?: Set<string>,
  excludedExtensions?: Set<string>,
  precomputedExcludedPaths?: Set<string>
): [Record<string, KeyInfo>, KeyInfo[]] {
  if (typeof rootPaths === 'string') {
    rootPaths = [rootPaths];
  }

  for (const rootPath of rootPaths) {
    if (!fs.existsSync(rootPath)) {
      throw new Error(`Root path '${rootPath}' does not exist.`);
    }
  }

  const configManager = new ConfigManager();
  const excludedDirsNames = excludedDirs || configManager.getExcludedDirs();
  const excludedExts = excludedExtensions || configManager.getExcludedExtensions();
  const projectRoot = getProjectRoot();
  const absoluteExcludedDirs = new Set<string>();
  
  for (const d of excludedDirsNames) {
    absoluteExcludedDirs.add(normalizePath(path.join(projectRoot, d)));
  }

  let exclusionSetForProcessing: Set<string>;
  if (precomputedExcludedPaths) {
    exclusionSetForProcessing = new Set([...precomputedExcludedPaths, ...absoluteExcludedDirs]);
  } else {
    const calculatedExcludedPathsList = configManager.getExcludedPaths();
    exclusionSetForProcessing = new Set([...calculatedExcludedPathsList, ...absoluteExcludedDirs]);
  }

  const pathToKeyInfo: Record<string, KeyInfo> = {}; // 映射 normPath -> KeyInfo
  const newlyGeneratedKeys: KeyInfo[] = []; // 跟踪新分配的KeyInfo对象
  let topLevelDirCount = 0; // 用于为根目录分配 'A', 'B', ... 的计数器

  /**
   * 辅助函数，将键解析为层级、目录、子目录组件
   */
  function parseKey(keyString: string | null): [number | null, string | null, string | null] {
    if (!keyString || !validateKey(keyString)) {
      return [null, null, null];
    }
    // 首先匹配带有子目录的键（例如 1Aa, 1Aa12）
    const match1 = keyString.match(/^([1-9]\d*)([A-Z])([a-z])/);
    if (match1) {
      const [, tierStr, dirLetter, subdirLetter] = match1;
      return [parseInt(tierStr), dirLetter, subdirLetter];
    }
    // 处理像 "1A", "1A1" 这样的情况（没有子目录字母）
    const match2 = keyString.match(/^([1-9]\d*)([A-Z])/);
    if (match2) {
      const [, tierStr, dirLetter] = match2;
      return [parseInt(tierStr), dirLetter, null];
    }
    console.warn(`Could not parse valid key: ${keyString}`);
    return [null, null, null];
  }

  /**
   * 递归处理目录和文件，生成上下文相关的键
   */
  function processDirectory(dirPath: string, exclusionSet: Set<string>, parentInfo: KeyInfo | null): void {
    try {
      const normDirPath = normalizePath(dirPath);

      // 1. 跳过排除的目录
      if (Array.from(exclusionSet).some(exPath => normDirPath.startsWith(exPath))) {
        console.debug(`Exclusion Check 1: Skipping excluded dir path: '${normDirPath}'`);
        return;
      }

      // --- 为当前处理的目录分配键 ---
      let currentDirKeyInfo: KeyInfo | null = null;
      if (parentInfo === null) { // 这是来自rootPaths的顶级目录
        const dirLetter = String.fromCharCode(ASCII_A_UPPER + topLevelDirCount);
        const keyStr = `1${dirLetter}`;
        const currentTier = 1;
        // 顶级根的父路径为null
        currentDirKeyInfo = {
          keyString: keyStr,
          normPath: normDirPath,
          parentPath: null,
          tier: currentTier,
          isDirectory: true
        };
        topLevelDirCount++;
        // 立即存储，以便在此调用中稍后需要时可用
        if (!pathToKeyInfo[normDirPath]) {
          pathToKeyInfo[normDirPath] = currentDirKeyInfo;
          newlyGeneratedKeys.push(currentDirKeyInfo);
          console.debug(`Assigned key '${currentDirKeyInfo.keyString}' to directory '${normDirPath}'`);
        } else { // 如果正确处理顶级目录，则不应发生
          console.warn(`Top-level directory '${normDirPath}' seems to be processed more than once.`);
          currentDirKeyInfo = pathToKeyInfo[normDirPath]; // 使用现有的
        }
      } else { // 这是一个子目录，其键是在处理其父目录时生成的
        currentDirKeyInfo = pathToKeyInfo[normDirPath];
        if (!currentDirKeyInfo) {
          // 这表明如果多线程（这里不是）可能存在逻辑缺陷或竞争条件
          console.error(`CRITICAL LOGIC ERROR: KeyInfo not found for directory '${normDirPath}' which should have been generated by its parent '${parentInfo ? parentInfo.normPath : 'None'}'. Halting.`);
          // 抛出错误可能比仅仅返回更好
          throw new KeyGenerationError(`KeyInfo missing for supposedly processed directory: ${normDirPath}`);
        }
      }

      // --- 处理此目录中的项目 ---
      let items: string[];
      try {
        // 使用readdirSync获取目录内容并排序
        items = fs.readdirSync(dirPath).sort();
      } catch (e) {
        console.error(`Error accessing directory '${dirPath}': ${e}`);
        return;
      }

      let fileCounter = 1;
      let subdirLetterOrd = ASCII_A_LOWER; // 此目录中 'a', 'b', ... 的计数器

      // 确定当前目录键是否表示子目录级别
      // 这是触发其子项提升的条件
      const parentKeyString = currentDirKeyInfo ? currentDirKeyInfo.keyString : null;
      // 检查使用匹配层级 + 大写 + 小写模式的正则表达式（此处不允许文件编号）
      const isParentKeyASubdir = Boolean(parentKeyString && /^[1-9]\d*[A-Z][a-z]$/.test(parentKeyString));

      console.debug(`Processing items in: '${normDirPath}' (Key: ${parentKeyString}, Is Subdir Key: ${isParentKeyASubdir})`);

      for (const itemName of items) {
        try {
          const itemPath = path.join(dirPath, itemName);
          const normItemPath = normalizePath(itemPath);

          // 使用fs.statSync获取项目信息
          const stats = fs.statSync(itemPath);
          const isDir = stats.isDirectory();
          const isFile = stats.isFile();

          // 应用标准排除（名称、类型、扩展名等）
          if (Array.from(exclusionSet).some(exPath => normItemPath.startsWith(exPath))) { // 再次检查可能匹配更深模式的项目
            console.debug(`Exclusion Check 1b: Skipping excluded item path: '${normItemPath}'`);
            continue;
          }
          if (excludedDirsNames.has(itemName) || itemName === ".gitkeep") {
            console.debug(`Exclusion Check 3: Skipping item name '${itemName}' in '${normDirPath}'`);
            continue;
          }
          if (itemName.endsWith("_module.md")) {
            console.debug(`Exclusion Check 4: Skipping mini-tracker '${itemName}' in '${normDirPath}'`);
            continue;
          }

          // 跳过既不是文件也不是目录的项目
          if (!(isDir || isFile)) {
            console.debug(`Skipping item '${itemName}' (not a file or directory) in '${normDirPath}'`);
            continue;
          }

          // 仅对文件检查扩展名排除
          if (isFile) {
            const ext = path.extname(itemName);
            if (excludedExts.has(ext)) {
              console.debug(`Exclusion Check 5: Skipping file '${itemName}' with extension '${ext}' in '${normDirPath}'`);
              continue;
            }
          }

          // --- 键生成逻辑 ---
          let itemKeyInfo: KeyInfo | null = null;

          // 确定父上下文
          const parentKeyString = currentDirKeyInfo ? currentDirKeyInfo.keyString : null;
          // 检查正在处理的*父目录*是否由子目录键表示
          const isParentDirASubdir = Boolean(parentKeyString && /^[1-9]\d*[A-Z][a-z]$/.test(parentKeyString));

          // <<< *** 修订的提升触发器 *** >>>
          // 提升仅在已经是子目录的目录内找到目录时发生
          const needsPromotion = isParentDirASubdir && isDir; // 在此处检查项目类型

          if (needsPromotion) {
            // --- 层级提升（仅由子子目录触发） ---
            // 此块现在仅对在键控子目录内找到的目录执行
            if (!parentKeyString) { // 如果needsPromotion为True，则应该不可能
              console.error(`Logic Error: Promotion needed but parent key string is missing for item '${itemName}'`);
              continue; // 跳过此项目
            }

            const [parsedParentTier, , parsedParentSubdirLetter] = parseKey(parentKeyString);
            if (parsedParentTier === null || parsedParentSubdirLetter === null) {
              console.error(`Logic Error: Could not parse parent key '${parentKeyString}' during promotion for DIR item '${itemName}'`);
              continue; // 跳过此项目
            }

            const newTier = parsedParentTier + 1;
            const newDirLetter = parsedParentSubdirLetter.toUpperCase(); // 提升的子目录成为目录

            // 在分配字符之前检查限制（此处仅适用于目录）
            if (subdirLetterOrd > ASCII_Z_LOWER) {
              const errorMsg = `Key generation failed: Exceeded maximum supported subdirectories (26, 'a'-'z') requiring promotion ` +
                `within parent directory key '${parentKeyString}' (path: '${normDirPath}'). ` +
                `Problematic item: '${itemName}' (path: '${normItemPath}'). ` +
                `Please reduce the number of direct subdirectories needing keys at this level ` +
                `or add problematic paths to exclusions in '.clinerules.config.json' ` +
                `(e.g., using 'cline-config --add-excluded-path "${normItemPath}"').`;
              console.error(errorMsg);
              throw new KeyGenerationError(errorMsg); // 终止生成
            }

            const newSubdirLetter = String.fromCharCode(subdirLetterOrd);
            const keyStr = `${newTier}${newDirLetter}${newSubdirLetter}`;
            subdirLetterOrd++;
            console.debug(`Promoting for DIR '${itemName}': parent '${parentKeyString}' -> new key '${keyStr}'`);

            // isDir在此块中始终为true
            itemKeyInfo = {
              keyString: keyStr,
              normPath: normItemPath,
              parentPath: normDirPath,
              tier: newTier,
              isDirectory: true
            };
          } else { // 无提升（项目是文件，或项目是其父不是子目录的目录）
            // --- 标准键分配 ---
            // 处理：
            // - 根目录中的文件（例如 1B1）
            // - 子目录中的文件（例如 1Ba1）<<-- 这是之前导致过早提升的情况
            // - 根目录中的目录（例如 1Ba）
            if (!currentDirKeyInfo) { // 应该只发生在初始根调用中
              console.error(`Logic Error: Missing currentDirKeyInfo for non-promotion case of item '${itemName}'`);
              continue; // 跳过此项目
            }

            const baseKeyPart = currentDirKeyInfo.keyString; // 例如 "1A" 或 "1Ba"
            const currentTier = currentDirKeyInfo.tier;

            if (isDir) { // 分配标准子目录键（例如 1Bb, 1Bc）
              // 在分配字符之前检查限制
              if (subdirLetterOrd > ASCII_Z_LOWER) {
                const errorMsg = `Key generation failed: Exceeded maximum supported subdirectories (26, 'a'-'z') ` +
                  `within parent directory key '${baseKeyPart}' (path: '${normDirPath}'). ` +
                  `Problematic item: '${itemName}' (path: '${normItemPath}'). ` +
                  `Please reduce the number of direct subdirectories needing keys at this level ` +
                  `or add problematic paths to exclusions in '.clinerules.config.json' ` +
                  `(e.g., using 'cline-config --add-excluded-path "${normItemPath}"').`;
                console.error(errorMsg);
                throw new KeyGenerationError(errorMsg); // 终止生成
              }

              const subdirLetter = String.fromCharCode(subdirLetterOrd);
              const keyStr = `${baseKeyPart}${subdirLetter}`;
              subdirLetterOrd++;
              console.debug(`Assigning standard subdir key '${keyStr}' for DIR item '${itemName}' under parent '${baseKeyPart}'`);
              
              itemKeyInfo = {
                keyString: keyStr,
                normPath: normItemPath,
                parentPath: normDirPath,
                tier: currentTier,
                isDirectory: true
              };
            } else { // isFile: 分配标准文件键（例如 1B1, 1Ba1, 1Ba2）
              const keyStr = `${baseKeyPart}${fileCounter}`;
              fileCounter++;
              console.debug(`Assigning standard file key '${keyStr}' for FILE item '${itemName}' under parent '${baseKeyPart}'`);
              
              itemKeyInfo = {
                keyString: keyStr,
                normPath: normItemPath,
                parentPath: normDirPath,
                tier: currentTier,
                isDirectory: false
              };
            }
          }

          // --- 验证，存储键并递归 ---
          if (itemKeyInfo) {
            if (validateKey(itemKeyInfo.keyString)) {
              if (pathToKeyInfo[normItemPath]) {
                // 如果目录在rootPaths中列出AND也是另一个rootPath的子目录，则可能发生这种情况
                console.warn(`Path '${normItemPath}' already has an assigned key '${pathToKeyInfo[normItemPath].keyString}'. Overwriting with new key '${itemKeyInfo.keyString}'. Check rootPaths/exclusions if unexpected.`);
              }
              pathToKeyInfo[normItemPath] = itemKeyInfo;
              newlyGeneratedKeys.push(itemKeyInfo);
              if (isDir) {
                // 将此项目的新生成信息作为父信息传递给递归调用
                processDirectory(itemPath, exclusionSet, itemKeyInfo);
              }
            } else {
              // 如果生成逻辑和限制正确，则理想情况下不应发生这种情况
              console.error(`Generated key '${itemKeyInfo.keyString}' for path '${normItemPath}' is invalid according to pattern '${HIERARCHICAL_KEY_PATTERN}'. Skipping item and its children.`);
              // 考虑在此处也抛出错误，因为它表明逻辑缺陷
              // throw new KeyGenerationError(`Invalid key generated: ${itemKeyInfo.keyString}`);
            }
          }
        } catch (itemErr) {
          // 捕获处理特定项目的错误，但继续处理目录中的其他项目
          console.error(`Error processing item '${itemName}' in directory '${dirPath}': ${itemErr}`);
          // 可选地，如果某些错误应该停止所有内容，则重新抛出：
          // if (itemErr instanceof KeyGenerationError) throw itemErr;
        }
      }
    } catch (err) {
      if (err instanceof KeyGenerationError) {
        // 向上传播特定错误以停止执行
        throw err;
      } else {
        // 捕获处理目录本身的一般错误
        console.error(`Failed to process directory '${dirPath}': ${err}`);
        // 决定是停止还是继续其他根路径
        // 现在，如果不是FileNotFoundError，则让它传播
        if (!(err instanceof Error && err.message.includes('ENOENT'))) { // 允许跳过之前处理的不存在的根
          throw err;
        }
      }
    }
  }

  // --- 主循环 ---
  for (const rootPath of rootPaths) {
    processDirectory(rootPath, exclusionSetForProcessing, null);
  }

  // 确保返回的列表包含唯一的KeyInfo对象（以防重新处理/重叠）
  // 使用Map保留顺序并确保基于KeyInfo相等的唯一性
  const uniqueNewKeysMap = new Map<string, KeyInfo>();
  for (const key of newlyGeneratedKeys) {
    uniqueNewKeysMap.set(key.keyString + key.normPath, key);
  }
  const uniqueNewKeys = Array.from(uniqueNewKeysMap.values());

  return [pathToKeyInfo, uniqueNewKeys];
}

/**
 * 验证键是否遵循层次化键格式
 * @param key 要验证的层次化键
 * @returns 如果有效则为true，否则为false
 */
export function validateKey(key: string): boolean {
  if (!key) return false; // 处理空字符串
  return HIERARCHICAL_KEY_PATTERN.test(key);
}

/**
 * 获取与层次化键字符串对应的文件/目录路径，
 * 可能使用上下文（由于非唯一键，需要谨慎使用）
 * 
 * @param keyString 层次化键字符串
 * @param pathToKeyInfo 将规范化路径映射到KeyInfo对象的字典
 * @param contextPath 可选的引用键的目录的规范化路径
 *                    如果多个路径共享相同的键字符串，则用于解决歧义
 * @returns 文件/目录路径，如果找不到键或没有上下文则为null
 */
export function getPathFromKey(
  keyString: string,
  pathToKeyInfo: Record<string, KeyInfo>,
  contextPath?: string
): string | null {
  const matchingInfos = Object.values(pathToKeyInfo).filter(info => info.keyString === keyString);

  if (matchingInfos.length === 0) {
    console.debug(`Key string '${keyString}' not found in pathToKeyInfo map.`);
    return null;
  }
  if (matchingInfos.length === 1) {
    return matchingInfos[0].normPath;
  }

  // 歧义键 - 需要上下文
  if (contextPath) {
    const normContextPath = normalizePath(contextPath);
    // 寻找其parentPath与contextPath匹配的匹配项
    for (const info of matchingInfos) {
      // 确保在比较之前parentPath不为null
      if (info.parentPath && normalizePath(info.parentPath) === normContextPath) {
        console.debug(`Resolved ambiguous key '${keyString}' using context '${normContextPath}' to path '${info.normPath}'`);
        return info.normPath;
      }
    }

    // 如果没有直接子匹配，可以添加更复杂的逻辑（例如，检查祖父母）如果需要
    console.warn(`Ambiguous key '${keyString}' found. Context path '${normContextPath}' provided, but no direct child match found among ${matchingInfos.length} possibilities: ${matchingInfos.map(i => i.normPath)}.`);
    return null; // 或抛出？或返回列表？现在，返回null
  } else {
    console.warn(`Ambiguous key '${keyString}' found. Multiple paths match: ${matchingInfos.map(i => i.normPath)}. Provide contextPath for disambiguation.`);
    return null; // 或抛出？或返回列表？现在，返回null
  }
}

/**
 * 获取与文件/目录路径对应的层次化键字符串
 * 
 * @param path 文件/目录路径
 * @param pathToKeyInfo 将规范化路径映射到KeyInfo对象的字典
 * @returns 层次化键字符串，如果找不到路径则为null
 */
export function getKeyFromPath(path: string, pathToKeyInfo: Record<string, KeyInfo>): string | null {
  const normPath = normalizePath(path);
  const info = pathToKeyInfo[normPath];
  return info ? info.keyString : null;
}

/**
 * 层次化排序键字符串列表（自然排序顺序）
 * 例如，1A1, 1A2, 1A10 而不是 1A1, 1A10, 1A2
 * 
 * @param keys 键字符串列表
 * @returns 包含排序后的键字符串的新列表
 */
export function sortKeyStringsHierarchically(keys: string[]): string[] {
  function sortKeyFunc(keyStr: string): (string | number)[] {
    if (!keyStr || typeof keyStr !== 'string') return []; // 处理无效输入
    const parts = keyStr.match(KEY_PATTERN) || [];
    // 将数字部分转换为整数以进行正确的数字排序
    try {
      // 确保层级（如果是数字，则为第一部分）被正确处理
      // 模式正确拆分，只需要转换
      const convertedParts = parts.map(p => /^\d+$/.test(p) ? parseInt(p) : p);
      return convertedParts;
    } catch (error) {
      console.warn(`Could not convert parts for sorting key string '${keyStr}', using basic string sort.`);
      return parts; // 回退
    }
  }

  // 在排序之前过滤掉潜在的null或非字符串元素
  const validKeys = keys.filter(k => typeof k === 'string' && k);
  return validKeys.sort((a, b) => {
    const partsA = sortKeyFunc(a);
    const partsB = sortKeyFunc(b);
    
    // 比较每个部分
    for (let i = 0; i < Math.min(partsA.length, partsB.length); i++) {
      const partA = partsA[i];
      const partB = partsB[i];
      
      // 如果两个部分都是数字，进行数字比较
      if (typeof partA === 'number' && typeof partB === 'number') {
        if (partA !== partB) return partA - partB;
      } 
      // 如果两个部分都是字符串，进行字符串比较
      else if (typeof partA === 'string' && typeof partB === 'string') {
        if (partA !== partB) return partA.localeCompare(partB);
      }
      // 如果类型不同，数字优先
      else if (typeof partA === 'number' && typeof partB === 'string') {
        return -1;
      }
      else if (typeof partA === 'string' && typeof partB === 'number') {
        return 1;
      }
    }
    
    // 如果所有比较的部分都相等，较短的键优先
    return partsA.length - partsB.length;
  });
}

/**
 * 基于主要是层级，然后是键字符串的自然排序，对KeyInfo对象列表进行排序
 * 
 * @param keyInfoList 要排序的KeyInfo对象列表
 * @returns 排序后的KeyInfo对象列表
 */
export function sortKeys(keyInfoList: KeyInfo[]): KeyInfo[] {
  function sortKeyFunc(keyInfo: KeyInfo): [(number | null), (string | number)[]] {
    // 处理潜在的null值，如果列表源不能保证干净
    if (!keyInfo || !keyInfo.keyString) return [Infinity, []];

    const key = keyInfo.keyString;
    const parts = key.match(KEY_PATTERN) || [];
    // 将数字部分转换为整数以进行正确的数字排序
    try {
      const convertedParts = parts.map(p => /^\d+$/.test(p) ? parseInt(p) : p);
      return [keyInfo.tier, convertedParts];
    } catch (error) {
      // 如果部分包含意外的非数字/非字母字符，则回退
      console.warn(`Could not convert parts for sorting key '${key}', using basic string sort.`);
      return [keyInfo.tier, parts]; // 如果转换失败，则使用原始部分
    }
  }

  return [...keyInfoList].sort((a, b) => {
    const [tierA, partsA] = sortKeyFunc(a);
    const [tierB, partsB] = sortKeyFunc(b);

    // 首先按层级排序
    if (tierA !== tierB) {
      return (tierA === null ? Infinity : tierA) - (tierB === null ? Infinity : tierB);
    }

    // 然后按键字符串的各部分排序
    for (let i = 0; i < Math.min(partsA.length, partsB.length); i++) {
      const partA = partsA[i];
      const partB = partsB[i];
      
      // 如果两个部分都是数字，进行数字比较
      if (typeof partA === 'number' && typeof partB === 'number') {
        if (partA !== partB) return partA - partB;
      }
      // 如果两个部分都是字符串，进行字符串比较
      else if (typeof partA === 'string' && typeof partB === 'string') {
        if (partA !== partB) return partA.localeCompare(partB);
      }
      // 如果类型不同，数字优先
      else if (typeof partA === 'number' && typeof partB === 'string') {
        return -1;
      }
      else if (typeof partA === 'string' && typeof partB === 'number') {
        return 1;
      }
    }
    
    // 如果所有比较的部分都相等，较短的键优先
    return partsA.length - partsB.length;
  });
}

/**
 * 使用新的上下文逻辑重新生成给定根路径的键
 *
 * @param rootPaths 要处理的根目录路径列表
 * @param excludedDirs 可选的要排除的目录名称集合
 * @param excludedExtensions 可选的要排除的文件扩展名集合
 * @param precomputedExcludedPaths 可选的预计算的要排除的绝对路径集合
 * @returns 包含以下内容的元组：
 *          - 将规范化路径映射到KeyInfo对象的字典
 *          - 新生成的KeyInfo对象列表
 * @throws FileNotFoundError 如果根路径不存在
 * @throws KeyGenerationError 如果违反键生成规则（例如，>26个子目录）
 */
export function regenerateKeys(
  rootPaths: string | string[],
  excludedDirs?: Set<string>,
  excludedExtensions?: Set<string>,
  precomputedExcludedPaths?: Set<string>
): [Record<string, KeyInfo>, KeyInfo[]] {
  // 简单调用主生成函数
  return generateKeys(rootPaths, excludedDirs, excludedExtensions, precomputedExcludedPaths);
}

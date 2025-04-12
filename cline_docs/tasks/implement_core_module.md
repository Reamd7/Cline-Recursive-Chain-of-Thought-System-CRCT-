# Task: 实现核心模块
   **Parent:** `implementation_plan_typescript_dependency_system.md`
   **Children:** 无

## 目标
使用TypeScript实现依赖处理系统的核心模块，包括依赖网格操作、键管理和异常处理。

## 上下文
核心模块是依赖处理系统的基础，提供了依赖网格操作、键管理和异常处理等功能。这些功能被系统的其他部分广泛使用，因此需要首先实现。核心模块对应于Python版本中的`cline_utils/dependency_system/core`目录。

## 重要原则
**本任务必须遵循以下核心原则：**
1. **不得修改Python代码**：Python实现被视为参考实现，所有的代码修改都只应该应用于TypeScript实现。
2. **TypeScript代码必须与Python代码一致**：如果发现TypeScript实现与Python实现之间存在差异，应始终通过修改TypeScript代码使其与Python实现保持一致。
3. **保持接口和行为完全一致**：确保两个版本的接口参数、返回值、异常处理和边缘情况行为完全一致。

## 步骤
1. 实现`exceptions.ts`文件
   - 在`src/ts-dependency-system/core`目录下创建`exceptions.ts`文件
   - 定义自定义异常类，如`KeyGenerationError`、`GridValidationError`等
   - 确保异常类继承自JavaScript的`Error`类，并提供适当的错误消息

2. 实现`dependency-grid.ts`文件
   - 在`src/ts-dependency-system/core`目录下创建`dependency-grid.ts`文件
   - 实现`compress`函数，使用运行长度编码（RLE）压缩依赖字符串
   - 实现`decompress`函数，解压缩RLE编码的依赖字符串
   - 实现`createInitialGrid`函数，创建初始依赖网格
   - 实现`getCharAt`和`setCharAt`函数，用于访问和修改压缩字符串中的字符
   - 实现`validateGrid`函数，验证依赖网格的一致性
   - 实现`addDependencyToGrid`和`removeDependencyFromGrid`函数，用于添加和删除依赖关系
   - 实现`getDependenciesFromGrid`函数，获取特定键的依赖关系
   - 实现`formatGridForDisplay`函数，格式化网格以便显示

3. 实现`key-manager.ts`文件
   - 在`src/ts-dependency-system/core`目录下创建`key-manager.ts`文件
   - 定义`KeyInfo`接口，存储生成的键的信息
   - 实现`generateKeys`函数，为文件和目录生成层次化、上下文相关的键
   - 实现`validateKey`函数，验证键是否符合层次化键格式
   - 实现`getPathFromKey`和`getKeyFromPath`函数，在键和路径之间进行转换
   - 实现`sortKeyStringsHierarchically`函数，对键字符串进行层次化排序
   - 实现`sortKeys`函数，对`KeyInfo`对象进行排序
   - 实现`regenerateKeys`函数，使用新的上下文逻辑重新生成键

4. 实现`index.ts`文件
   - 在`src/ts-dependency-system/core`目录下创建`index.ts`文件
   - 导出所有核心模块的公共API，以便其他模块使用

5. 编写单元测试
   - 在`src/ts-dependency-system/tests/core`目录下创建测试文件
   - 为`exceptions.ts`、`dependency-grid.ts`和`key-manager.ts`编写单元测试
   - 确保测试覆盖所有主要功能和边缘情况

## 依赖关系
- 要求：[设置TypeScript项目结构]
- 阻塞：[实现工具模块]、[实现IO模块]、[实现分析模块]、[实现命令行接口]

## 预期输出
一个完整的核心模块实现，包括以下内容：
- `exceptions.ts`文件，包含自定义异常类
- `dependency-grid.ts`文件，包含依赖网格操作函数
- `key-manager.ts`文件，包含键管理函数
- `index.ts`文件，导出公共API
- 单元测试文件，验证核心模块的功能

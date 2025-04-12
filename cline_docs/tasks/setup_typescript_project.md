# Task: 设置TypeScript项目结构
   **Parent:** `implementation_plan_typescript_dependency_system.md`
   **Children:** 无

## 目标
创建TypeScript项目的基本结构，包括目录、配置文件和依赖项，为后续实现依赖处理系统的各个模块做准备。

## 上下文
我们需要使用TypeScript + Node技术重新实现`cline_utils`目录中的Python依赖处理系统。在开始实现具体功能之前，需要先设置项目的基本结构，包括创建目录、配置TypeScript编译器、安装必要的依赖项等。

## 重要原则
**本任务必须遵循以下核心原则：**
1. **不得修改Python代码**：Python实现被视为参考实现，所有的代码修改都只应该应用于TypeScript实现。
2. **TypeScript代码必须与Python代码一致**：如果发现TypeScript实现与Python实现之间存在差异，应始终通过修改TypeScript代码使其与Python实现保持一致。
3. **保持接口和行为完全一致**：确保两个版本的接口参数、返回值、异常处理和边缘情况行为完全一致。

## 步骤
1. 在`src`目录下创建`ts-dependency-system`目录，作为TypeScript实现的根目录
2. 创建项目的基本目录结构, 参考 python 目录中的文件结构
   - 创建`src/ts-dependency-system/core`目录，用于存放核心模块
   - 创建`src/ts-dependency-system/utils`目录，用于存放工具模块
   - 创建`src/ts-dependency-system/io`目录，用于存放IO模块
   - 创建`src/ts-dependency-system/analysis`目录，用于存放分析模块
   - 创建`src/ts-dependency-system/tests`目录，用于存放测试文件
   - 创建`src/ts-dependency-system/bin`目录，用于存放可执行文件
3. 初始化Node.js项目
   - 在`src/ts-dependency-system`目录下运行`npm init -y`命令，创建`package.json`文件
   - 修改`package.json`文件，添加项目名称、描述、作者等信息，读取 pnpm 和 node 当前版本并限定在 package.json 中
   - 配置npmrc, 更换npm源 `registry=https://registry.npmmirror.com/`
4. 安装TypeScript和其他必要的依赖项
   - 安装TypeScript：`pnpm install typescript --save-dev`
   - 安装类型定义：`pnpm install @types/node --save-dev`
   - 安装测试框架：`pnpm install jest @types/jest @swc/core @swc/jest --save-dev`
   - 安装命令行工具：`pnpm install commander --save`
   - 安装文件系统工具：`pnpm install fs-extra @types/fs-extra --save`
   - 安装ts运行工具：`pnpm install tsx --save`
5. 配置TypeScript编译器
   - 在`src/ts-dependency-system`目录下创建`tsconfig.json`文件
   - 配置编译选项，包括目标ECMAScript版本、模块系统、输出目录等
6. 配置Jest测试框架
   - 在`src/ts-dependency-system`目录下创建`jest.config.js`文件
   - 配置Jest以支持TypeScript测试
7. 创建入口文件
   - 在`src/ts-dependency-system`目录下创建`index.ts`文件，作为模块的主入口
   - 在`src/ts-dependency-system/bin`目录下创建`dependency-processor.ts`文件，作为命令行工具的入口
8. 更新`package.json`文件，添加脚本命令
   - 添加构建命令：`"build": "tsc"`
   - 添加测试命令：`"test": "jest"`
   - 添加启动命令：`"start": "tsx ./src/dependency-processor.ts"`

## 依赖关系
- 要求：无
- 阻塞：[实现核心模块]、[实现工具模块]、[实现IO模块]、[实现分析模块]、[实现命令行接口]

## 预期输出
一个完整的TypeScript项目结构，包括以下内容：
- 项目目录结构
- `package.json`文件，包含项目信息和依赖项
- `tsconfig.json`文件，包含TypeScript编译器配置
- `jest.config.js`文件，包含Jest测试框架配置
- 入口文件`index.ts`和`dependency-processor.ts`
- 已安装的依赖项
- 测试 `tsx ./src/index.ts` 是能够正常运行的, 简单输出为 `hello world` 即可。

# Translation Contract: Markdown 文档翻译

**Feature**: 项目代码与文档多语言支持 | **Date**: 2025-12-29
**Version**: 1.0

## 概述 | Overview

本文档定义了 Markdown 文档翻译的契约和规范,确保所有翻译遵循统一的标准和格式。

---

## 翻译格式规范 | Translation Format Specification

### 段落交替格式 (Paragraph Alternating Format)

所有 Markdown 文档必须采用段落交替格式,即原文段落后紧跟对应的翻译段落。

#### 规则 | Rules

1. **标题翻译** (Headings):
   ```markdown
   # English Title

   ## 中文标题 | English Title

   ### Subtitle

   #### 子标题 | Subtitle
   ```

2. **段落翻译** (Paragraphs):
   ```markdown
   This is the original English paragraph that provides some information.

   这是原始英文段落的中文翻译,提供相同的信息。

   Another paragraph in English.

   另一个英文段落的翻译。
   ```

3. **列表翻译** (Lists):
   ```markdown
   - First item in English
   - 第一项的中文翻译 | First item

   - Second item in English
   - 第二项的中文翻译 | Second item

   - Third item in English
   - 第三项的中文翻译 | Third item
   ```

4. **代码块处理** (Code Blocks):
   ```markdown
   Here is a code example:

   ```python
   def hello():
       print("Hello, World!")
   ```

   以下是一个代码示例:

   ```python
   def hello():
       print("Hello, World!")
   ```

   代码说明: This function prints a greeting message.
   代码说明: 此函数打印一条问候消息。
   ```

5. **表格翻译** (Tables):
   ```markdown
   | English Header 1 | English Header 2 |
   | -----------------| ------------------|
   | Cell 1           | Cell 2            |

   | 中文表头 1 | 中文表头 2 |
   | ----------- | ----------- |
   | 单元格 1    | 单元格 2    |

   Or use inline translation:

   | Header 1 / 表头 1 | Header 2 / 表头 2 |
   | ------------------| -------------------|
   | Cell 1 / 单元格 1 | Cell 2 / 单元格 2  |
   ```

---

## 质量标准 | Quality Standards

### 准确性 (Accuracy)
- **忠实原文**: 翻译必须准确传达原文的含义,不得添加或删除信息
- **技术术语**: 技术术语必须使用统一的翻译对照表 (见 research.md)
- **上下文一致**: 同一概念在文档中必须使用相同的翻译

### 可读性 (Readability)
- **自然流畅**: 翻译应符合中文表达习惯,避免直译痕迹
- **简洁明确**: 避免冗余和啰嗦,保持句式简洁
- **专业规范**: 使用专业术语和正式书面语

### 格式一致性 (Format Consistency)
- **结构保持**: 必须保持原文的标题层级、列表和表格结构
- **标记规范**: 使用统一的标记格式区分原文和译文
- **标点符号**: 中文翻译应使用中文标点符号

---

## 验收标准 | Acceptance Criteria

### 文件级别检查
每个翻译后的 Markdown 文件必须满足:

1. **完整性**:
   - [ ] 所有非代码内容都有对应的中文翻译
   - [ ] 翻译覆盖率 ≥ 95%

2. **格式正确性**:
   - [ ] Markdown 语法正确,无渲染错误
   - [ ] 段落交替格式一致
   - [ ] 代码块未被翻译或修改

3. **质量检查**:
   - [ ] 技术术语使用一致
   - [ ] 翻译准确且可读
   - [ ] 无明显语法或拼写错误

### 段落级别检查
每个翻译段落必须满足:

1. **语义一致性**: 翻译与原文含义一致
2. **风格一致性**: 翻译风格与整体文档一致
3. **格式一致性**: 遵循段落交替格式

---

## 禁止行为 | Prohibited Actions

1. **禁止修改代码**:
   - 代码块必须保持原样,不得修改或翻译
   - 代码注释应单独添加在代码块下方

2. **禁止遗漏翻译**:
   - 不得跳过任何段落、列表项或表格
   - 如遇无法翻译的内容,应在翻译中标注 `[待翻译]` 或 `[To be translated]`

3. **禁止改变结构**:
   - 不得改变标题层级
   - 不得改变列表或表格的结构

4. **禁止机器翻译直接使用**:
   - 不得直接使用未审查的机器翻译
   - 所有翻译必须经过人工审查和修正

---

## 例外情况 | Exceptions

### 无需翻译的内容
1. **代码块**: 代码本身不需要翻译,但可添加中文说明
2. **命令示例**: 如 `npm install`、`git clone` 等命令保持原样
3. **URL 和链接**: URL 和路径保持原样
4. **专有名词**: 如 "Python"、"JavaScript"、"GitHub" 等通常保留原文

### 特殊处理
1. **技术术语**: 使用双语格式,如 "Chain-of-Thought (思维链)"
2. **首次出现**: 技术术语首次出现时应提供完整翻译和英文原文
3. **后续引用**: 后续引用可直接使用中文或保留英文 (根据上下文)

---

## 示例 | Examples

### 良好翻译示例 | Good Translation Example

```markdown
## Installation

Install the required dependencies using pip:

## 安装 | Installation

使用 pip 安装所需的依赖项:

```bash
pip install -r requirements.txt
```

After installation, you can verify the setup by running:

安装完成后,您可以通过运行以下命令来验证设置:

```bash
python -m pytest tests/
```
```

### 不良翻译示例 | Bad Translation Example

```markdown
## Installation

Install the required dependencies using pip:

## 安装
安装所需依赖:

```bash
pip install
```

[错误: 缺少命令参数,且未使用段落交替格式]
```

---

## 参考资源 | Reference Resources
- [Markdown 规范](https://commonmark.org/)
- [技术写作最佳实践](https://developers.google.com/tech-writing)
- [中文技术文档规范](https://zh.wikipedia.org/wiki/Wikipedia:格式手册/技术)

---

**文档版本**: 1.0 | **最后更新**: 2025-12-29

---
name: patent-disclosure-skill
description: "通用中国专利挖掘发现与交底书生成全流程：扫描项目文档挖掘专利点、讨论融合、权利要求7步法构造保护点、基于脱敏模版生成技术交底书（含名称规范/发明内容三步结构/产品方法两类实施方式/实施例布局策略）、联网查新、公式定稿（Unicode→LaTeX→pandoc→Word OMML原生公式）、生成后自检。| Patent mining, disclosure drafting with 7-step claims method, prior-art search, formula-to-OMML conversion, and consistency self-check."
version: "1.10.0"
user-invocable: true
argument-hint: "[可选：项目路径或技术主题关键词]"
allowed-tools: Read, Write, Edit, Grep, Glob, WebSearch, Bash
---

# 专利挖掘与交底书生成

本技能覆盖 **专利点挖掘** → **查新与差异化** → **交底书生成** → **自检完善** 全流程；分步指令在 **`prompts/`**，每步执行前 **`Read`** 对应文件，与步骤的对照见「Prompt 文件映射」。

## 环境与约定

- **语言**：默认与用户语种一致；专利与法律术语采用行业常用表述。
- **图示定稿（Step 7）**：**3.2**/**3.4** 用 fenced **mermaid**；执行方式、**`mmdc`** 安装与降级规则见下表「交底书定稿交付」行及 **`tools/README.md`**（正文不要求 ASCII 框图或 PlantUML）。
- **公式定稿（Step 7→Step 9）**：交底书 `.md` 中**围栏代码块公式**须经 **`tools/fix_formulas.py`** 转为 LaTeX `$$` display math，再用 **`pandoc`**（`-f markdown+tex_math_dollars`）生成 DOCX——pandoc 原生将 LaTeX 数学转为 Word OMML 公式对象。行内 Unicode 公式（`ν̇²`, `Δx` 等）无需额外处理，Word 现代版本可直接渲染。
- **权利要求构造**：在 Step 3–4 专利点分析和 Step 7 第五章保护点编写时，遵循 **`prompts/claims_drafting.md`**「权利要求书撰写7步法」——核心原则「顶天立地」，从核心区别特征一句话描述出发，经最小技术特征集→核心独权→从权分层→其他权利要求组的系统化流程。

---

## 触发条件

在用户使用以下任一方式时启用本技能：

- 明确提及：专利挖掘、专利点、技术交底书、交底书、专利交底书、查新、现有技术对比等
- 斜杠或简短指令：如 `/patent-disclosure-skill`、`/patent-disclosure`、`/交底书`
- **迭代模式（按意图识别）**：当用户意图明显是在**已有交底书或上一轮输出**上继续工作（如改章节、补实施例、补材料、修正参数/事实、调整表述等），**无需**用户写出「迭代」等固定词，也**不必**询问是否进入迭代——Agent 应 **`Read`** **`prompts/iteration_context.md`**，再 **`Read`** `prompts/merger.md`（侧重**新材料、扩展合并**）或 `prompts/correction_handler.md`（侧重**纠错、与事实或风格不符**），**严格按该文件开头的「执行门禁」**（优先执行，不可跳过）**做完合并或纠正**，**另存为新文件**：**`{案件名}_{YYYYMMDDHHmmss}.md`** 与同名 **`.docx`**（与首次定稿同一命名规则，见 **`disclosure_builder.md` §7.3 第 5 点**），**不覆盖**旧稿（除非用户明确要求）。**禁止**在迭代意图已成立时默认回到 Step 3–4 专利点全文分析（除非用户明确要求重新挖掘专利点）。对话中**已出现**交底书路径、附件或上文刚交付的草稿时，优先按迭代处理。

---

## 工具与数据来源

按任务选用能力；具体工具名称以当前 Agent 环境为准。

若扫描范围内含 **Word（.docx）** 或 **PowerPoint（.pptx）**，须在 Step 2 纳入阅读前用本仓库 **`docx_to_md.py`** / **`pptx_to_md.py`** 转为 Markdown；依赖 **`pip install -r requirements.txt`**，命令与说明见下表对应行。

### 常见任务与建议方式

| 任务 | 建议方式 |
|------|----------|
| 加载分步指令 | **`Read`** → `${CLAUDE_SKILL_DIR}/prompts/*.md`，见下表 |
| 读代码、设计文档、PDF、图片 | 文件读取工具；大仓库先用搜索/语义检索定位再精读 |
| Word（.docx）→ Markdown + 抽取图片（扫描前） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/docx_to_md.py --input {path}.docx --output {dir}/{name}.md`；图片默认写入与 `.md` 同级的 `{name}_media/`；需 `pip install -r requirements.txt`（含 mammoth）；复杂版式可改由所内导出 PDF/MD 再扫 |
| PowerPoint（.pptx）→ Markdown + 抽取图片（扫描前） | `Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/pptx_to_md.py --input {path}.pptx --output {dir}/{name}.md`；默认 `{name}_media/`；需 `pip install -r requirements.txt`（含 python-pptx）；**旧版 .ppt 不支持**，请先另存为 `.pptx`；图表/SmartArt 等若未以图片形状嵌入则可能仅能从备注或另行导出补全 |
| 罗列目录、按名找文件 | 目录列举 / 按文件名搜索 |
| 联网查新（Step 5） | 执行前 **`Read`** `prompts/prior_art_search.md`。**中国专利公布公告**：优先 **`Bash`** 运行 `cnipa_epub_search.py`；**须在生成命令前**归纳 **2～8 个相关度高的语义块**；**执行时须分多次调用**，**每次仅传一个**词块，**自行按 `pub_number` 合并**多轮 `EPUB_HITS_JSON`（勿单次工具调用堆多个 argv，见该 prompt）。一步拉取+解析、**不写 HTML 落盘**；须 **`pip install -r tools/requirements-cnipa.txt`** 且 **`python -m playwright install chromium`**。**`abstract` 规定必用**同该 prompt。需整句一次 AND 或保存 HTML 时用 `cnipa_epub_crawler.py`；异常或无果再 **WebSearch** |
| 交底书定稿交付（**须同时** .md + .docx） | **3.2** 系统框图与 **3.4** 流程图均用 fenced ``mermaid``，**不要** ASCII 文字流程图/框图。定稿执行 **`tools/mermaid_render.py`**：mermaid 转 PNG（失败块保留围栏）后默认生成同名 **.docx**；若 Word 失败，按 stderr 提示手动运行 **`md_to_docx.py`**。详见 **`tools/README.md`** |
| **公式定稿：Markdown → DOCX（含 Word 原生公式）** | **Step 9 必做**。`Bash` → `python3 ${CLAUDE_SKILL_DIR}/tools/fix_formulas.py -i {草稿}.md -o /tmp/{name}_math.md`，将围栏代码块公式转为 LaTeX `$$` 块（含 Unicode→LaTeX 约 80 个映射），再 `Bash` → `pandoc /tmp/{name}_math.md -f markdown+tex_math_dollars -t docx --resource-path={图片目录} -o {输出}.docx`。pandoc 原生将 LaTeX 数学转为 Word OMML 公式对象。需已安装 **pandoc**（`brew install pandoc` 或等效） |
| 保存交底书路径 | 写入用户指定路径；未指定时可建议 `./outputs/{案件标识}/`；**凡交付的** `.md` / `.docx` 须为 **`{案件名}_{YYYYMMDDHHmmss}`**（§7.3 第 5 点，**含首次定稿与迭代**），勿默认覆盖旧稿；`outputs/` 整目录默认由 `.gitignore` 忽略 |
| 迭代对话留档 | 每轮 **merger / correction** 交付后，在案件目录追加 **`交底书修订对话记录.md`**（**`tools/iteration_dialog_log.py`** 或等价手工），见 **`prompts/iteration_context.md`** |

---

## Prompt 文件映射

| 步骤 | 文件 | 用途 |
|------|------|------|
| Step 1 | `prompts/intake.md` | 边界与输入问题 |
| Step 2 | `prompts/project_scan.md` | 项目文档扫描；**须**对 `.docx`/`.pptx` 先转换再读（见该文件「Office 文档」节）；独立图片目录可跳过 |
| Step 3–4 | `prompts/patent_points_analyzer.md` | 候选专利点、融合与选定（含权利要求7步法步骤一～三：核心区别特征、最小特征集、技术主题审定） |
| Step 5 | `prompts/prior_art_search.md` | 联网查新与分析要求 |
| Step 6 | `prompts/disclosure_preview.md` | 全文前的摘要预览 |
| Step 7 | `prompts/disclosure_builder.md` + `prompts/template_reference.md` + `prompts/claims_drafting.md` | 交底书结构、脱敏与图示规范（含发明名称规范、发明内容三步结构、具体实施方式产品/方法两类范例、实施例布局策略）；**mermaid 系统框图与流程图范例在 template_reference**；**第五章保护点层次构造按 claims_drafting 步骤五～七** |
| Step 8 | `prompts/disclosure_self_check.md` | 内部自检（含名称规范、实施例充分性、保护点层次），不写入正文 |
| Step 9 | `tools/fix_formulas.py` + pandoc | 公式定稿：围栏代码块→LaTeX `$$`→pandoc→Word OMML 原生公式对象；详见工具表「公式定稿」行 |
| 迭代 | `prompts/iteration_context.md` | 迭代意图、落盘命名、**修订对话记录 md**（含对话/记录时间） |
| 迭代 | `prompts/merger.md` | 新材料增量合并；**文首含门禁**；输出 `{案件名}_{时间戳}.md`/`.docx` |
| 迭代 | `prompts/correction_handler.md` | 对话纠正；**文首含门禁**；输出 `{案件名}_{时间戳}.md`/`.docx` |

---

## 主流程（执行顺序）

1. **`Read`** `intake.md` → 执行 Step 1  
2. **`Read`** `project_scan.md` → 执行 Step 2  
3. **`Read`** `patent_points_analyzer.md` → 执行 Step 3–4  
4. **`Read`** `prior_art_search.md` → 执行 Step 5  
5. **`Read`** `disclosure_preview.md` → 执行 Step 6；用户可跳过  
6. **`Read`** `disclosure_builder.md`、**`Read`** `template_reference.md` 与 **`Read`** `claims_drafting.md` → 执行 Step 7（**首次交付**的 `.md`/`.docx` 亦须 **`{案件名}_{YYYYMMDDHHmmss}`**，§7.3 第 5 点）  
7. **`Read`** `disclosure_self_check.md` → 内部执行 Step 8，修订后交付  
8. **公式定稿**：执行 Step 9——`fix_formulas.py` 将围栏代码块公式转 LaTeX `$$` → **`pandoc`** 生成含 Word OMML 原生公式的 `.docx`，覆盖 `mermaid_render.py` 生成的纯文本版 DOCX。若 `.md` 中无围栏代码块公式，可跳过 `fix_formulas.py`，但仍建议用 pandoc 重转 DOCX 以保持公式兼容性  

**禁止**：交底书正文中包含「自检清单」章节；自检仅内部使用。

---

## 迭代模式（摘要）

**启用方式**：根据用户**自然语言意图**判断（见上文「触发条件」），**不要求**固定关键词，**默认不**为「是否迭代」打断用户。

- **补充材料 / 扩展章节**：`Read` → `iteration_context.md` → `merger.md`；合并结果**另存为**带时间戳的 `.md`/`.docx`（§7.3 第 5 点）；**追加** `交底书修订对话记录.md`（`iteration_dialog_log.py` 或手工）；完成后**必须**输出「合并摘要」留档  
- **指出错误 / 与事实或参数不符**：`Read` → `iteration_context.md` → `correction_handler.md`；纠正结果**另存为**带时间戳的 `.md`/`.docx`；**追加**对话记录；完成后**必须**输出「纠正摘要」留档  

主流程 Step 7→8 的 **`disclosure_self_check.md`** 仍在新稿定稿路径上内部执行。

---

## Agent 自用工作流检查清单

```
□ 已按步骤 Read 对应 prompts；Step 2 若目录含 Office，已执行 docx_to_md / pptx_to_md 并读了产出 `.md`
□ 识别到「在已有交底书上修改」类意图时，已 Read `iteration_context.md` 并选用 merger 或 correction_handler（而非从头跑扫描）；交付为**新** `{案件名}_{时间戳}.md`/`.docx`，未无故覆盖旧稿
□ 执行 merger / correction_handler 后，已在对话中输出该文件要求的留档摘要（合并摘要 / 纠正摘要）；案件目录已追加 **`交底书修订对话记录.md`**（或等价日志）
□ Step 3–4 已执行权利要求7步法步骤一～三：每个候选专利点有核心区别特征一句话描述 + 关键创新点；融合后有最小技术特征集；技术主题已审定（检查过窄/过宽）
□ 查新完成且写入 1.1 与区别论述（符合 `prior_art_search.md`：**优先** `tools/cnipa_epub_search.py`，**国知局侧已分多次调用、每轮一词，并已自行合并** `EPUB_HITS_JSON`；**`abstract` 必用且已充分理解后再概括**；异常或无果再 **WebSearch**）
□ 除用户明确跳过外，完成摘要预览
□ Step 7 已 `Read` `claims_drafting.md`；第五章保护点按步骤五～七层次布置（独立→从属→其他组）；发明名称符合规范（≤25字/技术术语/无宣传语）；发明内容三步结构完整；具体实施方式按产品/方法类型正确撰写；实施例充分支持权利要求保护范围
□ 脱敏、mermaid（定稿均已渲染为 PNG）、章节引用符合 template_reference；**已交付 .md 与 .docx**，且**文件名符合 §7.3 第 5 点**（**凡交付均含**时间戳后缀）；**正文无**技能/示例仓库类文末脚注
□ 自检在后台完成（含名称规范、实施例充分性、保护点层次），正文无自检清单章节
□ Step 9 公式定稿：`.md` 中围栏代码块已通过 `fix_formulas.py` 转为 `$$` LaTeX math；已用 **pandoc**（`-f markdown+tex_math_dollars`）生成最终 `.docx`，公式为 Word OMML 原生对象；pandoc 无 `\Deltax` 等非法 LaTeX 命令警告
```

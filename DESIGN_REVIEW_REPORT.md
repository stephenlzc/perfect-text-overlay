# GenImageText 项目解构与「美学 / 多样化」改进报告

> 结论先行：这个项目在**工程上很扎实**（字体回退、RTL/bidi、自动收缩、并发批处理、安全区可读性评分都做得不错），
> 但它的本质是「**确定性配置渲染器**」，不是「**设计引擎**」。它只保证「文字能读、不压主体」，几乎不做「让画面变好看」的决策。
> 所以你会觉得：加文字机械、底图单一、没有美感——这不是错觉，是架构定位决定的。

---

## 一、项目全景解构

### 1.1 一句话定位

**GenImageText 不是生图工具，是「给 AI 生图加规范文字」的工具链。**

核心思想是「图像生成」和「文字排版」分离：生图交给用户自己的工具（Midjourney / GPT Image 2 / SD / Gemini…），
本工具只负责：拆提示词 → 分析图片找安全区 → 叠加文字。这正好解释了「生图没问题」——生图本来就不是它做的。

### 1.2 模块地图（数据流）

| 模块 | 职责 | 输入 → 输出 |
|---|---|---|
| `gen_ecommerce.py` | CLI 入口 | 子命令 `init / prompt / render / batch / validate / check` |
| `scripts/prompt_separator.py` | 提示词分离 | 用户提示词 → 纯图提示词 + 文字需求 + 安全区 |
| `scripts/config_loader.py` | 模板配置校验 | `template.yaml` → Pydantic `TemplateConfig` |
| `scripts/i18n_manager.py` | 多语言 + 字体匹配 + 溢出估算 | `translations/*.json` → 每层文字 |
| `scripts/image_analyzer.py` | 图像分析 | 图片 → 安全区 / 配色 / 复杂度 / 可读性评分 |
| `scripts/layout_composer.py` | 「美学」排版引擎 | 图片+配置 → 每层的位置/颜色/效果调整方案 |
| `scripts/text_renderer.py` | 文字渲染 | 底图 + 图层 → 合成图（**核心，1192 行**） |
| `scripts/template_engine.py` | SVG 模板引擎 | 配置 → SVG（**旧路径，已被 PIL 取代**） |
| `scripts/batch_pipeline.py` | 批量编排 | 1 底图 × N 语言 → N 张成品，4 线程并发 |
| `presets/` | 8 个内置预设 | 每个 = `template.yaml` + `translations/` + 示例图 |
| `references/*.md` | 设计规范（文档） | 布局模式 / 触发词 / 流程图符号（**基本没接进代码**） |

### 1.3 两条并存的链路

1. **链路 A（交互式 / 旧）**：`prompt_separator` → 用户自己生图 → `image_analyzer` → `render_text_on_image`（走 SVG + cairosvg 旧路径）。
2. **链路 B（配置驱动批量 / 当前主推）**：`template.yaml` + `translations` → `config_loader` → `layout_composer` → `render_layers_pil`（PIL 直绘新路径）→ `batch_pipeline`。

⚠️ 两条链路的**效果能力不一致**：曲线文字（`text-on-curve`）只在旧 SVG 路径里有，PIL 主路径没有；旧路径有 `text_size: large/small`，新路径没有。这是历史包袱。

### 1.4 几个决定「单一 / 机械」的关键事实

- `assets/fonts/` 里**全部是 Bold 字重**：Roboto-Bold、OpenSans-Bold、NotoSansCJK{sc,tc,kr}-Bold、NotoSerifCJKsc-Bold。没有 Light/Regular/Medium/Black，没有衬线展示字、手写体、黑体之外的任何风格。
- 效果只有 **4 种**：`shadow`（硬偏移黑影）、`outline`（描边）、`glow`（高斯模糊叠加 3 次）、`backdrop`（半透明圆角矩形 / pill）。
- 图层类型只有 **3 种**：`text / badge / price`（见 `config_loader.py` 的 `LayerType`）。
- 每个 preset 只有 **1 条固定 `base_image_prompt`**，`prompt` 命令每次打印同一串。
- `references/layout_patterns.md` 等设计规范写了 150+ 行排版经验，但**只有 `_REGION_TO_SUGGESTED` 这一小段被接进了代码**，其余全部躺在文档里。

---

## 二、现状诊断：为什么「加文字机械」「底图单一」

### 2.1 「加文字」机械的根因（逐条对应代码）

1. **字体全家只有一个字重 → 所有标题看起来都一样**
   - `text_renderer.py` 的 `_FALLBACK_BY_SCRIPT`、`i18n_manager.py` 的 `get_font_for_language` 全部指向 `-Bold` 文件。
   - 拉丁文永远 Roboto-Bold / OpenSans-Bold，中文永远思源黑体 Bold。没有「标题用 Black + 正文用 Regular」的层级对比，没有衬线/手写/展示字的选择空间。
   - **这是「所有成品长得像」的最大单一原因。**

2. **效果是「扁平安全件」，不是「美化件」**
   - `shadow` = 偏移 `size//18+1` 画一份 150 alpha 的黑拷贝，不是真正的软阴影（无多层高斯）。
   - `glow` = 同色高斯模糊叠 3 次，只有单色光晕，做不出霓虹、渐变光。
   - `backdrop` = 一块 `(0,0,0,150)` 或 `(255,255,255,150)` 的圆角矩形，所有「衬底」长得一样。
   - 缺：渐变文字、描边渐变、内阴影、纹理/噪点、玻璃拟态、3D 挤出、装饰下划线/高亮、多色混排。

3. **排版参数极度受限**
   - 行高硬编码 `1.25`（`text_renderer.py` 的 `_render_layer_pil`），没有 `line_height` 参数。
   - 没有 `letter_spacing`（字间距 / 跟踪）、没有旋转、没有竖排（CJK 竖排）、PIL 主路径没有曲线文字。
   - 定位只有「锚点 + 单点 (x,y)」，没有九宫格留白、没有相对主体的偏移。

4. **「美学」引擎只做「避让」，不做「美化」**
   - `layout_composer.py` 的四步全部是**安全性校正**：位置微调（躲开复杂区）、对比度校正（WCAG 达标）、效果增强（太乱就补 shadow/backdrop）、层级排版（别粘连）。
   - 它从不算「这个布局好不好看」，只算「够不够可读」。结果就是**永远安全、永远平庸**。

5. **图层语义太粗**
   - 只有 text/badge/price。想表达「大数字+小标签的统计」「带装饰线的标题」「带引号的金句」「印章/角标」「编号步骤」都要用 badge/text 硬凑，效果自然机械。

### 2.2 「底图」单一的根因

（说明：你说的「加底图」我按两层理解，两层都是真问题。）

**层面一：预设的底图 prompt 是死字符串**
- 每个 preset 只有 1 条 `base_image_prompt`（如 amazon 永远是「无线耳机 + 纯白背景 + 底部留白」），`prompt` 命令每次输出完全相同。
- `prompt_separator.py` 的 `enhance_prompt` 只追加 4 个通用词（`high quality, professional, clean composition, suitable for text overlay`），对任何 prompt 都一样。
- `extract_style_hints` 只识别 6 种颜色、4 种字体风格，风格感知能力约等于无。

**层面二：工具自己叠加的「底图/衬底元素」单一**
- `backdrop` 衬底永远是黑/白半透明圆角矩形；没有渐变底、磨砂玻璃底、描边卡片、异形色块、底纹。
- `_resolve_backdrop_rgba` 只有 `auto-dark` / `auto-light` 两档，不会从画面主色调派生衬底色。

**共性根因**：没有「风格词汇库 / 设计令牌」。画风、配色、光影、材质、构图这些维度没有被建模，全靠写死。

### 2.3 本质总结

> 它是一个「**把模板坐标 + 翻译文案，用固定字体和 4 种安全效果，画到图上的确定性脚本**」。
> 要解决「单一 / 机械」，方向不是修某个函数，而是**从「渲染器」升级为「设计系统 + 审美决策引擎」**。

---

## 三、改进建议（按优先级，可落地）

### 🔴 P0 —— 快速见效、低风险、高收益（1~2 周内可做）

**1. 扩充字体库，引入字重与风格分层**
- 现状：`assets/fonts/` 全 Bold。
- 改法：新增字重（Roboto 的 Light/Regular/Medium/Black、思源黑体的 Light/Regular/Medium/Black）、至少 1 款衬线展示字（如 Playfair Display / 思源宋体非 Bold）、1 款手写/海报字、1 款等宽/科技字。
- 涉及：`assets/fonts/`、`i18n_manager.get_font_for_language`、`text_renderer._font_family / get_font`。
- 收益：**立竿见影**，同样一张图换字重/字体立刻拉开差距。

**2. 效果从「4 个开关」升级为「效果参数化」**
- 把 `shadow` 的偏移/模糊/透明度、`outline` 的宽度/颜色、`glow` 的半径/强度/颜色、`backdrop` 的圆角/内边距/透明度全部变成可配置参数（现在是硬编码）。
- 新增 3~5 个高价值效果：**渐变文字**（`fill: linear-gradient`）、**软阴影**（多层高斯）、**装饰下划线/高亮**、**描边 + 填充分离**（outline 色和 fill 色可独立）。
- 涉及：`config_loader.py`（加字段）、`text_renderer.py`（`_render_layer_pil` 拆效果）。

**3. 排版参数补全：`line_height`、`letter_spacing`、旋转、竖排**
- 把硬编码 `1.25` 行高、无字间距、无旋转变成 per-layer 参数；CJK 增加竖排支持。
- 涉及：`config_loader.py`、`text_renderer.py`。

**4. 每个 preset 的 `base_image_prompt` 模板化 + 变体**
- 现状：1 条死 prompt。
- 改法：prompt 拆成「主体 + 构图 + 光影 + 配色 + 材质」几段变量，`prompt` 命令加 `--style / --mood / --palette / --variant`，同一主题能随机/按需组合出 3~5 种底图 prompt。
- 涉及：`gen_ecommerce.py` 的 `prompt` 子命令、`prompt_separator.py`。

### 🟡 P1 —— 结构性升级（2~4 周）

**5. 引入「设计令牌 / 主题系统」（Design Tokens）**
- 现状：每个 layer 硬编码 hex 色、字体、字号。
- 改法：每个 preset 定义一套 tokens（主色 / 辅助色 / 强调色 / 背景色 / 字体配对 / 圆角 / 阴影 / 间距），layer 引用 token 而非写死。再把 tokens 打包成命名风格（`minimal`、`luxury`、`vibrant`、`editorial`、`tech`、`neon`、`handmade`），用户一键切换风格。
- 收益：**这是解决「单一」的关键杠杆**——风格不再靠每个 layer 手调。

**6. 把 `references/*.md` 设计规范变成代码可读的数据**
- 把 `layout_patterns.md`、`flowchart_symbols.md` 里的规则转成 `design_rules.json`（或 Python 常量），让布局/效果决策真正引用它，而不是躺在文档里。

**7. 图层类型扩展**
- 新增：`stat`（大数字 + 小标签）、`quote`（带引号装饰）、`headline`（带装饰线）、`sticker/seal`（印章角标）、`numbered_step`、`watermark`。
- 涉及：`config_loader.py` 的 `LayerType`、`text_renderer.py`。

**8. 「审美引擎」真正审美化**
- 现状：`layout_composer` 只算可读性（安全）。
- 改法：在「可读性」之外加「视觉平衡」评分（三分法 / 留白率 / 视觉重心 / 文字与主体关系），在**多个候选布局**里选「既安全又好看」的，而不是只微调一个固定坐标。
- 涉及：`layout_composer.py`、`image_analyzer.py`（新增 saliency/主体检测，替换现在的 8×8 网格复杂度）。

**9. 衬底「从画面派生」**
- `_resolve_backdrop_rgba` 只认 auto-dark/auto-light；改成从落点区域主色调派生「低饱和同色系半透明衬底」或磨砂玻璃效果，衬底不再永远是黑/白。

### 🟢 P2 —— 工程 / 架构清理（长期）

**10. 收敛双渲染器**
- 废弃或明确标记 `render_text_on_image` / `render_svg_template` / SVG+cairosvg 旧路径，统一到 `render_layers_pil`，避免功能不一致（曲线文字只在旧路径有、`text_size` 只在旧路径有）。

**11. 拆分 1192 行的 `text_renderer.py`**
- 拆成 `typography.py`（字体/换行/测量）、`effects.py`（效果）、`renderer.py`（合成），降低改动成本，也让新效果更好加。

**12. 分离「设计配置」与「语言翻译」**
- 现在样式（颜色/字体/效果）全塞在 `template.yaml`，文案在 `translations/`；建议把样式抽到独立的 `design.yaml`，翻译只管文案，多语言渲染时共享同一套设计令牌。

---

## 四、建议的落地顺序（最小可行路径）

1. **先做 P0-1（字重/字体）+ P0-2（效果参数化 + 渐变/软阴影）**——改动集中在字体库和 `text_renderer.py`，几小时~1 天，立刻能看出「不那么机械」。
2. **再做 P0-4（底图 prompt 模板化 + 变体）**——解决「底图单一」。
3. **然后 P1-5（设计令牌/主题系统）**——这是把「好看」系统化、可复用的关键，建议优先投入。
4. 其余按需推进；P2 的清理可以穿插做，不阻塞功能。

---

## 五、一句话总结

- **生图不用动**（本来就不归这个项目管）。
- **「加文字机械」** → 升级字体库（字重/风格分层）+ 效果参数化 + 排版参数补全 + 图层类型扩展。
- **「底图单一」** → `base_image_prompt` 模板化/多样化 + 衬底从画面派生 + 引入设计令牌。
- **根治方法** → 把项目从「确定性渲染器」改造成「设计令牌 + 审美决策引擎」。

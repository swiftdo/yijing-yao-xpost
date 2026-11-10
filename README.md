# yijing-yao-xpost · 周易爻帖 X 产出

> 一个 WorkBuddy Skill：给一句「卦名 + 爻位」，产出**一条可直接发的 X 帖子**和**一张 1600×900 横版知识卡片**。

| | |
|---|---|
| 类型 | Agent Skill（`SKILL.md` frontmatter 驱动），脚本也可独立运行 |
| 输入 | `乾卦九三`、`坤卦初六` …… 只需卦名 + 爻位 |
| 输出 | 帖子纯文本（贴在回复里，不落盘）＋ 1 张 PNG 卡片 |
| 规范源 | `SKILL.md`（触发与工作流）、`references/conventions.md`（完整约定） |

## 它做什么

**帖子是主，卡片是补充**，两边正文必须错开，只有帖子首行是有意重复的标识锚点。

| | 承担 | 不承担 |
|---|---|---|
| 帖子 | 首行标识、当下处境、义理体会、分寸、金句、图文钩子 | 卦象图、爻位术语、《象》《文言》原文 |
| 卡片 | 六爻卦图、本爻朱红高亮、爻辞与传文原文、「所处之位」三条、对照行 | 抒情、金句、帖子的白话义理 |

帖子骨架固定：首行 `卦 · 爻｜爻辞全文` → 1～3 段白话 → 一句收束 → `卦象与原文见图` → `#周易 #某卦`。成例见 `references/examples.md`。

**明确不做**：竖版卡片、意境配图、纯净版／题款版、多版备选图、其他尺寸、一次多图。

## 目录结构

```
yijing-yao-xpost/
├── SKILL.md                          Skill 入口：触发条件、交付物、6 步工作流、硬规则与坑
├── references/
│   ├── conventions.md                完整规范：图文分工、字数规则、版式、考据、配置字段、踩坑清单
│   └── examples.md                   乾九二 / 乾九三 / 坤初六 三份完整成例
├── scripts/
│   ├── wlen.py                       X 加权字符数核算（≤280，建议 ≤275）
│   └── render_card.py                配置 JSON → HTML → Chromium 截图 → 裁成 1600×900 PNG
└── assets/
    ├── card_template.html            卡片 HTML/CSS 模板，{{占位符}} 由脚本替换
    ├── ink_bg.png                    水墨底图（1536×944，已裁掉平台水印，不要再调图像生成）
    ├── example_92.json               乾九二配置：阳爻 · 得中
    ├── example_93.json               乾九三配置：阳爻 · 危地
    └── example_kun_chuliu.json       坤初六配置：阴爻 · 初爻 · 有《文言》
```

## 上手 · 当 Skill 用（推荐）

把仓库放到 WorkBuddy 的 skills 目录，用户级或项目级二选一：

```bash
# 用户级（所有项目可用）
git clone git@github.com:swiftdo/yijing-yao-xpost.git ~/.workbuddy/skills/yijing-yao-xpost
# 项目级（仅当前项目）
git clone git@github.com:swiftdo/yijing-yao-xpost.git <项目>/.workbuddy/skills/yijing-yao-xpost
```

之后在对话里直接说「乾卦九三」「坤卦初六」，或「帮我做一下 X 帖子的产出」「这一爻的知识卡片」。Agent 会按 `SKILL.md` 走完 6 步：

1. **考据**：联网核对爻辞与《象》原文（乾、坤才有《文言》，节引标「……」）
2. **写帖子**：按硬规则，首行给全卦、爻、爻辞
3. **核字数**：跑 `scripts/wlen.py`，超限删句，不扩写、不拆帖
4. **出卡片**：照示例 JSON 填一份配置，跑 `scripts/render_card.py`
5. **复检**：看图确认底部无裁切、要点不重叠、高亮爻位正确、无乱码
6. **交付**：展示 PNG，帖子以代码块贴进回复

## 上手 · 只跑脚本

### 1. 环境

| 依赖 | 用途 | 检查命令 |
|---|---|---|
| Python 3.8+ | 两个脚本 | `python3 -V` |
| Pillow | 截图后裁成 1600×900 | `python3 -c "import PIL; print(PIL.__version__)"` |
| `chromium` 或 `google-chrome` 在 `PATH` 中 | HTML → 无头截图 | `command -v chromium \|\| command -v google-chrome` |
| Noto Serif CJK SC / Noto Sans CJK SC | 中文排版（缺了会回退系统字体，中文仍可读但字形有差） | `fc-list \| grep "Noto Serif CJK SC"`（Linux） |

```bash
python3 -m pip install Pillow
```

`render_card.py` 用 `shutil.which("chromium") or shutil.which("google-chrome")` 找浏览器，找不到就报错退出；它**不会**自动发现 macOS 的 `Google Chrome.app`。macOS 上请放一个 wrapper 到 `PATH`：

```bash
mkdir -p ~/.local/bin
cat > ~/.local/bin/google-chrome <<'EOF'
#!/bin/sh
exec "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$@"
EOF
chmod +x ~/.local/bin/google-chrome
export PATH="$HOME/.local/bin:$PATH"   # 想长期生效就写进 ~/.zshrc
```

> 不要直接给 Chrome.app 里的二进制建软链：Chrome 会按自身路径去找 `Google Chrome Framework.framework`，软链会导致 `dlopen` 失败并以 SIGABRT 退出。用上面的 wrapper 脚本 `exec` 真实路径即可。

输出路径默认是 `/workspace/<配置里的 out>`（脚本会自动建目录）。在根目录不可写的机器上请显式传 `--out`，别用默认值：

```bash
python3 scripts/render_card.py assets/example_93.json --out ./乾卦九三_知识卡片_封面.png
```

### 2. 核字数

X 的 280 是**加权字符数**：ASCII 字符/换行算 1，CJK 汉字、中文标点、全角符号、emoji 算 2，纯中文帖实际约 140 字就到顶。

```bash
python3 scripts/wlen.py "乾 · 九二｜见龙在田，利见大人"
# weighted = 29 | 上限 280 | 余量 251 | 可发

python3 scripts/wlen.py post.txt       # 也可传文件
cat post.txt | python3 scripts/wlen.py -   # 或走 stdin
```

超限（>280）时脚本返回非零退出码。`references/examples.md` 标注的成例字数为 267（乾九二主推）、239（克制随笔版）、246（坤初六），其中 267 / 246 已用本脚本复核。

### 3. 出卡片

复制一份示例配置，按 `references/conventions.md` 第 6 节改字段，再渲染：

```bash
cp assets/example_93.json my_yao.json
python3 scripts/render_card.py my_yao.json --out ./my_yao.png
# 已生成: my_yao.png (1600x900)
```

脚本会把配置填进 `card_template.html`，把底图与 HTML 放进同一临时目录，用 Chromium `--headless=new` 截 1600×1000 的图，最后 `crop(0,0,1600,900)` 输出 PNG。

### 4. 复检（别省）

打开生成的 PNG，确认：底部对照行完整无裁切、要点与底行不重叠、朱红高亮落在正确爻位、中文无乱码。任一不符先改配置或模板，再重跑。

## 配置字段速查

| 区域 | 字段 | 说明 |
|---|---|---|
| 输出 | `out` | 文件名；不传 `--out` 时写到 `/workspace/<out>` |
| 左栏 | `gua_label`, `guaxiang`, `split_label`, `foot1`, `foot2` | 卦名与卦序、卦象说明、上下卦分界线文字、两行位置注记（`foot2` 可用 `<b>`） |
| 右栏 | `tag`, `seal`, `title`, `src1`, `src2`, `src3`, `points`, `bottom` | 标签、朱印单字、两行爻辞标题、爻辞、《象》、《文言》节引、三条「所处之位」、对照行 |
| 卦图 | `yao_lines`, `hot_from_bottom`, `hot_note` | 六行爻（**自上而下**，含 `name` / `yin` / `note`）、本爻自下而上第几爻（1～6）、本爻标注 |

要点：`src1` / `src2` 是单行字符串，`src3` 是两行数组（无《文言》时填 `[]`，模板自动省略该行）；配置里只允许 `<b>`、`<br>` 这类简单 HTML。脚本用 `i == 6 - hot_from_bottom` 定位高亮，并在配置第 3 行之后插入上下卦虚线分界。

三份示例配置刻意覆盖了易错场景，换卦时挑最接近的一份改：

| 配置 | 覆盖 |
|---|---|
| `example_92.json` | 阳爻、二爻得中、有《文言》、对照前一爻 |
| `example_93.json` | 阳爻、下卦之上危地、有《文言》且引文直接讲爻位 |
| `example_kun_chuliu.json` | 全阴爻（断开两段）、本爻即初爻（无前爻，改用乾坤对举）、坤卦有《文言》 |

## 改卦前必读

- **考据优先**：爻辞与《象》逐字联网核对（维基文库《周易》、识典古籍等），异文从通行本；只有乾、坤两卦有《文言》。
- **爻名**：阳称九、阴称六，位序自下而上为 初／二／三／四／五／上；阳爻整条实线，阴爻断开两段。
- **位置解读避争议**：不写三才归属、当位／失位等易家分歧，只用注家共识（二为臣位、五为君位、二五得中、下卦之上为危地）；优先引《文言》中直接讲爻位的句子。
- **初爻没有前一爻**：对照行改用对卦初爻对举（如「乾初九『潜龙勿用』 → 坤初六『履霜』」）或「本卦卦辞 → 初爻」，不要捏造前爻。
- **图文不重复**：同一义理两边可以都讲，但帖子用白话、卡片用术语与原文，换一套说法；首行已含爻辞，正文不再抄一遍。
- **语气克制**：用「不必」「宜」，不用「切忌／必须／切记」；避开鸡汤腔、排比堆砌与 AI 味总结。

## 已知坑

完整踩坑清单在 `references/conventions.md` 第 7 节，改模板前务必读一遍，最常踩的几条：

1. Chromium `--window-size=1600,1000` 实际可视高约 913 → 卡片按 900 设计并裁切，别改成 1000 高。
2. 底部对照行不要用 `position:absolute; bottom:0`，文本一长就与要点重叠；模板已改为正常文档流。
3. 阴爻高亮需保留 `.bar.yin.hot { background: none; }`，否则朱红阴爻会被画成整条实线。
4. 中文一律交给 HTML + 系统字体渲染，不让图像模型写中文（必乱码）；`ink_bg.png` 已去水印，直接复用，不再调用图像生成。
5. 每次渲染后看图复检，别只信「已生成」。

## 文档索引

| 想做什么 | 看哪里 |
|---|---|
| 改触发条件、交付物、工作流 | `SKILL.md` |
| 查完整规范、版式参数、全部字段、踩坑清单 | `references/conventions.md` |
| 照着写一条新帖 / 换卦步骤 | `references/examples.md` |
| 仓库地址 | `git@github.com:swiftdo/yijing-yao-xpost.git` |

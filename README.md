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

**明确不做**：竖版卡片、意境配图、纯净版／题款版、多版备选图、其他尺寸、一次多图、自动／静默发布到 X。

> 默认只交付内容、不碰 X 账号。用户明确要求发布且确认内容后，才追加可选流程，见 `references/publishing.md`。

## 目录结构

```
yijing-yao-xpost/
├── SKILL.md                          Skill 入口：触发条件、交付物、6 步工作流 + 可选发布、硬规则与坑
├── references/
│   ├── conventions.md                完整规范：图文分工、字数规则、版式、考据、配置字段、踩坑清单
│   ├── examples.md                   乾九二 / 乾九三 / 坤初六 三份完整成例
│   └── publishing.md                 可选：发布到 X 的流程、GitHub 参考实现、授权与确认门禁
├── scripts/
│   ├── wlen.py                       X 加权字符数核算（≤280，建议 ≤275）
│   ├── render_card.py                配置 JSON → HTML → Chromium 截图 → 裁成 1600×900 PNG
│   └── publish_x.py                  可选：默认 dry-run 的发布脚本，--send 才真发
└── assets/
    ├── card_template.html            卡片 HTML/CSS 模板，{{占位符}} 由脚本替换
    ├── ink_bg.png                    水墨底图（1536×944，已裁掉平台水印，不要再调图像生成）
    ├── example_92.json               乾九二配置：阳爻 · 得中
    ├── example_93.json               乾九三配置：阳爻 · 危地
    └── example_kun_chuliu.json       坤初六配置：阴爻 · 初爻 · 有《文言》
```

> 想直接照着跑一遍，看下面的「完整样例」一节：给出了从一句输入到成品的全部命令和真实输出。

## 上手 · 当 Skill 用（推荐）

把仓库放到 WorkBuddy 的 skills 目录，用户级或项目级二选一：

```bash
# 用户级（所有项目可用）
git clone git@github.com:swiftdo/yijing-yao-xpost.git ~/.workbuddy/skills/yijing-yao-xpost
# 项目级（仅当前项目）
git clone git@github.com:swiftdo/yijing-yao-xpost.git <项目>/.workbuddy/skills/yijing-yao-xpost
```

之后在对话里直接说「乾卦九三」「坤卦初六」，或「帮我做一下 X 帖子的产出」「这一爻的知识卡片」。Agent 会按 `SKILL.md` 走完默认的 6 步（第 7 步「发布到 X」是可选、默认不执行）：

1. **考据**：联网核对爻辞与《象》原文（乾、坤才有《文言》，节引标「……」）
2. **写帖子**：按硬规则，首行给全卦、爻、爻辞
3. **核字数**：跑 `scripts/wlen.py`，超限删句，不扩写、不拆帖
4. **出卡片**：照示例 JSON 填一份配置，跑 `scripts/render_card.py`
5. **复检**：看图确认底部无裁切、要点不重叠、高亮爻位正确、无乱码
6. **交付**：展示 PNG，帖子以代码块贴进回复。默认到此结束
7. **可选发布**：仅当用户明确要求且确认内容，才按 `references/publishing.md` 执行 dry-run → 确认 → `--send` → 回读

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

超限（>280）时脚本返回非零退出码。`references/examples.md` 的成例字数为 267（乾九二主推）、239（克制随笔版）、246（坤初六）；乾九三为 257（见下方完整样例，已实测）。

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

## 完整样例 · 串起来跑一遍「乾卦九三」

下面每一步都在本机实跑过，输出是真实结果。目标是拿到**一条 257 加权字符的帖子** ＋ **一张 1600×900 卡片**；默认到此为止，不碰 X 账号。

### A. 当 Skill 用：一句话

装好 Skill 后新开一个会话，输入：

```
乾卦九三
```

Agent 会自动考据 → 写帖 → 核字数 → 填配置 → 渲染 → 看图复检，最后交付两件东西：回复里的一个帖子代码块（内容就是下面的 `post.txt`），以及一张 PNG（内容就是下面的 `card.png`）。换一卦直接说「坤卦初六」。**不说「发到 X」就不会发布**；即使说了，也要再逐字确认一次才会真发（第 7 步）。Agent 侧同样需要「1. 环境」就绪。

### B. 只跑脚本：逐步照抄

**0 · 准备工作目录**（产物放 `/tmp`，不污染仓库）

```bash
REPO=/path/to/yijing-yao-xpost        # 改成你的克隆路径
mkdir -p /tmp/yijing-demo && cd /tmp/yijing-demo
```

**1 · 写帖子** —— 首行给全卦、爻、爻辞；正文用白话讲义理与处境，不抄原文、不摆术语

```bash
cat > post.txt <<'EOF'
乾 · 九三｜君子终日乾乾，夕惕若厉，无咎

被看见了，却还没到那个位子——比蛰伏更难熬。

往上够不着，往下也落不稳，进退都悬着。
能做的只有一件：一天做到晚，到夜里仍不松劲。

九三不谈龙，只谈「君子」。
讲的不是天赋，是危地上怎么自持。

卦象与原文见图
#周易 #乾卦
EOF
```

**2 · 核字数**

```bash
python3 "$REPO/scripts/wlen.py" post.txt
# weighted = 257 | 上限 280 | 余量 23 | 可发
```

257 在建议上限 275 之内，不用删句。超限（>280）时脚本返回非零退出码，按规范**删句，不拆帖、不扩写**。

**3 · 填卡片配置** —— 九三是「阳爻 · 下卦之上危地 · 有《文言》」，复制最贴近的示例

```bash
cp "$REPO/assets/example_93.json" card.json
```

三个最容易填错的字段：

| 字段 | 本例取值 | 说明 |
|---|---|---|
| `hot_from_bottom` | `3` | 九三是自下而上第三爻，朱红高亮落在这条 |
| `yao_lines` | 6 行，全 `yin: false` | 乾卦六阳爻；数组按**从上到下**排列，脚本自动在第 3 行后插分界线 |
| `src3` | 《文言》两行 | 乾卦有《文言》且此句正讲爻位；非乾、坤两卦填 `[]` |

**4 · 渲染**

```bash
python3 "$REPO/scripts/render_card.py" card.json --out ./card.png
# 已生成: card.png (1600x900)
```

> 本机 macOS 实测时，默认 `python3` 没有 Pillow、Chrome.app 也不在 `PATH`，上面这条会失败。按「1. 环境」配好 wrapper 后，等价的实测命令是：
>
> ```bash
> TMPBIN=$(mktemp -d)
> printf '#!/bin/sh\nexec "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" "$@"\n' > "$TMPBIN/google-chrome"
> chmod +x "$TMPBIN/google-chrome"
> PATH="$TMPBIN:$PATH" /opt/homebrew/bin/python3 "$REPO/scripts/render_card.py" card.json --out ./card.png
> ```

**5 · 看图复检**（别只信「已生成」）

```bash
/opt/homebrew/bin/python3 -c "from PIL import Image; print(Image.open('card.png').size)"
# (1600, 900)
```

打开 `card.png` 逐项确认：朱红落在九三（虚线分界下方第一条）而其余五爻为深灰；底部「对照：九二… → 九三…」完整、不与三条要点重叠；中文无方框乱码。本例四项均通过。

**6 · 交付**：把 `post.txt` 全文复制进 X 编辑框，`card.png` 作为附图上传。**默认流程到此结束。** 实测产物：`post.txt` 382 B、`card.json` 1.4 KiB、`card.png` 1.02 MiB。

**7 ·（可选）发布前先 dry-run**

```bash
python3 "$REPO/scripts/publish_x.py" --text-file post.txt --image ./card.png
```

```
----- 帖子预览 -----
（此处原样打印 post.txt 全文）
--------------------
加权字符：257 / 280（X 按 CJK 每字 2 计）
附图：card.png（1.02 MiB）
[dry-run] 检查通过：长度 OK / 图片 OK / 未读取凭证 / 未联网
[dry-run] 将执行：users/me 校验（可选）→ 媒体上传 → POST /2/tweets → 回读
[dry-run] 没有发送任何内容。人工确认后加 --send 才会发布。
```

确认无误且备好凭证后，才轮到下一节的 `--send`。

### 换一卦怎么改

最省事是换一份更贴近的模板：

```bash
cp "$REPO/assets/example_kun_chuliu.json" card.json
python3 "$REPO/scripts/render_card.py" card.json --out ./card.png
```

若从乾九三的配置改，必须动这几处（右列为坤初六的取值）：

| 字段 | 乾九三 | 坤初六 |
|---|---|---|
| `hot_from_bottom` | `3` | `1`（初爻） |
| `yao_lines[].yin` | 全 `false` | 全 `true`（阴爻画成断开两段） |
| `src3` | 《文言》两行 | 《文言》两行（坤卦也有，其余卦填 `[]`） |
| `bottom` | 「九二 → 九三」对照 | 乾坤对举「乾初九『潜龙勿用』 → 坤初六『履霜』」——**初爻没有前爻，别捏造** |
| `tag` / `title` / `src1` / `src2` / `points` | 九三原文与解读 | 初六原文与解读 |

帖子照 `references/examples.md` 例 3 重写（246 加权字符），再跑一次 `wlen.py` 与 `render_card.py`。

## 可选 · 发布到 X

**默认不发布。** 只有用户明确要求、且已确认帖子与卡片内容时，才走 `references/publishing.md`。该文档记录了 GitHub 上核验过的参考实现（X 官方 `xdevplatform/samples`、官方 CLI `xurl`、`agent-of-empires/post_to_x.py`、LifeOS 的 X Skill）、开发者账号与 OAuth scopes、计费前提、确认门禁与失败处理。

沿用完整样例的 `post.txt` 与 `card.png`（在仓库根目录运行时把 `$REPO/scripts/` 换成 `scripts/`）：

```bash
# 1. 首次一次性授权，拿用户级 OAuth 2.0 token（tweet.write / users.read / media.write / offline.access）
export X_ACCESS_TOKEN='<token>'

# 2. 预览：不联网、不读凭证、不发送（同完整样例第 7 步）
python3 "$REPO/scripts/publish_x.py" --text-file post.txt --image ./card.png

# 3. 人工确认后才真发
python3 "$REPO/scripts/publish_x.py" --text-file post.txt --image ./card.png --send --expect-user your_handle
```

`publish_x.py` 零第三方依赖，复用 `wlen.py` 校验 ≤280 加权字符（超限拒绝、不截断），走 v2 分块媒体上传 → `POST /2/tweets` → 回读逐字比对；发帖失败不自动重试，避免重复发布。**真实发送路径尚未用真实账号验证**（需要凭证，且调用有费用），发布前务必读一遍 `publishing.md` 的门禁与错误表。

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
| 照抄一条从输入到成品的完整命令流程 | 上文「完整样例」 |
| 改触发条件、交付物、工作流 | `SKILL.md` |
| 查完整规范、版式参数、全部字段、踩坑清单 | `references/conventions.md` |
| 照着写一条新帖 / 换卦步骤 | `references/examples.md` |
| 把内容发布到 X（可选流程） | `references/publishing.md` + `scripts/publish_x.py` |
| 仓库地址 | `git@github.com:swiftdo/yijing-yao-xpost.git` |

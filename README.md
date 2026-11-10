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
| 帖子 | 首行标识、误读纠偏、当下处境、具体动作与画面 | 卦象图、爻位术语、《象》《文言》原文、逐句译文、看图提示、说教口吻 |
| 卡片 | 六爻卦图、本爻朱红高亮、爻辞与传文原文**及其白话译文**、「所处之位」三条、对照行 | 抒情、金句、帖子的白话义理 |

**译文只上卡片**：帖子只有 280 加权字符，装不下逐句译文；卡片用古籍经注格式——原文大字、译文小字紧随其下。帖子里凡引文言词句，就在同一段用一句白话说清它指什么（如「「勿用」是没人用，「利见」是有人肯见」）。

帖子骨架固定：首行 `卦 · 爻｜爻辞全文` → **一个翻转** → 1～3 段能对上读者自己的场景 → **一句画面或判词收束** → `#周易 #某卦`。

**翻转是帖子的核**：先摆这爻最常见的读法，再给出更准的读法——`「终日乾乾」常被当成励志句。它写的不是勤奋，是不敢停。` 它不算说教，因为判断落在**文本**上而不是读者身上；但**翻转句本身要说白话**，别写成「《文言》说『或之者，疑之也』——拿不准，不是拿得稳」这种文言＋训诂对照。找不到明显误读时，改用单字重译（把九二的「见」拆成「被看见」与「被任用」）。

**主体写读者自己的事**：`桌上那份 offer 还没签，笔帽没拔`、`有人问起，只说再看看`、`夜里躺下，想的不是去了怎么干，是万一不成怎么回来`。写成第三人称意象（`脚已经站到边上`）就要读者先把自己搬进画面才成立，隔一层。

**结尾只收画面或判词**，不写「再往上一步是九四」这类指向下一爻的接续句——单篇读完就够了，多这一句是把读者从处境里拽出来报进度。判词要来自爻辞（如「无咎」→「没定，不算错」），不是作者下的结论。

**不写「卦象与原文见图」**：附图本身已说明，这行占掉约 18 加权字符却不传递任何内容，省下来补进正文的处境与动作。成例见 `references/examples.md`。

**明确不做**：竖版卡片、意境配图、纯净版／题款版、多版备选图、其他尺寸、一次多图、自动／静默发布到 X。

> 默认只交付内容、不碰 X 账号。用户明确要求发布且确认内容后，才追加可选流程，见 `references/publishing.md`。

## 目录结构

```
yijing-yao-xpost/
├── SKILL.md                          Skill 入口：触发条件、交付物、6 步工作流 + 可选发布、硬规则与坑
├── references/
│   ├── conventions.md                完整规范：图文分工、字数规则、版式、考据、配置字段、踩坑清单
│   ├── card-design.md                卡片视觉依据：借鉴来源、色彩推导、排印规则、改样式红线
│   ├── examples.md                   乾九二 / 乾九三 / 坤初六 / 乾九四 四份完整成例
│   └── publishing.md                 可选：发布到 X 的流程、GitHub 参考实现、授权与确认门禁
├── scripts/
│   ├── wlen.py                       X 加权字符数核算（≤280，建议 ≤275）
│   ├── render_card.py                配置 JSON → HTML → Chromium 截图 → 裁成 1600×900 PNG
│   └── publish_x.py                  可选：默认 dry-run 的发布脚本，--send 才真发
└── assets/
    ├── card_template.html            卡片 HTML/CSS 模板（书叶版式），{{占位符}} 由脚本替换
    ├── ink_bg.png                    水墨底图（1536×944，已裁掉平台水印，不要再调图像生成）
    ├── example_92.json               乾九二配置：阳爻 · 得中
    ├── example_93.json               乾九三配置：阳爻 · 危地
    ├── example_94.json               乾九四配置：阳爻 · 上卦之下 · 重刚不中
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

1. **考据**：联网核对爻辞与《象》原文，**并写下两段的白话译文**（乾、坤才有《文言》，节引只留一句、标「……」）
2. **写帖子**：按硬规则，首行给全卦、爻、爻辞
3. **核字数**：跑 `scripts/wlen.py`，超限删句，不扩写、不拆帖、不把译文挤进来
4. **出卡片**：照示例 JSON 填一份配置（含 `trans1` / `trans2`），跑 `scripts/render_card.py`
5. **复检**：看图确认底部无裁切、要点不重叠、高亮爻位正确、**译文与原文逐句对应且各占一行**、无乱码
6. **交付**：展示 PNG，帖子以代码块贴进回复。默认到此结束
7. **可选发布**：仅当用户明确要求且确认内容，才按 `references/publishing.md` 执行 dry-run → 确认 → `--send` → 回读

## 上手 · 只跑脚本

### 1. 环境

| 依赖 | 用途 | 检查命令 |
|---|---|---|
| Python 3.8+ | 两个脚本 | `python3 -V` |
| Pillow | 截图后裁成 1600×900 | `python3 -c "import PIL; print(PIL.__version__)"` |
| 一个 Chromium 系浏览器 | HTML → 无头截图 | `python3 -c "import sys; sys.path.insert(0,'scripts'); from render_card import find_browser; print(find_browser())"` |
| Noto Serif CJK SC / Noto Sans CJK SC（可选） | 中文排版；模板按 `Noto → Songti SC → 系统中文衬线` 回退，未装 Noto 实测中文仍清晰、字形略有差 | `fc-list \| grep "Noto Serif CJK SC"`（Linux） |

```bash
python3 -m pip install Pillow
```

**推荐装一个专用无头构建**（不与日常浏览器共用 profile，最快也最不会出事）：

```bash
npx --yes @puppeteer/browsers install chrome-headless-shell@stable
```

`render_card.py` 按这个顺序找浏览器，第一个能用就用：

1. `--chrome /path/to/browser` 参数
2. `CHROME_BIN` 环境变量
3. `PATH` 里的 `chrome-headless-shell` / `chromium` / `chromium-browser` / `google-chrome`
4. puppeteer、playwright 缓存里的无头构建
5. macOS 的 `Chromium.app` / `Google Chrome Canary.app` / `Google Chrome.app`

macOS 上第 5 步能直接命中 `Google Chrome.app`，**不需要再建 wrapper**。若你的机器上 Chrome 装在别处，用 `CHROME_BIN` 指过去即可：

```bash
CHROME_BIN="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  python3 scripts/render_card.py assets/example_93.json --out ./card.png
```

> **别给 Chrome.app 里的二进制建软链**：Chrome 会按自身路径去找 `Google Chrome Framework.framework`，软链会导致 `dlopen` 失败并以 SIGABRT 退出。要自定义路径就写个 `exec` 真路径的 wrapper 脚本，或用 `CHROME_BIN`。

> **为什么每次渲染都用一个临时 profile**：脚本固定传 `--user-data-dir=<临时目录>/profile`。不隔离的话，无头进程会和正在运行的 Chrome 抢同一个 profile 的单例锁，触发 Chrome 的 CHECK 断言——表现就是**跑一次卡片，Chrome 崩一次**，崩溃报告里进程名还写着「Google Chrome」。详见 `references/conventions.md` 第 7 节第 9 条。

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

超限（>280）时脚本返回非零退出码。`references/examples.md` 五条成例字数为 268（乾九二主推）、247（克制随笔版）、272（乾九三，见下方完整样例）、269（乾九四）、272（坤初六），均已实测。

### 3. 出卡片

复制一份示例配置，按 `references/conventions.md` 第 6 节改字段，再渲染：

```bash
cp assets/example_93.json my_yao.json
python3 scripts/render_card.py my_yao.json --out ./my_yao.png
# 已生成: my_yao.png (1600x900)
```

脚本会把配置填进 `card_template.html`，把底图与 HTML 放进同一临时目录，用 Chromium `--headless=new` 截 1600×1000 的图，最后 `crop(0,0,1600,900)` 输出 PNG。

模板是「书叶」版式：细版框、上提的版心与留大的地脚，水墨只在左半叶透出；配色只有**纸／四级墨／朱砂**，朱砂严格只给本爻与朱印两处，其余层级靠墨色明度与字重。原文界栏走**古籍经注格式**——爻辞大字、《象》中字、《文言》一句，每段原文下方紧跟一行小字白话译文（原文墨1／墨2，译文统一墨3）。设计依据、借鉴出处（[alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design)）与改样式红线见 `references/card-design.md`，改 CSS 前先读。

### 4. 复检（别省）

打开生成的 PNG，确认：底部对照行完整无裁切、要点与底行不重叠、朱砂高亮落在正确爻位（阴爻要断成两段）、朱砂只出现在两处、**每段译文与原文逐句对应且没折行**、中文无乱码。任一不符先改配置或模板，再重跑。译文写不短就改措辞——别缩字号，也别删「所处之位」。

## 完整样例 · 串起来跑一遍「乾卦九三」

下面每一步都在本机实跑过，输出是真实结果。目标是拿到**一条 272 加权字符的帖子** ＋ **一张 1600×900 卡片**；默认到此为止，不碰 X 账号。

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

**1 · 写帖子** —— 首行给全卦、爻、爻辞；正文用白话写处境与画面，不抄原文、不摆术语，不劝告、不下判断

```bash
cat > post.txt <<'EOF'
乾 · 九三｜君子终日乾乾，夕惕若厉，无咎

「终日乾乾」常被当成励志句。它写的不是勤奋，是不敢停。

白天做到晚，夜里还提着心——躺下了，脑子还在过白天的事。
往上够不着，往下也落不稳，这时候没人替你兜底。

九三不谈龙，只谈「君子」。
闹钟定在六点，睡前又核对了一遍。

#周易 #乾卦
EOF
```

**2 · 核字数**

```bash
python3 "$REPO/scripts/wlen.py" post.txt
# weighted = 272 | 上限 280 | 余量 8 | 可发
```

272 在建议上限 275 之内，不用删句。这一稿做了两件事：开头用一句翻转把「终日乾乾」从励志句改读成「不敢停」（判断落在文本上，不落在读者身上）；结尾不写议论，落在「闹钟定在六点，睡前又核对了一遍」这个动作上。超限（>280）时脚本返回非零退出码，按规范**删句，不拆帖、不扩写**。

**3 · 填卡片配置** —— 九三是「阳爻 · 下卦之上危地 · 有《文言》」，复制最贴近的示例

```bash
cp "$REPO/assets/example_93.json" card.json
```

三个最容易填错的字段：

| 字段 | 本例取值 | 说明 |
|---|---|---|
| `hot_from_bottom` | `3` | 九三是自下而上第三爻，朱红高亮落在这条 |
| `yao_lines` | 6 行，全 `yin: false` | 乾卦六阳爻；数组按**从上到下**排列，脚本自动在第 3 行后插分界线 |
| `trans1` / `trans2` | 各一句白话 | **必填**：爻辞与《象》的译文，各自压在一行内（约 40 字以内） |
| `src3` | 《文言》一句 | 只留一句、须一行内；非乾、坤两卦填 `[]` |

译文是这份改动里最容易做坏的地方：它不是「概括」，必须逐句对应原文。九三的「终日乾乾，夕惕若厉，无咎」如果翻成「要努力奋斗」就错了——「乾乾」是勤勉不懈、不是打鸡血，「夕惕若厉」是夜间戒惧如临险境。填法是**先按字义直译，再顺成口语**，别先顺口再倒推字义。

**4 · 渲染**

```bash
python3 "$REPO/scripts/render_card.py" card.json --out ./card.png
# 已生成: card.png (1600x900)
```

> 本机 macOS 实测时默认 `python3` 没有 Pillow，请用 `/opt/homebrew/bin/python3`。浏览器不用额外配——脚本会自己找到 `Google Chrome.app`；装了 `chrome-headless-shell` 则优先用它。等价的实测命令：
>
> ```bash
> /opt/homebrew/bin/python3 "$REPO/scripts/render_card.py" card.json --out ./card.png
> # 已生成: .../card.png (1600x900)｜浏览器: chrome-headless-shell
> ```

**5 · 看图复检**（别只信「已生成」）

```bash
/opt/homebrew/bin/python3 -c "from PIL import Image; print(Image.open('card.png').size)"
# (1600, 900)
```

打开 `card.png` 逐项确认：朱砂落在九三（虚线分界下方第一条）而其余五爻为墨色；朱砂除本爻外只出现在右上角朱印；原文区五行齐备（爻辞→译文→《象》→译文→《文言》一句），两条译文都只有一行、与各自原文逐句对应；底部「对照：九二… → 九三…」完整、不与三条要点重叠；中文无方框乱码。本例均通过。

**6 · 交付**：把 `post.txt` 全文复制进 X 编辑框，`card.png` 作为附图上传。**默认流程到此结束。** 实测产物：`post.txt` 405 B、`card.json` 1.5 KiB、`card.png` 0.87 MiB。

**7 ·（可选）发布前先 dry-run**

```bash
python3 "$REPO/scripts/publish_x.py" --text-file post.txt --image ./card.png
```

```
----- 帖子预览 -----
（此处原样打印 post.txt 全文）
--------------------
加权字符：272 / 280（X 按 CJK 每字 2 计）
附图：card.png（0.87 MiB）
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
| `src3` | 《文言》一句 | 《文言》一句（坤卦也有，其余卦填 `[]`） |
| `bottom` | 「九二 → 九三」对照 | 乾坤对举「乾初九『潜龙勿用』 → 坤初六『履霜』」——**初爻没有前爻，别捏造** |
| `tag` / `title` / `src1` / `src2` / `trans1` / `trans2` / `points` | 九三原文、译文与解读 | 初六原文、译文与解读 |

帖子照 `references/examples.md` 例 3 重写（262 加权字符），再跑一次 `wlen.py` 与 `render_card.py`。

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
| 右栏 | `tag`, `seal`, `title`, `src1`, `trans1`, `src2`, `trans2`, `src3`, `points`, `bottom` | 标签、朱印单字、两行爻辞标题、爻辞、爻辞译文、《象》、《象》译文、《文言》节引、三条「所处之位」、对照行 |
| 卦图 | `yao_lines`, `hot_from_bottom`, `hot_note` | 六行爻（**自上而下**，含 `name` / `yin` / `note`）、本爻自下而上第几爻（1～6）、本爻标注 |

要点：`src1` / `trans1` / `src2` / `trans2` 都是单行字符串，`trans1` 缺失脚本会直接报错退出（译文是必需项）；`src3` 是数组，但**只放一句**（无《文言》时填 `[]`，模板自动省略该行）。配置里只允许 `<b>`、`<br>` 这类简单 HTML。脚本用 `i == 6 - hot_from_bottom` 定位高亮，并在配置第 3 行之后插入上下卦虚线分界。

四份示例配置刻意覆盖了易错场景，换卦时挑最接近的一份改：

| 配置 | 覆盖 |
|---|---|
| `example_92.json` | 阳爻、二爻得中、有《文言》、对照前一爻 |
| `example_93.json` | 阳爻、下卦之上危地、有《文言》且引文直接讲爻位 |
| `example_94.json` | 阳爻、上卦之下（重刚不中、故「或」）、有《文言》、标题只四字 |
| `example_kun_chuliu.json` | 全阴爻（断开两段）、本爻即初爻（无前爻，改用乾坤对举）、坤卦有《文言》 |

## 改卦前必读

- **考据优先**：爻辞与《象》逐字联网核对（维基文库《周易》、识典古籍等），异文从通行本；只有乾、坤两卦有《文言》。
- **爻名**：阳称九、阴称六，位序自下而上为 初／二／三／四／五／上；阳爻整条实线，阴爻断开两段。
- **位置解读避争议**：不写三才归属、当位／失位等易家分歧，只用注家共识（二为臣位、五为君位、二五得中、下卦之上为危地）；优先引《文言》中直接讲爻位的句子。
- **初爻没有前一爻**：对照行改用对卦初爻对举（如「乾初九『潜龙勿用』 → 坤初六『履霜』」）或「本卦卦辞 → 初爻」，不要捏造前爻。
- **图文不重复**：同一义理两边可以都讲，但帖子用白话、卡片用术语与原文，换一套说法；首行已含爻辞，正文不再抄一遍。
- **必有一个翻转**：先搜一次大众版白话解读，看这爻被读成什么（多半励志化或道德化），写出落差——`「终日乾乾」常被当成励志句。它写的不是勤奋，是不敢停。` 判断落在**文本**上，不落在读者身上，所以它不算说教。翻转句**要用白话**，别搬训诂（`《文言》说「或之者，疑之也」` 这种读者要先解古文）。找不到明显误读就抓一个字重译（九二的「见」拆成「被看见」与「被任用」）。
- **从读者角度写**：主体不写「他站在边上」，写读者桌上正在发生的事——`桌上那份 offer 还没签，笔帽没拔`、`有人问起，只说再看看`。挑最常见的处境（跳槽、竞聘、要不要接）写一种，具体到能看见的物。
- **不做说教**：同路人讲见闻，不做老师。不劝告、不下指令、不下判断——删掉「宜」「不必」「应该」「就够了」和「这一爻讲的是 X」这类句式，结尾不写箴言式金句；用具体的处境、动作、画面把意思带出来。避开鸡汤腔、排比堆砌与 AI 味总结。翻转句是这条的唯一例外，别把两者混为一谈。
- **结尾收画面或判词**：`桌上那份 offer 还没签，笔帽没拔。`、`爻辞给的判词是「无咎」：没定，不算错。` **不写「再往上一步是九四」这类接续句**——单篇读完就够了，多一句只是把读者从处境里拽出来报进度。
- **引文言必译**：帖子里引了文言词句，就在同一段用一句白话说清它指什么（`「勿用」是没人用，「利见」是有人肯见`）。逐句译文不上帖子——280 加权字符装不下，译文一律放卡片。

## 已知坑

完整踩坑清单在 `references/conventions.md` 第 7 节，改模板前务必读一遍，最常踩的几条：

1. Chromium `--window-size=1600,1000` 实际可视高约 913 → 卡片按 900 设计并裁切，别改成 1000 高。
2. 底部对照行不要用 `position:absolute; bottom:0`，文本一长就与要点重叠；模板已改为正常文档流。
3. 阴爻高亮需保留 `.bar.yin.hot { background: none; }`，否则朱红阴爻会被画成整条实线。
4. 加了译文后右栏离 780px 上限只剩约 40px：`trans1` 折行、《文言》写到两行，底部对照行就会被切掉。译文长就改措辞，别缩字号。
5. 译文不是概括，要逐句对应原文；翻错了比不翻更坏。
6. 中文一律交给 HTML + 系统字体渲染，不让图像模型写中文（必乱码）；`ink_bg.png` 已去水印，直接复用，不再调用图像生成。
7. 每次渲染后看图复检，别只信「已生成」。

## 文档索引

| 想做什么 | 看哪里 |
|---|---|
| 照抄一条从输入到成品的完整命令流程 | 上文「完整样例」 |
| 改触发条件、交付物、工作流 | `SKILL.md` |
| 查完整规范、版式参数、全部字段、踩坑清单 | `references/conventions.md` |
| 改卡片配色、字体、版式，或想看设计依据 | `references/card-design.md` + `assets/card_template.html` |
| 照着写一条新帖 / 换卦步骤 | `references/examples.md` |
| 把内容发布到 X（可选流程） | `references/publishing.md` + `scripts/publish_x.py` |
| 仓库地址 | `git@github.com:swiftdo/yijing-yao-xpost.git` |

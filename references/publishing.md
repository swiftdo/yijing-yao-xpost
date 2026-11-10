# 发布到 X（可选流程）

> **状态**：流程已定义，`scripts/publish_x.py` 的 dry-run / 校验路径已本地验证；**真实发送路径未在真实 X 账号上验证**（缺开发者凭证，且发布不可逆、有调用成本）。本仓库不含任何凭证，默认交付仍是「只生成内容，不发布」。

## 1. 结论：可以实现吗

**可以实现，但有三个不可跳过的硬前提。** GitHub 上既有 X 官方样例、官方 CLI，也有把发帖封装成 Skill 的成熟实现，技术路径清晰；缺的不是代码，是账号授权、费用与人工确认。

| 判断 | 依据 |
|---|---|
| 技术上可行 | X 官方样例给出 `POST /2/tweets` 与 `POST /2/media/upload` 的完整 Python 代码；`xurl` 是 X 官方 CLI |
| 与本 Skill 契合 | 帖子 ≤280 加权字符已由 `wlen.py` 保证；卡片 1600×900 PNG 实测约 1 MB，远低于 X 的 5 MB 图片上限；「一帖一图」正好对上 |
| 必须新增 | X 开发者账号与用户级 OAuth 授权、凭证管理、人工确认门禁、发布后回读 |
| 不建议做 | 自动生成后静默发布、自动重试发帖、把凭证写进仓库 |

## 2. GitHub 调研（2026-11-10 核验）

以下仓库/文件均通过 GitHub API 实际读取过，不是搜索摘要：

| 来源 | 提供了什么 |
|---|---|
| [xdevplatform/samples · python/posts/create_post.py](https://github.com/xdevplatform/samples/blob/main/python/posts/create_post.py) | X 官方发帖样例：`POST https://api.x.com/2/tweets`，OAuth 2.0 PKCE，scopes `tweet.read tweet.write users.read offline.access`，用官方 `xdk` 的 `Client.posts.create()` |
| [xdevplatform/samples · python/media/media_upload_v2.py](https://github.com/xdevplatform/samples/blob/main/python/media/media_upload_v2.py) | X 官方附图样例：`POST https://api.x.com/2/media/upload` 的 INIT / APPEND / FINALIZE / STATUS 分块流程，额外需要 `media.write`；最后 `POST /2/tweets` 带 `media.media_ids` |
| [xdevplatform/xurl](https://github.com/xdevplatform/xurl) | X 官方 CLI（"The official CLI for the X API"）。快速核对与发帖可用 `xurl /2/users/me`、`xurl -X POST /2/tweets -d '{"text":"..."}'` |
| [agent-of-empires · marketing/x/post_to_x.py](https://github.com/agent-of-empires/agent-of-empires/blob/main/marketing/x/post_to_x.py) | 几乎就是本项目要的脚本形态：**dry-run 默认、`--send` 才真发、凭证只从环境变量读、拒绝发错账号、不自动重试**；注释里记录了「tweepy 的 v1.1 `media_upload` 在当前非 elevated 权限下 401，故手写 v2 分块上传」这个现实坑 |
| [danielmiessler/LifeOS · install/skills/X](https://github.com/danielmiessler/LifeOS/tree/main/LifeOS/install/skills/X) | 把 X 操作做成 **Skill** 的成熟范例：`SKILL.md` + `Intents/Post.md` + `Tools/post.ts`；其「send gate」、发布后回读、超限拒绝而不截断、凭证与 token 刷新集中一处，被本流程直接借鉴 |
| [tweepy/tweepy](https://github.com/tweepy/tweepy) | 常用 Python 库，`API.media_upload()` + `Client.create_tweet(text=..., media_ids=...)`。注意它的媒体上传走 v1.1，需 OAuth 1.0a 且当前权限下可能 401，本项目因此不用它 |
| [leongjiameng/twitter-bot](https://github.com/leongjiameng/twitter-bot/blob/master/main.py) | 完整 OAuth 2.0 PKCE + 自动刷新 + `media.write` 的 Web 实现，需要完整授权交互时参考 |

关键结论：**发纯文本用 v2 `POST /2/tweets`；发附图必须先经 v2 分块媒体上传拿 `media_id`，再把它塞进建帖请求**。别用老教程里的 v1.1 `upload.twitter.com` / `tweepy.API.media_upload` 路径，权限门槛更高。

## 3. 硬前提与成本

1. **X 开发者账号 + Project/App**：在开发者后台建应用，开启用户级 OAuth 2.0（PKCE），回调 URI 与后台完全一致。
   - 发帖 scopes：`tweet.read`、`tweet.write`、`users.read`、`offline.access`
   - 附图额外需要：`media.write`
   - App 权限至少 Read and Write；access token 有效期约 2 小时，靠 `offline.access` 的 refresh token 续期。
2. **凭证只放本地**：`X_ACCESS_TOKEN`（用户级 Bearer token）从环境变量读，token 文件若落盘需 `chmod 600`；**绝不写进仓库、配置 JSON 或日志**。本仓库 `.gitignore` 已忽略 `.env` 类文件。
3. **费用**：据 2026 年第三方资料与上述参考实现注释，X 自 2026-02 起对新接入采用按量计费，发帖约每条 $0.01–0.015，含外链的帖子显著更贵；**具体配额与计价以 X 官方开发者后台为准**。这意味着发布不是零成本操作，值得保留确认门禁。
4. **内容约束**：文本 ≤280 加权字符（`wlen.py` 已按 twitter-text 规则实现）；图片 ≤5 MB，支持 PNG/JPEG/WEBP/GIF，每帖最多 4 张（本 Skill 只用 1 张）。
5. **范围限制**：只发原创首帖 + 附图。自助层级的程序化回复、引用帖、点赞关注等能力在 2026 年受限或需更高套餐，与本 Skill 无关，不做。

## 4. 发布流程

默认流程仍是 `SKILL.md` 的 6 步，到第 6 步（展示 PNG + 帖子贴回复）就结束。下面是**用户明确要求发布时**才追加的流程。

### 步骤 0 · 确认意图

只有用户明确说「发到 X」「发布这条」才进入。生成阶段绝不顺手发布。

### 步骤 1 · 首次授权（一次性）

按官方样例的 PKCE 流程，或用 `xurl` 完成授权（`xurl` 的安装与登录见其仓库 README），拿到带上述 scopes 的用户级 access token：

```bash
export X_ACCESS_TOKEN='<用户级 OAuth 2.0 access token>'
# 可选：核对当前授权账号，防发错号
xurl /2/users/me
```

token 过期后用 refresh token 重新换取；不要把刷新逻辑塞进生成脚本。

### 步骤 2 · 备好内容

```bash
# 帖子存成纯文本文件（首行、正文、图文钩子、标签一并保留）
python3 scripts/wlen.py post.txt                     # 必须 ≤280，建议 ≤275
# 卡片渲染到可写路径（本机 / 不可写，别用 SKILL.md 里默认的 /workspace）
python3 scripts/render_card.py assets/example_93.json --out ./card.png
```

### 步骤 3 · dry-run 预览（默认，不联网、不需要凭证）

```bash
python3 scripts/publish_x.py --text-file post.txt --image ./card.png
```

脚本会打印帖子全文、加权字符数、图片大小，并校验：长度超限直接拒绝（**不截断**）、图片缺失/格式不对/超过 5 MB 直接拒绝。确认「没有发送任何内容」。

### 步骤 4 · 人工确认（不可省略）

把帖子全文与卡片给人看，得到**明确同意**后再继续。发布不可撤回，且每次调用都有费用。借鉴 LifeOS 的 send gate：脚本输出不等于发布成功，人没点头就不许带 `--send`。

### 步骤 5 · 真正发送

```bash
python3 scripts/publish_x.py --text-file post.txt --image ./card.png \
  --send --expect-user your_handle
```

内部顺序（对应官方样例）：

1. `GET /2/users/me` 校验账号（传了 `--expect-user` 时）
2. `POST /2/media/upload`：`INIT`（`media_type=image/png`、`media_category=tweet_image`）→ `APPEND`（4 MB 分块 multipart）→ `FINALIZE` → 必要时 `STATUS` 轮询
3. `POST /2/tweets`：`{"text": "...", "media": {"media_ids": ["<id>"]}}`，期望 201
4. `GET /2/tweets/{id}?tweet.fields=text` 回读，逐字比对，输出帖子 ID 与链接

### 步骤 6 · 交付与失败处理

成功时输出 `{"status":"posted","id":...,"url":...,"readback":"verified"}`；把链接贴回对话。**回读失败不等于没发出**——先到账号上人工核对，绝不重发。

## 5. 门禁与安全约定

| 约定 | 原因 |
|---|---|
| dry-run 是默认，`--send` 才真发 | 参考 agent-of-empires 与 LifeOS；未确认不触碰线上账号 |
| dry-run 不联网、不读凭证 | 无凭证也能预览，适合放进 Skill 的自动检查 |
| 超限文本拒绝，不截断 | 参考 LifeOS「Never sliced or ellipsized」；截断会毁掉帖子结构 |
| 凭证仅环境变量，仓库无密钥 | Skill 包会被复制、上传、分发，任何硬编码都会泄漏 |
| 发帖失败不自动重试 | 超时/429 时无法确认服务端是否已创建，盲目重试会重复发帖 |
| `--expect-user` 校验 handle | 防止用错账号发布 |
| 发布后回读逐字比对 | 脚本输出不作为成功凭据（LifeOS 的 Ideal State） |
| 只发原创首帖 | 自助层级的回复/引用受限，且本 Skill 不需要 |

## 6. 常见错误

| 现象 | 处理 |
|---|---|
| 401 / 403 | token 过期或 scope 不全；重新走 PKCE 授权，确认 `tweet.write`、`media.write`、`users.read` |
| 媒体上传 403 / 401 | 缺 `media.write`；或误用了 v1.1 上传端点，改用 `POST /2/media/upload` |
| 429 | 已限流；**不要自动重试**，先查账号上是否已有该帖 |
| 媒体 `processing_info.state = failed` | 重新上传图片后再发，此时尚未建帖，重试安全 |
| 回读不一致 / 超时 | 帖子可能已发出，人工核对账号后再决定是否重发 |
| 账号校验失败 | 授权到了别的账号，中止，不要「先发了再说」 |

## 7. 与现有资产的关系 / 待办

- 复用：`scripts/wlen.py`（加权字数）、`render_card.py` 产出的 1600×900 PNG、`references/examples.md` 的帖子骨架。
- 新增：`scripts/publish_x.py`（零第三方依赖，仅标准库 + `wlen.py`）。
- 契约变更：`SKILL.md` 工作流新增**可选**第 7 步；1～6 步与「明确不出」的默认交付不变。
- 待办（需要真实账号才能做）：用真实凭证跑通一次完整发送、验证回读字段、把 token 刷新纳入独立工具、记录实际计费；在此之前不要把 `--send` 写进任何自动化或定时任务。

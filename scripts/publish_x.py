#!/usr/bin/env python3
"""可选：把生成好的帖子与知识卡片发布到 X（Twitter）。

设计原则（见 references/publishing.md）：
  * 默认 dry-run，不联网、不读凭证、不发送任何内容。
  * 只有显式 --send 才会真正发帖；调用方必须已向人确认过内容。
  * 凭证只从环境变量 X_ACCESS_TOKEN 读取，绝不写文件、绝不入库。
  * 超限文本直接拒绝，不截断；发帖后回读校验；失败不自动重试。

用法:
  python3 scripts/publish_x.py --text-file post.txt --image card.png
  python3 scripts/publish_x.py --text-file post.txt --image card.png --send --expect-user your_handle

依赖: 仅 Python 标准库；wlen.py 从同目录复用。
真实发送路径需要有效的 X 用户级 OAuth 2.0 access token（scope 见 publishing.md），
本仓库不含凭证、不含授权流程，未经真实账号验证。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

from wlen import wlen

API = "https://api.x.com"
MAX_WEIGHTED = 280
MAX_IMAGE_BYTES = 5 * 1024 * 1024
CHUNK_BYTES = 4 * 1024 * 1024
MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


def http(method: str, url: str, token: str, *, params=None, json_body=None,
         body=None, content_type=None, timeout=30):
    """返回 (status_code, parsed_json)。HTTP 错误也作为结果返回，由调用方判断。"""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "yijing-yao-xpost/1.0",
    }
    data = None
    if json_body is not None:
        data = json.dumps(json_body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif body is not None:
        data = body
        headers["Content-Type"] = content_type or "application/octet-stream"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return resp.status, json.loads(raw) if raw.strip() else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            payload = {"raw": raw[:500]}
        return exc.code, payload
    except urllib.error.URLError as exc:
        raise SystemExit(f"网络错误（未确认是否已发出，请先核对账号）：{exc}")


def fail(stage: str, status: int, payload: dict) -> None:
    hint = ""
    if status in (401, 403):
        hint = " 检查 token 是否过期、App 权限与 scope（tweet.write / media.write / users.read）。"
    elif status == 429:
        hint = " 已限流；不要自动重试，先确认账号上是否已有该帖，避免重复发布。"
    raise SystemExit(
        f"{stage} 失败：HTTP {status}{hint}\n"
        + json.dumps(payload, ensure_ascii=False)[:800]
    )


def multipart(fields: dict, filename: str, chunk: bytes, mime: str):
    boundary = "----yijing" + uuid.uuid4().hex
    parts = []
    for key, value in fields.items():
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
            f"{value}\r\n".encode("utf-8")
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="media"; '
        f'filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode("utf-8")
    )
    parts.append(chunk)
    parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def upload_image(path: Path, token: str) -> str:
    """X API v2 chunked media upload: INIT -> APPEND -> FINALIZE -> (STATUS)。"""
    total = path.stat().st_size
    if total == 0:
        raise SystemExit("图片为空，已中止")
    mime = MEDIA_TYPES[path.suffix.lower()]
    url = f"{API}/2/media/upload"

    status, data = http("POST", url, token, params={
        "command": "INIT",
        "media_type": mime,
        "total_bytes": total,
        "media_category": "tweet_image",
    }, timeout=60)
    if status not in (200, 201, 202) or "id" not in data.get("data", {}):
        fail("媒体 INIT", status, data)
    media_id = str(data["data"]["id"])
    print(f"[media] INIT ok → media_id={media_id}")

    with path.open("rb") as fh:
        index, sent = 0, 0
        while sent < total:
            chunk = fh.read(CHUNK_BYTES)
            body, ctype = multipart({
                "command": "APPEND",
                "media_id": media_id,
                "segment_index": index,
            }, path.name, chunk, mime)
            status, data = http("POST", url, token, body=body,
                                content_type=ctype, timeout=120)
            if status not in (200, 201, 202, 204):
                fail(f"媒体 APPEND 第 {index} 段", status, data)
            sent += len(chunk)
            index += 1
            print(f"[media] APPEND {sent}/{total} bytes")

    status, data = http("POST", url, token, params={
        "command": "FINALIZE", "media_id": media_id,
    }, timeout=60)
    if not (200 <= status < 300) or data.get("errors") or data.get("error"):
        fail("媒体 FINALIZE", status, data)
    print("[media] FINALIZE ok")

    info = data.get("data", {}).get("processing_info")
    for _ in range(12):
        if not info:
            break
        state = info.get("state")
        if state == "succeeded":
            break
        if state == "failed":
            fail("媒体处理", 422, info)
        time.sleep(int(info.get("check_after_secs", 5)))
        status, data = http("GET", url, token, params={
            "command": "STATUS", "media_id": media_id,
        })
        if status != 200:
            fail("媒体 STATUS", status, data)
        info = data.get("data", {}).get("processing_info")
    return media_id


def main() -> None:
    ap = argparse.ArgumentParser(description="发布周易爻帖到 X（默认 dry-run）")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="帖子全文")
    src.add_argument("--text-file", help="从文件读帖子全文")
    ap.add_argument("--image", help="知识卡片 PNG 路径（可选，不带则发纯文本帖）")
    ap.add_argument("--send", action="store_true", help="真正发送；默认只预览不联网")
    ap.add_argument("--expect-user", help="发送前校验当前账号 handle，防发错号；--send 时必填")
    args = ap.parse_args()

    if args.send and not args.expect_user:
        raise SystemExit("--send 必须同时给 --expect-user：不校验账号就不许真发（防发错号）")

    text = (Path(args.text_file).read_text(encoding="utf-8")
            if args.text_file else args.text).rstrip("\n")
    if not text.strip():
        raise SystemExit("帖子为空，已中止")

    n = wlen(text)
    if n > MAX_WEIGHTED:
        raise SystemExit(f"帖子 {n} 加权字符 > {MAX_WEIGHTED}，拒绝发布（不截断）")

    image = None
    size = 0
    if args.image:
        image = Path(args.image)
        if not image.is_file():
            raise SystemExit(f"图片不存在：{image}")
        if image.suffix.lower() not in MEDIA_TYPES:
            raise SystemExit(f"不支持的图片格式：{image.suffix}")
        size = image.stat().st_size
        if size == 0 or size > MAX_IMAGE_BYTES:
            raise SystemExit(f"图片大小 {size} 字节超出 1B~5MB 限制")

    print("----- 帖子预览 -----")
    print(text)
    print("--------------------")
    print(f"加权字符：{n} / {MAX_WEIGHTED}（X 按 CJK 每字 2 计）")
    if image:
        print(f"附图：{image}（{size / 1024 / 1024:.2f} MiB）")

    if not args.send:
        checks = "长度 OK / " + ("图片 OK / " if image else "无附图 / ") \
                 + "未读取凭证 / 未联网"
        print(f"[dry-run] 检查通过：{checks}")
        steps = "users/me 校验（可选）→ 媒体上传 → " if image else "users/me 校验（可选）→ "
        print(f"[dry-run] 将执行：{steps}POST /2/tweets → 回读")
        print("[dry-run] 没有发送任何内容。人工确认后加 --send 才会发布。")
        return

    token = os.environ.get("X_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("未设置 X_ACCESS_TOKEN，已中止（未联网）。见 references/publishing.md")

    if args.expect_user:
        status, data = http("GET", f"{API}/2/users/me", token)
        if status != 200 or "username" not in data.get("data", {}):
            fail("账号校验 /2/users/me", status, data)
        actual = data["data"]["username"]
        if actual.lower() != args.expect_user.lstrip("@").lower():
            raise SystemExit(f"账号不符：当前 {actual}，期望 {args.expect_user}；已中止")
        print(f"[auth] 账号校验通过：@{actual}")

    media_ids = [upload_image(image, token)] if image else []
    payload = {"text": text}
    if media_ids:
        payload["media"] = {"media_ids": media_ids}

    print("[post] POST /2/tweets ...")
    status, data = http("POST", f"{API}/2/tweets", token, json_body=payload)
    if status != 201 or "id" not in data.get("data", {}):
        fail("发帖 /2/tweets", status, data)
    post_id = str(data["data"]["id"])

    status, read = http("GET", f"{API}/2/tweets/{post_id}", token,
                        params={"tweet.fields": "text"})
    verified = status == 200 and read.get("data", {}).get("text") == text
    print(json.dumps({
        "status": "posted",
        "id": post_id,
        "url": f"https://x.com/i/status/{post_id}",
        "media_ids": media_ids,
        "readback": "verified" if verified else "FAILED_CHECK_MANUALLY",
    }, ensure_ascii=False, indent=2))
    if not verified:
        print("警告：回读未通过，帖子可能已发出，请到账号上人工核对，不要重发。",
              file=sys.stderr)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""周易爻知识卡片生成器（横版 1600x900）。

用法:
  python3 render_card.py <config.json> [--out /abs/path/output.png] [--chrome /path/to/browser]

不传 --out 时输出到 /workspace/<config.out>。
配置字段见 references/conventions.md 第 6 节。

浏览器查找顺序：--chrome → CHROME_BIN → PATH 里的 chrome-headless-shell /
chromium / google-chrome → puppeteer、playwright 的缓存构建 → macOS App。
每次渲染都在临时目录里新建 user-data-dir，绝不碰日常浏览器的 profile。
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"

# 独立的无头 Chromium 构建优先：它们不读日常浏览器的 profile，
# 不会和用户正在用的 Chrome 抢单例锁（那正是「跑一次卡片，Chrome 崩一次」的成因）。
HEADLESS_PATTERNS = [
    "~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-*/chrome-headless-shell",
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-mac/headless_shell",
]
FULL_PATTERNS = [
    "~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
]
PATH_NAMES = [
    "chrome-headless-shell", "chromium", "chromium-browser",
    "google-chrome", "google-chrome-stable",
]
MAC_BUNDLES = [
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def build_html(cfg: dict) -> str:
    tpl = (ASSETS / "card_template.html").read_text(encoding="utf-8")

    rows = []
    for i, ln in enumerate(cfg["yao_lines"]):
        hot = (i == 6 - cfg["hot_from_bottom"])
        cls = " hot" if hot else ""
        note = cfg["hot_note"] if hot else ln.get("note", "")
        if ln.get("yin"):
            bar = f'<div class="bar yin{cls}"><i></i><i></i></div>'
        else:
            bar = f'<div class="bar{cls}"></div>'
        rows.append(
            f'<div class="yao">{bar}'
            f'<div class="name{cls}">{ln["name"]}</div>'
            f'<div class="note{cls}">{note}</div></div>'
        )
        if i == 2:  # 上卦三爻之后分界
            rows.append(
                f'<div class="split"><div class="dash"></div>'
                f'<div class="lab sans">{cfg["split_label"]}</div></div>'
            )

    points = "\n".join(
        f'          <div><span>·</span>{p}</div>' for p in cfg["points"]
    )
    trans1 = (cfg.get("trans1") or "").strip()
    if not trans1:
        raise SystemExit("缺少 trans1：卡片必须给出爻辞的白话译文")
    trans2 = (cfg.get("trans2") or "").strip()
    src2 = cfg.get("src2") or ""
    src2_block = (
        f'        <div class="src2">{src2}</div>\n'
        f'        <div class="trans2">{trans2}</div>'
    ) if src2 else ""
    if src2 and not trans2:
        src2_block = f'        <div class="src2">{src2}</div>'
    src3 = cfg.get("src3") or []
    src3_block = (
        f'        <div class="src3">{"<br>".join(src3)}</div>' if src3 else ""
    )

    repl = {
        "GUA_LABEL": cfg["gua_label"],
        "GUAXIANG": cfg["guaxiang"],
        "YAO_ROWS": "\n".join(rows),
        "FOOT1": cfg["foot1"],
        "FOOT2": cfg["foot2"],
        "TAG": cfg["tag"],
        "SEAL": cfg["seal"],
        "TITLE": "<br>".join(cfg["title"]),
        "SRC1": cfg["src1"],
        "TRANS1": trans1,
        "SRC2_BLOCK": src2_block,
        "SRC3_BLOCK": src3_block,
        "POINTS": points,
        "BOTTOM": cfg["bottom"],
    }
    for key, value in repl.items():
        tpl = tpl.replace("{{" + key + "}}", value)
    if "{{" in tpl:
        raise SystemExit("模板存在未替换占位符：" + tpl[tpl.index("{{"):tpl.index("{{") + 40])
    return tpl


def find_browser(explicit: str | None = None) -> str:
    """按「专用无头构建 → PATH → macOS App」的顺序找浏览器。"""
    if explicit:
        if Path(explicit).is_file():
            return explicit
        raise SystemExit(f"--chrome 指向的文件不存在：{explicit}")

    env = os.environ.get("CHROME_BIN", "").strip()
    if env:
        if Path(env).is_file():
            return env
        raise SystemExit(f"CHROME_BIN 指向的文件不存在：{env}")

    # 专用无头构建最先：不共享日常浏览器的单例与 profile。
    for pattern in HEADLESS_PATTERNS:
        for hit in sorted(glob.glob(os.path.expanduser(pattern)), reverse=True):
            if os.access(hit, os.X_OK):
                return hit

    for name in PATH_NAMES:
        hit = shutil.which(name)
        if hit:
            return hit

    for pattern in FULL_PATTERNS:
        for hit in sorted(glob.glob(os.path.expanduser(pattern)), reverse=True):
            if os.access(hit, os.X_OK):
                return hit

    for cand in MAC_BUNDLES:
        if Path(cand).is_file():
            return cand

    raise SystemExit(
        "未找到可用的浏览器。任选一种：\n"
        "  1) 装独立的无头构建（推荐，与日常 Chrome 完全隔离）：\n"
        "     npx --yes @puppeteer/browsers install chrome-headless-shell@stable\n"
        "  2) 指定路径：CHROME_BIN=/path/to/chrome 或 --chrome /path/to/chrome"
    )


def _tempdir():
    try:
        return tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
    except TypeError:  # Python < 3.10
        return tempfile.TemporaryDirectory()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="配置 JSON 路径")
    ap.add_argument("--out", help="输出 PNG 绝对路径（默认 /workspace/<out>）")
    ap.add_argument("--chrome", help="指定浏览器可执行文件（也可用 CHROME_BIN）")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else Path("/workspace") / cfg["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(cfg)

    browser = find_browser(args.chrome)
    is_shell = "headless" in Path(browser).name.lower()

    with _tempdir() as td:
        tmp = Path(td)
        shutil.copy(ASSETS / "ink_bg.png", tmp / "ink_bg.png")
        page = tmp / "page.html"
        page.write_text(html, encoding="utf-8")
        raw = tmp / "raw.png"
        # 每次渲染给一个独立 profile：与用户日常 Chrome 互不干扰，
        # 也不会把登录态、扩展、缓存写进真实 profile。
        profile = tmp / "profile"

        flags = [
            f"--user-data-dir={profile}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-extensions",
            "--disable-sync",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-breakpad",
            "--disable-crash-reporter",
            "--noerrdialogs",
            "--mute-audio",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            "--force-device-scale-factor=1",
            "--window-size=1600,1000",
            "--virtual-time-budget=3000",
            f"--screenshot={raw}",
            f"file://{page}",
        ]
        if not is_shell:
            flags.insert(0, "--headless=new")

        try:
            proc = subprocess.run(
                [browser] + flags, capture_output=True, text=True, timeout=90
            )
        except subprocess.TimeoutExpired:
            raise SystemExit(f"截图超时（90s）：{browser}")

        if proc.returncode != 0 or not raw.exists():
            err = ((proc.stderr or "") + (proc.stdout or "")).strip()
            raise SystemExit(
                f"截图失败（exit {proc.returncode}）\n浏览器：{browser}\n{err[-800:]}"
            )

        from PIL import Image
        Image.open(raw).crop((0, 0, 1600, 900)).save(out)

    print(f"已生成: {out} (1600x900)｜浏览器: {Path(browser).name}")


if __name__ == "__main__":
    main()

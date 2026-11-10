#!/usr/bin/env python3
"""周易爻知识卡片生成器（横版 1600x900）。

用法:
  python3 render_card.py <config.json> [--out /abs/path/output.png]

不传 --out 时输出到 /workspace/<config.out>。
配置字段见 references/conventions.md 第 6 节。
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config", help="配置 JSON 路径")
    ap.add_argument("--out", help="输出 PNG 绝对路径（默认 /workspace/<out>）")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    out = Path(args.out) if args.out else Path("/workspace") / cfg["out"]
    out.parent.mkdir(parents=True, exist_ok=True)
    html = build_html(cfg)

    chromium = shutil.which("chromium") or shutil.which("google-chrome")
    if not chromium:
        raise SystemExit("未找到 chromium / google-chrome")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        shutil.copy(ASSETS / "ink_bg.png", tmp / "ink_bg.png")
        page = tmp / "page.html"
        page.write_text(html, encoding="utf-8")
        raw = tmp / "raw.png"
        subprocess.run([
            chromium, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--allow-file-access-from-files",
            "--force-device-scale-factor=1", "--window-size=1600,1000",
            "--virtual-time-budget=3000", f"--screenshot={raw}",
            f"file://{page}",
        ], check=True, capture_output=True)
        from PIL import Image
        Image.open(raw).crop((0, 0, 1600, 900)).save(out)

    print(f"已生成: {out} (1600x900)")


if __name__ == "__main__":
    main()

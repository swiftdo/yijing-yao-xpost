#!/usr/bin/env python3
"""X 加权字符数核算（twitter-text 规则）。

用法:
  python3 wlen.py "帖子文本"
  python3 wlen.py post.txt
  cat post.txt | python3 wlen.py -
"""
import re
import sys
from pathlib import Path

# twitter-text 把每个链接都折算成 t.co 的 23 个字符，与实际长度无关。
TCO_LEN = 23
URL_RE = re.compile(r"(?:https?://|www\.)[!-~]+", re.IGNORECASE)
# 紧跟在链接后面的标点不算链接的一部分，仍按普通字符计。
TRAILING = ".,;:!?)]}'\u3002\uff0c\uff1b\uff1a\uff01\uff1f\u300d\u300f\uff09"


def _weighted(s: str) -> int:
    total = 0
    for ch in s:
        cp = ord(ch)
        if (cp <= 0x10FF) or (0x2000 <= cp <= 0x200D) \
                or (0x2010 <= cp <= 0x201F) or (0x2032 <= cp <= 0x2037):
            total += 1
        else:
            total += 2
    return total


def wlen(s: str) -> int:
    total, pos = 0, 0
    for m in URL_RE.finditer(s):
        total += _weighted(s[pos:m.start()])
        url = m.group().rstrip(TRAILING)
        total += TCO_LEN + _weighted(m.group()[len(url):])
        pos = m.end()
    return total + _weighted(s[pos:])


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-":
            text = sys.stdin.read()
        elif Path(arg).is_file():
            text = Path(arg).read_text(encoding="utf-8")
        elif Path(arg).suffix.lower() in {".txt", ".md"}:
            # 防止把文件名当成帖子正文核算：文件不存在时直接报错，别静默放行
            raise SystemExit(f"文件不存在：{arg}")
        else:
            text = arg
    else:
        text = sys.stdin.read()
    n = wlen(text.rstrip("\n"))
    status = "可发" if n <= 280 else "超限"
    print(f"weighted = {n} | 上限 280 | 余量 {280 - n} | {status}")
    if n > 280:
        sys.exit(1)


if __name__ == "__main__":
    main()

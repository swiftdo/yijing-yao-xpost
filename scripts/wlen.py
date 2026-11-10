#!/usr/bin/env python3
"""X 加权字符数核算（twitter-text 规则）。

用法:
  python3 wlen.py "帖子文本"
  python3 wlen.py post.txt
  cat post.txt | python3 wlen.py -
"""
import sys
from pathlib import Path


def wlen(s: str) -> int:
    total = 0
    for ch in s:
        cp = ord(ch)
        if (cp <= 0x10FF) or (0x2000 <= cp <= 0x200D) \
                or (0x2010 <= cp <= 0x201F) or (0x2032 <= cp <= 0x2037):
            total += 1
        else:
            total += 2
    return total


def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "-":
            text = sys.stdin.read()
        elif Path(arg).is_file():
            text = Path(arg).read_text(encoding="utf-8")
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

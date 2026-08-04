#!/usr/bin/env python3
"""Converts plain text with [title](url) links to Telegram MarkdownV2 format.

Usage:
    echo "plain text with [link](url)" | python3 escape_mdv2.py

Reads from stdin, writes escaped MarkdownV2 to stdout.
Hyperlink syntax [text](url) is preserved as valid MarkdownV2 links.
All other special characters are escaped.
"""

import re
import sys

SPECIAL_CHARS = r'_*[]()~`>#+=|{}.!-'


def escape_mdv2(text):
    # 1. Extract and protect hyperlinks
    links = []
    def protect(m):
        links.append((m.group(1), m.group(2)))
        return f'\x00LINK{len(links)-1}\x00'

    protected = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', protect, text)

    # 2. Escape all special chars in the remaining text
    escaped = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', protected)

    # 3. Restore links with internal escaping
    def restore(m):
        idx = int(m.group(1))
        title, url = links[idx]
        # Escape special chars inside title and url
        t = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', title)
        u = re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', url)
        return f'[{t}]({u})'

    result = re.sub(r'\x00LINK(\d+)\x00', restore, escaped)
    return result


if __name__ == '__main__':
    text = sys.stdin.read()
    print(escape_mdv2(text))

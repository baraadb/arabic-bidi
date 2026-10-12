#!/usr/bin/env python3
"""check_bidi.py — find common Arabic/RTL + English mixing problems.

Usage:
    python3 check_bidi.py FILE [FILE ...]
    cat reply.md | python3 check_bidi.py -

Works on Markdown, HTML, SVG and plain text. Prints one finding per line:
    file:line: LEVEL code: message  -> suggestion
Exits 1 if any ERROR was found, otherwise 0. Standard library only.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass

RTL_LETTER = re.compile(r"[֐-ࣿיִ-﷿ﹰ-﻿]")
ARABIC_LETTER = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
LATIN_LETTER = re.compile(r"[A-Za-zÀ-ɏ]")
STRONG = re.compile(r"[A-Za-zÀ-ɏ֐-ࣿיִ-﷿ﹰ-﻿]")
URL = re.compile(r"https?://\S+|[\w.+-]+@[\w-]+\.[\w.]+")
TAG = re.compile(r"<[^>]+>")


@dataclass
class Finding:
    line: int
    level: str
    code: str
    message: str
    fix: str


def first_strong(text: str) -> str | None:
    m = STRONG.search(text)
    if not m:
        return None
    return "rtl" if RTL_LETTER.match(m.group()) else "ltr"


def strip_md_prefix(line: str) -> str:
    """Remove list markers, heading hashes, quote markers and leading digits/punctuation
    that don't carry direction, but keep markdown that hides a Latin word (**, `, [)."""
    s = line.lstrip()
    s = re.sub(r"^(>\s*)+", "", s)
    s = re.sub(r"^#{1,6}\s+", "", s)
    s = re.sub(r"^([-*+]|\d+[.)])\s+", "", s)
    s = re.sub(r"^\|\s*", "", s)
    return s


def check_markdown(lines: list[str]) -> list[Finding]:
    out: list[Finding] = []
    in_code = False
    for i, raw in enumerate(lines, 1):
        if raw.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code or not ARABIC_LETTER.search(raw):
            continue
        cells = [c for c in raw.strip().strip("|").split("|")] if raw.lstrip().startswith("|") else [raw]
        for cell in cells:
            if not ARABIC_LETTER.search(cell):
                continue  # pure-English cell is fine
            body = strip_md_prefix(cell)
            # remove markdown link targets so the URL doesn't count as text
            visible = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", body)   # images and badges
            visible = re.sub(r"\]\([^)]*\)", "]", visible)          # link targets
            visible = TAG.sub("", visible)                              # inline HTML tags
            visible = visible.replace("‏", "א") if visible.startswith("‏") else visible
            if first_strong(visible) == "ltr":
                lead = visible.strip()[:30]
                out.append(Finding(i, "ERROR", "starts-ltr",
                                   f"Arabic line starts with a Latin run: «{lead}»",
                                   "rephrase so the line starts with an Arabic word (or prefix U+200F as last resort)"))
        risky = [
            (r"(?<!‎)\b[A-Za-z]{1,3}(\+\+|#)(?!‎)", "symbol after English (C++, C#) shows reversed"),
            (r"(?<!‎)(?<![\w.])\.[A-Za-z]{2,}", "leading dot (.NET) jumps to the other side"),
            (r"[A-Za-z]\S*\s+\d+\+(?!‎)", "trailing + after a version (20+) jumps before the name"),
            (r"(?<![\w‎])\d+\s*-\s*\d+(?![\w‎])", "number range with '-' shows reversed (10-20 -> 20-10)"),
            (r"(?<![\w‎])\+\d[\d ]{5,}", "phone number with + / spaces shows reversed"),
            (r"(?<![\w‎])-\d+(\.\d+)?%", "negative percentage reorders"),
            (r"(?<![\w‎])[$€£]\d", "currency symbol before number moves to the other side"),
        ]
        for pattern, why in risky:
            if re.search(pattern, raw) and ARABIC_LETTER.search(raw):
                out.append(Finding(i, "WARN", "symbol-jump", why,
                                   "rephrase in Arabic, or wrap the item in U+200E (LRM) on both sides"))
        text_no_code = re.sub(r"`[^`]*`", "", raw)
        text_no_code = re.sub(r"\]\([^)]*\)", "]", text_no_code)
        text_no_code = TAG.sub(" ", text_no_code)
        for m in URL.finditer(text_no_code):
            if True:
                out.append(Finding(i, "WARN", "bare-url",
                                   f"bare URL/email inside Arabic text: {m.group()[:40]}",
                                   "wrap it in backticks or a markdown link with Arabic text"))
    return out


def check_html(lines: list[str], text: str) -> list[Finding]:
    out: list[Finding] = []
    has_arabic = bool(ARABIC_LETTER.search(TAG.sub(" ", text)))
    if not has_arabic:
        return out
    lower = text.lower()
    if not re.search(r"""dir\s*=\s*["']?(rtl|auto)""", lower) and "direction: rtl" not in lower \
            and "direction:rtl" not in lower and 'direction="rtl"' not in lower:
        out.append(Finding(1, "ERROR", "no-dir",
                           "page contains Arabic but declares no dir=\"rtl\"/\"auto\"",
                           'add <html lang="ar" dir="rtl"> or dir="rtl" on the Arabic container'))
    is_rtl_page = bool(re.search(r"""<html[^>]*dir\s*=\s*["']?rtl""", lower)) or bool(
        re.search(r"""^\s*<[a-z]+[^>]*dir\s*=\s*["']?rtl""", lower))
    physical = re.compile(r"(?<![-\w])(margin-left|margin-right|padding-left|padding-right|border-left|border-right"
                          r"|text-align\s*:\s*(left|right)|float\s*:\s*(left|right)|(?<!-)\bleft\s*:|(?<!-)\bright\s*:)")
    in_pre = False
    for i, line in enumerate(lines, 1):
        l = line.lower()
        if re.search(r"<pre(?![^>]*dir)", l) and not re.search(r"pre\s*{[^}]*direction\s*:\s*ltr", lower):
            out.append(Finding(i, "WARN", "pre-dir", "<pre> on an Arabic page without dir=\"ltr\"",
                               'add dir="ltr" to code blocks'))
        if "<pre" in l:
            in_pre = True
        if "</pre>" in l:
            in_pre = False
            line = re.sub(r"(?is).*</pre>", "", line)
            l = line.lower()
        if is_rtl_page and not in_pre and not re.search(r"direction\s*:\s*ltr", l):
            for m in physical.finditer(l):
                out.append(Finding(i, "WARN", "physical-css",
                                   f"physical direction CSS `{m.group().strip()}` on an RTL page",
                                   "use logical properties (margin-inline-start, text-align: start, inset-inline-start...)"))
        if "letter-spacing" in l and not re.search(r"letter-spacing\s*:\s*(0|normal)", l):
            out.append(Finding(i, "INFO", "letter-spacing",
                               "letter-spacing breaks Arabic letter joining if applied to Arabic text",
                               "reset to 0 for Arabic text, or scope it to Latin-only elements"))
        if re.search(r"font-style\s*:\s*italic", l):
            out.append(Finding(i, "INFO", "italic", "italic on Arabic text renders poorly",
                               "use weight or color for emphasis on Arabic"))
        visible = TAG.sub(" ", line)
        if ARABIC_LETTER.search(visible) and not in_pre:
            for m in URL.finditer(visible):
                if not re.search(r"<bdi|dir\s*=\s*.?ltr|<code|<a ", line, re.I):
                    out.append(Finding(i, "WARN", "unisolated",
                                       f"URL/email in Arabic text without isolation: {m.group()[:40]}",
                                       "wrap in <bdi> or <span dir=\"ltr\">"))
        if re.search(r"<(input|textarea)(?![^>]*dir)", l) and not re.search(
                r"type\s*=\s*.?(checkbox|radio|hidden|submit|button|range|color|file)", l):
            out.append(Finding(i, "INFO", "input-dir", "form field without dir",
                               'use dir="auto" for free text, dir="ltr" for email/url/tel/password'))
    if "<canvas" in lower and "direction" not in lower and "rtl" not in lower.split("<canvas", 1)[1]:
        out.append(Finding(1, "WARN", "canvas", "canvas/chart found; canvas ignores CSS direction",
                           "set ctx.direction='rtl' or the chart library's rtl options"))
    return out


def check(text: str) -> list[Finding]:
    lines = text.splitlines()
    has_tags = bool(re.search(r"<(html|body|div|p|svg|span|section)\b", text, re.I))
    is_markdown = bool(re.search(r"^(#{1,6} |[-*+] |\d+\. |```)", text, re.M))
    looks_html = bool(re.match(r"\s*(<!doctype|<html|<svg|<\?xml)", text, re.I)) or (has_tags and not is_markdown)
    findings = check_html(lines, text) if looks_html else check_markdown(lines)
    return findings


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    errors = 0
    for path in argv[1:]:
        text = sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()
        for f in check(text):
            errors += f.level == "ERROR"
            print(f"{path}:{f.line}: {f.level} {f.code}: {f.message}  -> {f.fix}")
    if errors == 0:
        print("no errors found")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

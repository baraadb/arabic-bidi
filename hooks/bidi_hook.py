#!/usr/bin/env python3
"""Claude Code PostToolUse hook: check files Claude just wrote for Arabic/RTL bidi problems.

Reads the hook event JSON on stdin. If the written file is a page or document type and the
checker finds errors, prints them on stderr and exits 2, which sends the report back to Claude so it
can fix the lines. Warnings only are passed back as additional context (exit 0).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "skills", "arabic-bidi", "scripts"))

from check_bidi import check  # noqa: E402

EXTENSIONS = {".html", ".htm", ".svg", ".md", ".mdx", ".jsx", ".tsx", ".vue", ".svelte", ".txt"}
MAX_LINES = 15


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("path")
    if not path or os.path.splitext(path)[1].lower() not in EXTENSIONS or not os.path.isfile(path):
        return 0
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError):
        return 0

    findings = [f for f in check(text) if f.level in ("ERROR", "WARN")]
    if not findings:
        return 0

    lines = [f"arabic-bidi: {len(findings)} issue(s) in {os.path.basename(path)}:"]
    for f in findings[:MAX_LINES]:
        lines.append(f"  line {f.line}: {f.level} {f.code}: {f.message} -> {f.fix}")
    if len(findings) > MAX_LINES:
        lines.append(f"  ...and {len(findings) - MAX_LINES} more")
    if any(f.level == "ERROR" for f in findings):
        lines.append("Fix the ERROR lines; check the WARN lines and fix any that would display wrongly.")
        print("\n".join(lines), file=sys.stderr)
        return 2
    # warnings only: pass them to Claude as context without blocking
    lines.append("These are warnings: check them and fix any that would display wrongly.")
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": "\n".join(lines)}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())

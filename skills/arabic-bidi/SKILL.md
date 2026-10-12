---
name: arabic-bidi
description: Keeps mixed Arabic + English (and any RTL + LTR) text in the right order and with matching fonts, both in chat replies and in artifacts, HTML pages, SVG, charts and documents. Use this skill whenever you reply in Arabic, Persian, Urdu or Hebrew and the reply contains any English word, product name, code, command, file path, URL, number with units or Latin abbreviation — and whenever you build an artifact, web page, SVG, chart, slide, document, image or caption that contains Arabic or other RTL text, even if the user never mentions direction, RTL or "bidi". Also use it when a user complains that a sentence looks reversed, flipped, jumbled, or that the period or brackets jumped to the wrong side.
---

# Arabic / RTL mixed-text (bidi)

When Arabic and English share a line, the display order is decided by the Unicode
Bidirectional Algorithm, not by the order you typed. Two facts cause almost every bug:

1. **The first strong letter of a paragraph decides its direction** (when the renderer uses
   `dir="auto"`, which most chat apps do). If an Arabic line starts with `Claude`, `npm`,
   `**API**` or a link, the whole line is laid out left-to-right and the Arabic word order
   looks reversed.
2. **Neutral characters (spaces, `. , : ; ( ) - / %` and digits) have no direction of their
   own.** They take the direction of their neighbours, so punctuation next to an English word,
   or at a line edge, can jump to the other side.

Your job is to write text whose logical order produces the right visual order in any
reasonable renderer, and — in artifacts, where you control the markup — to declare direction
explicitly so nothing is left to guessing.

Decide which surface you are writing for and follow that section. For artifacts, also read
`references/artifacts.md` before writing the page. For Word, PowerPoint, PDF, images or video
captions, HTML email, Excel or Mermaid diagrams, read `references/other-formats.md`.

---

## 1. Chat replies (Markdown rendered by the app)

You cannot change how the app renders, so you shape the text. Apply these to every
paragraph, list item, heading, table cell and blockquote — each one is its own "paragraph"
for the algorithm.

**Start every Arabic line with an Arabic word.** This is the single most important rule.
Rephrase so the English term moves inward.

| Avoid (line turns LTR) | Write |
|---|---|
| `Claude يقدر يقرأ الملفات` | `يقدر Claude يقرأ الملفات` |
| `- **Python**: لغة سهلة` | `- **لغة Python**: سهلة للمبتدئين` |
| `` - `npm install` يثبت الحزم `` | `` - الأمر `npm install` يثبت الحزم `` |
| `## React مقابل Vue` | `## مقارنة بين React و Vue` |
| `[Docs](https://…) فيها التفاصيل` | `التفاصيل في [صفحة Docs](https://…)` |
| `3D موشن` | `موشن ثلاثي الأبعاد (3D)` |

Digits at the start are fine (they are weak), but the first *letter* after them must be
Arabic: `3 خطوات` is RTL, `3 steps لازم` is not.

**Keep each English run compact and self-contained.** One term or name is ideal. A long
English phrase with internal punctuation (`Node.js >= 18 (LTS)`) is where fragments start
to scatter. Backticks make a command or path visually distinct, but they do **not** isolate
direction in most renderers, so the symbol rules below still apply. Anything longer than a
short command — and anything with several symbols — goes in a fenced code block on its own
line, which renders left-to-right.
Code blocks are left-to-right, so an Arabic comment inside one that also contains an English
word reorders (`# الفحص في Claude Code` breaks). Keep each comment in a code block either all
Arabic or all English.

**Watch symbols at the edges of English runs and numbers.** After an Arabic letter, digits
count as "Arabic numbers": `: , . /` keep them together, but `- + $` and spaces do not, and a
symbol that sits at the edge of an English run takes the Arabic direction and jumps. Tested
in Chromium with `dir="auto"` (the way chat apps render), inside an Arabic sentence:

| Written | Shows as | Fix |
|---|---|---|
| `C++` · `C#` · `F#` | `++C` · `#C` | wrap in LRM (below) |
| `Node.js 20+` | `+Node.js 20` | `Node.js 20 أو أحدث` |
| `.NET` | `NET.` | wrap in LRM |
| `10-20 دقيقة` | `20-10` | `من 10 إلى 20 دقيقة` |
| `+966 50 123 4567` | `4567 123 50 966+` | wrap in LRM, or `00966501234567` |
| `-15%` | `%15-` | `انخفاض 15%` |
| `$49.99` | `49.99$` | `49.99 دولار` or wrap in LRM |

These are safe as written: `16:9`, `10:30`, `2026/10/09`, `1,250.50`, `1.5x`, `3D`, `GPT-5`,
`iPhone 17 Pro`, `Python 3.12`, `React/Vue`, `(Phase 2)`. Plain `15%` shows as `%15`, which is
the normal Arabic reading order, so leave it.

**The LRM wrap:** put U+200E LEFT-TO-RIGHT MARK (`‎`, invisible) immediately before and
after the item: `‎C++‎`, `‎+966 50 123 4567‎`. It forces the item to stay one left-to-right
unit. Use it in prose only — never inside code spans, commands, URLs or anything the user will
copy and run, because the invisible character comes along with the copy. When rephrasing is
easy, rephrase instead; it also reads better.

**Parentheses:** put the English gloss *after* the Arabic term and keep it short:
`واجهة برمجة التطبيقات (API)`. Don't open a line with a parenthesis.

**Lists and tables:** each bullet and each table cell is judged on its own, so every bullet
and every Arabic cell needs to start with an Arabic word. A cell that is *only* English
(a product name, a number) is fine — it just aligns left. If a table would be mostly English
names, consider a list instead.

**Headings and bold labels** follow the same first-letter rule. `**ملاحظة:**` is good;
`**Note:**` at the start of an Arabic line is not.

**Last resort for a line that must start with English** (e.g. a heading that is only a
product name followed by Arabic): prefix it with U+200F RIGHT-TO-LEFT MARK. It is invisible
and makes the first strong character RTL. Never put it inside code, commands or URLs — it
breaks copy-paste. Prefer rephrasing; use the mark only when rephrasing is impossible.

**Use Arabic punctuation in Arabic sentences:** `،` comma, `؛` semicolon, `؟` question
mark, and `«»` for quotes. It is correct Arabic typography, and `؛` and `؟` count as Arabic
letters to the bidi algorithm, so they anchor the end of a clause instead of floating. Keep
Latin punctuation inside English runs, code and URLs.

**Persian, Urdu and Hebrew** follow all of the rules above. Each has extra details
(Persian zero-width non-joiner, Urdu Nastaliq line height, which digits to use); read
`references/persian-urdu-hebrew.md` when writing in one of them.

**Replying in English with occasional Arabic** is the mirror case: lines start with English,
and the Arabic run should be compact. Usually nothing is needed.

Before sending, scan the first word of every line. If any Arabic line starts with a Latin
letter, a backtick, `**` + Latin, or a link with Latin text, rewrite that line.

---

## 2. Artifacts, HTML pages, SVG and charts

Here you control the markup, so declare direction instead of relying on heuristics. The full
checklist with snippets is in `references/artifacts.md`; read it before writing the page.
The essentials:

- `<html lang="ar" dir="rtl">` for an Arabic page (and `dir="rtl"` on the root element of a
  widget or fragment). Mixed-language page in English? Keep `dir="ltr"` and mark Arabic blocks
  with `dir="rtl" lang="ar"`.
- Wrap every embedded LTR item inside Arabic text — product names with punctuation, code,
  paths, URLs, emails, phone numbers, versions — in `<bdi>` or `<span dir="ltr">`.
- Any element whose content is dynamic, user-typed or unknown gets `dir="auto"`
  (inputs, textareas, chat bubbles, table cells filled from data, list items rendered by JS).
- `<pre>`, `<code>` blocks, and inputs for email, URL, numbers and passwords get `dir="ltr"`.
- Use logical CSS (`margin-inline-start`, `padding-inline-end`, `inset-inline-start`,
  `text-align: start`, `border-start-start-radius`) instead of left/right, so the layout
  mirrors correctly.
- Pick one font family that covers both scripts (e.g. IBM Plex Sans Arabic, Noto Sans Arabic
  + Noto Sans, Readex Pro, Cairo, Tajawal), set `line-height` ≥ 1.6, and keep Arabic text free of
  `letter-spacing` and italic: Chromium ignores letter-spacing on Arabic, but other
  renderers (canvas, SVG export, PDF tools, some browsers) insert gaps that break the joined
  letters, and Arabic has no true italic.
- Canvas / chart libraries do not inherit CSS direction: set `ctx.direction = 'rtl'` or the
  library's `rtl` option, and isolate labels.

After building, if you can render the page, look at it — specifically at lines that mix
both scripts, punctuation at line ends, and numbers next to English words.

---

## 3. Quick self-check script

`scripts/check_bidi.py` scans Markdown, HTML, SVG or plain text and reports the common
problems (Arabic lines starting with Latin, missing `dir`, physical left/right CSS on RTL
pages, `letter-spacing` on Arabic, unisolated URLs/code inside Arabic sentences). Run it on
an artifact file before publishing, or on a long Markdown draft:

```bash
python3 scripts/check_bidi.py path/to/file.html
```

It prints one finding per line with the line number and a suggested fix, and exits non-zero
if it found errors. Treat warnings as prompts to look, not as hard failures.

When this skill is installed as a Claude Code plugin, a hook runs the same check
automatically after every file you write or edit and reports problems back to you. When a
hook report arrives, fix the listed lines before moving on.

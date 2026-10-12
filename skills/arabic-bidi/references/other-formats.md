# Other formats — Word, PowerPoint, PDF, images, video captions

The text-writing rules from SKILL.md (start lines with an Arabic word, keep English runs
compact) still apply everywhere. These are the format-specific switches on top.

## Word (.docx)

Direction is set per paragraph and per run, and Arabic uses the **complex-script** font slot,
not the normal one:

```xml
<w:p>
  <w:pPr><w:bidi/><w:jc w:val="start"/></w:pPr>
  <w:r>
    <w:rPr>
      <w:rFonts w:ascii="IBM Plex Sans" w:hAnsi="IBM Plex Sans" w:cs="IBM Plex Sans Arabic"/>
      <w:rtl/>
      <w:szCs w:val="28"/>   <!-- size for Arabic; w:sz is for Latin -->
    </w:rPr>
    <w:t>النص العربي</w:t>
  </w:r>
</w:p>
```

- `<w:bidi/>` on the paragraph = RTL paragraph. `<w:rtl/>` on the run = Arabic run.
- Latin runs inside an Arabic paragraph: separate `<w:r>` without `<w:rtl/>`.
- Bold/size for Arabic: `<w:bCs/>` and `<w:szCs/>` (the `Cs` variants), otherwise they are
  ignored for Arabic text.
- Tables: `<w:bidiVisual/>` in `<w:tblPr>` to order columns right-to-left.
- docx (JavaScript library): `new Paragraph({ bidirectional: true, children: [new TextRun({ text, rightToLeft: true, font: { cs: 'IBM Plex Sans Arabic' } })] })`.

## PowerPoint (.pptx)

```xml
<a:pPr algn="r" rtl="1"/>
<a:rPr lang="ar-SA"><a:cs typeface="IBM Plex Sans Arabic"/></a:rPr>
```

- `rtl="1"` on the paragraph properties; `algn="r"` for right alignment.
- Font for Arabic goes in `<a:cs>`; `<a:latin>` only affects Latin.
- python-pptx has no direct API for `rtl`; set it on the `a:pPr` element via lxml.

## PDF (HTML → PDF)

Build the HTML exactly as in `artifacts.md` and print with a Chromium-based renderer
(Playwright / headless Chrome). Avoid ReportLab and older PDF libraries for Arabic — they
don't shape letters (they come out disconnected and reversed) unless you add
`arabic-reshaper` + `python-bidi`, which is fragile for mixed text.

## Images (Pillow)

Pillow shapes Arabic correctly only with the **raqm** layout engine:

```python
from PIL import features, ImageFont, ImageDraw
assert features.check('raqm'), "Install libraqm (apt install libraqm0) for Arabic shaping"
font = ImageFont.truetype("IBMPlexSansArabic-Bold.ttf", 64, layout_engine=ImageFont.Layout.RAQM)
draw.text((x, y), "نص عربي مع Claude", font=font, direction="rtl", language="ar", anchor="ra")
```

Without raqm, letters render disconnected and in reverse order. Do not "fix" that with
`arabic_reshaper` + `get_display` when raqm is available — it double-reverses.
Use `anchor="ra"` (right-ascender) and give `x` as the right edge.

## Video captions (ffmpeg / ASS / libass)

- libass must be built with fribidi and harfbuzz (`ffmpeg -filters | grep ass` working is not
  enough; render a test frame with mixed text and look).
- In ASS styles, set `Encoding` to `178` (Arabic) and use a font containing both scripts.
- Mixed lines: put U+200F (RLM) at the start of each Arabic caption line and isolate Latin
  runs with U+2068 … U+2069 (FSI … PDI) if punctuation jumps.
- Word-by-word highlighting splits a line into separate events; each fragment loses its
  neighbours' context, so isolate each Latin fragment explicitly.

## Terminal / plain text files

Most terminals don't implement bidi; Arabic in a terminal may appear reversed no matter
what. Don't try to "fix" file content by reversing strings — store logical order and
let the viewer render it.

## HTML email

Email clients (Outlook desktop especially) strip `<head>` styles and do not reliably inherit
direction. Repeat the direction everywhere:

```html
<html lang="ar" dir="rtl">
<body dir="rtl" style="direction:rtl; text-align:right; font-family:Tahoma, Arial, sans-serif;">
  <table role="presentation" dir="rtl" width="100%">
    <tr><td dir="rtl" align="right" style="direction:rtl; text-align:right;">النص</td></tr>
  </table>
```

- Put `dir="rtl"` and `align="right"` on every `<table>` and `<td>` that holds Arabic, plus
  inline `style="direction:rtl; text-align:right"`. Inline styles are the only styles every
  client keeps.
- Web fonts are ignored by Outlook and Gmail; use a system font stack that has Arabic
  (Tahoma, Arial, Segoe UI) and put the web font first only as an enhancement.
- Isolate emails, links and phone numbers with `<span dir="ltr">`, since `<bdi>` support is
  inconsistent in email clients.
- Plain-text alternative: start each Arabic line with an Arabic word (chat rules).

## Excel (.xlsx)

```python
from openpyxl.styles import Alignment, Font
ws.sheet_view.rightToLeft = True          # column A on the right, like Arabic Excel
cell.alignment = Alignment(horizontal="right", readingOrder=2)  # 2 = right-to-left
cell.font = Font(name="Arial")            # Excel fonts with Arabic: Arial, Tahoma, Calibri
```

- `rightToLeft` flips the whole sheet; set it on every sheet that is mainly Arabic.
- `readingOrder=2` sets RTL per cell; `readingOrder=0` (context) is fine for mixed data.
- Number formats are unaffected by direction. Keep headers in Arabic and data as-is.
- For Google Sheets, the equivalent is the sheet's "Right-to-left" setting.

## Mermaid diagrams

Mermaid lays out the graph left-to-right or top-to-bottom regardless of language, and its
labels have no direction setting.

- For a flow that should read right-to-left, use `flowchart RL`.
- Quote labels and keep them short: `A["تسجيل الدخول"] --> B["لوحة التحكم"]`.
- Start every label with an Arabic word; put English terms inside, not first.
- Avoid symbols at label edges (`?`, `:`, `-`, `+`), which jump; use `؟` instead of `?`.
- Render and look. If a mixed label still reorders, split it into two lines with `<br>`
  so each line is pure Arabic or pure English.

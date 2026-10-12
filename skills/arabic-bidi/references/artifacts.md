# Artifacts, HTML, SVG and charts — RTL checklist

Contents: 1. Page skeleton · 2. Isolating LTR items · 3. Dynamic text · 4. Layout (logical CSS) ·
5. Fonts · 6. Numbers and dates · 7. Icons · 8. Forms · 9. Tables · 10. SVG · 11. Canvas and
chart libraries · 12. Final visual check

## 1. Page skeleton

```html
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root { --font: "IBM Plex Sans Arabic", "Noto Sans Arabic", system-ui, sans-serif; }
    body { font-family: var(--font); line-height: 1.7; text-align: start; }
    code, pre, kbd { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; }
    pre { direction: ltr; text-align: left; unicode-bidi: isolate; }
    bdi, .ltr { unicode-bidi: isolate; }
  </style>
</head>
```

- `dir` belongs on `<html>` (or the widget's root element). Don't fake RTL with
  `text-align: right` — alignment is not direction, and the word order stays wrong.
- `lang="ar"` picks correct shaping, hyphenation and screen-reader voice.
- English page with an Arabic section: keep `dir="ltr"` on `<html>` and put
  `dir="rtl" lang="ar"` on the Arabic block.

## 2. Isolating LTR items inside Arabic text

Wrap these in `<bdi>` (or `<span dir="ltr">` when you know it is LTR):

- product or brand names that contain punctuation or digits: `<bdi>Node.js 20</bdi>`,
  `<bdi>C++</bdi>`, `<bdi>iPhone 17 Pro</bdi>`
- inline code, commands, file paths: `<code dir="ltr">npm run build</code>`
- URLs, emails, @handles, hashtags in Latin
- phone numbers with `+`, prices with currency symbols, version ranges, ratios like `16:9`
- anything ending the sentence right before Arabic punctuation

A single plain English word usually needs nothing, but isolating it is never harmful.

```html
<p>ثبّت <bdi>Node.js 20</bdi> ثم شغّل الأمر <code dir="ltr">npm install</code> داخل المجلد.</p>
<p>راسلنا على <bdi>support@example.com</bdi> أو اتصل على <bdi dir="ltr">+966 50 123 4567</bdi>.</p>
```

## 3. Dynamic and unknown-direction text

Anything whose content you don't write yourself gets `dir="auto"`, so each item picks its
direction from its own first strong letter:

```html
<li dir="auto">${item.title}</li>
<input type="text" dir="auto">
<textarea dir="auto"></textarea>
```

For multi-line user content where each line may differ, use
`unicode-bidi: plaintext;` on the element — every line then gets its own direction.

In JavaScript, when you create elements: `el.dir = 'auto'`. When you build strings that mix
an Arabic template with an unknown value, wrap the value with FSI…PDI
(`'⁨' + value + '⁩'`) if you can't use an element.

## 4. Layout: use logical properties

| Physical (avoid) | Logical (use) |
|---|---|
| `margin-left` / `margin-right` | `margin-inline-start` / `margin-inline-end` |
| `padding-left` / `padding-right` | `padding-inline-start` / `padding-inline-end` |
| `left:` / `right:` | `inset-inline-start:` / `inset-inline-end:` |
| `text-align: left` / `right` | `text-align: start` / `end` |
| `border-left` | `border-inline-start` |
| `border-top-left-radius` | `border-start-start-radius` |
| `float: left` | `float: inline-start` |

Flexbox `row` and grid columns already follow `dir`; don't add `row-reverse` to "make it
RTL" — that double-flips. Horizontal scroll containers and sliders also start from the right
in RTL; test them.

## 5. Fonts

The usual "two fonts don't match" problem: Latin falls back to a different font with a
different size and baseline. Prefer one family that covers both scripts:

| Family (Google Fonts) | Feel |
|---|---|
| IBM Plex Sans Arabic | neutral, technical, excellent Latin |
| Noto Sans Arabic (+ Noto Sans) | widest coverage, safe default |
| Readex Pro | modern, rounded, variable |
| Cairo | friendly, compact |
| Tajawal | light, geometric |
| Noto Kufi Arabic | bold headings |
| Amiri / Noto Naskh Arabic | traditional, long-form reading |

If you must pair two families, list the Latin one first only when its x-height visually
matches the Arabic one; otherwise list the Arabic family first (it contains Latin) and use the
second only for code.

Rules for Arabic text:
- `line-height` 1.6–1.9 (Arabic has tall ascenders and deep descenders).
- Arabic generally needs ~10–15% larger size than Latin for the same perceived size.
- **No `letter-spacing`** on Arabic. Chromium silently ignores it for Arabic, but canvas,
  SVG exports, PDF pipelines and some other engines insert gaps that break the joined
  letters. Reset it on Arabic headings if a design system adds it (`letter-spacing: 0`).
- **No italic** (`font-style: italic`) — use weight or color for emphasis.
- No `text-transform: uppercase` assumptions; Arabic has no case.
- `font-weight` only from weights you actually loaded, or the browser fakes a smeared bold.

## 6. Numbers and dates

- Choose a digit style and keep it consistent. Gulf and tech audiences usually expect Western
  digits (0–9); `Intl.NumberFormat('ar')` may output Arabic-Indic digits (٠–٩). Force Western
  digits with the locale `'ar-u-nu-latn'`:
  ```js
  new Intl.NumberFormat('ar-u-nu-latn', { style: 'currency', currency: 'SAR' }).format(1250)
  new Intl.DateTimeFormat('ar-u-nu-latn', { dateStyle: 'long' }).format(new Date())
  ```
- Numbers in tables and stats: `font-variant-numeric: tabular-nums;`.
- Percentages, negative numbers and ranges next to Arabic words: wrap in `<bdi>` if they look
  off (`<bdi>-12%</bdi>`).

## 7. Icons

Mirror icons that imply direction (back/next arrows, chevrons, "reply", progress, undo/redo
are debated — mirror arrows, don't mirror clocks, checkmarks, media play, logos, or charts'
time axis unless intended):

```css
[dir="rtl"] .icon-directional { transform: scaleX(-1); }
```

"Next" in RTL points left; "back" points right.

## 8. Forms

```html
<label for="name">الاسم</label>
<input id="name" type="text" dir="auto">
<input type="email" dir="ltr" placeholder="name@example.com">
<input type="url" dir="ltr">
<input type="tel" dir="ltr">
<input type="password" dir="ltr">
```

Placeholders follow the input's `dir`; a Latin placeholder in an `auto` input still aligns
right until the user types. That's acceptable.

## 9. Tables

With `dir="rtl"` on the page, the first column appears on the right — correct for Arabic
readers. Give cells that hold data from outside `dir="auto"`. Numeric columns: align with
`text-align: end` (or `start` consistently) and `tabular-nums`.

## 10. SVG

SVG text does not reliably inherit HTML direction:

```svg
<svg viewBox="0 0 400 120" xmlns="http://www.w3.org/2000/svg" direction="rtl">
  <text x="380" y="40" direction="rtl" text-anchor="start" font-family="IBM Plex Sans Arabic">
    عنوان الرسم <tspan direction="ltr" unicode-bidi="isolate">API v2</tspan>
  </text>
</svg>
```

With `direction="rtl"`, `text-anchor="start"` anchors at the **right** edge of the text,
so place `x` at the right side. Keep mixed labels short; split long mixed labels into
separate `<text>` elements if they still misbehave.

## 11. Canvas and chart libraries

Canvas ignores CSS direction:

```js
ctx.direction = 'rtl';
ctx.textAlign = 'right';
ctx.font = '16px "IBM Plex Sans Arabic"';
await document.fonts.ready; // draw only after the web font loads
```

Chart.js:
```js
options: {
  locale: 'ar-u-nu-latn',
  plugins: {
    legend:  { rtl: true, textDirection: 'rtl', labels: { font: { family: 'IBM Plex Sans Arabic' } } },
    tooltip: { rtl: true, textDirection: 'rtl' }
  },
  scales: { x: { reverse: true } } // only if the categorical axis should read right-to-left
}
```

ECharts / others: look for `rtl`, `textDirection` or `inverse` options, set the font family
explicitly, and keep time axes left-to-right unless the user asks otherwise (most Arabic
readers still read time series left-to-right).

Mermaid and similar diagram renderers handle RTL poorly; put Arabic labels in short nodes,
avoid mixed punctuation inside a label, and visually verify.

## 12. Final visual check

If you can render the page (headless browser, screenshot), look specifically at:
1. every line that mixes Arabic and Latin text,
2. punctuation at the end of mixed lines,
3. numbers, percentages and ranges next to English words,
4. directional icons, sliders, carousels,
5. Arabic headings — joined letters, no letter-spacing gaps,
6. narrow (phone) width, where wrapping changes which runs touch the line edge.

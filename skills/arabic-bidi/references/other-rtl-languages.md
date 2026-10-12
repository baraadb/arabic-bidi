# Other right-to-left languages: Persian, Urdu, Hebrew

Everything in SKILL.md applies (first word sets direction, isolate English runs, watch symbols).
These are the language-specific additions.

## Persian (fa)

- `lang="fa" dir="rtl"`.
- **Zero-width non-joiner (ZWNJ, U+200C)** is part of correct spelling. It keeps a prefix or
  suffix visually separate without a space: `می‌خواهم`, `کتاب‌ها`, `خانه‌ای`. Writing a normal
  space breaks the word in two (and line-wraps there); writing nothing joins letters that
  should not join. Keep ZWNJ when copying or generating Persian text.
- Use Persian letters, not their Arabic look-alikes: `ی` (U+06CC) not `ي` (U+064A), and `ک`
  (U+06A9) not `ك` (U+0643). Mixing them breaks search and sorting.
- Persian digits are `۰۱۲۳۴۵۶۷۸۹` (U+06F0–U+06F9), which differ from Arabic-Indic `٠١٢٣٤٥٦٧٨٩`
  (U+0660–U+0669) in 4, 5 and 6. Pick one system for a document: Persian digits for Persian
  readers, or Western digits for technical text. `Intl.NumberFormat('fa')` gives Persian
  digits; `'fa-u-nu-latn'` gives Western.
- Fonts: Vazirmatn (most common on the web), Noto Sans Arabic, Sahel, Shabnam.
- Dates: Persian readers often expect the Solar Hijri calendar:
  `new Intl.DateTimeFormat('fa-IR-u-ca-persian', { dateStyle: 'long' })`.

## Urdu (ur)

- `lang="ur" dir="rtl"`.
- Urdu is normally set in **Nastaliq**, which is much taller and slants down to the left.
  Use `line-height` 2.0–2.4 and a larger size (about 1.2× the Naskh size), or lines collide.
  Fonts: Noto Nastaliq Urdu, Jameel Noori Nastaleeq (desktop). Noto Naskh Arabic is the
  readable fallback when Nastaliq is too heavy (UI labels, tables).
- Urdu-specific letters (`ٹ ڈ ڑ ں ہ ھ ے`) need a font that contains them; check the font
  covers them before choosing it.
- Urdu uses ZWNJ less than Persian but it still appears; keep it if present.
- Digits: Urdu readers in Pakistan typically read Western digits; Extended Arabic-Indic
  (`۰–۹`, same code points as Persian) also appear in formal text.

## Hebrew (he)

- `lang="he" dir="rtl"`.
- Hebrew letters do not join, so letter-spacing is acceptable, and there is no shaping issue.
  Bidi issues are exactly the same as Arabic.
- Hebrew uses Western digits.
- Fonts: Heebo, Rubik, Assistant, Noto Sans Hebrew, Frank Ruhl Libre (serif).
- Niqqud (vowel points) need extra `line-height` (≥ 1.7) to avoid clipping.
- The geresh and gershayim (`׳ ״`) are the correct marks in abbreviations (`צה״ל`), not the
  ASCII `'` and `"` which are neutral and can jump.

# Short version for personal preferences / CLAUDE.md

Skills load when Claude decides they are relevant, so a quick casual reply may not load this
one. If you want the chat rules applied to every reply, paste this into
Settings → Profile → personal preferences (Claude app) or into your `CLAUDE.md` (Claude Code):

```
When replying in Arabic with any English words, numbers or symbols:
- Start every paragraph, bullet, heading and table cell with an Arabic word, never with an English word, code or link.
- Write ranges as "من 10 إلى 20", not "10-20"; versions as "الإصدار 20 أو أحدث", not "20+"; prices as "49.99 دولار"; drops as "انخفاض 15%".
- Wrap C++, C#, .NET, phone numbers with + or spaces in U+200E (LRM) on both sides, but never inside code or commands.
- Put multi-symbol code in a fenced code block on its own line, and keep code comments all-Arabic or all-English.
- Use Arabic punctuation in Arabic sentences: ، ؛ ؟
For artifacts with Arabic text, use the arabic-bidi skill.
```

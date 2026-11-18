# Tests — news-image-20261118

Run on 18 November 2026 (WITA) on the build machine (Python 3.12.3; the
entry targets Python 3.13 and uses only the standard library: `math`, `os`,
`struct`, `zlib`).

## Determinism

```
MAKEFUN_OUTPUT_DIR=/tmp/ni18a python3 main.py
MAKEFUN_OUTPUT_DIR=/tmp/ni18b python3 main.py
cmp /tmp/ni18a/entry.png /tmp/ni18b/entry.png  ->  BYTE-IDENTICAL
sha256: 23bdb5bb5fd8b8b73fb6b22ae7835459892679b85f73818c3e5fe44702a65baa
```

Run three times total across three code revisions (after each layout fix);
every pair of runs in the same revision was byte-identical.

## Gate checks (PNG, size, dimensions)

- Valid PNG: magic bytes `89 50 4E 47`, IHDR / IDAT / IEND chunks present,
  all chunk CRCs verified OK.
- Size: **22,110 bytes** (limit 1,048,576) — 2.1% of the cap.
- Dimensions: **1024 x 1024** (limit 1024 x 1024).
- No network calls anywhere in `main.py` (verified by reading the code:
  only `os.environ`/`os.makedirs` for the output directory).

## Visual check

The rendered image was opened and inspected at full size after each
revision. Final revision verified:

- Masthead "THE WORLD IN ONE DAY" and date "WEDNESDAY, 18 NOVEMBER 2026"
  are large, centred, and spelled correctly.
- All six headlines are visible and spelled correctly:
  "US STRIKES IRAN'S QESHM ISLAND BASE", "KERCH BRIDGE HIT FOR SECOND
  DAY", "APEC OPENS IN SHENZHEN", "DEMOCRATS FLIP ALASKA SENATE",
  "US LOSES MEASLES-FREE STATUS", "EBOLA SURGE IN DR CONGO".
- All six summaries and the "IN BRIEF" footer line fit inside their
  panels with no clipping or overflow (two layout bugs found and fixed
  during testing: a panel fill that hid the headlines, and smoke/ballot
  artwork spilling outside its illustration area).
- Every illustration stays inside its own panel: Gulf island + missile
  trails, broken Kerch Bridge, Shenzhen skyline, ballot box with check,
  spiky measles virus, Ebola filament.

## Known limitations

- Text is drawn with a built-in 5x7 bitmap font (no font files are
  available offline in the sandbox). Headlines are large and legible at
  small display sizes; the smaller summary lines are a bonus at full
  resolution.
- The entry is a drawn front page, not a photograph: it competes on
  clarity, breadth and correctness of the day's news, per the judge's
  criteria (date named, consequential stories across regions and fields,
  readable from the image alone, faithful to what was reported).

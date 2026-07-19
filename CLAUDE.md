# Blitz — SAT question feed

A static, scrollable SAT practice app in the style of Dolphin. Runs entirely on
GitHub Pages (no server, no build step). The question bank is a folder of JSON files,
grown by scraping official College Board practice-test PDFs. The app samples questions
by configurable proportions and lazy-loads each question only when its card appears.

**Read this file at the start of every session before touching the project.**

---

## Current state

- The app (`index.html`), the directory generator (`build_directory.py`), and the
  directory (`directory.json`) are complete and working.
- **Bank so far: SAT Practice Test 4, Reading & Writing Module 1 (33 questions),** in
  `questions/reading-writing/sat4-rw1-01.json` … `sat4-rw1-33.json`.
- **The main job in most sessions is scraping more questions** into the bank. The
  immediate next task is finishing Test 4: R&W Module 2, Math Module 1, Math Module 2
  (87 more questions).

---

## What the app does

- Vertical, snap-scrolling feed of SAT questions, one per screen, like a social feed.
- Each card shows: section/module/topic tags, an optional passage (R&W), an optional
  figure image (math), the question stem, tappable choices, and — after answering —
  correct/wrong highlighting plus a text explanation.
- A settings sheet controls the mix: a **section slider** (math vs reading-writing), a
  **module slider** (module 1 vs module 2), and **topic chips** (which topics are in
  the pool). Settings persist in `localStorage`. The feed is infinite.

---

## Hard constraints (why the design is the way it is)

GitHub Pages serves **static files only** — no server, no database, and **no way for
the browser to list a folder.** So:

1. The bank is plain JSON files committed to the repo, one file per question.
2. Because the browser can't discover files, a **directory file** (`directory.json`)
   lists every question's tags. The app loads it once, samples on the tags, then
   fetches each question file on demand.
3. `directory.json` is **generated** by `build_directory.py` — never hand-edited — and
   must be regenerated after any question is added, removed, or changed.

Also important: **you cannot download the College Board PDFs with curl/wget** — the
network proxy returns 503 for `satsuite.collegeboard.org`. Read the PDFs with the
`web_fetch` tool using PDF text extraction instead.

---

## Repo layout

```
repo/
├─ index.html            # the app (single file, vanilla JS) — don't rewrite unless asked
├─ directory.json        # GENERATED index: [{id, section, module, topic}, ...]
├─ build_directory.py    # scans questions/, validates, rewrites directory.json
└─ questions/
   ├─ reading-writing/
   │  ├─ sat4-rw1-01.json …            # one file per question
   │  └─ images/                       # PNGs for R&W figure questions, named <id>.png
   └─ math/
      ├─ (math question files go here)
      └─ images/                       # PNGs for math figure questions, named <id>.png
```

- Section folders are exactly `reading-writing/` and `math/`.
- Each has an `images/` subfolder for figure PNGs. `build_directory.py` ignores
  non-`.json` files, so images don't affect the directory.
- The app builds a question's path as `questions/<section>/<id>.json`.

---

## How to add a question (write the file directly — there is no script for this)

Create a JSON file at `questions/<section>/<id>.json`. One question per file. Write it
directly; do not build or run any generator. Follow this exact shape:

```json
{
  "id": "sat4-rw1-05",
  "section": "reading-writing",
  "module": 1,
  "topic": "Text structure and purpose",
  "source": "sat4",
  "passage": "The following text is adapted from Susan Glaspell's 1912 short story ...",
  "stem": "It did seem that the picture failed to fit in ...\n\nWhich choice best states the main purpose of the text?",
  "choices": [
    "To reveal the shop owner's conflicted feelings about the new picture",
    "To convey the shop owner's resentment of the person he got the new picture from",
    "To describe the items that the shop owner most highly prizes",
    "To explain differences between the new picture and other pictures in the shop"
  ],
  "answer": "To reveal the shop owner's conflicted feelings about the new picture",
  "explanation": "The text first shows the owner fuming that the picture doesn't belong, then reveals he is 'secretly proud' of it — so the purpose is to reveal his conflicted feelings. Nothing shows resentment of the seller, ranks his prized items, or explains how the pictures differ."
}
```

### Field rules
- **`id`** — must equal the filename (without `.json`). Scheme: `<source>-<sec><module>-<qq>`
  where `sec` is `rw` or `m`, `module` is `1` or `2`, `qq` is the two-digit question
  number. Examples: `sat4-rw2-07`, `sat4-m1-15`.
- **`section`** — `"reading-writing"` or `"math"`, matching the folder it's in.
- **`module`** — the number `1` or `2`.
- **`topic`** — one label from the topic list below.
- **`source`** — the test slug, e.g. `"sat4"`.
- **`passage`** — *optional.* Include for any R&W question that has a passage, a poem,
  or a notes list, including the intro line ("The following text is adapted from…").
  Put the passage/context here and the question line in `stem`.
- **`stem`** — the question itself. For R&W, the item text plus the "Which choice…"
  line, joined by a blank line (`\n\n`). Copy **verbatim** from the questions PDF.
- **`choices`** — the four options as strings, **in order A, B, C, D**, with no "A)"
  prefix (the app adds the letters). Copy verbatim.
- **`answer`** — the **exact text** of the correct choice. Get the correct *letter*
  from the answer-explanations PDF, then copy that choice's text here verbatim. It must
  match one entry in `choices` character-for-character.
- **`explanation`** — 2–4 sentences, **in your own words.** Do NOT copy the College
  Board explanation verbatim — read it, then reword why the answer is right (and
  ideally why the others are wrong).
- **`image`** — *optional.* For any question that depends on a figure, graph,
  table-as-image, or geometry diagram. Set it to `"<id>.png"`. When the figure is
  tabular data, ALSO transcribe that data into `passage` in brackets so the question
  is answerable from text even before the PNG exists (e.g.
  `"[Table: iron SPC 20%, AST 28%, HTC 90%, OCC 98%; …]"`).

---

## Topic labels (use these exactly)

**Reading & Writing:** Words in context · Text structure and purpose · Cross-text
connections · Central ideas and details · Command of evidence (textual) · Command of
evidence (quantitative) · Inferences · Form, structure, and sense · Transitions ·
Rhetorical synthesis

**Math:** Linear equations · Linear functions · Systems of equations · Ratios, rates,
proportions · Percentages · Nonlinear functions / quadratics · Exponential functions ·
Geometry · Trigonometry · Statistics and probability · Data analysis

The answer-explanations PDF usually names the skill — use it as a hint. If a question
doesn't fit cleanly, pick the closest and stay consistent.

---

## Figures (graphs, tables-as-images, diagrams)

PDF text extraction gives you the text but NOT the embedded images, so figure PNGs
can't be pulled automatically — Hansen adds them by hand (screenshot from the PDF into
`questions/<section>/images/<id>.png`). When you scrape a figure question:

1. Set `"image": "<id>.png"` on the question.
2. If it's a table or simple data, also transcribe the data into `passage` so the
   question works from text alone.
3. `build_directory.py` prints a list of referenced-but-missing images at the end of
   each run — that's the screenshot to-do list.

The app hides a missing image gracefully, so a question with an `image` field but no
PNG still works as long as its data is in the passage.

---

## How to scrape a test (the core workflow)

**Source: official College Board linear digital SAT practice tests (Tests 4–11).**
Each test is three PDFs at `https://satsuite.collegeboard.org`:

| Test | Questions PDF | Answer explanations PDF |
|---|---|---|
| 4 | `/media/pdf/sat-practice-test-4-digital.pdf` | `/media/pdf/sat-practice-test-4-answers-digital.pdf` |
| 5 | `/media/pdf/sat-practice-test-5-digital.pdf` | `/media/pdf/sat-practice-test-5-answers-digital.pdf` |
| 6 | `/media/pdf/sat-practice-test-6-digital.pdf` | `/media/pdf/sat-practice-test-6-answers-digital.pdf` |
| 7 | `/media/pdf/sat-practice-test-7-digital.pdf` | `/media/pdf/sat-practice-test-7-answers-digital.pdf` |
| 8 | `/media/pdf/sat-practice-test-8-digital.pdf` | `/media/pdf/sat-practice-test-8-answers-digital.pdf` |
| 9 | `/media/pdf/sat-practice-test-9-digital.pdf` | `/media/pdf/sat-practice-test-9-answers-digital.pdf` |
| 10 | `/media/pdf/sat-practice-test-10-digital.pdf` | `/media/pdf/sat-practice-test-10-answers-digital.pdf` |
| 11 | `/media/pdf/sat-practice-test-11-digital.pdf` | `/media/pdf/sat-practice-test-11-answers-digital.pdf` |

Each test has four modules: R&W Module 1, R&W Module 2, Math Module 1, Math Module 2.

**Steps:**
1. **Read both PDFs as text** via `web_fetch` with PDF text extraction (curl/wget fail
   — proxy 503). The PDFs are large; fetch in chunks with a token limit (~28–30k) and
   page through. The questions PDF gives stems, passages, and choices; the answers PDF
   gives the correct letter and the official explanation.
2. **Match by question number within each module** — question N in the questions PDF
   lines up with "QUESTION N" in that module's section of the answers PDF.
3. **Write one JSON file per question** following the schema and field rules above.
   Copy stems/passages/choices verbatim; take the correct letter from the answers PDF
   and set `answer` to that choice's exact text; **reword** the explanation; flag
   figures with `image` and transcribe tabular data into `passage`.
4. **Run `python build_directory.py`.** It validates everything (answer matches a
   choice, id matches filename, section matches folder, no duplicates) and refuses to
   write if anything is malformed, so a broken scrape can't ship. Fix any errors it
   prints, then rerun.
5. **Note the missing-image list** it prints so Hansen knows what to screenshot.
6. Commit and push.

---

## Example prompts to give this project

- *"Read PROJECT.md, then finish scraping Test 4: R&W Module 2, Math Module 1, and Math
  Module 2. Write the JSON files following the schema, regenerate the directory, and
  list any figures I need to screenshot."*
- *"Read PROJECT.md, then scrape Test 5 (all four modules) into the bank."*
- *"Read PROJECT.md. Regenerate directory.json and tell me which figure images are
  still missing."*

---

## The sampler (how the mix is honored) — reference only, don't change unless asked

Nested, so the three axes never contradict:
1. Pick a **section** by the section slider (only among sections that have active-topic
   questions).
2. Pick a **module** by the module slider (only among modules with active-topic
   questions in that section; forced if only one qualifies).
3. Pick a **question** at random among matching section + module + an on-topic.

Sampling runs on `directory.json` (tags only), so it's fast at any bank size. Only
after a question is picked does the app fetch that one file (cached, with dedupe).

---

## Build conventions

- Single-file `index.html`, vanilla JS, no framework, no build tools.
- Fonts: Space Grotesk (display/body) + JetBrains Mono (data/labels).
- Dark terminal aesthetic. Section accents: math = teal (#4fd1c5), R&W = amber (#f6a04d).
- Deploy: push to the repo, enable GitHub Pages on the branch.
- App name **Blitz** — set in the `.brand` element, the `<title>`, and the
  `blitz.settings.v1` localStorage key.

---

## Merging

- **When your changes are complete and pushed, merge the pull request into the
  default branch automatically — don't wait to be asked.** Only hold off if the
  user explicitly says not to merge, or if the work is clearly still in progress
  (unresolved review feedback, failing checks, or an open question).

---

## Session checklist

1. Read this file.
2. Scraping? Read both PDFs via `web_fetch`, match by question number, write one JSON
   file per question per the schema, **reword explanations**, flag figures.
3. Run `python build_directory.py`; fix any validation errors, rerun until clean.
4. Never hand-edit `directory.json`.
5. Keep `answer` matched verbatim to a `choices` entry.

---

## Possible next features (not built)

- **Video explanations** (Dolphin's signature): add an optional `video` URL field to a
  question and render it in the explain area — no directory change needed.
- **Progress across reloads**: the seen/accuracy counter now persists in
  `localStorage` (`blitz.progress.v1`), and settings has a "Delete all app data"
  button that clears it. Could still add per-question history, or Supabase for
  cross-device sync.
- **Directory splitting**: only if `directory.json` ever gets too big (fine into the
  tens of thousands of entries).

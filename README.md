# reflection-analyser

**Reflective-writing analysis** — the [lens-family](https://github.com/michael-borck/lens-analysers)
member that reads a learning journal / reflection / portfolio entry as **reflection**, not just
as prose.

> `document-analyser` reads readability; this reads *reflective depth*. Different signals from
> the same words. **Explicit-only** (`auto_routable: false`) — same pattern as
> `conversation-analyser`: text and prose extensions auto-route to `document-analyser`; invoke
> `reflection-analyser` deliberately when you want the reflective-depth interpretation.

Built around the markers commonly used in reflective-writing rubrics
([Moon's depth scale](https://www.tandfonline.com/doi/abs/10.1080/0307507990240207),
Gibbs' reflective cycle, the SOLO taxonomy): metacognition, criticality, evidence linkage,
affect language, and forward-looking action.

## Install

```bash
pip install reflection-analyser
```

Optional: read `.pdf` / `.docx` / `.pptx` journals (otherwise plain-text / `.md` only):

```bash
pip install 'reflection-analyser[documents]'
```

## Use

**Python:**

```python
from reflection_analyser import ReflectionAnalyser

# From text directly
result = ReflectionAnalyser().analyse_text("Looking back, I realised that…")

# From a file (composes on document-analyser for binary docs when [documents] is installed)
result = ReflectionAnalyser().analyse("journal.md")
result = ReflectionAnalyser().analyse("journal.docx")  # requires [documents]

print(result.depth_band)               # "dialogic"
print(result.composite_depth_score)    # 0.62
print(result.metacognition.count)      # 7
print(result.criticality.count)        # 3
```

**CLI:**

```bash
reflection-analyser journal.md
reflection-analyser journal.txt --json
reflection-analyser journal.docx                 # needs [documents] extra
echo "Looking back…" | reflection-analyser -
reflection-analyser serve
reflection-analyser manifest
```

**HTTP** (`reflection-analyser serve` on port 8015):

```bash
curl -F file=@journal.md http://localhost:8015/analyse
```

## Signals

For a piece of reflective writing:

- **Metacognition** — first-person + cognitive verbs (`I realised`, `I noticed`, `looking back`,
  `on reflection`). Surface depth indicator.
- **Criticality** — contrast/qualification phrases (`however`, `in contrast`, `that said`,
  `on the other hand`). Marker of dialogic vs descriptive reflection.
- **Evidence** — references to specific moments, sources, dates, quotes — proper-noun and
  citation density. Concrete vs abstract.
- **Affect** — emotion words (`frustrated`, `surprised`, `confident`, `uncertain`). Too few =
  clinical; presence indicates engagement.
- **Action / forward-looking** — `next time`, `going forward`, `I will`, future-tense intent.
  Marker of transformative reflection.

**Composite depth score** (0–1) combines per-marker coverages; mapped to a Moon-style band:

| Band | Score | Description |
|---|---|---|
| descriptive | 0.0–0.25 | "What happened" only — events recounted, little interpretation |
| dialogic | 0.25–0.5 | Some self-questioning + critical thought |
| critical | 0.5–0.75 | Multiple perspectives, evidence linkage, qualification |
| transformative | 0.75–1.0 | Forward-looking insight, evidence-linked, change-oriented |

The score is a **signal, not a grade** — it's meant to inform human judgement, not replace it.

## The family

| What you want | Use |
|---|---|
| Document text + readability | **document-analyser** |
| Reflective depth on that text | **reflection-analyser** (this) |
| Human-AI conversation analysis | **conversation-analyser** |
| Any file → right engine | **auto-analyser** |

## Limits

- Lexicon-based v1 — fast, transparent, but catches phrasing not meaning. A reflective sentence
  without our trigger words underscores; a non-reflective sentence with `I realised` overscores.
- English-only for v1.
- Calibrated against generic reflective-writing rubrics; tune the band thresholds in
  `_BAND_THRESHOLDS` for your unit's specific rubric if needed.
- Vision/LLM-augmented depth scoring is a possible follow-on; not in v1.

## License

MIT

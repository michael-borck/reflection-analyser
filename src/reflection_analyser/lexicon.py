"""Marker lexicons + matcher.

Conservative phrase-level lexicons covering the five marker families. Each
entry is a regex (compiled lazily on first use) so word-boundary handling
stays consistent. Keep entries phrase-level: matching `realised` as a bare
word over-fires (`he realised it was wrong` is a narrative phrase, not
reflection); `I realised` is the reflective form.

Adjust the lexicons — not the analyser logic — to tune the signal.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Patterns are case-insensitive at compile time. The lexicons below are
# *fragments*; we wrap them in word boundaries when compiling.


_METACOGNITION_PHRASES = [
    r"I (?:realised|realized|came to (?:see|realise|realize|understand)|recognised|recognized)",
    r"(?:looking|reflecting) back",
    r"on reflection",
    r"I (?:noticed|noted)",
    r"I (?:learnt|learned) (?:that|how)",
    r"I (?:think|thought|believe|believed)",
    r"in hindsight",
    r"I came to (?:think|believe)",
    r"I (?:understand|understood) (?:now|that)",
]


_CRITICALITY_PHRASES = [
    r"however",
    r"on the other hand",
    r"in contrast",
    r"that said",
    r"although",
    r"despite",
    r"nevertheless",
    r"nonetheless",
    r"alternatively",
    r"by contrast",
    r"this (?:contradicts|conflicts with|challenges)",
    r"one (?:view|perspective) is .{0,80}? another",
]


# Evidence: explicit reference to a specific source / quote / date / number.
# Note: we deliberately don't include bare 4-digit years — "I started uni in 2018"
# is a temporal reference, not evidence. The APA pattern below catches the
# evidence-shaped use ("(Smith, 2020)").
_EVIDENCE_PHRASES = [
    r"according to \w+",
    r"as (\w+\s){0,3}(?:argues|argued|writes|wrote|notes|notes that|points out)",
    r"\([A-Z]\w+,? \d{4}\)",                # in-text APA
    r"\[[0-9]+\]",                          # numeric citation
    r"\"[^\"]{8,}\"",                       # a quoted span ≥ 8 chars
    r"\bp\.\s?\d+\b",                       # page reference
]


# Affect: feelings + first-person. Wrapped with "I (was|felt) X" to avoid
# scoring narratives like "the customer was frustrated".
_AFFECT_PHRASES = [
    r"I (?:was|felt|feel|am|have been) (?:frustrated|surprised|confused|uncertain|confident|nervous|anxious|excited|proud|disappointed|overwhelmed|relieved|grateful)",
    r"I (?:struggled|enjoyed|hated|loved|disliked|appreciated)",
    r"(?:it|this) was (?:frustrating|surprising|exciting|disappointing|overwhelming|rewarding)",
    r"a sense of (?:relief|achievement|frustration|confusion|pride)",
]


# Forward-looking action / intent.
_FORWARD_PHRASES = [
    r"next time",
    r"going forward",
    r"in (?:the )?future",
    r"I will",
    r"I plan to",
    r"I intend to",
    r"I (?:hope|want) to",
    r"my next step",
    r"from now on",
]


@dataclass
class CompiledLexicon:
    name: str
    patterns: list[re.Pattern]

    def find_hits(self, text: str, sentences: list[str], *, sample_cap: int = 5) -> tuple[int, list[str]]:
        """Count hits across the text; return (count, sample sentences with hits)."""
        count = 0
        sample: list[str] = []
        sample_seen: set[str] = set()
        for p in self.patterns:
            for m in p.finditer(text):
                count += 1
                # Find the sentence containing this hit (linear scan; sentences are typically <300).
                pos = m.start()
                acc = 0
                hit_sentence = ""
                for s in sentences:
                    acc += len(s)
                    if acc >= pos:
                        hit_sentence = s.strip()
                        break
                if hit_sentence and hit_sentence not in sample_seen and len(sample) < sample_cap:
                    sample.append(hit_sentence)
                    sample_seen.add(hit_sentence)
        return count, sample


def _compile(name: str, phrases: list[str]) -> CompiledLexicon:
    """Compile each phrase, wrapping with word boundaries *only* where the phrase
    starts/ends with a word character. Patterns that already use punctuation
    anchors (`(Author, 2020)`, `"quoted span"`, `[42]`) need no boundary —
    `\\b` next to non-word chars over-restricts (fails the inner-quote case).
    """
    compiled: list[re.Pattern] = []
    for phrase in phrases:
        prefix = r"\b" if _first_real_char_is_word(phrase) else ""
        suffix = r"\b" if _last_real_char_is_word(phrase) else ""
        compiled.append(re.compile(prefix + phrase + suffix, re.IGNORECASE))
    return CompiledLexicon(name=name, patterns=compiled)


_WORD_RE = re.compile(r"\w")


def _first_real_char_is_word(phrase: str) -> bool:
    """Skip leading regex meta-chars to find the first 'real' character."""
    skip = set(r"(?:\\")
    for c in phrase:
        if c in skip:
            continue
        return bool(_WORD_RE.match(c))
    return False


def _last_real_char_is_word(phrase: str) -> bool:
    skip = set(r")?:")
    for c in reversed(phrase):
        if c in skip:
            continue
        return bool(_WORD_RE.match(c))
    return False


# Lazily-built singletons — compile on first use.
_LEXICONS: dict[str, CompiledLexicon] | None = None


def lexicons() -> dict[str, CompiledLexicon]:
    global _LEXICONS
    if _LEXICONS is None:
        _LEXICONS = {
            "metacognition": _compile("metacognition", _METACOGNITION_PHRASES),
            "criticality":   _compile("criticality",   _CRITICALITY_PHRASES),
            "evidence":      _compile("evidence",      _EVIDENCE_PHRASES),
            "affect":        _compile("affect",        _AFFECT_PHRASES),
            "forward":       _compile("forward",       _FORWARD_PHRASES),
        }
    return _LEXICONS

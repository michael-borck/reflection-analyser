"""Unit tests for the marker lexicons."""
from reflection_analyser.lexicon import lexicons


def _hits(name: str, text: str) -> int:
    """Pure count for the named marker family in `text`."""
    sentences = [s for s in text.split(". ") if s]
    count, _ = lexicons()[name].find_hits(text, sentences)
    return count


class TestMetacognition:
    def test_first_person_realised(self):
        assert _hits("metacognition", "I realised that I had been wrong.") == 1

    def test_looking_back(self):
        assert _hits("metacognition", "Looking back, the choice was clear.") == 1

    def test_he_realised_does_not_fire(self):
        # "he realised" is narrative, not reflection — must NOT match.
        assert _hits("metacognition", "He realised it was Tuesday.") == 0

    def test_phrases_with_us_and_uk_spelling(self):
        # Lexicon includes both `realised` and `realized`.
        assert _hits("metacognition", "I realized something new.") == 1


class TestCriticality:
    def test_however(self):
        assert _hits("criticality", "It was hard. However, I learned a lot.") == 1

    def test_on_the_other_hand(self):
        assert _hits("criticality", "On the other hand, the data was clear.") == 1

    def test_no_false_positive(self):
        assert _hits("criticality", "Today I went to class.") == 0


class TestEvidence:
    def test_apa_in_text(self):
        assert _hits("evidence", "As noted (Smith, 2020), the trend is clear.") == 1

    def test_quoted_span(self):
        assert _hits("evidence", 'The author wrote "this is a quotation".') == 1

    def test_page_reference(self):
        assert _hits("evidence", "See p. 42 for details.") == 1


class TestAffect:
    def test_i_felt_frustrated(self):
        assert _hits("affect", "I felt frustrated by the result.") == 1

    def test_third_person_frustrated_does_not_fire(self):
        # "the customer was frustrated" should NOT count.
        assert _hits("affect", "The customer was frustrated.") == 0


class TestForward:
    def test_next_time(self):
        assert _hits("forward", "Next time I will plan more carefully.") >= 1  # 'next time' + 'I will'

    def test_going_forward(self):
        assert _hits("forward", "Going forward, I'll keep notes.") == 1

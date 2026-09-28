"""Unit tests for citation extraction and verification."""

from groundedrag.guardrails import build_answer, extract_citations, is_fully_cited


def test_extracts_valid_citations_in_range():
    citations = extract_citations(
        "Reset the password [1] and notify IT [2].", ["chunk-a", "chunk-b"]
    )
    assert [c.index for c in citations] == [1, 2]
    assert all(c.valid for c in citations)
    assert citations[0].chunk_id == "chunk-a"


def test_flags_citation_out_of_range():
    citations = extract_citations("See procedure [3].", ["chunk-a"])
    assert citations[0].valid is False
    assert citations[0].chunk_id is None


def test_no_citations_is_not_fully_cited():
    assert is_fully_cited("This is not documented.", []) is False


def test_fully_cited_requires_every_citation_valid():
    citations = extract_citations("A [1] and B [2].", ["chunk-a"])
    assert is_fully_cited("A [1] and B [2].", citations) is False


def test_build_answer_fully_cited():
    answer = build_answer("Reset the password [1].", ["chunk-a"])
    assert answer.text == "Reset the password [1]."
    assert answer.fully_cited is True
    assert answer.citations[0].chunk_id == "chunk-a"


def test_build_answer_flags_uncited_claims():
    answer = build_answer("This is a claim with no citation.", ["chunk-a"])
    assert answer.fully_cited is False
    assert answer.citations == []

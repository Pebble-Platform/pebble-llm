"""Change 017 — the orthography half of the tone checker (no model, no data).

Tone splitting / placement / allowed-tone sets decide WHICH spellings the CTC model is
asked to compare; a bug here silently turns the checker into a spelling checker.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts" / "vietnamese-ser"))

import tone_check as tc


@pytest.mark.parametrize(
    ("syl", "base", "tone"),
    [
        ("ma", "ma", "ngang"),
        ("mà", "ma", "huyen"),
        ("má", "ma", "sac"),
        ("mả", "ma", "hoi"),
        ("mã", "ma", "nga"),
        ("mạ", "ma", "nang"),
        ("người", "ngươi", "huyen"),  # tone on ơ, horn kept on both u and o
        ("Việt", "viêt", "nang"),  # lower-cased, circumflex kept
        ("hoà", "hoa", "huyen"),  # new-style spelling parses the same
        ("hòa", "hoa", "huyen"),
    ],
)
def test_split_tone(syl, base, tone):
    assert tc.split_tone(syl) == (base, tone)


@pytest.mark.parametrize(
    ("base", "tone", "spelled"),
    [
        ("ma", "sac", "má"),
        ("ngươi", "huyen", "người"),  # ươ → mark on ơ
        ("viêt", "nang", "việt"),  # diacritic vowel wins
        ("hoa", "huyen", "hòa"),  # open 2-vowel cluster → first vowel (old style)
        ("thuy", "hoi", "thủy"),
        ("hoan", "sac", "hoán"),  # coda present → last vowel of the cluster
        ("ngoai", "huyen", "ngoài"),  # 3-vowel cluster → middle
        ("qua", "nga", "quã"),  # qu is the onset, a is the nucleus
        ("gia", "huyen", "già"),  # gi + vowel: gi is the onset
        ("gin", "huyen", "gìn"),  # gi + consonant: i is the nucleus
        ("giư", "nga", "giữ"),
        ("ma", "ngang", "ma"),
    ],
)
def test_place_tone(base, tone, spelled):
    assert tc.place_tone(base, tone) == spelled


@pytest.mark.parametrize("syl", ["người", "việt", "hòa", "khuya", "giữ", "quả", "đẹp", "chạch"])
def test_roundtrip(syl):
    base, tone = tc.split_tone(syl)
    assert tc.place_tone(base, tone) == syl


@pytest.mark.parametrize(
    ("base", "allowed"),
    [
        ("hoc", ("sac", "nang")),  # học / hóc
        ("đep", ("sac", "nang")),
        ("thach", ("sac", "nang")),
        ("muôt", ("sac", "nang")),
        ("ma", tc.TONES),
        ("anh", tc.TONES),  # -nh is a sonorant coda, not checked
        ("ngươi", tc.TONES),
    ],
)
def test_allowed_tones(base, allowed):
    assert tc.allowed_tones(base) == allowed


def test_normalize_text():
    assert tc.normalize_text("  Định đi trốn à? Trốn mãi…  ") == "định đi trốn à trốn mãi"


def test_normalize_text_keeps_digits_for_exclusion():
    # digits are spoken as words the script doesn't spell → caller must exclude the clip
    assert tc.normalize_text("5 lần") == "5 lần"


def test_syllable_without_vowel_is_not_placeable():
    assert tc.split_tone("hm") == ("hm", "ngang")
    assert tc.place_tone("hm", "sac") is None

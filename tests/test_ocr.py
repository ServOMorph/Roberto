from __future__ import annotations

import numpy as np
import pytest

from _compat import extract_percent, preprocess_zone


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("7%", 7),
        ("50 %", 50),
        ("  100%  ", 100),
        ("0%", 0),
        ("contexte 42% restant", 42),
        ("", None),
        ("aucun chiffre", None),
        ("101%", None),
        ("999%", None),
        ("42", None),
    ],
)
def test_extract_percent(text, expected):
    assert extract_percent(text) == expected


def test_extract_percent_takes_first_match():
    assert extract_percent("12% puis 34%") == 12


def test_preprocess_zone_scales_and_binarises():
    frame = np.zeros((10, 20, 3), dtype=np.uint8)
    frame[3:7, 5:15] = 255

    image = preprocess_zone(frame, invert=False)

    assert image.size == (80, 40)
    values = set(np.array(image).flatten().tolist())
    assert values <= {0, 255}


def test_preprocess_zone_invert_flips_result():
    frame = np.zeros((10, 20, 3), dtype=np.uint8)
    frame[3:7, 5:15] = 255

    straight = np.array(preprocess_zone(frame, invert=False))
    inverted = np.array(preprocess_zone(frame, invert=True))

    assert np.array_equal(straight, 255 - inverted)

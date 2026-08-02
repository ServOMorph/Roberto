from __future__ import annotations

from _compat import clamp_box


def test_clamp_box_keeps_box_inside_virtual_desktop(fake_virtual_desktop):
    fake_virtual_desktop(0, 0, 1920, 1080)

    assert clamp_box(100, 200, 300, 400) == {"left": 100, "top": 200, "width": 300, "height": 400}


def test_clamp_box_pushes_back_negative_origin(fake_virtual_desktop):
    fake_virtual_desktop(0, 0, 1920, 1080)

    assert clamp_box(-500, -500, 300, 400) == {"left": 0, "top": 0, "width": 300, "height": 400}


def test_clamp_box_pushes_back_overflow(fake_virtual_desktop):
    fake_virtual_desktop(0, 0, 1920, 1080)

    assert clamp_box(1900, 1000, 300, 400) == {"left": 1620, "top": 680, "width": 300, "height": 400}


def test_clamp_box_shrinks_box_larger_than_desktop(fake_virtual_desktop):
    fake_virtual_desktop(0, 0, 800, 600)

    assert clamp_box(0, 0, 5000, 5000) == {"left": 0, "top": 0, "width": 800, "height": 600}


def test_clamp_box_supports_negative_desktop_origin(fake_virtual_desktop):
    fake_virtual_desktop(-1920, -200, 3840, 1280)

    assert clamp_box(-3000, -1000, 200, 200) == {"left": -1920, "top": -200, "width": 200, "height": 200}

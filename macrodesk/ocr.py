"""Lecture OCR des zones de surveillance déclarées dans l'UI."""

from __future__ import annotations

import re
from typing import Any

import cv2
import numpy as np
import pytesseract
from PIL import Image

from .screen import grab_bgr

OCR_PSM_MODES = ("--psm 7", "--psm 8", "--psm 6")
OCR_WHITELIST = "-c tessedit_char_whitelist=0123456789%"


def extract_percent(text: str) -> int | None:
    match = re.search(r"(\d{1,3})\s*%", text)
    if not match:
        return None
    value = int(match.group(1))
    return value if 0 <= value <= 100 else None


def preprocess_zone(frame: np.ndarray, invert: bool) -> Image.Image:
    """Agrandit et binarise une petite zone d'écran pour fiabiliser l'OCR sur du texte minuscule."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    scaled = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    mode = cv2.THRESH_BINARY_INV if invert else cv2.THRESH_BINARY
    _, binary = cv2.threshold(scaled, 0, 255, mode + cv2.THRESH_OTSU)
    return Image.fromarray(binary)


def read_zone_text(zone: dict[str, Any]) -> str:
    """Essaie plusieurs prétraitements/modes Tesseract, retient le premier lisible comme un %."""
    box = {"left": zone["left"], "top": zone["top"], "width": zone["width"], "height": zone["height"]}
    frame = grab_bgr(box)
    fallback = ""
    for invert in (True, False):
        image = preprocess_zone(frame, invert)
        for psm in OCR_PSM_MODES:
            text = pytesseract.image_to_string(image, config=f"{psm} {OCR_WHITELIST}")
            if not fallback:
                fallback = text
            if extract_percent(text) is not None:
                return text
    return fallback

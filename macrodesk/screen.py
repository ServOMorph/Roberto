"""Capture d'écran et tracé de zones sur le bureau virtuel Windows."""

from __future__ import annotations

import ctypes

import cv2
import mss
import numpy as np


def enable_dpi_awareness() -> None:
    """Use physical pixels consistently for global hooks and screen captures."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass


def virtual_desktop() -> dict[str, int]:
    with mss.mss() as capture:
        return capture.monitors[0]


def leftmost_screen() -> dict[str, int]:
    """MSS reports physical Windows coordinates, including negative coordinates
    for monitors located left of the primary display."""
    with mss.mss() as capture:
        return min(capture.monitors[1:], key=lambda screen: screen["left"])


def clamp_box(left: int, top: int, width: int, height: int) -> dict[str, int]:
    """Keep a capture rectangle inside the Windows virtual desktop."""
    with mss.mss() as capture:
        virtual = capture.monitors[0]
    final_width = min(width, virtual["width"])
    final_height = min(height, virtual["height"])
    final_left = max(virtual["left"], min(left, virtual["left"] + virtual["width"] - final_width))
    final_top = max(virtual["top"], min(top, virtual["top"] + virtual["height"] - final_height))
    return {"left": int(final_left), "top": int(final_top), "width": int(final_width), "height": int(final_height)}


def grab_bgr(box: dict[str, int]) -> np.ndarray:
    with mss.mss() as capture:
        frame = np.array(capture.grab(box))
    return cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


def select_zone_rectangle() -> dict[str, int] | None:
    """Overlay plein écran pour tracer un rectangle à la souris. Bloquant, à lancer hors du thread UI."""
    import tkinter as tk

    virtual = virtual_desktop()

    result: dict[str, int] | None = None
    start: dict[str, int] = {}
    rect_id: int | None = None

    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-alpha", 0.25)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    # -fullscreen ne couvre que l'écran principal ; on positionne explicitement
    # la fenêtre sur tout le bureau virtuel (les 3 écrans) via l'API Windows,
    # car la géométrie Tk ne gère pas les coordonnées négatives multi-écrans.
    root.geometry(f"{virtual['width']}x{virtual['height']}+0+0")
    root.update_idletasks()
    # winfo_id() renvoie la fenêtre enfant Tk ; déplacer celle-ci laisse le
    # toplevel réel à +0+0, qui clippe alors tout ce qui est à gauche de x=0
    # (écrans aux coordonnées négatives). Il faut déplacer le toplevel.
    handle = root.winfo_id()
    toplevel = ctypes.windll.user32.GetParent(handle) or handle
    ctypes.windll.user32.MoveWindow(
        toplevel, virtual["left"], virtual["top"], virtual["width"], virtual["height"], True
    )
    canvas = tk.Canvas(root, cursor="cross", bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    def on_press(event: "tk.Event") -> None:
        nonlocal rect_id
        start["x"], start["y"] = event.x_root, event.y_root
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="#4ade80", width=2)

    def on_drag(event: "tk.Event") -> None:
        if rect_id is not None:
            x0 = start["x"] - root.winfo_rootx()
            y0 = start["y"] - root.winfo_rooty()
            canvas.coords(rect_id, x0, y0, event.x, event.y)

    def on_release(event: "tk.Event") -> None:
        nonlocal result
        end_x, end_y = event.x_root, event.y_root
        left, top = min(start["x"], end_x), min(start["y"], end_y)
        width, height = abs(end_x - start["x"]), abs(end_y - start["y"])
        if width > 4 and height > 4:
            result = {"left": int(left), "top": int(top), "width": int(width), "height": int(height)}
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", lambda _event: root.destroy())
    root.mainloop()
    return result

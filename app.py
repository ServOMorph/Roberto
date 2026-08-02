from __future__ import annotations

import json
import re
import threading
import time
import uuid
import ctypes
from datetime import datetime
from pathlib import Path
from typing import Any

import cv2
import mss
import numpy as np
import pytesseract
import webview
from PIL import Image
from pynput import keyboard, mouse


APP_DIR = Path(__file__).resolve().parent
MACROS_DIR = APP_DIR / "data" / "macros"
ZONES_FILE = APP_DIR / "data" / "zones.json"
CONTROL_FLAG_FILE = APP_DIR / "data" / "control.flag"
CONTROL_SESSION_FLAG_FILE = APP_DIR / "data" / "control_session.flag"
CONTEXT_WIDTH = 320
CONTEXT_HEIGHT = 220
SEARCH_WIDTH = 1100
SEARCH_HEIGHT = 820
MATCH_THRESHOLD = 0.55


def enable_dpi_awareness() -> None:
    """Use physical pixels consistently for global hooks and screen captures."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass


def mark_control_active() -> None:
    """Signal that the machine's mouse/keyboard is under automated control.

    Written as a plain flag file (not in-memory state) so that external
    processes replaying a macro (workflow_test.py, conversation_test.py)
    can raise it even though they run outside the UI's process.
    """
    CONTROL_FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_FLAG_FILE.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")


def clear_control_active() -> None:
    try:
        CONTROL_FLAG_FILE.unlink()
    except FileNotFoundError:
        pass


def mark_session_active() -> None:
    """Signal that an orchestrated OpenCode session is running (workflow_test.py,
    conversation_test.py), from launch to end — not only during the mouse/keyboard
    replay itself, but also while waiting on OpenCode's response.
    """
    CONTROL_SESSION_FLAG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONTROL_SESSION_FLAG_FILE.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")


def clear_session_active() -> None:
    try:
        CONTROL_SESSION_FLAG_FILE.unlink()
    except FileNotFoundError:
        pass


def is_control_active() -> bool:
    return CONTROL_FLAG_FILE.exists() or CONTROL_SESSION_FLAG_FILE.exists()


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


def safe_name(name: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9 _-]", "", name).strip()
    return cleaned[:60] or datetime.now().strftime("Macro %Y-%m-%d %H-%M")


def key_name(key: keyboard.Key | keyboard.KeyCode) -> str:
    if isinstance(key, keyboard.KeyCode):
        value = key.char
        # Windows reports Ctrl+V as the control character \x16. Store the
        # physical key instead so replaying it while Ctrl is held pastes.
        if value and 1 <= ord(value) <= 26:
            value = chr(ord(value) + 96)
        return value or f"vk:{key.vk}"
    return key.name or str(key)


def restore_key(value: str) -> keyboard.Key | keyboard.KeyCode | None:
    if len(value) == 1:
        if 1 <= ord(value) <= 26:
            value = chr(ord(value) + 96)
        return keyboard.KeyCode.from_char(value)
    if value.startswith("vk:"):
        try:
            return keyboard.KeyCode.from_vk(int(value[3:]))
        except ValueError:
            return None
    return getattr(keyboard.Key, value, None)


class MacroStore:
    def __init__(self) -> None:
        MACROS_DIR.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for metadata_path in MACROS_DIR.glob("*/macro.json"):
            try:
                macro = json.loads(metadata_path.read_text(encoding="utf-8"))
                items.append({
                    "id": macro["id"],
                    "name": macro["name"],
                    "createdAt": macro["createdAt"],
                    "events": len(macro.get("events", [])),
                })
            except (OSError, KeyError, json.JSONDecodeError):
                continue
        return sorted(items, key=lambda item: item["createdAt"], reverse=True)

    def load(self, macro_id: str) -> dict[str, Any] | None:
        path = MACROS_DIR / macro_id / "macro.json"
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def save(self, macro: dict[str, Any]) -> None:
        folder = MACROS_DIR / macro["id"]
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "macro.json").write_text(json.dumps(macro, ensure_ascii=False, indent=2), encoding="utf-8")

    def delete(self, macro_id: str) -> bool:
        folder = MACROS_DIR / macro_id
        if not folder.is_dir():
            return False
        # Files created by this app only; remove them individually before the empty folder.
        for child in folder.iterdir():
            if child.is_file():
                child.unlink()
        folder.rmdir()
        return True


class ZoneStore:
    def __init__(self) -> None:
        ZONES_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not ZONES_FILE.exists():
            ZONES_FILE.write_text("[]", encoding="utf-8")

    def list(self) -> list[dict[str, Any]]:
        try:
            return json.loads(ZONES_FILE.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []

    def find(self, zone_id: str) -> dict[str, Any] | None:
        for zone in self.list():
            if zone["id"] == zone_id:
                return zone
        return None

    def find_by_name(self, name: str) -> dict[str, Any] | None:
        for zone in self.list():
            if zone["name"].casefold() == name.casefold():
                return zone
        return None

    def save_all(self, zones: list[dict[str, Any]]) -> None:
        ZONES_FILE.write_text(json.dumps(zones, ensure_ascii=False, indent=2), encoding="utf-8")

    def add(self, zone: dict[str, Any]) -> None:
        zones = self.list()
        zones.append(zone)
        self.save_all(zones)

    def rename(self, zone_id: str, name: str) -> None:
        zones = self.list()
        for zone in zones:
            if zone["id"] == zone_id:
                zone["name"] = safe_name(name)
        self.save_all(zones)

    def delete(self, zone_id: str) -> bool:
        zones = self.list()
        remaining = [zone for zone in zones if zone["id"] != zone_id]
        if len(remaining) == len(zones):
            return False
        self.save_all(remaining)
        return True


def select_zone_rectangle() -> dict[str, int] | None:
    """Overlay plein écran pour tracer un rectangle à la souris. Bloquant, à lancer hors du thread UI."""
    import tkinter as tk

    with mss.mss() as capture:
        virtual = capture.monitors[0]

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


class MacroEngine:
    def __init__(self) -> None:
        self.store = MacroStore()
        self.zone_store = ZoneStore()
        self.zone_capturing = False
        self.zone_message = ""
        self.lock = threading.RLock()
        self.status = "ready"
        self.message = "Prêt. Choisissez une action, puis appuyez sur F8."
        self.action_mode = "record"
        self.record_mouse_moves = True
        self.pending_name = ""
        self.selected_id: str | None = None
        self.recording: dict[str, Any] | None = None
        self.recording_started = 0.0
        self.last_move_at = 0.0
        self.last_move_position: tuple[int, int] | None = None
        self.pressed_keys: set[str] = set()
        self.stop_event = threading.Event()
        self.ui_bounds: tuple[int, int, int, int] | None = None
        self.mouse_controller = mouse.Controller()
        self.keyboard_controller = keyboard.Controller()
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)

    def start_listeners(self) -> None:
        self.mouse_listener.start()
        self.keyboard_listener.start()

    def event_time(self) -> float:
        return round(time.monotonic() - self.recording_started, 4)

    def in_ui(self, x: int, y: int) -> bool:
        if not self.ui_bounds:
            return False
        left, top, width, height = self.ui_bounds
        return left <= x < left + width and top <= y < top + height

    def add_event(self, event: dict[str, Any]) -> None:
        with self.lock:
            if self.status == "recording" and self.recording is not None:
                event["at"] = self.event_time()
                self.recording["events"].append(event)

    def on_move(self, x: int, y: int) -> None:
        if self.status != "recording" or not self.record_mouse_moves or self.in_ui(x, y):
            return
        now = time.monotonic()
        previous = self.last_move_position
        if previous and now - self.last_move_at < 0.012 and abs(x - previous[0]) < 3 and abs(y - previous[1]) < 3:
            return
        self.last_move_at = now
        self.last_move_position = (x, y)
        self.add_event({"kind": "move", "x": x, "y": y})

    def capture_click_context(self, x: int, y: int) -> dict[str, Any] | None:
        with self.lock:
            recording = self.recording
            index = len(recording["events"]) if recording else 0
        if not recording:
            return None
        box = clamp_box(x - CONTEXT_WIDTH // 2, y - CONTEXT_HEIGHT // 2, CONTEXT_WIDTH, CONTEXT_HEIGHT)
        image = grab_bgr(box)
        filename = f"click-{index:05d}.png"
        cv2.imwrite(str(MACROS_DIR / recording["id"] / filename), image)
        return {
            "image": filename,
            "left": box["left"],
            "top": box["top"],
            "width": box["width"],
            "height": box["height"],
            "offsetX": x - box["left"],
            "offsetY": y - box["top"],
        }

    def on_click(self, x: int, y: int, button: mouse.Button, pressed: bool) -> None:
        if self.status != "recording" or self.in_ui(x, y):
            return
        event: dict[str, Any] = {"kind": "mouse_down" if pressed else "mouse_up", "x": x, "y": y, "button": button.name}
        if pressed:
            context = self.capture_click_context(x, y)
            if context:
                event["context"] = context
        self.add_event(event)

    def on_scroll(self, x: int, y: int, dx: int, dy: int) -> None:
        if self.status == "recording" and not self.in_ui(x, y):
            self.add_event({"kind": "scroll", "x": x, "y": y, "dx": dx, "dy": dy})

    def on_press(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key == keyboard.Key.f8:
            threading.Thread(target=self.start_current, daemon=True).start()
            return
        if key == keyboard.Key.f9:
            self.stop()
            return
        if self.status == "recording":
            name = key_name(key)
            if name not in self.pressed_keys:
                self.pressed_keys.add(name)
                self.add_event({"kind": "key_down", "key": name})

    def on_release(self, key: keyboard.Key | keyboard.KeyCode) -> None:
        if key in (keyboard.Key.f8, keyboard.Key.f9):
            return
        if self.status == "recording":
            name = key_name(key)
            self.pressed_keys.discard(name)
            self.add_event({"kind": "key_up", "key": name})

    def prepare_recording(self, name: str) -> dict[str, Any]:
        with self.lock:
            if self.status != "ready":
                return self.state()
            self.action_mode = "record"
            self.pending_name = safe_name(name)
            self.message = f"{self.pending_name} prête à être enregistrée. Appuyez sur F8."
            return self.state()

    def set_action_mode(self, mode: str) -> dict[str, Any]:
        with self.lock:
            if self.status != "ready":
                return self.state()
            if mode == "play" and not self.selected_id:
                self.message = "Sélectionnez une macro à lire."
            else:
                self.action_mode = mode
                self.message = "Appuyez sur F8 pour lancer, F9 pour arrêter."
            return self.state()

    def set_record_mouse_moves(self, enabled: bool) -> dict[str, Any]:
        with self.lock:
            if self.status == "ready":
                self.record_mouse_moves = bool(enabled)
            return self.state()

    def select(self, macro_id: str | None) -> dict[str, Any]:
        with self.lock:
            self.selected_id = macro_id if macro_id and self.store.load(macro_id) else None
            return self.state()

    def rename(self, macro_id: str, name: str) -> dict[str, Any]:
        with self.lock:
            macro = self.store.load(macro_id)
            if macro:
                macro["name"] = safe_name(name)
                self.store.save(macro)
                self.message = "Macro renommée."
            return self.state()

    def delete(self, macro_id: str) -> dict[str, Any]:
        with self.lock:
            if self.status == "ready" and self.store.delete(macro_id):
                if self.selected_id == macro_id:
                    self.selected_id = None
                self.message = "Macro supprimée."
            return self.state()

    def create_zone(self, name: str) -> dict[str, Any]:
        with self.lock:
            if self.zone_capturing:
                return self.state()
            self.zone_capturing = True
            self.zone_message = "Tracez la zone à l'écran (Échap pour annuler)…"
        threading.Thread(target=self.capture_zone, args=(safe_name(name),), daemon=True).start()
        return self.state()

    def capture_zone(self, name: str) -> None:
        box = select_zone_rectangle()
        with self.lock:
            self.zone_capturing = False
            if box:
                self.zone_store.add({"id": uuid.uuid4().hex, "name": name, **box})
                self.zone_message = f"Zone « {name} » enregistrée."
            else:
                self.zone_message = "Capture de zone annulée."

    def rename_zone(self, zone_id: str, name: str) -> dict[str, Any]:
        with self.lock:
            self.zone_store.rename(zone_id, name)
            self.zone_message = "Zone renommée."
            return self.state()

    def delete_zone(self, zone_id: str) -> dict[str, Any]:
        with self.lock:
            if self.zone_store.delete(zone_id):
                self.zone_message = "Zone supprimée."
            return self.state()

    def test_zone_ocr(self, zone_id: str) -> dict[str, Any]:
        zone = self.zone_store.find(zone_id)
        if not zone:
            return {"text": "", "percent": None}
        text = read_zone_text(zone)
        return {"text": text.strip(), "percent": extract_percent(text)}

    def start_current(self) -> None:
        with self.lock:
            if self.status != "ready":
                return
            if self.action_mode == "record":
                self.start_recording_locked()
            elif self.selected_id:
                macro_id = self.selected_id
                self.status = "playing"
                self.stop_event.clear()
                self.message = "Lecture en cours — F9 pour arrêter."
                threading.Thread(target=self.play, args=(macro_id,), daemon=True).start()
            else:
                self.message = "Aucune macro sélectionnée pour la lecture."

    def start_recording_locked(self) -> None:
        macro_id = uuid.uuid4().hex
        name = self.pending_name or datetime.now().strftime("Macro %Y-%m-%d %H-%M")
        (MACROS_DIR / macro_id).mkdir(parents=True, exist_ok=True)
        self.recording = {"id": macro_id, "name": name, "createdAt": datetime.now().isoformat(timespec="seconds"), "events": []}
        self.recording_started = time.monotonic()
        self.last_move_at = 0.0
        self.last_move_position = None
        self.pressed_keys.clear()
        self.stop_event.clear()
        self.status = "recording"
        self.message = "Enregistrement en cours — F9 pour arrêter."

    def stop(self) -> None:
        with self.lock:
            if self.status == "recording" and self.recording:
                self.store.save(self.recording)
                self.selected_id = self.recording["id"]
                self.message = f"Enregistrement terminé : {self.recording['name']}."
                self.recording = None
                self.pending_name = ""
                self.pressed_keys.clear()
                self.status = "ready"
            elif self.status == "playing":
                self.stop_event.set()
                self.message = "Arrêt demandé…"

    def verify_click(self, macro: dict[str, Any], event: dict[str, Any]) -> tuple[int, int] | None:
        context = event.get("context")
        if not context:
            return event["x"], event["y"]
        template = cv2.imread(str(MACROS_DIR / macro["id"] / context["image"]), cv2.IMREAD_GRAYSCALE)
        if template is None:
            self.message = "Image de vérification absente : lecture annulée."
            return None
        search = clamp_box(event["x"] - SEARCH_WIDTH // 2, event["y"] - SEARCH_HEIGHT // 2, SEARCH_WIDTH, SEARCH_HEIGHT)
        frame = cv2.cvtColor(grab_bgr(search), cv2.COLOR_BGR2GRAY)
        if frame.shape[0] < template.shape[0] or frame.shape[1] < template.shape[1]:
            self.message = "Zone de vérification trop petite : lecture annulée."
            return None
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        _, score, _, location = cv2.minMaxLoc(result)
        if score < MATCH_THRESHOLD:
            self.message = f"Clic bloqué : contexte non reconnu (fiabilité {score:.0%})."
            return None
        return search["left"] + location[0] + context["offsetX"], search["top"] + location[1] + context["offsetY"]

    def play(self, macro_id: str) -> None:
        macro = self.store.load(macro_id)
        if not macro:
            with self.lock:
                self.status = "ready"
                self.message = "Macro introuvable."
            return
        previous_at = 0.0
        mark_control_active()
        try:
            for event in macro.get("events", []):
                if self.stop_event.wait(max(0, event.get("at", 0) - previous_at)):
                    break
                previous_at = event.get("at", previous_at)
                kind = event.get("kind")
                if kind == "move":
                    self.mouse_controller.position = (event["x"], event["y"])
                elif kind in ("mouse_down", "mouse_up"):
                    if kind == "mouse_down":
                        destination = self.verify_click(macro, event)
                        if destination is None:
                            break
                        self.mouse_controller.position = destination
                    button = getattr(mouse.Button, event["button"], None)
                    if button:
                        (self.mouse_controller.press if kind == "mouse_down" else self.mouse_controller.release)(button)
                elif kind == "scroll":
                    self.mouse_controller.position = (event["x"], event["y"])
                    self.mouse_controller.scroll(event["dx"], event["dy"])
                elif kind in ("key_down", "key_up"):
                    restored = restore_key(event["key"])
                    if restored:
                        (self.keyboard_controller.press if kind == "key_down" else self.keyboard_controller.release)(restored)
        except Exception as error:
            with self.lock:
                self.message = f"Lecture interrompue : {error}"
        finally:
            clear_control_active()
            with self.lock:
                if self.status == "playing":
                    self.status = "ready"
                    if self.message == "Lecture en cours — F9 pour arrêter.":
                        self.message = "Lecture terminée."
                self.stop_event.clear()

    def set_ui_bounds(self, left: int, top: int, width: int, height: int) -> None:
        self.ui_bounds = (left, top, width, height)

    def state(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "message": self.message,
            "actionMode": self.action_mode,
            "recordMouseMoves": self.record_mouse_moves,
            "pendingName": self.pending_name,
            "selectedId": self.selected_id,
            "macros": self.store.list(),
            "zones": self.zone_store.list(),
            "zoneCapturing": self.zone_capturing,
            "zoneMessage": self.zone_message,
            "controlActive": is_control_active(),
        }


class Api:
    def __init__(self, engine: MacroEngine) -> None:
        self.engine = engine

    def get_state(self) -> dict[str, Any]:
        return self.engine.state()

    def prepare_recording(self, name: str) -> dict[str, Any]:
        return self.engine.prepare_recording(name)

    def set_action_mode(self, mode: str) -> dict[str, Any]:
        return self.engine.set_action_mode(mode)

    def set_record_mouse_moves(self, enabled: bool) -> dict[str, Any]:
        return self.engine.set_record_mouse_moves(enabled)

    def select_macro(self, macro_id: str | None) -> dict[str, Any]:
        return self.engine.select(macro_id)

    def rename_macro(self, macro_id: str, name: str) -> dict[str, Any]:
        return self.engine.rename(macro_id, name)

    def delete_macro(self, macro_id: str) -> dict[str, Any]:
        return self.engine.delete(macro_id)

    def set_ui_bounds(self, left: int, top: int, width: int, height: int) -> None:
        self.engine.set_ui_bounds(int(left), int(top), int(width), int(height))

    def create_zone(self, name: str) -> dict[str, Any]:
        return self.engine.create_zone(name)

    def rename_zone(self, zone_id: str, name: str) -> dict[str, Any]:
        return self.engine.rename_zone(zone_id, name)

    def delete_zone(self, zone_id: str) -> dict[str, Any]:
        return self.engine.delete_zone(zone_id)

    def test_zone_ocr(self, zone_id: str) -> dict[str, Any]:
        return self.engine.test_zone_ocr(zone_id)


def main() -> None:
    enable_dpi_awareness()
    clear_control_active()
    clear_session_active()
    engine = MacroEngine()
    engine.start_listeners()
    # MSS reports physical Windows coordinates, including negative coordinates
    # for monitors located left of the primary display.
    with mss.mss() as capture:
        left_screen = min(capture.monitors[1:], key=lambda screen: screen["left"])
    window = webview.create_window(
        "Macrodesk",
        str(APP_DIR / "ui" / "index.html"),
        js_api=Api(engine),
        width=max(500, left_screen["width"] // 2),
        height=left_screen["height"],
        x=left_screen["left"],
        y=left_screen["top"],
        min_size=(420, 600),
        background_color="#10131a",
    )
    def sync_ui_bounds(window, *_args) -> None:
        engine.set_ui_bounds(window.x, window.y, window.width, window.height)

    window.events.shown += sync_ui_bounds
    window.events.moved += sync_ui_bounds
    window.events.resized += sync_ui_bounds
    webview.start(debug=False)


if __name__ == "__main__":
    main()

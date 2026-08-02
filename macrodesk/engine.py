"""Moteur d'enregistrement et de relecture des macros."""

from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime
from typing import Any

import cv2
from pynput import keyboard, mouse

from .control import clear_control_active, is_control_active, mark_control_active
from .keys import key_name, restore_key, safe_name
from .ocr import extract_percent, read_zone_text
from .screen import clamp_box, grab_bgr, select_zone_rectangle
from .store import MacroStore, ZoneStore

CONTEXT_WIDTH = 320
CONTEXT_HEIGHT = 220
SEARCH_WIDTH = 1100
SEARCH_HEIGHT = 820
MATCH_THRESHOLD = 0.55


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

    def stop_listeners(self) -> None:
        self.stop_event.set()
        self.mouse_listener.stop()
        self.keyboard_listener.stop()

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
        cv2.imwrite(str(self.store.folder(recording["id"]) / filename), image)
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
        self.store.folder(macro_id).mkdir(parents=True, exist_ok=True)
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
        template = cv2.imread(str(self.store.folder(macro["id"]) / context["image"]), cv2.IMREAD_GRAYSCALE)
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

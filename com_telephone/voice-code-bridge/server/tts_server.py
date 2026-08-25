import io
import json
import os
import tempfile
import asyncio
import wave
from http.server import BaseHTTPRequestHandler, HTTPServer
from piper import PiperVoice
from piper.config import SynthesisConfig

PORT = 5002
PIPER_MODEL_PATH = "voices/fr_FR-upmc-medium.onnx"
SYN_CONFIG = SynthesisConfig(length_scale=1.0)

EDGE_VOICE = "fr-FR-DeniseNeural"

print("Chargement de la voix Piper de secours...", flush=True)
piper_voice = PiperVoice.load(PIPER_MODEL_PATH)
print("Voix Piper chargee.", flush=True)


def synth_piper(text):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        piper_voice.synthesize_wav(text, wav_file, syn_config=SYN_CONFIG)
    return buffer.getvalue(), "audio/wav"


def synth_edge(text):
    import edge_tts
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        asyncio.run(edge_tts.Communicate(text, voice=EDGE_VOICE).save(tmp_path))
        with open(tmp_path, "rb") as f:
            return f.read(), "audio/mpeg"
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != "/synthesize":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            text = json.loads(body).get("text", "")
        except Exception:
            self.send_response(400)
            self.end_headers()
            return

        try:
            audio_bytes, mime = synth_edge(text)
        except Exception as e:
            print(f"edge-tts indisponible ({e}), bascule sur Piper", flush=True)
            try:
                audio_bytes, mime = synth_piper(text)
            except Exception as e2:
                print(f"Piper en echec aussi ({e2})", flush=True)
                self.send_response(500)
                self.end_headers()
                return

        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(audio_bytes)))
        self.end_headers()
        self.wfile.write(audio_bytes)

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Serveur TTS demarre sur le port {PORT}", flush=True)
    server.serve_forever()

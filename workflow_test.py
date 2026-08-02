"""Test de bout en bout du pont Macrodesk <-> OpenCode.

Pré-requis : une macro nommée ``opencode-envoyer`` enregistrée avec :
clic dans le chat, Ctrl+V, puis clic sur Envoyer.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import pyperclip

from app import APP_DIR, MacroEngine, MacroStore


BRIDGE_DIR = APP_DIR / "_workflow_test"
POLL_SECONDS = 1
DEFAULT_TIMEOUT = 180


def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def wait_for_answer(path: Path, timeout: int) -> str:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            answer = path.read_text(encoding="utf-8").strip()
            if answer:
                return answer
        time.sleep(POLL_SECONDS)
    raise TimeoutError(f"Aucune réponse écrite dans {path} après {timeout} secondes.")


def find_macro(name: str) -> dict:
    for summary in MacroStore().list():
        if summary["name"].casefold() == name.casefold():
            macro = MacroStore().load(summary["id"])
            if macro:
                return macro
    raise FileNotFoundError(
        f"Macro « {name} » introuvable. Créez-la dans Macrodesk avant de lancer ce test."
    )


def run_macro(engine: MacroEngine, macro: dict) -> None:
    """Rejoue la macro tout en laissant F9 disponible comme arrêt d'urgence."""
    with engine.lock:
        engine.status = "playing"
        engine.stop_event.clear()
        engine.message = "Workflow : envoi du prompt en cours — F9 pour arrêter."
    engine.play(macro["id"])
    outcome = engine.message.casefold()
    if "bloqué" in outcome or "interrompue" in outcome or "arrêt demandé" in outcome:
        raise RuntimeError(f"La macro ne s'est pas terminée correctement : {engine.message}")


def send_prompt(engine: MacroEngine, macro: dict, prompt: str) -> None:
    pyperclip.copy(prompt)
    # Le collage est volontairement enregistré dans la macro sous Ctrl+V.
    run_macro(engine, macro)


def request_prompt(request_file: Path, response_file: Path) -> str:
    return f"""Tu es OpenCode et tu participes à un test local d'automatisation.

Lis précisément la demande dans le fichier :
{request_file}

Exécute uniquement cette demande dans le dossier de travail partagé. Quand c'est terminé,
écris un compte rendu concis et factuel dans ce fichier exact :
{response_file}

Ne te limite pas à une réponse dans le chat : l'écriture du fichier de réponse est le signal
attendu par le workflow. Termine ensuite ta réponse dans le chat par « FICHIER ÉCRIT ».
"""


def follow_up_prompt(previous_response: Path, response_file: Path, artifact: Path) -> str:
    return f"""Poursuis le test local d'automatisation.

Lis le premier compte rendu :
{previous_response}

Vérifie que le fichier attendu existe et contient exactement `macro bridge OK` :
{artifact}

Écris ton verdict final (SUCCÈS ou ÉCHEC, avec une phrase de justification) dans ce fichier exact :
{response_file}

Ne te limite pas au chat : l'écriture de ce fichier est obligatoire. Termine ensuite dans le chat
par « FICHIER ÉCRIT ».
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Teste l'envoi de prompts vers OpenCode au moyen d'une macro Macrodesk.")
    parser.add_argument("--macro", default="opencode-envoyer", help="nom exact de la macro d'envoi")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="délai maximal par réponse, en secondes")
    args = parser.parse_args()

    if args.timeout < 10:
        parser.error("--timeout doit être d'au moins 10 secondes")

    macro = find_macro(args.macro)
    BRIDGE_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    request = BRIDGE_DIR / f"{stamp}-demande.md"
    response_one = BRIDGE_DIR / f"{stamp}-reponse-1.md"
    response_two = BRIDGE_DIR / f"{stamp}-reponse-2.md"
    artifact = BRIDGE_DIR / f"{stamp}-artefact.txt"
    manifest = BRIDGE_DIR / f"{stamp}-manifest.json"

    write_text(
        request,
        f"""# Test Macrodesk / OpenCode

Crée le fichier `{artifact}` et écris-y exactement :

macro bridge OK

Ne modifie aucun autre fichier que ceux explicitement demandés dans ce test.
""",
    )
    write_text(
        manifest,
        json.dumps(
            {"macro": macro["name"], "startedAt": datetime.now().isoformat(timespec="seconds"), "status": "started"},
            ensure_ascii=False,
            indent=2,
        ),
    )

    engine = MacroEngine()
    engine.start_listeners()
    try:
        print("Étape 1/2 — envoi de la demande à OpenCode…")
        send_prompt(engine, macro, request_prompt(request.resolve(), response_one.resolve()))
        print(f"Attente de la réponse dans {response_one.name}…")
        first_response = wait_for_answer(response_one, args.timeout)
        print("Réponse 1 reçue.")

        print("Étape 2/2 — demande de vérification à OpenCode…")
        send_prompt(engine, macro, follow_up_prompt(response_one.resolve(), response_two.resolve(), artifact.resolve()))
        print(f"Attente de la réponse dans {response_two.name}…")
        final_response = wait_for_answer(response_two, args.timeout)

        expected = "macro bridge OK"
        artifact_ok = artifact.exists() and artifact.read_text(encoding="utf-8").strip() == expected
        response_ok = "succès" in final_response.casefold() or "succes" in final_response.casefold()
        status = "passed" if artifact_ok and response_ok else "failed"
        write_text(
            manifest,
            json.dumps(
                {
                    "macro": macro["name"],
                    "startedAt": stamp,
                    "status": status,
                    "artifact": str(artifact),
                    "firstResponse": first_response,
                    "finalResponse": final_response,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"Test {status.upper()} — résultat : {manifest}")
        return 0 if status == "passed" else 1
    except (FileNotFoundError, RuntimeError, TimeoutError) as error:
        print(f"TEST BLOQUÉ : {error}", file=sys.stderr)
        return 2
    finally:
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())

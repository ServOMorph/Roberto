"""Conversation Macrodesk <-> OpenCode en dix échanges autour d'un script Python."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import argparse

from app import APP_DIR, MacroEngine
from workflow_test import (
    DEFAULT_WATCH_THRESHOLD,
    ContextLimitReached,
    find_macro,
    find_zone,
    send_prompt,
    wait_for_answer,
    write_text,
)


TIMEOUT_PER_TURN = 180
STEPS = [
    "Analyse le besoin et propose une architecture courte, sans encore créer de fichier.",
    "Crée une première version fonctionnelle du script dans le dossier de projet indiqué.",
    "Ajoute le comptage séparé des lignes totales, non vides et vides, avec gestion des fichiers introuvables.",
    "Ajoute une interface de ligne de commande argparse avec plusieurs chemins et une option --json.",
    "Crée des tests unitaires standard-library couvrant les cas normaux et les erreurs de fichiers.",
    "Exécute les tests, corrige le script si nécessaire et consigne le résultat précis.",
    "Relis le code pour améliorer les types, les messages d'erreur et la portabilité Windows.",
    "Ajoute une documentation d'utilisation concise dans un README local avec trois exemples.",
    "Fais une revue finale : vérifie les cas limites et applique uniquement les corrections nécessaires.",
    "Fais la validation finale, récapitule les fichiers créés et donne la commande exacte pour utiliser le script.",
]


def prompt_for_turn(
    turn: int,
    project: Path,
    response_file: Path,
    previous_response: str | None,
) -> str:
    context = "Aucun échange précédent : commence par cadrer le travail."
    if previous_response:
        context = f"Voici le compte rendu du tour précédent, que tu dois prendre en compte :\n\n{previous_response[:6000]}"
    return f"""Tu es OpenCode dans une conversation de test automatisée, tour {turn}/10.

Objectif commun : construire progressivement, uniquement dans le dossier `{project}`, un script Python standard-library nommé `line_counter.py`. Il doit analyser un ou plusieurs fichiers texte et afficher les nombres de lignes totales, non vides et vides, avec une option JSON.

Action de ce tour : {STEPS[turn - 1]}

Contraintes : n'utilise aucun réseau, ne modifie aucun fichier hors de `{project}`, et ne supprime aucun fichier existant. Tu peux lire les fichiers créés aux tours précédents.

{context}

À la fin, écris un compte rendu factuel du tour dans ce fichier exact :
`{response_file}`

Ce fichier est obligatoire ; le prochain tour lira son contenu avant de te répondre. Tu peux aussi répondre dans le chat, mais termine par « FICHIER ÉCRIT ».
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Conversation Macrodesk <-> OpenCode en dix échanges.")
    parser.add_argument("--watch-zone", default=None, help="nom de la zone Macrodesk à lire par OCR avant chaque envoi")
    parser.add_argument("--watch-threshold", type=int, default=DEFAULT_WATCH_THRESHOLD, help="pourcentage de contexte au-delà duquel l'envoi est refusé")
    args = parser.parse_args()

    macro = find_macro("opencode-envoyer")
    watch_zone = find_zone(args.watch_zone) if args.watch_zone else None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    root = APP_DIR / "_workflow_test" / f"conversation-{stamp}"
    project = root / "python_project"
    project.mkdir(parents=True)
    manifest = root / "manifest.json"
    responses: list[dict[str, str]] = []
    engine = MacroEngine()
    engine.start_listeners()

    try:
        previous_response: str | None = None
        for turn in range(1, 11):
            response_file = root / f"reponse-{turn:02d}.md"
            print(f"Tour {turn}/10 — envoi du prompt…", flush=True)
            send_prompt(engine, macro, prompt_for_turn(turn, project.resolve(), response_file.resolve(), previous_response), watch_zone, args.watch_threshold)
            print(f"Tour {turn}/10 — attente de {response_file.name}…", flush=True)
            previous_response = wait_for_answer(response_file, TIMEOUT_PER_TURN)
            responses.append({"turn": str(turn), "response": previous_response})
            print(f"Tour {turn}/10 — réponse reçue.", flush=True)

        script = project / "line_counter.py"
        compile_result = subprocess.run(
            [sys.executable, "-m", "py_compile", str(script)],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=20,
        ) if script.exists() else None
        status = "passed" if script.exists() and compile_result and compile_result.returncode == 0 else "failed"
        write_text(
            manifest,
            json.dumps(
                {
                    "status": status,
                    "macro": macro["name"],
                    "project": str(project),
                    "script": str(script),
                    "turnsCompleted": len(responses),
                    "compileStderr": compile_result.stderr if compile_result else "line_counter.py absent",
                    "responses": responses,
                },
                ensure_ascii=False,
                indent=2,
            ),
        )
        print(f"CONVERSATION {status.upper()} — manifeste : {manifest}", flush=True)
        return 0 if status == "passed" else 1
    except Exception as error:
        write_text(manifest, json.dumps({"status": "blocked", "error": str(error), "turnsCompleted": len(responses)}, ensure_ascii=False, indent=2))
        print(f"CONVERSATION BLOQUÉE : {error}", file=sys.stderr, flush=True)
        return 2
    finally:
        engine.stop_event.set()
        engine.mouse_listener.stop()
        engine.keyboard_listener.stop()


if __name__ == "__main__":
    raise SystemExit(main())

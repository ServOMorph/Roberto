"""Test de bout en bout du pont Macrodesk <-> agent.

Pré-requis : la macro d'envoi du profil de l'agent (clic dans le chat, Ctrl+V, envoi).

Lancer : ``py -m scripts.workflow_check``
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys

import agents
from agents.base import AgentProfile
from bridge import ContextLimitReached, UserAbort, find_macro, send_prompt, wait_for_answer, write_text

from .common import RUNS_DIR, add_agent_arguments, controlled_session, resolve_watch_zone

DEFAULT_TIMEOUT = 180
EXPECTED_ARTIFACT = "macro bridge OK"


def request_prompt(request_file: Path, response_file: Path, agent: AgentProfile | None = None) -> str:
    label = agent.label if agent else "l'agent"
    ack = agent.write_ack if agent else "FICHIER ÉCRIT"
    return f"""Tu es {label} et tu participes à un test local d'automatisation.

Lis précisément la demande dans le fichier :
{request_file}

Exécute uniquement cette demande dans le dossier de travail partagé. Quand c'est terminé,
écris un compte rendu concis et factuel dans ce fichier exact :
{response_file}

Ne te limite pas à une réponse dans le chat : l'écriture du fichier de réponse est le signal
attendu par le workflow. Termine ensuite ta réponse dans le chat par « {ack} ».
"""


def follow_up_prompt(
    previous_response: Path,
    response_file: Path,
    artifact: Path,
    agent: AgentProfile | None = None,
) -> str:
    ack = agent.write_ack if agent else "FICHIER ÉCRIT"
    return f"""Poursuis le test local d'automatisation.

Lis le premier compte rendu :
{previous_response}

Vérifie que le fichier attendu existe et contient exactement `{EXPECTED_ARTIFACT}` :
{artifact}

Écris ton verdict final (SUCCÈS ou ÉCHEC, avec une phrase de justification) dans ce fichier exact :
{response_file}

Ne te limite pas au chat : l'écriture de ce fichier est obligatoire. Termine ensuite dans le chat
par « {ack} ».
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Teste l'envoi de prompts vers un agent au moyen d'une macro Macrodesk.")
    add_agent_arguments(parser)
    parser.add_argument("--macro", default=None, help="nom exact de la macro d'envoi (défaut : celle du profil de l'agent)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="délai maximal par réponse, en secondes")
    args = parser.parse_args()
    if args.timeout < 10:
        parser.error("--timeout doit être d'au moins 10 secondes")
    return args


def main() -> int:
    args = parse_args()
    agent = agents.get(args.agent)
    macro = find_macro(args.macro or agent.send_macro)
    watch_zone = resolve_watch_zone(args)
    RUNS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    request = RUNS_DIR / f"{stamp}-demande.md"
    response_one = RUNS_DIR / f"{stamp}-reponse-1.md"
    response_two = RUNS_DIR / f"{stamp}-reponse-2.md"
    artifact = RUNS_DIR / f"{stamp}-artefact.txt"
    manifest = RUNS_DIR / f"{stamp}-manifest.json"

    def write_manifest(payload: dict) -> None:
        write_text(manifest, json.dumps({"agent": agent.key, "macro": macro["name"], **payload}, ensure_ascii=False, indent=2))

    write_text(
        request,
        f"""# Test Macrodesk / {agent.label}

Crée le fichier `{artifact}` et écris-y exactement :

{EXPECTED_ARTIFACT}

Ne modifie aucun autre fichier que ceux explicitement demandés dans ce test.
""",
    )
    write_manifest({"startedAt": datetime.now().isoformat(timespec="seconds"), "status": "started"})

    with controlled_session() as (engine, abort_event):
        try:
            print(f"Étape 1/2 — envoi de la demande à {agent.label}…")
            send_prompt(
                engine,
                macro,
                request_prompt(request.resolve(), response_one.resolve(), agent),
                watch_zone,
                args.watch_threshold,
                abort_event,
                agent,
            )
            print(f"Attente de la réponse dans {response_one.name}…")
            first_response = wait_for_answer(response_one, args.timeout, abort_event)
            print("Réponse 1 reçue.")

            print(f"Étape 2/2 — demande de vérification à {agent.label}…")
            send_prompt(
                engine,
                macro,
                follow_up_prompt(response_one.resolve(), response_two.resolve(), artifact.resolve(), agent),
                watch_zone,
                args.watch_threshold,
                abort_event,
                agent,
            )
            print(f"Attente de la réponse dans {response_two.name}…")
            final_response = wait_for_answer(response_two, args.timeout, abort_event)

            artifact_ok = artifact.exists() and artifact.read_text(encoding="utf-8").strip() == EXPECTED_ARTIFACT
            response_ok = "succès" in final_response.casefold() or "succes" in final_response.casefold()
            status = "passed" if artifact_ok and response_ok else "failed"
            write_manifest(
                {
                    "startedAt": stamp,
                    "status": status,
                    "artifact": str(artifact),
                    "firstResponse": first_response,
                    "finalResponse": final_response,
                }
            )
            print(f"Test {status.upper()} — résultat : {manifest}")
            return 0 if status == "passed" else 1
        except UserAbort as error:
            write_manifest({"startedAt": stamp, "status": "interrompu_utilisateur", "message": str(error)})
            print(f"ARRÊT UTILISATEUR (Échap) : {error} — état noté dans {manifest}", file=sys.stderr)
            return 4
        except ContextLimitReached as error:
            print(f"ARRÊT CONTEXTE : {error}", file=sys.stderr)
            return 3
        except (FileNotFoundError, RuntimeError, TimeoutError) as error:
            print(f"TEST BLOQUÉ : {error}", file=sys.stderr)
            return 2


if __name__ == "__main__":
    raise SystemExit(main())

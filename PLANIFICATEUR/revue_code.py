import argparse
import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent
ZONES_MD = RACINE.parent / ".claude" / "zones.md"

MODELE_DEFAUT = "sonnet"
TIMEOUT_DEFAUT_MIN = 30
BUDGET_DEFAUT = 5.0
NIVEAUX_AUTORISES = ("low", "medium", "high", "max")
OUTILS_REVUE = ["Read", "Glob", "Grep", "Bash"]
BASH_AUTORISE_REVUE = ["Bash(git:*)"]
BASH_INTERDIT_REVUE = ["Bash(git push:*)"]


def charger_zones(chemin=None):
    chemin = Path(chemin) if chemin else ZONES_MD
    if not chemin.exists():
        return {}
    zones = {}
    for ligne in chemin.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne.startswith("|") or ligne.startswith("|-"):
            continue
        parties = [p.strip() for p in ligne.strip("|").split("|")]
        if len(parties) != 2 or not parties[0]:
            continue
        alias, dossier = parties
        if alias.lower() == "alias":
            continue
        zones[alias] = dossier
    return zones


def resoudre_cible(argument, chemin_zones=None):
    zones = charger_zones(chemin_zones)
    if argument in zones:
        return Path(zones[argument]).resolve()
    chemin = Path(argument)
    if chemin.is_dir():
        return chemin.resolve()
    raise ValueError(
        "cible inconnue : '{}' n'est ni un alias de {} ni un dossier existant".format(
            argument, chemin_zones or ZONES_MD
        )
    )


def construire_commande(niveau, budget_usd=BUDGET_DEFAUT):
    if niveau not in NIVEAUX_AUTORISES:
        raise ValueError("niveau refuse : {} (autorises : {})".format(niveau, NIVEAUX_AUTORISES))
    commande = [
        "claude",
        "-p",
        "/code-review {}".format(niveau),
        "--restricted",
        "--permission-prompts",
        "none",
        "--output-format",
        "json",
        "--model",
        MODELE_DEFAUT,
        "--max-budget-usd",
        str(budget_usd),
        "--tools",
    ]
    commande.extend(OUTILS_REVUE)
    commande.append("--allowedTools")
    commande.extend(BASH_AUTORISE_REVUE)
    commande.append("--disallowedTools")
    commande.extend(BASH_INTERDIT_REVUE)
    return commande


def _tuer_arbre(proc):
    if os.name == "nt":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        return
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        proc.kill()


def lancer(dossier_cible, niveau, timeout_min, budget_usd=BUDGET_DEFAUT):
    commande = construire_commande(niveau, budget_usd)
    options_popen = {} if os.name == "nt" else {"start_new_session": True}
    proc = subprocess.Popen(
        commande,
        cwd=str(dossier_cible),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        **options_popen,
    )
    timeout_atteint = False
    try:
        stdout, stderr = proc.communicate(timeout=timeout_min * 60)
    except subprocess.TimeoutExpired:
        timeout_atteint = True
        _tuer_arbre(proc)
        stdout, stderr = proc.communicate()
    return proc.returncode, stdout, stderr, timeout_atteint


def ecrire_sortie(dossier_cible, niveau, code_retour, stdout, stderr, timeout_atteint):
    dossier_sortie = Path(dossier_cible) / "ROBERTO"
    dossier_sortie.mkdir(exist_ok=True)
    horodatage = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    chemin = dossier_sortie / "revue_brute_{}.json".format(horodatage)
    contenu = {
        "date": datetime.now().isoformat(timespec="seconds"),
        "dossier_cible": str(dossier_cible),
        "niveau": niveau,
        "code_retour": code_retour,
        "timeout_atteint": timeout_atteint,
        "stdout": stdout,
        "stderr": stderr,
    }
    chemin.write_text(json.dumps(contenu, indent=2, ensure_ascii=False), encoding="utf-8")
    return chemin


def executer(
    argument_cible,
    niveau="max",
    timeout_min=TIMEOUT_DEFAUT_MIN,
    budget_usd=BUDGET_DEFAUT,
    chemin_zones=None,
):
    dossier_cible = resoudre_cible(argument_cible, chemin_zones)
    if not dossier_cible.is_dir():
        raise ValueError("dossier cible introuvable : {}".format(dossier_cible))
    code_retour, stdout, stderr, timeout_atteint = lancer(
        dossier_cible, niveau, timeout_min, budget_usd
    )
    chemin_sortie = ecrire_sortie(dossier_cible, niveau, code_retour, stdout, stderr, timeout_atteint)
    return chemin_sortie, code_retour


def construire_parser():
    parser = argparse.ArgumentParser(
        description="Lance /code-review niveau max sur un projet cible, sans surveillance."
    )
    parser.add_argument("cible", help="alias de .claude/zones.md ou chemin de dossier")
    parser.add_argument("--niveau", default="max", choices=NIVEAUX_AUTORISES)
    parser.add_argument("--timeout", type=int, default=TIMEOUT_DEFAUT_MIN)
    parser.add_argument("--budget", type=float, default=BUDGET_DEFAUT)
    return parser


def main():
    args = construire_parser().parse_args()
    try:
        chemin_sortie, code_retour = executer(args.cible, args.niveau, args.timeout, args.budget)
    except ValueError as exc:
        print("erreur : {}".format(exc), file=sys.stderr)
        return 1
    print("sortie brute : {}".format(chemin_sortie))
    return 0 if code_retour == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

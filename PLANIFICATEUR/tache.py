import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import orchestrateur


def _lire(chemin):
    if not Path(chemin).exists():
        return {"butoir": orchestrateur.BUTOIR_DEFAUT, "taches": []}
    return orchestrateur.charger_queue(chemin)


def ajouter(donnees, args, allowlist):
    if any(t["id"] == args.id for t in donnees["taches"]):
        return 1, "id deja present : {}".format(args.id)
    if not orchestrateur.dossier_autorise(args.dossier, allowlist):
        return 1, (
            "dossier refuse : {}\nIl doit figurer dans allowlist.txt (ou etre "
            "situe dessous) et exister.".format(args.dossier)
        )
    tache = {
        "id": args.id,
        "dossier": str(Path(args.dossier).resolve()),
        "prompt": args.prompt,
        "modele": args.modele,
        "budget_usd": args.budget,
        "timeout_min": args.timeout,
        "statut": "en_attente",
        "tentatives": 0,
        "historique": [],
    }
    if args.heure_min:
        tache["heure_min"] = args.heure_min
    if args.outils:
        tache["outils"] = args.outils
    donnees["taches"].append(tache)
    return 0, "ajoutee : {}".format(args.id)


def lister(donnees):
    if not donnees["taches"]:
        return 0, "file vide"
    lignes = ["butoir : {}".format(donnees.get("butoir", orchestrateur.BUTOIR_DEFAUT))]
    for tache in donnees["taches"]:
        prompt = tache.get("prompt", "")
        if len(prompt) > 60:
            prompt = prompt[:60] + "..."
        lignes.append(
            "{:<16} {:<12} {:<8} {:<7} {}".format(
                tache["id"],
                tache.get("statut", "?"),
                tache.get("modele", "-"),
                tache.get("heure_min", "-"),
                prompt,
            )
        )
    return 0, "\n".join(lignes)


def supprimer(donnees, identifiant):
    avant = len(donnees["taches"])
    donnees["taches"] = [t for t in donnees["taches"] if t["id"] != identifiant]
    if len(donnees["taches"]) == avant:
        return 1, "id introuvable : {}".format(identifiant)
    return 0, "supprimee : {}".format(identifiant)


def reinitialiser(donnees, identifiant):
    cibles = [
        t
        for t in donnees["taches"]
        if identifiant in ("*", t["id"]) and t.get("statut") != "en_attente"
    ]
    if not cibles:
        return 1, "rien a reinitialiser"
    for tache in cibles:
        tache["statut"] = "en_attente"
        tache["tentatives"] = 0
        for cle in ("raison", "detail", "refus", "duree_s", "cout_usd", "log"):
            tache.pop(cle, None)
    return 0, "reinitialisee(s) : {}".format(", ".join(t["id"] for t in cibles))


def construire_parser():
    parser = argparse.ArgumentParser(
        prog="tache", description="Gestion de la file du planificateur nocturne"
    )
    parser.add_argument("--queue", default=None, help="chemin de queue.json")
    sous = parser.add_subparsers(dest="commande", required=True)

    ajout = sous.add_parser("add", help="ajouter une tache")
    ajout.add_argument("id")
    ajout.add_argument("dossier")
    ajout.add_argument("prompt")
    ajout.add_argument("--modele", default=orchestrateur.MODELE_DEFAUT)
    ajout.add_argument("--budget", type=float, default=orchestrateur.BUDGET_DEFAUT)
    ajout.add_argument("--timeout", type=int, default=orchestrateur.TIMEOUT_DEFAUT_MIN)
    ajout.add_argument("--heure-min", dest="heure_min", default=None)
    ajout.add_argument("--outils", nargs="+", default=None)

    sous.add_parser("list", help="lister la file")

    suppression = sous.add_parser("rm", help="supprimer une tache")
    suppression.add_argument("id")

    remise = sous.add_parser("reset", help="remettre une tache en attente")
    remise.add_argument("id", help="identifiant, ou * pour toutes")

    return parser


def executer(argv=None):
    args = construire_parser().parse_args(argv)
    chemin = Path(args.queue) if args.queue else orchestrateur.FICHIER_QUEUE
    donnees = _lire(chemin)

    if args.commande == "list":
        return lister(donnees)
    if args.commande == "add":
        code, message = ajouter(donnees, args, orchestrateur.charger_allowlist())
    elif args.commande == "rm":
        code, message = supprimer(donnees, args.id)
    else:
        code, message = reinitialiser(donnees, args.id)

    if code == 0:
        orchestrateur.sauver_queue(donnees, chemin)
    return code, message


def main():
    code, message = executer()
    print(message)
    return code


if __name__ == "__main__":
    sys.exit(main())

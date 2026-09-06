import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

RACINE = Path(__file__).resolve().parent
FICHIER_SUIVI_DEFAUT = RACINE / "suivi_revues.json"
RACINES_SCAN_DEFAUT = [
    Path(r"C:\Users\raph6\Documents\ServOMorph"),
    Path(r"D:\ServOMorph"),
]
SEUIL_JOURS_DEFAUT = 90


def normaliser_chemin(dossier):
    return str(Path(dossier).resolve())


def lister_candidats(racines):
    candidats = []
    for racine in racines:
        if not racine.is_dir():
            continue
        for entree in sorted(racine.iterdir()):
            if not entree.is_dir():
                continue
            if (entree / ".git").is_dir() and (entree / ".claude").is_dir():
                candidats.append(entree)
    return candidats


def epoch_dernier_commit(projet):
    try:
        sortie = subprocess.run(
            ["git", "-C", str(projet), "log", "-1", "--format=%ct"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (subprocess.CalledProcessError, OSError):
        return projet.stat().st_mtime
    valeur = sortie.stdout.strip()
    if not valeur:
        return projet.stat().st_mtime
    try:
        return float(valeur)
    except ValueError:
        return projet.stat().st_mtime


def filtrer_pertinents(candidats, seuil_jours):
    limite = datetime.now().timestamp() - seuil_jours * 86400
    pertinents = []
    for projet in candidats:
        epoch = epoch_dernier_commit(projet)
        if epoch >= limite:
            pertinents.append((projet, epoch))
    return pertinents


def charger_suivi(fichier):
    if not fichier.exists():
        return {"projets": {}}
    with fichier.open("r", encoding="utf-8") as f:
        return json.load(f)


def sauvegarder_suivi(fichier, suivi):
    with fichier.open("w", encoding="utf-8") as f:
        json.dump(suivi, f, ensure_ascii=False, indent=2, sort_keys=True)


def classer(pertinents, suivi):
    projets = suivi.get("projets", {})
    lignes = []
    for projet, epoch_modif in pertinents:
        cle = normaliser_chemin(projet)
        info = projets.get(cle)
        derniere_review = info.get("derniere_review") if info else None
        lignes.append(
            {
                "chemin": cle,
                "nom": projet.name,
                "jamais_review": derniere_review is None,
                "derniere_review": derniere_review,
                "epoch_dernier_commit": epoch_modif,
            }
        )
    lignes.sort(
        key=lambda l: (
            not l["jamais_review"],
            l["derniere_review"] or "",
            -l["epoch_dernier_commit"],
        )
    )
    return lignes


def choisir(racines=None, seuil_jours=SEUIL_JOURS_DEFAUT, fichier_suivi=FICHIER_SUIVI_DEFAUT):
    racines = racines or RACINES_SCAN_DEFAUT
    candidats = lister_candidats(racines)
    pertinents = filtrer_pertinents(candidats, seuil_jours)
    suivi = charger_suivi(fichier_suivi)
    return classer(pertinents, suivi)


def marquer_review(chemin, niveau, resultat, fichier_suivi=FICHIER_SUIVI_DEFAUT, date=None):
    dossier = Path(chemin)
    if not dossier.is_dir():
        raise ValueError("dossier introuvable : {}".format(chemin))
    suivi = charger_suivi(fichier_suivi)
    cle = normaliser_chemin(dossier)
    suivi.setdefault("projets", {})[cle] = {
        "nom": dossier.name,
        "derniere_review": date or datetime.now().strftime("%Y-%m-%d"),
        "niveau": niveau,
        "resultat": resultat,
    }
    sauvegarder_suivi(fichier_suivi, suivi)
    return cle


def construire_parser():
    parser = argparse.ArgumentParser(
        description="Selectionne le prochain projet a passer en revue de code, ou enregistre une revue faite."
    )
    sous_parsers = parser.add_subparsers(dest="commande")

    parser_prochain = sous_parsers.add_parser("prochain", help="affiche le projet le plus pertinent")
    parser_prochain.add_argument("--seuil-jours", type=int, default=SEUIL_JOURS_DEFAUT)

    parser_lister = sous_parsers.add_parser("lister", help="affiche tous les projets pertinents classes")
    parser_lister.add_argument("--seuil-jours", type=int, default=SEUIL_JOURS_DEFAUT)

    parser_marquer = sous_parsers.add_parser("marquer", help="enregistre une revue faite pour un projet")
    parser_marquer.add_argument("chemin")
    parser_marquer.add_argument("--niveau", default="max")
    parser_marquer.add_argument("--resultat", default="")

    return parser


def main():
    args = construire_parser().parse_args()
    commande = args.commande or "prochain"

    if commande == "marquer":
        cle = marquer_review(args.chemin, args.niveau, args.resultat)
        print("enregistre : {}".format(cle))
        return 0

    lignes = choisir(seuil_jours=args.seuil_jours)

    if commande == "lister":
        print(json.dumps(lignes, ensure_ascii=False, indent=2))
        return 0

    a_faire = [l for l in lignes if l["jamais_review"]]
    if not a_faire:
        print(json.dumps({"message": "aucun projet pertinent jamais review"}, ensure_ascii=False))
        return 1
    print(json.dumps(a_faire[0], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

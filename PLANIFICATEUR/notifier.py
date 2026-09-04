import json
import urllib.error
import urllib.request

URL_SEND = "http://127.0.0.1:5000/send"
PROJET = "roberto"
TIMEOUT_S = 5


def resumer(donnees, meta, chemin_rapport):
    taches = donnees.get("taches", [])
    compteurs = {"faite": 0, "refus": 0, "echouee": 0, "reportee": 0}
    for tache in taches:
        statut = tache.get("statut")
        if statut in compteurs:
            compteurs[statut] += 1
    cout = sum(t.get("cout_usd") or 0 for t in taches)
    lignes = [
        "Nuit terminee ({} -> {})".format(
            meta["debut"].strftime("%H:%M"), meta["fin"].strftime("%H:%M")
        ),
        "{} faite(s), {} avec outils refuses, {} echouee(s), {} reportee(s)".format(
            compteurs["faite"],
            compteurs["refus"],
            compteurs["echouee"],
            compteurs["reportee"],
        ),
        "Cout total {:.4f} $".format(cout),
    ]
    a_signaler = [
        t
        for t in taches
        if t.get("statut") in ("refus", "echouee") and t.get("raison") != "hors_allowlist"
    ]
    for tache in a_signaler[:5]:
        lignes.append("- {} : {}".format(tache["id"], tache.get("raison", "?")))
    lignes.append("Rapport : {}".format(chemin_rapport))
    return "\n".join(lignes)


def envoyer(texte, url=URL_SEND, projet=PROJET):
    charge = json.dumps({"text": texte, "project": projet}, ensure_ascii=False)
    requete = urllib.request.Request(
        url,
        data=charge.encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(requete, timeout=TIMEOUT_S) as reponse:
            return True, reponse.status
    except (urllib.error.URLError, OSError, ValueError) as erreur:
        return False, str(erreur)


def notifier(donnees, meta, chemin_rapport):
    return envoyer(resumer(donnees, meta, chemin_rapport))

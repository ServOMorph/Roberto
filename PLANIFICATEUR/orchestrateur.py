import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

import notifier
import rapport

FICHIER_ALLOWLIST = RACINE / "allowlist.txt"
FICHIER_QUEUE = RACINE / "queue.json"
DOSSIER_LOGS = RACINE / "logs"

BUTOIR_DEFAUT = "06:00"
RETRY_QUOTA_MIN = 25
MODELE_DEFAUT = "sonnet"
BUDGET_DEFAUT = 1.0
TIMEOUT_DEFAUT_MIN = 20
OUTILS_DEFAUT = ["Read", "Edit", "Write", "Glob", "Grep", "Bash"]
BASH_AUTORISE_DEFAUT = ["Bash(git:*)", "Bash(npm test:*)", "Bash(npm run typecheck:*)"]
BASH_INTERDIT_DEFAUT = ["Bash(git push:*)", "Bash(npm run dev:*)", "Bash(npm run package:*)"]

STATUTS_TERMINES = {"faite", "echouee", "refus", "reportee"}

MOTIFS_QUOTA = re.compile(
    r"usage limit|rate.?limit|quota|limit reached|limite d.usage|resets? at|"
    r"try again later|5-hour|five.?hour|too many requests",
    re.IGNORECASE,
)


def journal(message):
    horodatage = datetime.now().strftime("%H:%M:%S")
    print("[{}] {}".format(horodatage, message), flush=True)


def charger_allowlist(chemin=None):
    chemin = chemin or FICHIER_ALLOWLIST
    if not Path(chemin).exists():
        return []
    lignes = Path(chemin).read_text(encoding="utf-8").splitlines()
    dossiers = []
    for ligne in lignes:
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#"):
            continue
        dossiers.append(Path(ligne).resolve())
    return dossiers


def dossier_autorise(dossier, allowlist):
    if not dossier:
        return False
    try:
        cible = Path(dossier).resolve(strict=True)
    except OSError:
        return False
    if not cible.is_dir():
        return False
    for racine in allowlist:
        if cible == racine or cible.is_relative_to(racine):
            return True
    return False


def heure_cible(depart, hhmm):
    heures, minutes = [int(x) for x in hhmm.split(":")]
    cible = depart.replace(hour=heures, minute=minutes, second=0, microsecond=0)
    if cible <= depart:
        cible += timedelta(days=1)
    return cible


def charger_queue(chemin=None):
    chemin = chemin or FICHIER_QUEUE
    donnees = json.loads(Path(chemin).read_text(encoding="utf-8"))
    if isinstance(donnees, list):
        donnees = {"taches": donnees}
    donnees.setdefault("butoir", BUTOIR_DEFAUT)
    donnees.setdefault("taches", [])
    for tache in donnees["taches"]:
        tache.setdefault("statut", "en_attente")
        tache.setdefault("tentatives", 0)
        tache.setdefault("historique", [])
    return donnees


def sauver_queue(donnees, chemin=None):
    chemin = chemin or FICHIER_QUEUE
    Path(chemin).write_text(
        json.dumps(donnees, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def reprendre_apres_crash(donnees):
    interrompues = []
    for tache in donnees["taches"]:
        if tache["statut"] == "en_cours":
            tache["statut"] = "echouee"
            tache["raison"] = "interrompue"
            tache["detail"] = (
                "Run en cours lors d'un arret precedent. Non rejoue "
                "automatiquement : l'etat du depot peut etre partiel."
            )
            interrompues.append(tache["id"])
    return interrompues


def construire_commande(tache):
    outils = tache.get("outils") or OUTILS_DEFAUT
    bash_autorise = tache.get("bash_autorise")
    if bash_autorise is None:
        bash_autorise = BASH_AUTORISE_DEFAUT if "Bash" in outils else []
    commande = [
        "claude",
        "-p",
        tache["prompt"],
        "--restricted",
        "--permission-prompts",
        "none",
        "--output-format",
        "json",
        "--model",
        tache.get("modele", MODELE_DEFAUT),
        "--max-budget-usd",
        str(tache.get("budget_usd", BUDGET_DEFAUT)),
        "--tools",
    ]
    commande.extend(outils)
    if bash_autorise:
        commande.append("--allowedTools")
        commande.extend(bash_autorise)
    bash_interdit = tache.get("bash_interdit")
    if bash_interdit is None:
        bash_interdit = BASH_INTERDIT_DEFAUT if "Bash" in outils else []
    if bash_interdit:
        commande.append("--disallowedTools")
        commande.extend(bash_interdit)
    return commande


def est_erreur_quota(payload, stdout, stderr):
    if payload:
        if payload.get("api_error_status") in (429, "429"):
            return True
        for champ in ("subtype", "terminal_reason", "stop_reason"):
            valeur = payload.get(champ)
            if isinstance(valeur, str) and re.search(r"limit|quota", valeur, re.I):
                return True
        message = payload.get("result")
        if isinstance(message, str) and MOTIFS_QUOTA.search(message):
            return True
    return bool(MOTIFS_QUOTA.search(stderr or "")) or bool(
        MOTIFS_QUOTA.search(stdout or "")
    )


def classer_resultat(code_retour, stdout, stderr, timeout_atteint):
    resultat = {
        "statut": "echouee",
        "raison": "inconnue",
        "detail": "",
        "cout_usd": None,
        "duree_ms": None,
        "refus": [],
    }
    if timeout_atteint:
        resultat["raison"] = "timeout"
        resultat["detail"] = "Delai wall-clock depasse, process tue."
        return resultat

    payload = None
    if stdout:
        try:
            payload = json.loads(stdout)
        except (ValueError, TypeError):
            payload = None

    if payload:
        resultat["cout_usd"] = payload.get("total_cost_usd")
        resultat["duree_ms"] = payload.get("duration_ms")
        resultat["refus"] = payload.get("permission_denials") or []

    if est_erreur_quota(payload, stdout, stderr):
        resultat["raison"] = "quota"
        resultat["detail"] = "Limite d'usage atteinte."
        return resultat

    if payload is None:
        resultat["raison"] = "sortie_illisible"
        resultat["detail"] = "Sortie JSON absente ou non parsable (exit {}).".format(
            code_retour
        )
        return resultat

    if payload.get("is_error"):
        sous_type = payload.get("subtype") or ""
        if sous_type == "error_max_budget_usd":
            resultat["raison"] = "budget"
            resultat["detail"] = "Plafond --max-budget-usd atteint."
        else:
            resultat["raison"] = sous_type or "erreur_run"
            resultat["detail"] = str(payload.get("result") or "")[:500]
        return resultat

    if resultat["refus"]:
        resultat["statut"] = "refus"
        resultat["raison"] = "outils_refuses"
        noms = sorted({r.get("tool_name", "?") for r in resultat["refus"]})
        resultat["detail"] = (
            "Le run s'est termine sans erreur mais {} appel(s) d'outil ont ete "
            "refuses ({}). Resultat non fiable.".format(
                len(resultat["refus"]), ", ".join(noms)
            )
        )
        return resultat

    resultat["statut"] = "faite"
    resultat["raison"] = "succes"
    resultat["detail"] = str(payload.get("result") or "")[:2000]
    return resultat


def _tuer_arbre(proc):
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
            capture_output=True,
        )
    else:
        proc.kill()


def ecrire_log(tache, tentative, commande, code_retour, stdout, stderr):
    DOSSIER_LOGS.mkdir(exist_ok=True)
    chemin = DOSSIER_LOGS / "{}_{}.log".format(tache["id"], tentative)
    contenu = [
        "date        : {}".format(datetime.now().isoformat(timespec="seconds")),
        "dossier     : {}".format(tache["dossier"]),
        "commande    : {}".format(json.dumps(commande, ensure_ascii=False)),
        "code_retour : {}".format(code_retour),
        "",
        "--- stdout ---",
        stdout or "",
        "",
        "--- stderr ---",
        stderr or "",
    ]
    chemin.write_text("\n".join(contenu), encoding="utf-8")
    return chemin


def lancer(tache, tentative):
    commande = construire_commande(tache)
    timeout_s = float(tache.get("timeout_min", TIMEOUT_DEFAUT_MIN)) * 60
    debut = time.monotonic()
    timeout_atteint = False
    proc = subprocess.Popen(
        commande,
        cwd=tache["dossier"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    try:
        stdout, stderr = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        timeout_atteint = True
        _tuer_arbre(proc)
        stdout, stderr = proc.communicate()
    duree_s = round(time.monotonic() - debut, 1)
    chemin_log = ecrire_log(
        tache, tentative, commande, proc.returncode, stdout, stderr
    )
    resultat = classer_resultat(proc.returncode, stdout, stderr, timeout_atteint)
    resultat["duree_s"] = duree_s
    resultat["log"] = str(chemin_log)
    resultat["code_retour"] = proc.returncode
    return resultat


def appliquer_resultat(tache, resultat):
    tache["tentatives"] += 1
    tache["historique"].append(
        {
            "date": datetime.now().isoformat(timespec="seconds"),
            "raison": resultat["raison"],
            "duree_s": resultat.get("duree_s"),
            "cout_usd": resultat.get("cout_usd"),
            "log": resultat.get("log"),
        }
    )
    tache["log"] = resultat.get("log")
    tache["duree_s"] = resultat.get("duree_s")
    tache["cout_usd"] = resultat.get("cout_usd")
    tache["raison"] = resultat["raison"]
    tache["detail"] = resultat["detail"]
    tache["refus"] = resultat.get("refus") or []
    if resultat["raison"] == "quota":
        tache["statut"] = "en_attente"
    else:
        tache["statut"] = resultat["statut"]


def tache_prete(tache, maintenant, depart):
    if tache["statut"] != "en_attente":
        return True
    heure_min = tache.get("heure_min")
    if not heure_min:
        return True
    return maintenant >= heure_cible(depart, heure_min)


def dormir(secondes, butoir):
    restant = (butoir - datetime.now()).total_seconds()
    delai = max(0, min(secondes, restant))
    if delai > 0:
        time.sleep(delai)
    return delai


def executer(donnees, depart=None):
    depart = depart or datetime.now()
    butoir = heure_cible(depart, donnees.get("butoir", BUTOIR_DEFAUT))
    allowlist = charger_allowlist()
    attente_cumulee = 0

    interrompues = reprendre_apres_crash(donnees)
    for identifiant in interrompues:
        journal("tache {} : marquee interrompue (arret precedent)".format(identifiant))
    if interrompues:
        sauver_queue(donnees)

    for tache in donnees["taches"]:
        if tache["statut"] == "en_attente" and not dossier_autorise(
            tache.get("dossier"), allowlist
        ):
            tache["statut"] = "echouee"
            tache["raison"] = "hors_allowlist"
            tache["detail"] = "Dossier absent de allowlist.txt, inexistant ou invalide."
            journal("tache {} : refusee (hors allowlist)".format(tache["id"]))
    sauver_queue(donnees)

    while datetime.now() < butoir:
        en_attente = [t for t in donnees["taches"] if t["statut"] == "en_attente"]
        if not en_attente:
            break
        maintenant = datetime.now()
        pretes = [t for t in en_attente if tache_prete(t, maintenant, depart)]
        if not pretes:
            prochaines = [
                heure_cible(depart, t["heure_min"])
                for t in en_attente
                if t.get("heure_min")
            ]
            if not prochaines:
                break
            delai = (min(prochaines) - maintenant).total_seconds()
            journal("aucune tache prete, attente de {} min".format(int(delai / 60) + 1))
            attente_cumulee += dormir(delai + 1, butoir)
            continue

        tache = pretes[0]
        tache["statut"] = "en_cours"
        sauver_queue(donnees)
        journal(
            "tache {} : lancement (tentative {})".format(
                tache["id"], tache["tentatives"] + 1
            )
        )
        resultat = lancer(tache, tache["tentatives"] + 1)
        appliquer_resultat(tache, resultat)
        sauver_queue(donnees)
        journal("tache {} : {} ({})".format(tache["id"], tache["statut"], tache["raison"]))

        if resultat["raison"] == "quota":
            journal("quota atteint, nouvelle tentative dans {} min".format(RETRY_QUOTA_MIN))
            attente_cumulee += dormir(RETRY_QUOTA_MIN * 60, butoir)

    for tache in donnees["taches"]:
        if tache["statut"] in ("en_attente", "en_cours"):
            tache["statut"] = "reportee"
            tache.setdefault("raison", "butoir")
            tache.setdefault("detail", "Butoir atteint avant execution.")
    sauver_queue(donnees)

    return {
        "debut": depart,
        "fin": datetime.now(),
        "butoir": butoir,
        "attente_cumulee_s": int(attente_cumulee),
    }


def main():
    if not FICHIER_QUEUE.exists():
        journal("queue.json introuvable")
        return 1
    donnees = charger_queue()
    meta = executer(donnees)
    chemin = rapport.generer(donnees, meta, RACINE)
    journal("rapport : {}".format(chemin))
    if "--no-push" not in sys.argv:
        envoye, detail = notifier.notifier(donnees, meta, chemin)
        journal(
            "push com_telephone : {}".format("ok" if envoye else "indisponible ({})".format(detail))
        )
    if "--no-open" not in sys.argv and os.name == "nt":
        os.startfile(str(chemin))
    return 0


if __name__ == "__main__":
    sys.exit(main())

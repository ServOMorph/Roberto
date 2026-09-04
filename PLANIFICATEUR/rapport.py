import html
from datetime import datetime
from pathlib import Path

LIBELLES = {
    "faite": "Faite",
    "refus": "Outils refuses",
    "echouee": "Echouee",
    "reportee": "Reportee",
    "en_attente": "En attente",
    "en_cours": "En cours",
}

CSS = """
:root { --bg:#08110f; --surface:#101e1a; --line:#29443c; --text:#d8e5df;
        --muted:#9ab1a7; --accent:#7de7b8; --accent-dark:#082117;
        --alerte:#e77d7d; --tiede:#e7d17d; }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--text);
       font-family:Arial, sans-serif; line-height:1.55; }
.wrap { width:min(1120px, calc(100% - 40px)); margin:0 auto; padding:60px 0 80px; }
.eyebrow { color:var(--accent); font-size:.78rem; font-weight:700;
           letter-spacing:.12em; text-transform:uppercase; }
h1,h2 { line-height:1.05; letter-spacing:-.045em; }
h1 { margin:14px 0 10px; font-size:clamp(2.2rem, 6vw, 4rem); }
h2 { margin:56px 0 20px; font-size:clamp(1.5rem, 3vw, 2.2rem); }
.lead { color:var(--muted); font-size:1.1rem; margin:0; }
.cards { display:grid; grid-template-columns:repeat(4, 1fr); gap:20px; margin-top:40px; }
.cards article { padding:22px 24px; border:1px solid var(--line); border-radius:4px;
                 background:var(--surface); }
.cards .valeur { font-size:2.4rem; font-weight:800; letter-spacing:-.045em; }
.cards .etiquette { color:var(--muted); font-size:.85rem; }
.meta { margin-top:26px; color:var(--muted); font-size:.92rem; }
.meta span { margin-right:26px; white-space:nowrap; }
table { width:100%; border-collapse:collapse; margin-top:10px; font-size:.93rem; }
th { text-align:left; padding:10px 12px; border-bottom:1px solid var(--line);
     color:var(--muted); font-size:.78rem; letter-spacing:.12em; text-transform:uppercase; }
td { padding:14px 12px; border-bottom:1px solid var(--line); vertical-align:top; }
tr:last-child td { border-bottom:none; }
.pastille { display:inline-block; padding:3px 10px; border-radius:4px;
            font-size:.78rem; font-weight:700; letter-spacing:.06em;
            text-transform:uppercase; white-space:nowrap; }
.s-faite { background:var(--accent); color:var(--accent-dark); }
.s-refus { background:var(--tiede); color:var(--accent-dark); }
.s-echouee { background:var(--alerte); color:var(--accent-dark); }
.s-reportee { background:transparent; border:1px solid var(--line); color:var(--muted); }
.prompt { color:var(--text); }
.chemin { color:var(--muted); font-size:.85rem; word-break:break-all; }
.detail { margin-top:8px; color:var(--muted); font-size:.87rem;
          white-space:pre-wrap; word-break:break-word; }
.alerte { margin-top:8px; padding:12px 14px; border-left:3px solid var(--tiede);
          background:var(--surface); color:var(--text); font-size:.87rem; }
.vide { color:var(--muted); }
footer { margin-top:70px; padding-top:26px; border-top:1px solid var(--line);
         color:var(--muted); font-size:.9rem; }
@media (max-width:760px) { .cards { grid-template-columns:1fr 1fr; } table, tbody, tr, td { display:block; } th { display:none; } td { border-bottom:none; } tr { border-bottom:1px solid var(--line); padding:10px 0; } }
"""


def _duree(secondes):
    if secondes is None:
        return "-"
    secondes = int(secondes)
    if secondes < 60:
        return "{} s".format(secondes)
    return "{} min {:02d} s".format(secondes // 60, secondes % 60)


def _cout(valeur):
    if valeur is None:
        return "-"
    return "{:.4f} $".format(valeur)


def _ligne(tache):
    statut = tache.get("statut", "en_attente")
    prompt = tache.get("prompt", "")
    if len(prompt) > 220:
        prompt = prompt[:220] + "..."
    cellules = [
        "<td><span class='pastille s-{}'>{}</span></td>".format(
            html.escape(statut), html.escape(LIBELLES.get(statut, statut))
        ),
        "<td><strong>{}</strong><div class='chemin'>{}</div></td>".format(
            html.escape(str(tache.get("id", "?"))),
            html.escape(str(tache.get("dossier", ""))),
        ),
        "<td><div class='prompt'>{}</div>{}</td>".format(
            html.escape(prompt), _bloc_detail(tache)
        ),
        "<td>{}</td>".format(html.escape(str(tache.get("modele", "-")))),
        "<td>{}</td>".format(_duree(tache.get("duree_s"))),
        "<td>{}</td>".format(_cout(tache.get("cout_usd"))),
        "<td>{}</td>".format(tache.get("tentatives", 0)),
        "<td>{}</td>".format(_lien_log(tache)),
    ]
    return "<tr>{}</tr>".format("".join(cellules))


def _bloc_detail(tache):
    blocs = []
    refus = tache.get("refus") or []
    if refus:
        noms = ", ".join(sorted({r.get("tool_name", "?") for r in refus}))
        blocs.append(
            "<div class='alerte'>{} appel(s) d'outil refuses : {}. "
            "Le run s'est termine sans erreur mais n'a pas pu agir.</div>".format(
                len(refus), html.escape(noms)
            )
        )
    detail = tache.get("detail")
    if detail:
        etiquette = tache.get("raison", "")
        blocs.append(
            "<div class='detail'>{}{}</div>".format(
                "[{}] ".format(html.escape(str(etiquette))) if etiquette else "",
                html.escape(str(detail)),
            )
        )
    return "".join(blocs)


def _lien_log(tache):
    chemin = tache.get("log")
    if not chemin:
        return "<span class='vide'>-</span>"
    return "<a href='{}'>log</a>".format(html.escape(Path(chemin).as_uri()))


def generer(donnees, meta, dossier_sortie):
    taches = donnees.get("taches", [])
    compteurs = {cle: 0 for cle in ("faite", "refus", "echouee", "reportee")}
    for tache in taches:
        statut = tache.get("statut")
        if statut in compteurs:
            compteurs[statut] += 1
    cout_total = sum(t.get("cout_usd") or 0 for t in taches)

    cartes = [
        ("Faites", compteurs["faite"]),
        ("Outils refuses", compteurs["refus"]),
        ("Echouees", compteurs["echouee"]),
        ("Reportees", compteurs["reportee"]),
    ]
    html_cartes = "".join(
        "<article><div class='valeur'>{}</div>"
        "<div class='etiquette'>{}</div></article>".format(valeur, etiquette)
        for etiquette, valeur in cartes
    )

    entetes = [
        "Statut",
        "Tache",
        "Prompt / resultat",
        "Modele",
        "Duree",
        "Cout",
        "Tent.",
        "Log",
    ]
    html_entetes = "".join("<th>{}</th>".format(e) for e in entetes)
    html_lignes = "".join(_ligne(t) for t in taches) or (
        "<tr><td colspan='8' class='vide'>Aucune tache dans la file.</td></tr>"
    )

    debut = meta["debut"]
    fin = meta["fin"]
    page = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rapport nocturne {date}</title>
<style>{css}</style>
</head>
<body>
<div class="wrap">
  <div class="eyebrow">Planificateur nocturne</div>
  <h1>Rapport du {date}</h1>
  <p class="lead">{total} tache(s) dans la file, cout total {cout}.</p>
  <div class="cards">{cartes}</div>
  <div class="meta">
    <span>Debut {debut}</span>
    <span>Fin {fin}</span>
    <span>Duree totale {duree}</span>
    <span>Butoir {butoir}</span>
    <span>Attente cumulee {attente}</span>
  </div>
  <h2>Detail des taches</h2>
  <table>
    <thead><tr>{entetes}</tr></thead>
    <tbody>{lignes}</tbody>
  </table>
  <footer>Genere le {genere}. Un statut "Outils refuses" signale un run termine
  sans erreur mais dont les actions ont ete bloquees : le resultat n'est pas fiable.</footer>
</div>
</body>
</html>
""".format(
        css=CSS,
        date=debut.strftime("%d/%m/%Y"),
        total=len(taches),
        cout=_cout(cout_total),
        cartes=html_cartes,
        debut=debut.strftime("%H:%M"),
        fin=fin.strftime("%H:%M"),
        duree=_duree((fin - debut).total_seconds()),
        butoir=meta["butoir"].strftime("%H:%M"),
        attente=_duree(meta.get("attente_cumulee_s")),
        entetes=html_entetes,
        lignes=html_lignes,
        genere=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    )

    chemin = Path(dossier_sortie) / "rapport_{}.html".format(
        debut.strftime("%Y-%m-%d")
    )
    chemin.write_text(page, encoding="utf-8")
    return chemin

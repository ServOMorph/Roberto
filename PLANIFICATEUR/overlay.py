import tkinter as tk
from tkinter import scrolledtext

BG = "#08110f"
SURFACE = "#101e1a"
LINE = "#29443c"
TEXTE = "#d8e5df"
MUTED = "#9ab1a7"
ACCENT = "#7de7b8"
ACCENT_DARK = "#082117"

LIBELLES_STATUT = {
    "faite": "Faite",
    "refus": "Outils refuses",
    "echouee": "Echouee",
    "reportee": "Reportee",
    "en_attente": "En attente",
    "en_cours": "En cours",
}


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


def _fenetre_pleine_page(titre):
    fenetre = tk.Tk()
    fenetre.title(titre)
    fenetre.configure(bg=BG)
    fenetre.attributes("-fullscreen", True)
    fenetre.attributes("-topmost", True)
    fenetre.bind("<Escape>", lambda _evenement: fenetre.destroy())
    return fenetre


def _zone_texte(parent):
    zone = scrolledtext.ScrolledText(
        parent,
        bg=SURFACE,
        fg=TEXTE,
        insertbackground=TEXTE,
        relief="flat",
        borderwidth=0,
        font=("Consolas", 11),
        wrap="word",
    )
    zone.tag_configure("titre_tache", foreground=ACCENT, font=("Consolas", 11, "bold"))
    zone.tag_configure("muted", foreground=MUTED)
    return zone


def _bouton(parent, texte, commande):
    return tk.Button(
        parent,
        text=texte,
        command=commande,
        bg=ACCENT,
        fg=ACCENT_DARK,
        activebackground=SURFACE,
        activeforeground=ACCENT,
        relief="flat",
        font=("Arial", 13, "bold"),
        padx=36,
        pady=12,
        cursor="hand2",
    )


def afficher_annonce(donnees, butoir):
    taches = donnees.get("taches", [])

    fenetre = _fenetre_pleine_page("Planificateur nocturne")

    tk.Label(
        fenetre, text="PLANIFICATEUR NOCTURNE", bg=BG, fg=ACCENT,
        font=("Arial", 14, "bold"),
    ).pack(pady=(50, 4))
    tk.Label(
        fenetre, text="Lancement du test", bg=BG, fg=TEXTE,
        font=("Arial", 30, "bold"),
    ).pack(pady=(0, 16))
    tk.Label(
        fenetre,
        text=(
            "{} tache(s) en file. Butoir : {}. "
            "Confinement --restricted, aucun git push, commits locaux uniquement."
        ).format(len(taches), butoir.strftime("%H:%M")),
        bg=BG, fg=MUTED, font=("Arial", 13),
    ).pack(pady=(0, 24))

    zone = _zone_texte(fenetre)
    zone.pack(fill="both", expand=True, padx=120, pady=(0, 24))
    for tache in taches:
        zone.insert("end", "{}\n".format(tache.get("id", "?")), "titre_tache")
        zone.insert(
            "end",
            "  dossier : {}\n".format(tache.get("dossier", "")),
            "muted",
        )
        if tache.get("heure_min"):
            zone.insert(
                "end",
                "  pas avant : {}\n".format(tache["heure_min"]),
                "muted",
            )
        prompt = tache.get("prompt", "")
        if len(prompt) > 300:
            prompt = prompt[:300] + "..."
        zone.insert("end", "  {}\n\n".format(prompt))
    zone.configure(state="disabled")

    tk.Label(
        fenetre,
        text="Le lancement demarre l'orchestrateur PLANIFICATEUR/orchestrateur.py.",
        bg=BG, fg=MUTED, font=("Arial", 11),
    ).pack(pady=(0, 12))

    _bouton(fenetre, "OK - Lancer le test", fenetre.destroy).pack(pady=(0, 50))

    fenetre.mainloop()


def afficher_fin(donnees, meta):
    taches = donnees.get("taches", [])
    compteurs = {cle: 0 for cle in ("faite", "refus", "echouee", "reportee")}
    for tache in taches:
        statut = tache.get("statut")
        if statut in compteurs:
            compteurs[statut] += 1
    cout_total = sum(t.get("cout_usd") or 0 for t in taches)
    duree_totale = (meta["fin"] - meta["debut"]).total_seconds()

    fenetre = _fenetre_pleine_page("Planificateur nocturne - Termine")

    tk.Label(
        fenetre, text="PLANIFICATEUR NOCTURNE", bg=BG, fg=ACCENT,
        font=("Arial", 14, "bold"),
    ).pack(pady=(50, 4))
    tk.Label(
        fenetre, text="Test termine", bg=BG, fg=TEXTE,
        font=("Arial", 30, "bold"),
    ).pack(pady=(0, 16))
    tk.Label(
        fenetre,
        text=(
            "Faites {} / Outils refuses {} / Echouees {} / Reportees {} - "
            "duree totale {} - cout total {}"
        ).format(
            compteurs["faite"], compteurs["refus"], compteurs["echouee"],
            compteurs["reportee"], _duree(duree_totale), _cout(cout_total),
        ),
        bg=BG, fg=MUTED, font=("Arial", 13),
    ).pack(pady=(0, 24))

    zone = _zone_texte(fenetre)
    zone.pack(fill="both", expand=True, padx=120, pady=(0, 24))
    for tache in taches:
        statut = tache.get("statut", "?")
        zone.insert(
            "end",
            "{} - {}\n".format(
                tache.get("id", "?"), LIBELLES_STATUT.get(statut, statut)
            ),
            "titre_tache",
        )
        zone.insert(
            "end",
            "  raison : {} - duree {} - cout {} - tentatives {}\n".format(
                tache.get("raison", "-"),
                _duree(tache.get("duree_s")),
                _cout(tache.get("cout_usd")),
                tache.get("tentatives", 0),
            ),
            "muted",
        )
        detail = tache.get("detail")
        if detail:
            detail_court = str(detail)
            if len(detail_court) > 400:
                detail_court = detail_court[:400] + "..."
            zone.insert("end", "  {}\n".format(detail_court))
        if tache.get("log"):
            zone.insert("end", "  log : {}\n".format(tache["log"]), "muted")
        zone.insert("end", "\n")
    zone.configure(state="disabled")

    _bouton(fenetre, "Fermer", fenetre.destroy).pack(pady=(0, 50))

    fenetre.mainloop()

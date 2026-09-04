import json
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import notifier
import orchestrateur
import rapport
import tache


class TestAllowlist(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.autorise = self.base / "projet_ok"
        self.autorise.mkdir()
        (self.autorise / "sous").mkdir()
        self.interdit = self.base / "projet_ko"
        self.interdit.mkdir()
        self.fichier = self.base / "allowlist.txt"
        self.fichier.write_text(
            "# commentaire\n\n{}\n".format(self.autorise), encoding="utf-8"
        )
        self.liste = orchestrateur.charger_allowlist(self.fichier)

    def tearDown(self):
        self.tmp.cleanup()

    def test_commentaires_et_lignes_vides_ignores(self):
        self.assertEqual(self.liste, [self.autorise])

    def test_dossier_liste_accepte(self):
        self.assertTrue(orchestrateur.dossier_autorise(str(self.autorise), self.liste))

    def test_sous_dossier_accepte(self):
        self.assertTrue(
            orchestrateur.dossier_autorise(str(self.autorise / "sous"), self.liste)
        )

    def test_dossier_hors_liste_refuse(self):
        self.assertFalse(orchestrateur.dossier_autorise(str(self.interdit), self.liste))

    def test_traversee_refusee(self):
        chemin = str(self.autorise / ".." / "projet_ko")
        self.assertFalse(orchestrateur.dossier_autorise(chemin, self.liste))

    def test_dossier_inexistant_refuse(self):
        self.assertFalse(
            orchestrateur.dossier_autorise(str(self.base / "absent"), self.liste)
        )

    def test_valeurs_vides_refusees(self):
        self.assertFalse(orchestrateur.dossier_autorise("", self.liste))
        self.assertFalse(orchestrateur.dossier_autorise(None, self.liste))

    def test_fichier_absent_donne_liste_vide(self):
        vide = orchestrateur.charger_allowlist(self.base / "absent.txt")
        self.assertEqual(vide, [])
        self.assertFalse(orchestrateur.dossier_autorise(str(self.autorise), vide))


class TestHeureCible(unittest.TestCase):
    def test_heure_a_venir_le_meme_jour(self):
        depart = datetime(2026, 9, 3, 23, 0)
        self.assertEqual(
            orchestrateur.heure_cible(depart, "23:30"), datetime(2026, 9, 3, 23, 30)
        )

    def test_heure_passee_bascule_au_lendemain(self):
        depart = datetime(2026, 9, 3, 23, 0)
        self.assertEqual(
            orchestrateur.heure_cible(depart, "06:00"), datetime(2026, 9, 4, 6, 0)
        )

    def test_heure_egale_bascule_au_lendemain(self):
        depart = datetime(2026, 9, 3, 6, 0)
        self.assertEqual(
            orchestrateur.heure_cible(depart, "06:00"), datetime(2026, 9, 4, 6, 0)
        )


class TestCommande(unittest.TestCase):
    def test_flags_de_confinement_presents(self):
        cmd = orchestrateur.construire_commande(
            {"prompt": "p", "dossier": "d", "id": "t"}
        )
        self.assertIn("--restricted", cmd)
        self.assertIn("--output-format", cmd)
        self.assertEqual(cmd[cmd.index("--output-format") + 1], "json")
        self.assertEqual(cmd[cmd.index("--permission-prompts") + 1], "none")

    def test_git_push_interdit_par_defaut(self):
        cmd = orchestrateur.construire_commande(
            {"prompt": "p", "dossier": "d", "id": "t"}
        )
        interdits = cmd[cmd.index("--disallowedTools") + 1 :]
        self.assertIn("Bash(git push:*)", interdits)

    def test_pas_de_bash_sans_outil_bash(self):
        cmd = orchestrateur.construire_commande(
            {"prompt": "p", "dossier": "d", "id": "t", "outils": ["Read", "Grep"]}
        )
        self.assertNotIn("--allowedTools", cmd)
        self.assertNotIn("--disallowedTools", cmd)


class TestClassement(unittest.TestCase):
    def test_succes(self):
        sortie = json.dumps(
            {
                "is_error": False,
                "subtype": "success",
                "result": "ok",
                "total_cost_usd": 0.01,
                "permission_denials": [],
            }
        )
        res = orchestrateur.classer_resultat(0, sortie, "", False)
        self.assertEqual(res["statut"], "faite")
        self.assertEqual(res["cout_usd"], 0.01)

    def test_refus_outils_malgre_is_error_faux(self):
        sortie = json.dumps(
            {
                "is_error": False,
                "subtype": "success",
                "result": "je n'ai pas pu",
                "permission_denials": [{"tool_name": "Write", "tool_input": {}}],
            }
        )
        res = orchestrateur.classer_resultat(0, sortie, "", False)
        self.assertEqual(res["statut"], "refus")
        self.assertEqual(res["raison"], "outils_refuses")

    def test_budget_epuise(self):
        sortie = json.dumps(
            {
                "is_error": True,
                "subtype": "error_max_budget_usd",
                "terminal_reason": "budget_exhausted",
            }
        )
        res = orchestrateur.classer_resultat(1, sortie, "", False)
        self.assertEqual(res["statut"], "echouee")
        self.assertEqual(res["raison"], "budget")

    def test_quota_via_status_429(self):
        sortie = json.dumps({"is_error": True, "api_error_status": 429})
        res = orchestrateur.classer_resultat(1, sortie, "", False)
        self.assertEqual(res["raison"], "quota")

    def test_quota_via_stderr(self):
        res = orchestrateur.classer_resultat(
            1, "", "Claude usage limit reached, resets at 3am", False
        )
        self.assertEqual(res["raison"], "quota")

    def test_timeout(self):
        res = orchestrateur.classer_resultat(None, "", "", True)
        self.assertEqual(res["raison"], "timeout")

    def test_sortie_illisible(self):
        res = orchestrateur.classer_resultat(1, "pas du json", "", False)
        self.assertEqual(res["raison"], "sortie_illisible")

    def test_erreur_generique(self):
        sortie = json.dumps(
            {"is_error": True, "subtype": "error_during_execution", "result": "boum"}
        )
        res = orchestrateur.classer_resultat(1, sortie, "", False)
        self.assertEqual(res["raison"], "error_during_execution")


class TestReprise(unittest.TestCase):
    def test_tache_en_cours_marquee_interrompue_sans_rejeu(self):
        donnees = {
            "taches": [
                {"id": "a", "statut": "en_cours", "tentatives": 1, "historique": []},
                {"id": "b", "statut": "faite", "tentatives": 1, "historique": []},
                {"id": "c", "statut": "en_attente", "tentatives": 0, "historique": []},
            ]
        }
        interrompues = orchestrateur.reprendre_apres_crash(donnees)
        self.assertEqual(interrompues, ["a"])
        self.assertEqual(donnees["taches"][0]["statut"], "echouee")
        self.assertEqual(donnees["taches"][0]["raison"], "interrompue")
        self.assertEqual(donnees["taches"][1]["statut"], "faite")
        self.assertEqual(donnees["taches"][2]["statut"], "en_attente")

    def test_persistance_aller_retour(self):
        with tempfile.TemporaryDirectory() as tmp:
            chemin = Path(tmp) / "queue.json"
            chemin.write_text(
                json.dumps(
                    {"taches": [{"id": "a", "dossier": "d", "prompt": "p"}]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            donnees = orchestrateur.charger_queue(chemin)
            self.assertEqual(donnees["taches"][0]["statut"], "en_attente")
            self.assertEqual(donnees["butoir"], "06:00")
            donnees["taches"][0]["statut"] = "faite"
            orchestrateur.sauver_queue(donnees, chemin)
            relu = orchestrateur.charger_queue(chemin)
            self.assertEqual(relu["taches"][0]["statut"], "faite")


class TestLiaisonTardive(unittest.TestCase):
    def test_ecriture_suit_le_fichier_courant(self):
        origine = orchestrateur.FICHIER_QUEUE
        with tempfile.TemporaryDirectory() as tmp:
            cible = Path(tmp) / "queue.json"
            orchestrateur.FICHIER_QUEUE = cible
            try:
                orchestrateur.sauver_queue({"taches": []})
            finally:
                orchestrateur.FICHIER_QUEUE = origine
            self.assertTrue(cible.exists())
        self.assertEqual(orchestrateur.FICHIER_QUEUE, origine)

    def test_allowlist_suit_le_fichier_courant(self):
        origine = orchestrateur.FICHIER_ALLOWLIST
        with tempfile.TemporaryDirectory() as tmp:
            cible = Path(tmp) / "allowlist.txt"
            cible.write_text(tmp, encoding="utf-8")
            orchestrateur.FICHIER_ALLOWLIST = cible
            try:
                liste = orchestrateur.charger_allowlist()
            finally:
                orchestrateur.FICHIER_ALLOWLIST = origine
            self.assertEqual(liste, [Path(tmp).resolve()])


class TestRapport(unittest.TestCase):
    def test_generation(self):
        donnees = {
            "taches": [
                {
                    "id": "audit",
                    "dossier": "D:\\projet",
                    "prompt": "fais l'audit",
                    "modele": "sonnet",
                    "statut": "faite",
                    "raison": "succes",
                    "detail": "termine",
                    "duree_s": 92,
                    "cout_usd": 0.12,
                    "tentatives": 1,
                },
                {
                    "id": "risque",
                    "dossier": "D:\\projet",
                    "prompt": "<script>alert(1)</script>",
                    "modele": "sonnet",
                    "statut": "refus",
                    "raison": "outils_refuses",
                    "detail": "bloque",
                    "refus": [{"tool_name": "Write"}],
                    "tentatives": 1,
                },
                {
                    "id": "reste",
                    "dossier": "D:\\projet",
                    "prompt": "plus tard",
                    "statut": "reportee",
                    "raison": "butoir",
                    "detail": "butoir atteint",
                    "tentatives": 0,
                },
            ]
        }
        meta = {
            "debut": datetime(2026, 9, 3, 23, 30),
            "fin": datetime(2026, 9, 4, 2, 15),
            "butoir": datetime(2026, 9, 4, 6, 0),
            "attente_cumulee_s": 1500,
        }
        with tempfile.TemporaryDirectory() as tmp:
            chemin = rapport.generer(donnees, meta, tmp)
            self.assertTrue(chemin.exists())
            contenu = chemin.read_text(encoding="utf-8")
        self.assertIn("rapport_2026-09-03.html", chemin.name)
        for identifiant in ("audit", "risque", "reste"):
            self.assertIn(identifiant, contenu)
        self.assertIn("s-refus", contenu)
        self.assertIn("appel(s) d'outil refuses", contenu)
        self.assertIn("#7de7b8", contenu)
        self.assertIn("0.1200 $", contenu)
        self.assertIn("1 min 32 s", contenu)
        self.assertNotIn("<script>alert(1)</script>", contenu)

    def test_file_vide(self):
        meta = {
            "debut": datetime(2026, 9, 3, 23, 0),
            "fin": datetime(2026, 9, 3, 23, 1),
            "butoir": datetime(2026, 9, 4, 6, 0),
            "attente_cumulee_s": 0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            chemin = rapport.generer({"taches": []}, meta, tmp)
            self.assertIn("Aucune tache", chemin.read_text(encoding="utf-8"))


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.projet = self.base / "projet"
        self.projet.mkdir()
        self.interdit = self.base / "ailleurs"
        self.interdit.mkdir()
        self.allowlist = self.base / "allowlist.txt"
        self.allowlist.write_text(str(self.projet), encoding="utf-8")
        self.queue = self.base / "queue.json"
        self.origine = orchestrateur.FICHIER_ALLOWLIST
        orchestrateur.FICHIER_ALLOWLIST = self.allowlist

    def tearDown(self):
        orchestrateur.FICHIER_ALLOWLIST = self.origine
        self.tmp.cleanup()

    def _run(self, *argv):
        return tache.executer(["--queue", str(self.queue), *argv])

    def test_ajout_valide(self):
        code, _ = self._run("add", "t1", str(self.projet), "fais un truc", "--budget", "0.5")
        self.assertEqual(code, 0)
        donnees = json.loads(self.queue.read_text(encoding="utf-8"))
        self.assertEqual(donnees["taches"][0]["id"], "t1")
        self.assertEqual(donnees["taches"][0]["budget_usd"], 0.5)
        self.assertEqual(donnees["taches"][0]["statut"], "en_attente")

    def test_ajout_hors_allowlist_refuse_sans_ecriture(self):
        code, message = self._run("add", "t1", str(self.interdit), "p")
        self.assertEqual(code, 1)
        self.assertIn("dossier refuse", message)
        self.assertFalse(self.queue.exists())

    def test_id_duplique_refuse(self):
        self._run("add", "t1", str(self.projet), "p")
        code, message = self._run("add", "t1", str(self.projet), "p")
        self.assertEqual(code, 1)
        self.assertIn("deja present", message)

    def test_suppression(self):
        self._run("add", "t1", str(self.projet), "p")
        self.assertEqual(self._run("rm", "t1")[0], 0)
        self.assertEqual(self._run("rm", "t1")[0], 1)

    def test_reset(self):
        self._run("add", "t1", str(self.projet), "p")
        donnees = orchestrateur.charger_queue(self.queue)
        donnees["taches"][0].update({"statut": "echouee", "tentatives": 3, "raison": "quota"})
        orchestrateur.sauver_queue(donnees, self.queue)
        code, _ = self._run("reset", "*")
        self.assertEqual(code, 0)
        relu = orchestrateur.charger_queue(self.queue)
        self.assertEqual(relu["taches"][0]["statut"], "en_attente")
        self.assertEqual(relu["taches"][0]["tentatives"], 0)
        self.assertNotIn("raison", relu["taches"][0])

    def test_liste(self):
        self._run("add", "t1", str(self.projet), "p", "--heure-min", "01:00")
        code, message = self._run("list")
        self.assertEqual(code, 0)
        self.assertIn("t1", message)
        self.assertIn("01:00", message)


class TestNotifier(unittest.TestCase):
    def test_resume(self):
        donnees = {
            "taches": [
                {"id": "a", "statut": "faite", "cout_usd": 0.2},
                {"id": "b", "statut": "echouee", "raison": "timeout"},
                {"id": "c", "statut": "reportee"},
            ]
        }
        meta = {
            "debut": datetime(2026, 9, 3, 23, 0),
            "fin": datetime(2026, 9, 4, 5, 0),
        }
        texte = notifier.resumer(donnees, meta, "C:\\rapport.html")
        self.assertIn("1 faite(s)", texte)
        self.assertIn("1 echouee(s)", texte)
        self.assertIn("1 reportee(s)", texte)
        self.assertIn("0.2000 $", texte)
        self.assertIn("b : timeout", texte)

    def test_bridge_injoignable_ne_leve_pas(self):
        envoye, detail = notifier.envoyer("test", url="http://127.0.0.1:1/send")
        self.assertFalse(envoye)
        self.assertIsInstance(detail, str)


if __name__ == "__main__":
    unittest.main(verbosity=2)

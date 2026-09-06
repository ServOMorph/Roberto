import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent))

import selection_projet


def creer_projet(base, nom, avec_git=True, avec_claude=True):
    dossier = base / nom
    dossier.mkdir()
    if avec_git:
        (dossier / ".git").mkdir()
    if avec_claude:
        (dossier / ".claude").mkdir()
    return dossier


class TestListerCandidats(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_garde_git_et_claude_seulement(self):
        complet = creer_projet(self.base, "complet")
        creer_projet(self.base, "sans_claude", avec_claude=False)
        creer_projet(self.base, "sans_git", avec_git=False)
        candidats = selection_projet.lister_candidats([self.base])
        self.assertEqual(candidats, [complet])

    def test_ignore_les_fichiers(self):
        (self.base / "fichier.txt").write_text("x", encoding="utf-8")
        self.assertEqual(selection_projet.lister_candidats([self.base]), [])

    def test_racine_absente_ignoree(self):
        absente = self.base / "absente"
        self.assertEqual(selection_projet.lister_candidats([absente]), [])


class TestFiltrerPertinents(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.projet = creer_projet(self.base, "projet")

    def tearDown(self):
        self.tmp.cleanup()

    @patch("selection_projet.epoch_dernier_commit")
    def test_projet_recent_conserve(self, mock_epoch):
        import time

        mock_epoch.return_value = time.time()
        pertinents = selection_projet.filtrer_pertinents([self.projet], seuil_jours=90)
        self.assertEqual(len(pertinents), 1)

    @patch("selection_projet.epoch_dernier_commit")
    def test_projet_ancien_exclu(self, mock_epoch):
        import time

        mock_epoch.return_value = time.time() - 200 * 86400
        pertinents = selection_projet.filtrer_pertinents([self.projet], seuil_jours=90)
        self.assertEqual(pertinents, [])


class TestEpochDernierCommit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.projet = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    @patch("selection_projet.subprocess.run")
    def test_lit_le_timestamp_git(self, mock_run):
        mock_run.return_value = MagicMock(stdout="1700000000\n")
        self.assertEqual(selection_projet.epoch_dernier_commit(self.projet), 1700000000.0)

    @patch("selection_projet.subprocess.run")
    def test_repli_sur_mtime_si_echec_git(self, mock_run):
        mock_run.side_effect = OSError("git absent")
        attendu = self.projet.stat().st_mtime
        self.assertEqual(selection_projet.epoch_dernier_commit(self.projet), attendu)

    @patch("selection_projet.subprocess.run")
    def test_repli_sur_mtime_si_sortie_vide(self, mock_run):
        mock_run.return_value = MagicMock(stdout="\n")
        attendu = self.projet.stat().st_mtime
        self.assertEqual(selection_projet.epoch_dernier_commit(self.projet), attendu)


class TestSuivi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.fichier = self.base / "suivi.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_fichier_absent_donne_structure_vide(self):
        self.assertEqual(selection_projet.charger_suivi(self.fichier), {"projets": {}})

    def test_sauvegarde_puis_relecture(self):
        suivi = {"projets": {"a": {"nom": "a"}}}
        selection_projet.sauvegarder_suivi(self.fichier, suivi)
        self.assertEqual(selection_projet.charger_suivi(self.fichier), suivi)


class TestClasser(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.jamais_review = creer_projet(self.base, "jamais_review")
        self.deja_review = creer_projet(self.base, "deja_review")

    def tearDown(self):
        self.tmp.cleanup()

    def test_jamais_review_prioritaire(self):
        pertinents = [(self.jamais_review, 100.0), (self.deja_review, 200.0)]
        suivi = {
            "projets": {
                selection_projet.normaliser_chemin(self.deja_review): {
                    "derniere_review": "2026-01-01"
                }
            }
        }
        lignes = selection_projet.classer(pertinents, suivi)
        self.assertEqual(lignes[0]["nom"], "jamais_review")
        self.assertTrue(lignes[0]["jamais_review"])
        self.assertFalse(lignes[1]["jamais_review"])

    def test_a_epoque_egale_review_la_plus_ancienne_dabord(self):
        autre_deja_review = creer_projet(self.base, "autre_deja_review")
        pertinents = [(self.deja_review, 100.0), (autre_deja_review, 100.0)]
        suivi = {
            "projets": {
                selection_projet.normaliser_chemin(self.deja_review): {
                    "derniere_review": "2026-05-01"
                },
                selection_projet.normaliser_chemin(autre_deja_review): {
                    "derniere_review": "2026-01-01"
                },
            }
        }
        lignes = selection_projet.classer(pertinents, suivi)
        self.assertEqual(lignes[0]["nom"], "autre_deja_review")


class TestMarquerReview(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.fichier = self.base / "suivi.json"
        self.projet = creer_projet(self.base, "projet")

    def tearDown(self):
        self.tmp.cleanup()

    def test_ajoute_une_entree(self):
        cle = selection_projet.marquer_review(
            self.projet, "max", "rien trouve", fichier_suivi=self.fichier, date="2026-09-06"
        )
        suivi = json.loads(self.fichier.read_text(encoding="utf-8"))
        self.assertEqual(
            suivi["projets"][cle],
            {
                "nom": "projet",
                "derniere_review": "2026-09-06",
                "niveau": "max",
                "resultat": "rien trouve",
            },
        )

    def test_dossier_absent_leve_erreur(self):
        with self.assertRaises(ValueError):
            selection_projet.marquer_review(
                self.base / "absent", "max", "", fichier_suivi=self.fichier
            )


if __name__ == "__main__":
    unittest.main()

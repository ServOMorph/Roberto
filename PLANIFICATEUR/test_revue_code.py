import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import revue_code


class TestChargerZones(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.fichier = self.base / "zones.md"

    def tearDown(self):
        self.tmp.cleanup()

    def _ecrire(self, contenu):
        self.fichier.write_text(contenu, encoding="utf-8")

    def test_table_markdown_parsee(self):
        self._ecrire(
            "# Zones\n\n"
            "| Alias | Dossier |\n"
            "|-------|---------|\n"
            "| roberto | D:\\ServOMorph\\Roberto |\n"
            "| creazik | D:\\ServOMorph\\creazik_v2 |\n"
        )
        zones = revue_code.charger_zones(self.fichier)
        self.assertEqual(
            zones,
            {"roberto": "D:\\ServOMorph\\Roberto", "creazik": "D:\\ServOMorph\\creazik_v2"},
        )

    def test_fichier_absent_donne_dict_vide(self):
        self.assertEqual(revue_code.charger_zones(self.base / "absent.md"), {})

    def test_ligne_hors_tableau_ignoree(self):
        self._ecrire("# Zones\n\nTexte libre non tabulaire.\n")
        self.assertEqual(revue_code.charger_zones(self.fichier), {})

    def test_alias_contenant_le_mot_alias_conserve(self):
        self._ecrire(
            "| Alias | Dossier |\n"
            "|-------|---------|\n"
            "| AliasBackup | D:\\Backups |\n"
        )
        zones = revue_code.charger_zones(self.fichier)
        self.assertEqual(zones, {"AliasBackup": "D:\\Backups"})


class TestResoudreCible(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.projet = self.base / "projet"
        self.projet.mkdir()
        self.zones = self.base / "zones.md"
        self.zones.write_text(
            "| Alias | Dossier |\n|-------|---------|\n| test | {} |\n".format(self.projet),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    def test_alias_connu_resolu(self):
        self.assertEqual(
            revue_code.resoudre_cible("test", self.zones), self.projet.resolve()
        )

    def test_chemin_direct_resolu(self):
        self.assertEqual(
            revue_code.resoudre_cible(str(self.projet), self.zones), self.projet.resolve()
        )

    def test_alias_et_chemin_inconnus_refuses(self):
        with self.assertRaises(ValueError):
            revue_code.resoudre_cible("inconnu", self.zones)


class TestConstruireCommande(unittest.TestCase):
    def test_niveau_max_dans_le_prompt(self):
        commande = revue_code.construire_commande("max")
        self.assertIn("/code-review max", commande)

    def test_restricted_present(self):
        self.assertIn("--restricted", revue_code.construire_commande("max"))

    def test_budget_par_defaut_transmis(self):
        commande = revue_code.construire_commande("max")
        idx = commande.index("--max-budget-usd")
        self.assertEqual(commande[idx + 1], str(revue_code.BUDGET_DEFAUT))

    def test_budget_personnalise_transmis(self):
        commande = revue_code.construire_commande("max", budget_usd=2.5)
        idx = commande.index("--max-budget-usd")
        self.assertEqual(commande[idx + 1], "2.5")

    def test_git_push_interdit(self):
        commande = revue_code.construire_commande("max")
        idx = commande.index("--disallowedTools")
        self.assertIn("Bash(git push:*)", commande[idx + 1 :])

    def test_write_edit_absents_des_outils(self):
        commande = revue_code.construire_commande("max")
        idx = commande.index("--tools")
        idx_fin = commande.index("--allowedTools")
        outils = commande[idx + 1 : idx_fin]
        self.assertNotIn("Write", outils)
        self.assertNotIn("Edit", outils)

    def test_niveau_ultra_refuse(self):
        with self.assertRaises(ValueError):
            revue_code.construire_commande("ultra")


class TestEcrireSortie(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()

    def tearDown(self):
        self.tmp.cleanup()

    def test_sortie_ecrite_dans_roberto(self):
        chemin = revue_code.ecrire_sortie(self.base, "max", 0, "stdout", "stderr", False)
        self.assertEqual(chemin.parent, self.base / "ROBERTO")
        self.assertTrue(chemin.exists())

    def test_aucune_ecriture_hors_roberto(self):
        avant = set(self.base.iterdir())
        revue_code.ecrire_sortie(self.base, "max", 0, "stdout", "stderr", False)
        apres = set(self.base.iterdir())
        self.assertEqual(apres - avant, {self.base / "ROBERTO"})


class TestExecuter(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.projet = self.base / "projet"
        self.projet.mkdir()
        self.zones = self.base / "zones.md"
        self.zones.write_text(
            "| Alias | Dossier |\n|-------|---------|\n| test | {} |\n".format(self.projet),
            encoding="utf-8",
        )

    def tearDown(self):
        self.tmp.cleanup()

    @patch("revue_code.lancer")
    def test_cible_inexistante_leve_avant_tout_lancement(self, mock_lancer):
        with self.assertRaises(ValueError):
            revue_code.executer("absent", chemin_zones=self.zones)
        mock_lancer.assert_not_called()

    @patch("revue_code.lancer", return_value=(0, '{"result": "ok"}', "", False))
    def test_alias_lance_et_ecrit_sortie(self, mock_lancer):
        chemin, code = revue_code.executer("test", chemin_zones=self.zones)
        self.assertEqual(code, 0)
        self.assertEqual(chemin.parent, self.projet / "ROBERTO")
        mock_lancer.assert_called_once()
        dossier_appele = mock_lancer.call_args[0][0]
        self.assertEqual(Path(dossier_appele), self.projet.resolve())


if __name__ == "__main__":
    unittest.main()

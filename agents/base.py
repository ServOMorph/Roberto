"""Description d'un agent pilotable par le pont Macrodesk.

Un agent est entièrement décrit par ce profil : le pont (`bridge/`) et les scripts
(`scripts/`) n'en connaissent rien d'autre. Ajouter un agent revient à écrire un module
qui expose un `AgentProfile` et à l'enregistrer dans `agents/__init__.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

CONTEXT_USED = "used"
CONTEXT_REMAINING = "remaining"


@dataclass(frozen=True)
class AgentProfile:
    key: str
    """Identifiant en minuscules, utilisé par --agent."""

    label: str
    """Nom lisible de l'agent, pour les messages et les manifestes."""

    send_macro: str
    """Nom exact de la macro Macrodesk qui colle le presse-papiers et envoie."""

    context_zone: str
    """Nom de la zone de surveillance OCR affichant le pourcentage de contexte."""

    context_metric: str = CONTEXT_USED
    """`used` : le pourcentage lu monte avec le remplissage. `remaining` : il descend."""

    compact_command: str = "/compact"
    """Commande à envoyer pour faire compacter le contexte de l'agent."""

    compact_ack: str = "COMPACT TERMINE"
    """Marqueur que l'agent doit écrire pour confirmer le compactage."""

    write_ack: str = "FICHIER ÉCRIT"
    """Marqueur de fin de réponse dans le chat, après écriture du fichier attendu."""

    def __post_init__(self) -> None:
        if self.context_metric not in (CONTEXT_USED, CONTEXT_REMAINING):
            raise ValueError(f"context_metric inconnu : {self.context_metric!r}")

    def context_exceeded(self, percent: int, threshold: int) -> bool:
        """Vrai quand le contexte lu impose un compactage avant d'envoyer un prompt."""
        if self.context_metric == CONTEXT_REMAINING:
            return percent <= threshold
        return percent >= threshold

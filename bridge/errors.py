"""Interruptions propres au pont Macrodesk <-> agent."""

from __future__ import annotations


class ContextLimitReached(RuntimeError):
    """Le contexte de l'agent impose un compactage avant tout nouvel envoi."""


class UserAbort(RuntimeError):
    """Levée quand l'utilisateur appuie sur Échap pendant une session de contrôle."""

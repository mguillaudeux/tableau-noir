"""Les enquêtes : des questions qui traversent tout le corpus, et des réponses chiffrées.

Chaque enquête a deux moitiés : les calculs (ici, testés, à partir du corpus) et le texte
(`data/enquetes/{slug}.py`, écrit à la main). À l'export, chaque nombre du texte est vérifié
contre les résultats des calculs, comme pour le coin de l'analyste.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from tableau_noir.enquetes import (
    clubs,
    formations,
    holdups,
    manques,
    messi,
    pertes,
    possession,
    pressing,
    temps,
)

Compute = Callable[..., dict[str, Any]]
# slug → (calcul, tables supplémentaires nécessaires, parmi "shapes", "losses" et "players")
REGISTRY: dict[str, tuple[Compute, tuple[str, ...]]] = {
    "pressing": (lambda c, s: pressing.compute(c), ()),
    "clubs": (clubs.compute, ()),
    "temps": (temps.compute, ()),
    "possession": (possession.compute, ()),
    "manques": (manques.compute, ()),
    "formations": (formations.compute, ("shapes", "players")),
    "pertes": (pertes.compute, ("losses",)),
    "messi": (messi.compute, ("players",)),
    "holdups": (holdups.compute, ()),
}

"""Les enquêtes : des questions qui traversent tout le corpus, et des réponses chiffrées.

Chaque enquête a deux moitiés : les calculs (ici, testés, à partir du corpus) et le texte
(`data/enquetes/{slug}.py`, écrit à la main). À l'export, chaque nombre du texte est vérifié
contre les résultats des calculs, comme pour le coin de l'analyste.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pandas as pd

from tableau_noir.enquetes import pressing

Compute = Callable[[pd.DataFrame], dict[str, Any]]
REGISTRY: dict[str, Compute] = {"pressing": pressing.compute}

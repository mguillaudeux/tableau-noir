"""Enquête n° 2 · Club et sélection : le même sport ?

Quatre championnats complets 2015/16 face aux tournois de sélections 2018–2024, même source de
données : ce qui ne change pas (les buts, les xG), ce qui change (les pertes de balle, les
transitions, le pressing, l'équilibre de la possession), et ce qui décide un match dans les deux.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from tableau_noir.enquetes.common import (
    LEAGUES_2015,
    OTHER_CONFEDS,
    TOURNAMENTS,
    by_competition,
    portrait,
)


def compute(corpus: pd.DataFrame, shots: pd.DataFrame | None = None) -> dict[str, Any]:
    sb = corpus[corpus["source"] == "statsbomb"]
    clubs = sb[sb["comp"].isin(LEAGUES_2015)]
    sels = sb[sb["comp"].isin(TOURNAMENTS + OTHER_CONFEDS)]
    euros = sb[sb["comp"].isin(TOURNAMENTS)]
    top = sb.sort_values("possession").iloc[-1]
    return {
        "possession_record": {
            "team": str(top["team"]),
            "opponent": str(top["opponent"]),
            "comp": str(top["comp"]),
            "possession_pct": int(round(100 * float(top["possession"]))),
            "score": f"{int(top['goals'])}-{int(top['goals_against'])}",
        },
        "club": portrait(clubs, shots),
        "selection": portrait(sels, shots),
        "selection_europe_americas": portrait(euros, shots),
        "selection_knockout": portrait(sels[sels["knockout"]], shots),
        "selection_groups": portrait(sels[~sels["knockout"]], shots),
        "leagues": by_competition(sb, LEAGUES_2015, shots),
        "tournaments": by_competition(sb, TOURNAMENTS + OTHER_CONFEDS, shots),
        "finals": portrait(sb[sb["comp"] == "ucl-finals"], shots),
    }

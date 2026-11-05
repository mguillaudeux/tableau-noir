"""Enquête n° 3 · 2004 → 2024 : ce qui a changé.

Trois séries qui se suivent dans le temps, chacune à source constante : les matchs du Barça en
Liga de 2004/05 à 2020/21 (un seul club, mais dix-sept saisons), les tournois de sélections de
2018 à 2024, et les championnats (2015/16 complets, puis un club dominant par saison).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.enquetes.common import (
    LEAGUES_2015,
    PTS,
    RECENT_CLUBS,
    TOURNAMENTS,
    _r,
    by_competition,
)


def dist(d: pd.DataFrame) -> float | None:
    return _r(float(np.hypot(105 - d["x"], 34 - d["y"]).mean()), 1) if len(d) else None


def barca_seasons(corpus: pd.DataFrame, shots: pd.DataFrame) -> list[dict[str, Any]]:
    b = corpus[corpus["comp"].isin(("liga-barca", "liga-2015"))].copy()
    b["pts"] = b["result"].map(PTS)
    out = []
    for season, g in b.groupby("season"):
        us = g[g["team"] == "Barcelona"]
        them = g[g["team"] != "Barcelona"]
        s = shots[
            shots["match_id"].isin(g["match_id"].unique()) & (shots["set_piece"] != "penalty")
        ]
        s_us = s[s["team"] == "Barcelona"]
        s_them = s[s["team"] != "Barcelona"]
        out.append(
            {
                "season": str(season),
                "year": int(str(season)[:4]) + 1,
                "n": int(us["match_id"].nunique()),
                "barca": {
                    "ppda": _r(us["ppda"].mean(), 1),
                    "counterpress_pct": _r(100 * us["counterpress"].mean(), 1),
                    "possession_pct": _r(100 * us["possession"].mean(), 1),
                    "short_pass_pct": _r(100 * us["short_share"].mean(), 1),
                    "goals": _r(us["goals"].mean()),
                    "xg": _r(us["xg"].mean()),
                    "pts": _r(us["pts"].mean()),
                    "shot_distance_m": dist(s_us),
                    "outside_box_pct": _r(100 * (s_us["x"] < 88.5).mean(), 1),
                    "losses": _r(us["losses"].mean(), 1),
                },
                "opponents": {
                    "ppda": _r(them["ppda"].mean(), 1),
                    "shot_distance_m": dist(s_them),
                    "outside_box_pct": _r(100 * (s_them["x"] < 88.5).mean(), 1),
                    "def_height_m": _r(them["def_height"].mean(), 1),
                },
            }
        )
    return out


def compute(corpus: pd.DataFrame, shots: pd.DataFrame | None = None) -> dict[str, Any]:
    assert shots is not None
    sb = corpus[corpus["source"] == "statsbomb"]
    bs = barca_seasons(sb, shots)
    first, last = bs[0], bs[-1]
    peak = max(bs, key=lambda x: x["barca"]["pts"] or 0)
    far = shots[
        (shots["set_piece"] != "penalty") & (np.hypot(105 - shots["x"], 34 - shots["y"]) >= 25)
    ]
    bshots = shots[
        shots["match_id"].isin(sb[sb["comp"].isin(("liga-barca", "liga-2015"))]["match_id"])
        & (shots["team"] == "Barcelona")
        & (shots["set_piece"] != "penalty")
    ]
    xg_per_shot_by_season = bshots.groupby("season")["xg"].mean()
    return {
        "barca": bs,
        "barca_matches": int(sum(b["n"] for b in bs)),
        "barca_xg_per_shot_min": _r(float(xg_per_shot_by_season.min())),
        "barca_xg_per_shot_max": _r(float(xg_per_shot_by_season.max())),
        "xg_of_shots_from_25m": _r(float(far["xg"].mean())),
        "barca_first": first,
        "barca_last": last,
        "barca_peak": peak,
        "tournaments": by_competition(sb, TOURNAMENTS, shots),
        "leagues_2015": by_competition(sb, LEAGUES_2015, shots),
        "recent_clubs": by_competition(sb, RECENT_CLUBS, shots),
    }

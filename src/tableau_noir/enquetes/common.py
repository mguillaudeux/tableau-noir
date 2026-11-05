"""Ce que plusieurs enquêtes partagent : les groupes de compétitions, et le portrait chiffré
d'un groupe de matchs (buts, xG, possession, pressing, transitions, tirs…)."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.enquetes.pressing import outcome, paired

PTS = {"W": 3, "D": 1, "L": 0}
LEAGUES_2015 = ("pl-2015", "liga-2015", "seriea-2015", "ligue1-2015")
TOURNAMENTS = ("wc-2018", "euro-2020", "wc-2022", "euro-2024")
OTHER_CONFEDS = ("copa-2024", "can-2023")
RECENT_CLUBS = ("ligue1-2021", "ligue1-2022", "bundesliga-2023")
LABELS = {
    "pl-2015": "Premier League 2015/16",
    "liga-2015": "La Liga 2015/16",
    "seriea-2015": "Serie A 2015/16",
    "ligue1-2015": "Ligue 1 2015/16",
    "bundesliga-2015": "Bundesliga 2015/16",
    "bundesliga-2023": "Bundesliga 2023/24",
    "ligue1-2021": "Ligue 1 2021/22",
    "ligue1-2022": "Ligue 1 2022/23",
    "wc-2018": "Coupe du monde 2018",
    "euro-2020": "Euro 2020",
    "wc-2022": "Coupe du monde 2022",
    "euro-2024": "Euro 2024",
    "copa-2024": "Copa América 2024",
    "can-2023": "CAN 2023",
    "ucl-finals": "Finales de LDC 2009–2019",
}


def _r(v: float, d: int = 2) -> float | None:
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), d)


def portrait(g: pd.DataFrame, shots: pd.DataFrame | None = None) -> dict[str, Any]:
    """Le portrait d'un ensemble de matchs (lignes équipe-match du corpus)."""
    if g.empty:
        return {}
    pm = g.groupby("match_id")
    p = paired(g)
    o_poss = outcome(p, "possession", True)
    o_xg = outcome(p, "xg", True)
    o_press = outcome(p, "ppda", False)
    ga = g["goals_against"].sum()
    xga = g["xg_against"].sum()
    out: dict[str, Any] = {
        "matches": int(g["match_id"].nunique()),
        "goals_per_match": _r(pm["goals"].sum().mean()),
        "xg_per_match": _r(pm["xg"].sum().mean()),
        "shots_per_match": _r(pm["shots"].sum().mean(), 1),
        "draws_pct": int(round(100 * (pm["result"].first() == "D").mean())),
        "possession_gap": _r(100 * (g["possession"] - 0.5).abs().mean(), 1),
        "possession_over_60_pct": int(round(100 * (g["possession"] > 0.6).mean())),
        "ppda": _r(g["ppda"].mean(), 1),
        "press_per_min": _r(g["press_per_min"].mean()),
        "counterpress_pct": _r(100 * g["counterpress"].mean(), 1),
        "short_pass_pct": _r(100 * g["short_share"].mean(), 1),
        "losses_per_team": _r(g["losses"].mean(), 1),
        "regain_5s_pct": _r(100 * g["regain_5s"].mean(), 1),
        "transition_goals_pct": _r(100 * g["tr_goals_against"].sum() / ga, 1) if ga else None,
        "transition_xg_pct": _r(100 * g["tr_xg_against"].sum() / xga, 1) if xga else None,
        "def_height_m": _r(g["def_height"].mean(), 1),
        "more_possession": {"win_pct": o_poss["win_pct"], "loss_pct": o_poss["loss_pct"]},
        "more_xg": {"win_pct": o_xg["win_pct"], "loss_pct": o_xg["loss_pct"]},
        "more_pressing": {"win_pct": o_press["win_pct"], "loss_pct": o_press["loss_pct"]},
    }
    if shots is not None:
        s = shots[shots["match_id"].isin(g["match_id"].unique())]
        s = s[s["set_piece"] != "penalty"]
        if len(s):
            dist = np.hypot(105 - s["x"], 34 - s["y"])
            out["shots"] = {
                "n": int(len(s)),
                "distance_m": _r(dist.mean(), 1),
                "outside_box_pct": _r(100 * (s["x"] < 88.5).mean(), 1),
                "xg_per_shot": _r(s["xg"].mean(), 3),
                "header_pct": _r(100 * (s["body"] == "head").mean(), 1),
                "conversion_pct": _r(100 * s["goal"].mean(), 1),
            }
    return out


def by_competition(
    corpus: pd.DataFrame, comps: tuple[str, ...], shots: pd.DataFrame | None = None
) -> list[dict[str, Any]]:
    out = []
    for c in comps:
        g = corpus[corpus["comp"] == c]
        if g.empty:
            continue
        out.append(
            {"comp": c, "label": LABELS.get(c, c), "year": int(g["year"].median())}
            | portrait(g, shots)
        )
    return out

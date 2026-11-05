"""Enquête n° 4 · La possession ne sert à rien (sauf au plus fort).

Avoir le ballon crée des occasions et en retire à l'adversaire, de façon parfaitement symétrique,
mais les points ne suivent pas : en championnat, la part de victoires est la même à 40 % et à
60 % de possession, et à force égale l'équipe qui a le ballon perd plus souvent. En sélection,
la possession « prédit » le résultat parce qu'elle appartient au plus fort.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.enquetes.common import LABELS, LEAGUES_2015, OTHER_CONFEDS, PTS, TOURNAMENTS, _r
from tableau_noir.enquetes.pressing import outcome, paired, strength_table, z

BANDS = [0, 0.4, 0.45, 0.5, 0.55, 0.6, 1.0]
BAND_LABELS = ["<40", "40-45", "45-50", "50-55", "55-60", ">60"]


def bands(g: pd.DataFrame) -> list[dict[str, Any]]:
    g = g.copy()
    g["pts"] = g["result"].map(PTS)
    g["band"] = pd.cut(g["possession"], BANDS, labels=BAND_LABELS)
    out = []
    for lab in BAND_LABELS:
        b = g[g["band"] == lab]
        out.append(
            {
                "band": lab,
                "n": int(len(b)),
                "win_pct": int(round(100 * (b["result"] == "W").mean())),
                "loss_pct": int(round(100 * (b["result"] == "L").mean())),
                "xg": _r(b["xg"].mean()),
                "xg_against": _r(b["xg_against"].mean()),
                "pts": _r(b["pts"].mean()),
            }
        )
    return out


def compute(corpus: pd.DataFrame, shots: pd.DataFrame | None = None) -> dict[str, Any]:
    sb = corpus[corpus["source"] == "statsbomb"]
    clubs = sb[sb["comp"].isin(LEAGUES_2015)]
    sels = sb[sb["comp"].isin(TOURNAMENTS + OTHER_CONFEDS)]
    m = strength_table(clubs)
    opp = clubs[["match_id", "team", "possession"]].rename(
        columns={"team": "opponent", "possession": "poss_o"}
    )
    m = m.merge(opp, on=["match_id", "opponent"])
    m["dposs"] = m["possession"] - m["poss_o"]
    eq = m[(m["dstr"].abs() < 0.3) & (m["dposs"] > 0.1)]
    fav = m[(m["dstr"] > 0.5) & (m["dposs"] > 0.1)]
    out_ = m[(m["dstr"] < -0.5) & (m["dposs"] > 0.1)]
    x1 = np.column_stack([np.ones(len(m)), z(m["dposs"])])
    x2 = np.column_stack([np.ones(len(m)), z(m["dposs"]), z(m["dstr"])])
    b1 = np.linalg.lstsq(x1, m["gd"].to_numpy(float), rcond=None)[0]
    b2 = np.linalg.lstsq(x2, m["gd"].to_numpy(float), rcond=None)[0]

    def win(g: pd.DataFrame) -> dict[str, Any]:
        return {
            "n": int(len(g)),
            "win_pct": int(round(100 * (g["result"] == "W").mean())),
            "loss_pct": int(round(100 * (g["result"] == "L").mean())),
        }

    by_comp = []
    for c in LEAGUES_2015 + TOURNAMENTS + OTHER_CONFEDS:
        g = sb[sb["comp"] == c]
        o = outcome(paired(g), "possession", True)
        by_comp.append({"comp": c, "label": LABELS[c], "year": int(g["year"].median())} | o)
    lost = sb[(sb["possession"] > 0.65) & (sb["result"] == "L")].sort_values(
        "possession", ascending=False
    )
    big = sb[sb["possession"] > 0.65]
    return {
        "clubs_matches": int(clubs["match_id"].nunique()),
        "clubs_rows": int(len(clubs)),
        "selections_rows": int(len(sels)),
        "selections_matches": int(sels["match_id"].nunique()),
        "bands_club": bands(clubs),
        "bands_selection": bands(sels),
        "corr_possession_xg_club": _r(clubs["possession"].corr(clubs["xg"])),
        "corr_possession_xg_selection": _r(sels["possession"].corr(sels["xg"])),
        "equal_strength": win(eq),
        "favourite": win(fav),
        "outsider": win(out_),
        "effect_alone": _r(b1[1]),
        "effect_with_strength": _r(b2[1]),
        "strength_effect": _r(b2[2]),
        "by_competition": by_comp,
        "over_65": win(big),
        "lost_with_the_ball": [
            {
                "comp": r["comp"],
                "label": LABELS.get(r["comp"], r["comp"]),
                "stage": r["stage"],
                "team": r["team"],
                "opponent": r["opponent"],
                "possession_pct": int(round(100 * r["possession"])),
                "score": f"{int(r['goals'])}-{int(r['goals_against'])}",
                "xg": _r(r["xg"]),
                "xg_against": _r(r["xg_against"]),
            }
            for _, r in lost.head(8).iterrows()
        ],
    }

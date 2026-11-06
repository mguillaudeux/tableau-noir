"""Enquête n° 9 · Les hold-up : quand les xG se trompent.

L'équipe qui a créé le moins d'occasions (en xG) gagne-t-elle souvent ? Selon l'écart d'xG, en
club et en sélection, en phase finale, et au fil du temps ; et les plus gros hold-up du corpus.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from tableau_noir.enquetes.common import LABELS, PTS, _r

BINS = [0.0, 0.25, 0.5, 1.0, 1.5, 2.0, 6.0]


def _rate(g: pd.DataFrame) -> dict[str, Any]:
    """Résultats de l'équipe qui a le moins d'xG (une ligne par match)."""
    n = int(len(g))
    if not n:
        return {"n": 0}
    return {
        "n": n,
        "win_pct": _r(100 * (g["result"] == "W").mean(), 1),
        "draw_pct": _r(100 * (g["result"] == "D").mean(), 1),
        "loss_pct": _r(100 * (g["result"] == "L").mean(), 1),
    }


def compute(corpus: pd.DataFrame, shots: pd.DataFrame | None = None) -> dict[str, Any]:
    d = corpus.copy()
    d["gap"] = d["xg"] - d["xg_against"]
    sb = d[d["source"] == "statsbomb"]
    under = sb[sb["gap"] < 0]  # l'équipe qui a le moins d'xG, une ligne par match
    ko_sel = under[(under["kind"] == "selection") & under["knockout"]]
    # selon l'écart d'xG
    bins = []
    cut = pd.cut(-under["gap"], BINS)
    for i, (lo, hi) in enumerate(zip(BINS[:-1], BINS[1:], strict=True)):
        g = under[cut.cat.codes == i]
        bins.append(
            {
                "lo": lo,
                "hi": hi if hi < 6 else None,
                "pts": _r(g["result"].map(PTS).mean()),
            }
            | _rate(g)
        )
    by_comp: list[dict[str, Any]] = []
    for comp, g in under.groupby("comp"):
        if len(g) >= 25:
            by_comp.append(
                {
                    "comp": str(comp),
                    "label": LABELS.get(str(comp), str(comp)),
                    "kind": str(g["kind"].iloc[0]),
                    "year": int(g["year"].median()),
                }
                | _rate(g)
            )
    by_comp.sort(key=lambda r: float(r["win_pct"]))
    # le Barça et ses adversaires, période par période
    barca = []
    b = under[under["comp"] == "liga-barca"]
    eras = ((2004, 2010, "2004–09"), (2010, 2016, "2010–15"), (2016, 2022, "2016–21"))
    for lo, hi, label in eras:
        g = b[(b["year"] >= lo) & (b["year"] < hi)]
        barca.append(
            {
                "era": label,
                "barca_under": int((g["team"] == "Barcelona").sum()),
                "opp_under_win_pct": _r(
                    100 * (g[g["team"] != "Barcelona"]["result"] == "W").mean(), 1
                ),
            }
            | _rate(g)
        )
    heists = sb[(sb["result"] == "W") & (sb["gap"] < 0)].sort_values("gap").head(10)
    top: list[dict[str, Any]] = []
    for r in heists.to_dict("records"):
        top.append(
            {
                "comp": r["comp"],
                "label": LABELS.get(str(r["comp"]), str(r["comp"])),
                "season": str(r["season"]),
                "stage": r["stage"],
                "team": r["team"],
                "opponent": r["opponent"],
                "goals": int(r["goals"]),
                "goals_against": int(r["goals_against"]),
                "xg": _r(r["xg"]),
                "xg_against": _r(r["xg_against"]),
                "gap": _r(-r["gap"]),
                "penalties": bool(r["penalties"]),
                "match_id": r["match_id"],
            }
        )
    wy = d[(d["source"] == "wyscout") & (d["gap"] < 0) & (d["kind"] == "club")]
    return {
        "matches": int(sb["match_id"].nunique()),
        "overall": _rate(under),
        "club": _rate(under[under["kind"] == "club"]),
        "selection": _rate(under[under["kind"] == "selection"]),
        "selection_group": _rate(under[(under["kind"] == "selection") & ~under["knockout"]]),
        "selection_knockout": _rate(ko_sel),
        "selection_knockout_shootouts": int(ko_sel["penalties"].astype(bool).sum()),
        "selection_knockout_pens_wins": int(
            ((ko_sel["result"] == "W") & ko_sel["penalties"].astype(bool)).sum()
        ),
        "selection_knockout_regular": int(
            ((ko_sel["result"] == "W") & ~ko_sel["penalties"].astype(bool)).sum()
        ),
        "wyscout_club_2017": _rate(wy),
        "bins": bins,
        "by_comp": by_comp,
        "barca": barca,
        "heists": top,
    }

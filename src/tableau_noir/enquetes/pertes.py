"""Enquête n° 7 · Où meurent les attaques.

Où l'on perd le ballon (six bandes de 17,5 m, depuis son propre but), et ce que chaque perte
coûte : tirs et xG concédés dans les 15 secondes. En club et en sélection, et dans le temps.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from tableau_noir.enquetes.common import LABELS, _r

BAND_LABELS = ["0–17 m", "17–35 m", "35–52 m", "52–70 m", "70–87 m", "87–105 m"]
SELECTION_COMPS = (
    "wc-2018",
    "euro-2020",
    "wc-2022",
    "euro-2024",
    "copa-2024",
    "can-2023",
    "euro-2016",
)


def _profile(g: pd.DataFrame) -> dict[str, Any]:
    """Par bande : part des pertes, coût par 100 pertes (tirs, xG), part récupérée en 5 s."""
    tot = g["losses"].sum()
    bands = []
    for b in range(6):
        h = g[g["band"] == b]
        n = h["losses"].sum()
        bands.append(
            {
                "band": b,
                "label": BAND_LABELS[b],
                "share_pct": _r(100 * n / tot, 1) if tot else None,
                "shots_per_100": _r(100 * h["shots_against"].sum() / n, 1) if n else None,
                "xg_per_100": _r(100 * h["xg_against"].sum() / n, 2) if n else None,
                "goals_per_1000": _r(1000 * h["goals_against"].sum() / n, 1) if n else None,
                "regained_5s_pct": _r(100 * h["regained_5s"].sum() / n, 1) if n else None,
            }
        )
    per_match = g.groupby(["match_id", "team"])["losses"].sum()  # pertes par équipe et par match
    return {
        "matches": int(g["match_id"].nunique()),
        "losses_per_team": _r(per_match.mean(), 1),
        "own_half_pct": _r(100 * g[g["band"] < 3]["losses"].sum() / tot, 1) if tot else None,
        "xg_share_own_third_pct": _r(
            100 * g[g["band"] < 2]["xg_against"].sum() / g["xg_against"].sum(), 1
        )
        if g["xg_against"].sum()
        else None,
        "bands": bands,
    }


def compute(corpus: pd.DataFrame, shots: pd.DataFrame, losses: pd.DataFrame) -> dict[str, Any]:
    lo = losses.copy()
    lo["kind"] = lo["comp"].map(lambda c: "selection" if c in SELECTION_COMPS else "club")
    lo["source"] = lo["comp"].map(
        lambda c: "wyscout" if c.endswith("-2017") or c == "euro-2016" else "statsbomb"
    )
    sb = lo[lo["source"] == "statsbomb"]
    overall = _profile(sb)
    by_kind = {k: _profile(sb[sb["kind"] == k]) for k in ("club", "selection")}
    # le temps : le Barça saison par saison, et les périodes hors Barça
    barca = sb[(sb["comp"].isin(("liga-barca", "liga-2015"))) & (sb["team"] == "Barcelona")]
    barca_years = []
    for year, g in barca.groupby(barca["year"].astype(int)):
        p = _profile(g)
        if p["matches"] >= 10:
            barca_years.append(
                {
                    "year": int(year),
                    "own_half_pct": p["own_half_pct"],
                    "losses_per_team": p["losses_per_team"],
                }
            )
    eras = []
    for lo_y, hi_y, label in (
        (2015, 2017, "2015–16"),
        (2017, 2021, "2017–20"),
        (2021, 2026, "2021–24"),
    ):
        g = sb[(sb["year"] >= lo_y) & (sb["year"] < hi_y) & (sb["comp"] != "liga-barca")]
        if g["match_id"].nunique() >= 50:
            p = _profile(g)
            eras.append(
                {
                    "era": label,
                    "matches": p["matches"],
                    "own_half_pct": p["own_half_pct"],
                    "losses_per_team": p["losses_per_team"],
                    "xg_per_100_band1": p["bands"][1]["xg_per_100"],
                    "xg_per_100_band4": p["bands"][4]["xg_per_100"],
                }
            )
    by_comp = []
    for comp, g in sb.groupby(sb["comp"].astype(str)):
        if g["match_id"].nunique() >= 30:
            p = _profile(g)
            by_comp.append(
                {
                    "comp": str(comp),
                    "label": LABELS.get(str(comp), str(comp)),
                    "matches": p["matches"],
                    "own_half_pct": p["own_half_pct"],
                    "xg_per_100_band1": p["bands"][1]["xg_per_100"],
                }
            )

    # le coût d'une perte dans ses 17–35 m, à travers le temps : trois fils comparables
    def cost(g: pd.DataFrame) -> dict[str, Any]:
        p = _profile(g)
        return {
            "matches": p["matches"],
            "xg_per_100": p["bands"][1]["xg_per_100"],
            "shots_per_100": p["bands"][1]["shots_per_100"],
        }

    barca_ids = set(sb.loc[sb["team"] == "Barcelona", "match_id"])
    bm = sb[sb["comp"].isin(("liga-barca", "liga-2015")) & sb["match_id"].isin(barca_ids)]
    barca_opp = []
    for lo_y, hi_y, label in (
        (2004, 2010, "2004–09"),
        (2010, 2016, "2010–15"),
        (2016, 2022, "2016–21"),
    ):
        g = bm[(bm["year"] >= lo_y) & (bm["year"] < hi_y)]
        barca_opp.append(
            {"era": label}
            | {f"opp_{k}": v for k, v in cost(g[g["team"] != "Barcelona"]).items()}
            | {f"barca_{k}": v for k, v in cost(g[g["team"] == "Barcelona"]).items()}
        )
    clubs_then_now = [
        {"comp": c, "label": LABELS.get(c, c)} | cost(sb[sb["comp"] == c])
        for c in (
            "bundesliga-2015",
            "bundesliga-2023",
            "ligue1-2015",
            "ligue1-2021",
            "ligue1-2022",
        )
    ]
    leagues_2015 = cost(sb[sb["comp"].isin(("pl-2015", "liga-2015", "seriea-2015", "ligue1-2015"))])
    selections = [
        {"comp": c, "label": LABELS.get(c, c)} | cost(sb[sb["comp"] == c])
        for c in ("wc-2018", "euro-2020", "wc-2022", "euro-2024", "copa-2024", "can-2023")
    ]
    return {
        "barca_opp": barca_opp,
        "clubs_then_now": clubs_then_now,
        "leagues_2015": leagues_2015,
        "selections": selections,
        "overall": overall,
        "by_kind": by_kind,
        "barca_years": barca_years,
        "eras": eras,
        "by_comp": by_comp,
        "cost_ratio_band1_band4": _r(
            overall["bands"][1]["xg_per_100"] / overall["bands"][4]["xg_per_100"], 1
        )
        if overall["bands"][4]["xg_per_100"]
        else None,
    }

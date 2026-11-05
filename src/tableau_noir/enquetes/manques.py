"""Enquête n° 5 · Le but le plus cher jamais raté.

Une occasion « décisive » : un tir manqué d'au moins 0,30 xG alors qu'un but aurait mis l'équipe
devant ou à égalité, dans un match qu'elle n'a finalement pas gagné (tirs au but compris).
On regarde aussi ce que le football rate en général : la conversion des grosses occasions et des
penaltys, en club et en sélection, et dans le temps ; puis les finales où les xG se sont trompés.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from tableau_noir.enquetes.common import LABELS, _r

BIG = 0.3
ERAS = [
    (2009, 2015, "2009–14"),
    (2015, 2017, "2015–16"),
    (2017, 2021, "2017–20"),
    (2021, 2026, "2021–24"),
]


def _with_results(shots: pd.DataFrame, corpus: pd.DataFrame) -> pd.DataFrame:
    res = corpus[["match_id", "team", "result", "penalties", "year", "source"]]
    s = shots.merge(res, on=["match_id", "team"], how="left")
    s["diff"] = s["score_for"] - s["score_against"]
    return s


def _miss(r: pd.Series) -> dict[str, Any]:
    return {
        "match_id": r["match_id"],
        "comp": r["comp"],
        "stage": r["stage"],
        "team": r["team"],
        "opponent": r["opponent"],
        "player": r["player"],
        "minute": int(r["minute"]),
        "xg": _r(r["xg"]),
        "score": f"{int(r['score_for'])}-{int(r['score_against'])}",
        "final": f"{int(r['final_for'])}-{int(r['final_against'])}",
        "result": r["result"],
        "on_target": bool(r["on_target"]),
        "penalty": r["set_piece"] == "penalty",
    }


def decisive(s: pd.DataFrame) -> pd.DataFrame:
    m = s[(s["xg"] >= BIG) & (~s["goal"]) & (s["period"] <= 4)]
    m = m[m["diff"].isin([-1, 0]) & (m["result"] != "W")]
    return m.sort_values("xg", ascending=False)


def _conversion(g: pd.DataFrame) -> dict[str, Any]:
    big = g[(g["xg"] >= BIG) & (g["set_piece"] != "penalty")]
    pens = g[g["set_piece"] == "penalty"]
    return {
        "shots": int(len(g)),
        "goals_per_xg": _r(g["goal"].sum() / g["xg"].sum()) if g["xg"].sum() else None,
        "big_chances": int(len(big)),
        "big_chance_pct": int(round(100 * big["goal"].mean())) if len(big) else None,
        "big_chance_xg": _r(big["xg"].mean()) if len(big) else None,
        "penalties": int(len(pens)),
        "penalty_pct": int(round(100 * pens["goal"].mean())) if len(pens) else None,
    }


def compute(corpus: pd.DataFrame, shots: pd.DataFrame) -> dict[str, Any]:
    s = _with_results(shots, corpus)
    s = s[s["period"] <= 4]  # pas la séance de tirs au but
    sb = s[s["source"] == "statsbomb"]  # un seul modèle d'xG, pour comparer
    dec = decisive(sb)
    open_play = dec[dec["set_piece"] != "penalty"]
    tourn = open_play[(open_play["kind"] == "selection") & open_play["knockout"]]
    finals = dec[dec["stage"] == "Final"]
    # les plus chers : phases finales de sélection, finales (toutes), et en championnat
    top_tournaments = [_miss(r) for _, r in tourn.head(10).iterrows()]
    top_finals = [_miss(r) for _, r in finals.head(8).iterrows()]
    pens_missed = sb[
        (sb["set_piece"] == "penalty")
        & (~sb["goal"])
        & (sb["kind"] == "selection")
        & sb["knockout"]
        & (sb["result"] != "W")
    ]
    top_pens = [_miss(r) for _, r in pens_missed.sort_values("minute", ascending=False).iterrows()]
    # ce qu'on rate : club et sélection
    conv = {k: _conversion(sb[sb["kind"] == k]) for k in ("club", "selection")}
    conv["selection_knockout"] = _conversion(sb[(sb["kind"] == "selection") & sb["knockout"]])
    # dans le temps : le Barça (une équipe, 17 saisons) et les saisons complètes
    barca = sb[sb["comp"].isin(("liga-barca", "liga-2015")) & (sb["team"] == "Barcelona")]
    by_season = []
    for season, g in barca.groupby("season"):
        c = _conversion(g)
        by_season.append({"season": str(season)} | c)
    eras = []
    for lo, hi, label in ERAS:
        g = sb[(sb["year"] >= lo) & (sb["year"] < hi) & (sb["comp"] != "liga-barca")]
        if len(g) < 200:
            continue
        eras.append(
            {"era": label, "comps": sorted({LABELS.get(c, c) for c in g["comp"].unique()})}
            | _conversion(g)
        )
    # les finales où les xG se sont trompés
    fin = corpus[(corpus["stage"] == "Final") & (corpus["result"] == "W")].copy()
    fin["xg_gap"] = fin["xg"] - fin["xg_against"]
    lied = fin[fin["xg_gap"] < 0].sort_values("xg_gap")
    shots_by = sb.groupby(["match_id", "team"]).agg(
        shots=("xg", "size"), on_target=("on_target", "sum")
    )
    finals_rows = [
        {
            "match_id": r["match_id"],
            "shots_winner": int(shots_by["shots"].get((r["match_id"], r["team"]), 0)),
            "shots_loser": int(shots_by["shots"].get((r["match_id"], r["opponent"]), 0)),
            "on_target_winner": int(shots_by["on_target"].get((r["match_id"], r["team"]), 0)),
            "on_target_loser": int(shots_by["on_target"].get((r["match_id"], r["opponent"]), 0)),
            "comp": r["comp"],
            "winner": r["team"],
            "loser": r["opponent"],
            "score": f"{int(r['goals'])}-{int(r['goals_against'])}",
            "penalties": bool(r["penalties"]),
            "xg_winner": _r(r["xg"]),
            "xg_loser": _r(r["xg_against"]),
            "gap": _r(r["xg_gap"]),
        }
        for _, r in lied.head(8).iterrows()
    ]
    n_finals = int(len(fin))
    return {
        "big_threshold": BIG,
        "n_shots": int(len(sb)),
        "n_decisive": int(len(dec)),
        "n_decisive_tournaments": int(len(tourn)),
        "top_tournaments": top_tournaments,
        "top_finals": top_finals,
        "penalties_missed": top_pens,
        "conversion": conv,
        "barca_seasons": by_season,
        "eras": eras,
        "finals": {
            "n": n_finals,
            "xg_lied": int(len(lied)),
            "xg_lied_pct": int(round(100 * len(lied) / n_finals)) if n_finals else None,
            "rows": finals_rows,
        },
        "barca_big_chance_pct": int(
            round(
                100 * barca[(barca["xg"] >= BIG) & (barca["set_piece"] != "penalty")]["goal"].mean()
            )
        ),
        "big_chance_pct_range": [
            min(e["big_chance_pct"] for e in eras),
            max(e["big_chance_pct"] for e in eras),
        ],
    }

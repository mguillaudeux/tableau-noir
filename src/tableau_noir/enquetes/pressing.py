"""Enquête n° 1 · Le pressing fait-il gagner ?

Sur les matchs StatsBomb (les seuls avec des événements de pression) : qui gagne quand une équipe
presse plus que l'autre, ce que le pressing produit (occasions créées, concédées) et ce qu'il
rapporte (points), et les contre-exemples qui comptent.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

PTS = {"W": 3, "D": 1, "L": 0}


def _r(v: float, d: int = 2) -> float:
    return round(float(v), d)


def paired(df: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par match : les deux équipes côte à côte."""
    a = df.drop_duplicates("match_id", keep="first").set_index("match_id")
    b = df.drop_duplicates("match_id", keep="last").set_index("match_id")
    both = a.join(b, rsuffix="_b")
    return both[both["team"] != both["team_b"]]


def outcome(p: pd.DataFrame, key: str, more_is_more: bool) -> dict[str, Any]:
    """Résultat de l'équipe qui a « plus » de `key` que l'autre (victoire, nul, défaite)."""
    a, b = p[key], p[f"{key}_b"]
    ok = a.notna() & b.notna() & (a != b)
    p = p[ok]
    first = (p[key] > p[f"{key}_b"]) == more_is_more
    res = np.where(first, p["result"], p["result_b"])
    n = int(len(res))
    return {
        "n": n,
        "win": int((res == "W").sum()),
        "draw": int((res == "D").sum()),
        "loss": int((res == "L").sum()),
        "win_pct": int(round(100 * (res == "W").mean())) if n else None,
        "loss_pct": int(round(100 * (res == "L").mean())) if n else None,
    }


def quartiles(df: pd.DataFrame, key: str, ascending: bool = True) -> list[dict[str, Any]]:
    labels = ["q1", "q2", "q3", "q4"]
    q = pd.qcut(df[key], 4, labels=labels if ascending else labels[::-1])
    out = []
    for lab in labels:
        g = df[q == lab]
        out.append(
            {
                "quartile": lab,
                "n": int(len(g)),
                "value": _r(g[key].mean(), 2),
                "possession": int(round(100 * g["possession"].mean())),
                "xg": _r(g["xg"].mean()),
                "xg_against": _r(g["xg_against"].mean()),
                "goals": _r(g["goals"].mean()),
                "goals_against": _r(g["goals_against"].mean()),
                "win_pct": int(round(100 * (g["result"] == "W").mean())),
                "pts": _r(g["result"].map(PTS).mean()),
                "tr_xg_against": _r(g["tr_xg_against"].mean()),
            }
        )
    return out


def compute(corpus: pd.DataFrame) -> dict[str, Any]:
    df = corpus[corpus["source"] == "statsbomb"].copy()
    df["pts"] = df["result"].map(PTS)
    p = paired(df)
    ko = p[p["knockout"]]
    outcomes = {
        "ppda": outcome(p, "ppda", False),
        "press_per_min": outcome(p, "press_per_min", True),
        "counterpress": outcome(p, "counterpress", True),
        "high_recoveries": outcome(p, "high_recoveries", True),
        "possession": outcome(p, "possession", True),
        "xg": outcome(p, "xg", True),
    }
    outcomes_ko = {k: outcome(ko, k, k not in ("ppda",)) for k in outcomes}
    # pressing ≈ possession : corrélation, et effet du PPDA une fois la possession retirée
    s = df.dropna(subset=["ppda", "possession"])

    def z(v: pd.Series) -> np.ndarray:
        out: np.ndarray = ((v - v.mean()) / v.std()).to_numpy(float)
        return out

    x = np.column_stack([np.ones(len(s)), z(s["ppda"]), z(s["possession"])])
    gd = (s["goals"] - s["goals_against"]).to_numpy(float)
    xgd = (s["xg"] - s["xg_against"]).to_numpy(float)
    b_gd = np.linalg.lstsq(x, gd, rcond=None)[0]
    b_xgd = np.linalg.lstsq(x, xgd, rcond=None)[0]
    # les cas : vainqueurs de tournoi, et les blocs bas qui ont gagné en phase finale
    champions = {
        "wc-2022": "Argentina",
        "euro-2024": "Spain",
        "euro-2020": "Italy",
        "wc-2018": "France",
    }
    champ_rows = []
    for comp, name in champions.items():
        g = df[(df["comp"] == comp) & (df["team"] == name)]
        allc = df[df["comp"] == comp]
        order = list(allc.groupby("team")["ppda"].mean().sort_values().index)
        rank = order.index(name) + 1
        champ_rows.append(
            {
                "comp": comp,
                "team": name,
                "ppda": _r(g["ppda"].mean(), 1),
                "ppda_comp": _r(allc["ppda"].mean(), 1),
                "rank": rank,
                "of": int(allc["team"].nunique()),
                "counterpress": int(round(100 * g["counterpress"].mean())),
                "counterpress_comp": int(round(100 * allc["counterpress"].mean())),
            }
        )
    cases = ko.copy()
    cases["presser_is_a"] = cases["ppda"] < cases["ppda_b"]
    rows = []
    for mid, r in cases.iterrows():
        low, high = ("_b", "") if r["presser_is_a"] else ("", "_b")  # low = bloc bas
        rows.append(
            {
                "match_id": mid,
                "comp": r["comp"],
                "stage": r["stage"],
                "low_block": r[f"team{low}"],
                "presser": r[f"team{high}"],
                "ppda_low": _r(r[f"ppda{low}"], 1),
                "ppda_high": _r(r[f"ppda{high}"], 1),
                "possession_low": int(round(100 * r[f"possession{low}"])),
                "score_low": int(r[f"goals{low}"]),
                "score_high": int(r[f"goals{high}"]),
                "low_result": r[f"result{low}"],
                "xg_low": _r(r[f"xg{low}"]),
                "xg_high": _r(r[f"xg{high}"]),
            }
        )
    rows.sort(key=lambda x: -(x["ppda_low"] - x["ppda_high"]))
    # un vrai bloc bas : moins de 45 % de possession (sinon le PPDA ne mesure que le ballon qu'on a)
    low_wins = [x for x in rows if x["low_result"] == "W" and x["possession_low"] < 45][:8]
    pq = quartiles(df, "ppda")
    return {
        "n_matches": int(len(p)),
        "n_rows": int(len(df)),
        "xg_gap_q1_q4": _r(pq[0]["xg"] - pq[3]["xg"]),
        "n_knockout": int(len(ko)),
        "outcomes": outcomes,
        "outcomes_knockout": outcomes_ko,
        "ppda_quartiles": pq,
        "counterpress_quartiles": quartiles(df.dropna(subset=["counterpress"]), "counterpress"),
        "corr_ppda_possession": _r(np.corrcoef(s["ppda"], s["possession"])[0, 1]),
        "effect_per_sd": {
            "ppda_on_goal_diff": _r(b_gd[1]),
            "possession_on_goal_diff": _r(b_gd[2]),
            "ppda_on_xg_diff": _r(b_xgd[1]),
            "possession_on_xg_diff": _r(b_xgd[2]),
        },
        "champions": champ_rows,
        "low_block_wins": low_wins,
        "biggest_gap_cases": rows[:12],
    }

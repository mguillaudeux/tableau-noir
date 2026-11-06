"""Enquête n° 6 · La défense à trois, et les formations qui mentent.

Deux sources, deux questions. La composition annoncée (StatsBomb la donne pour chaque match) dit
qui joue à trois derrière, et comment ça a changé entre 2004 et 2024, en club et en sélection.
L'endroit où chaque défenseur touche le ballon (la médiane de ses touches, `players.csv`) dit ce
que devient la défense une fois le ballon dans les pieds : le latéral qui monte seul, et le piston.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.enquetes.common import LABELS, _r

SELECTION_COMPS = ("wc-2018", "euro-2020", "wc-2022", "euro-2024", "copa-2024", "can-2023")
LEAGUE_COMPS = ("pl-2015", "liga-2015", "seriea-2015", "ligue1-2015")
RECENT = ("bundesliga-2015", "bundesliga-2023", "ligue1-2021", "ligue1-2022")
TOURNAMENTS = ("wc-2018", "euro-2020", "wc-2022", "euro-2024", "copa-2024", "can-2023")
ERAS = ((2004, 2010, "2004–09"), (2010, 2016, "2010–15"), (2016, 2022, "2016–21"))
MIN_MINUTES = 60
LOPSIDED = 10.0  # mètres d'écart entre les deux latéraux : l'un monte, l'autre reste


def _back(f: object) -> int | None:
    return int(str(f).split("-")[0]) if isinstance(f, str) and f[:1].isdigit() else None


def _pct(s: pd.Series) -> float | None:
    return _r(100 * s.mean(), 1) if len(s) else None


def _share(g: pd.DataFrame) -> dict[str, Any]:
    return {"n": int(len(g)), "back_three_pct": _pct(g["back"] == 3)}


def defence_lines(players: pd.DataFrame, shapes: pd.DataFrame) -> pd.DataFrame:
    """Une ligne par équipe et par match : où touchent le ballon les défenseurs, rangés de gauche à
    droite. Défense à quatre annoncée et quatre défenseurs (60 min et plus), ou à trois et cinq."""
    d = players[(players["position"] == "DF") & (players["minutes"] >= MIN_MINUTES)]
    d = d.dropna(subset=["touch_x", "touch_y"]).drop_duplicates(["match_id", "player_id"])
    ann = shapes[["match_id", "team", "announced"]].drop_duplicates(["match_id", "team"])
    d = d.merge(ann, on=["match_id", "team"])
    rows = []
    for (mid, team), g in d.groupby(["match_id", "team"], sort=False):
        back = _back(g["announced"].iloc[0])
        if (back, len(g)) not in ((3, 5), (4, 4)):
            continue
        g = g.sort_values("touch_y")
        wide = g.iloc[[0, -1]]
        centre = g.iloc[1:-1]
        wx = wide["touch_x"].to_numpy(float)
        rows.append(
            {
                "match_id": mid,
                "team": team,
                "comp": str(g["comp"].iloc[0]),
                "year": int(g["year"].iloc[0]),
                "back": back,
                "centre_x": float(centre["touch_x"].mean()),
                "wide_x": float(wx.mean()),
                "wide_adv": float(wx.mean() - centre["touch_x"].mean()),
                "asym": float(abs(wx[0] - wx[1])),
                # les quatre (ou cinq) positions, le latéral le plus haut ramené à droite (y > 34)
                "slots": _slots(g),
            }
        )
    return pd.DataFrame(rows)


def _slots(g: pd.DataFrame) -> list[tuple[float, float]]:
    pts = list(zip(g["touch_x"].astype(float), g["touch_y"].astype(float), strict=True))
    if pts[0][0] > pts[-1][0]:  # le latéral le plus haut est à gauche : on retourne le terrain
        pts = [(x, 68 - y) for x, y in reversed(pts)]
    return pts


def _profile(g: pd.DataFrame) -> dict[str, Any]:
    if g.empty:
        return {"n": 0}
    return {
        "n": int(len(g)),
        "centre_x": _r(g["centre_x"].mean(), 1),
        "wide_x": _r(g["wide_x"].mean(), 1),
        "wide_adv": _r(g["wide_adv"].mean(), 1),
        "asym": _r(g["asym"].mean(), 1),
        "lopsided_pct": _pct(g["asym"] >= LOPSIDED),
    }


def _shape(g: pd.DataFrame) -> list[dict[str, float | None]]:
    """La défense « moyenne » : position médiane de chaque défenseur, de gauche à droite."""
    arr = np.array(g["slots"].tolist(), dtype=float)  # (n, k, 2)
    med = np.median(arr, axis=0)
    return [{"x": _r(x, 1), "y": _r(y, 1)} for x, y in med]


def compute(
    corpus: pd.DataFrame, shots: pd.DataFrame, shapes: pd.DataFrame, players: pd.DataFrame
) -> dict[str, Any]:
    s = shapes.dropna(subset=["announced"]).copy()
    s["back"] = s["announced"].map(_back)
    s["kind"] = s["comp"].map(lambda c: "selection" if c in SELECTION_COMPS else "club")
    # 1. la défense à trois annoncée, dans le temps
    b = s[s["comp"] == "liga-barca"]
    barca = []
    for lo, hi, label in ERAS:
        g = b[(b["year"] >= lo) & (b["year"] < hi)]
        barca.append(
            {
                "era": label,
                "barca": _share(g[g["team"] == "Barcelona"]),
                "opp": _share(g[g["team"] != "Barcelona"]),
            }
        )
    by_comp = [
        {"comp": c, "label": LABELS.get(c, c)} | _share(s[s["comp"] == c])
        for c in LEAGUE_COMPS + RECENT + TOURNAMENTS
    ]
    leagues = s[s["comp"].isin(LEAGUE_COMPS)]
    tournaments = s[s["comp"].isin(TOURNAMENTS)]
    big4 = s[s["comp"].isin(("wc-2018", "euro-2020", "wc-2022", "euro-2024"))]

    def top(g: pd.DataFrame) -> list[dict[str, Any]]:
        return [
            {"shape": k, "pct": _r(100 * v / len(g), 1)}
            for k, v in Counter(g["announced"]).most_common(6)
        ]

    # 2. ce que devient la défense, ballon au pied
    lines = defence_lines(players, s)
    four = lines[lines["back"] == 4]
    three = lines[lines["back"] == 3]
    lop = four[four["asym"] >= LOPSIDED]
    level = four[four["asym"] < LOPSIDED / 2]
    four_kind = four.assign(
        kind=four["comp"].map(lambda c: "selection" if c in SELECTION_COMPS else "club")
    )
    lb = four[four["comp"] == "liga-barca"]
    lop_barca = []
    for lo, hi, label in ERAS:
        g = lb[(lb["year"] >= lo) & (lb["year"] < hi)]
        lop_barca.append(
            {
                "era": label,
                "barca": _profile(g[g["team"] == "Barcelona"]),
                "opp": _profile(g[g["team"] != "Barcelona"]),
            }
        )
    return {
        "teams": int(len(s)),
        "overall": _share(s),
        "leagues_2015": _share(leagues),
        "tournaments": _share(tournaments),
        "big_tournaments": _share(big4),
        "barca": barca,
        "by_comp": by_comp,
        "top_leagues_2015": top(leagues),
        "top_tournaments": top(tournaments),
        "shapes_compare": [
            {
                "shape": k,
                "leagues_pct": _r(100 * (leagues["announced"] == k).mean(), 1),
                "tournaments_pct": _r(100 * (tournaments["announced"] == k).mean(), 1),
            }
            for k in dict.fromkeys(
                [x["shape"] for x in top(leagues)] + [x["shape"] for x in top(tournaments)]
            )
        ],
        "four": _profile(four),
        "three": _profile(three),
        "wingback_higher": _r(three["wide_x"].mean() - four["wide_x"].mean(), 1)
        if len(three) and len(four)
        else None,
        "shape_level": _shape(level) if len(level) else [],
        "shape_lopsided": _shape(lop) if len(lop) else [],
        "shape_three": _shape(three) if len(three) else [],
        "four_by_kind": {
            k: _profile(four_kind[four_kind["kind"] == k]) for k in ("club", "selection")
        },
        "four_barca": lop_barca,
        "four_by_comp": [
            {"comp": c, "label": LABELS.get(c, c)} | _profile(four[four["comp"] == c])
            for c in LEAGUE_COMPS + TOURNAMENTS
        ],
    }

"""Enquête n° 8 · Messi et Mbappé, le même joueur ?

Les deux, match par match (`players.csv`) : ce qu'ils font pour 90 minutes (occasions, ballons
touchés dans la surface, dribbles, passes qui font avancer, passes décisives d'intention), et où ils
touchent le ballon. Au même âge, coéquipiers au PSG, en club et en sélection, et Messi saison par
saison, de 2004/05 à 2023.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from tableau_noir.enquetes.common import _r

MESSI = "Lionel Messi"
MBAPPE = "Kylian Mbappé"
SELECTION_COMPS = ("wc-2018", "euro-2020", "wc-2022", "euro-2024", "copa-2024", "can-2023")
MIN_SEASON = 900  # minutes pour qu'une saison compte
PER90 = {
    "npxg": "npxg",
    "goals": "goals",
    "shots": "shots",
    "box": "box_touches",
    "dribbles": "dribbles",
    "progressive": "progressive",
    "key_passes": "key_passes",
    "touches": "touches",
    "xt": "xt",
}


def profile(g: pd.DataFrame) -> dict[str, Any]:
    """Le profil d'un joueur sur des matchs : pour 90 minutes, et où il touche le ballon."""
    m = float(g["minutes"].sum())
    if m <= 0:
        return {"matches": 0}
    out: dict[str, Any] = {"matches": int(len(g)), "minutes": int(round(m))}
    for k, col in PER90.items():
        out[k] = _r(90 * g[col].sum() / m, 2)
    out["touch_x"] = _r(g["touch_x"].median(), 1)
    out["touch_y"] = _r(g["touch_y"].median(), 1)
    out["pass_pct"] = _r(100 * g["passes_ok"].sum() / g["passes"].sum(), 1)
    return out


def _season_start(season: str) -> int:
    return int(str(season)[:4])


def compute(corpus: pd.DataFrame, shots: pd.DataFrame, players: pd.DataFrame) -> dict[str, Any]:
    p = players[players["player"].isin((MESSI, MBAPPE))].drop_duplicates(["match_id", "player"])
    me = p[p["player"] == MESSI]
    mb = p[p["player"] == MBAPPE]
    barca = me[me["comp"].isin(("liga-barca", "liga-2015"))]
    # Messi, saison par saison au Barça
    seasons = []
    for season, g in barca.groupby("season"):
        if g["minutes"].sum() >= MIN_SEASON:
            seasons.append(
                {"season": str(season), "age": _season_start(str(season)) - 1987} | profile(g)
            )
    psg_me = me[me["comp"].isin(("ligue1-2021", "ligue1-2022"))]
    psg_mb = mb[mb["comp"].isin(("ligue1-2021", "ligue1-2022"))]
    # au même âge : Messi en 2010/11 et 2011/12 (23–24 ans), Mbappé au PSG en 2021/22 et 2022/23
    same_age_me = barca[barca["season"].isin(("2010/2011", "2011/2012"))]

    def spells(df: pd.DataFrame, groups: list[tuple[str, tuple[str, ...]]]) -> list[dict[str, Any]]:
        return [{"key": k, "comps": list(c)} | profile(df[df["comp"].isin(c)]) for k, c in groups]

    me_eras = []
    for lo, hi, key in ((2004, 2009, "winger"), (2009, 2015, "nine"), (2015, 2021, "playmaker")):
        g = barca[barca["season"].map(_season_start).between(lo, hi - 1)]
        me_eras.append({"key": key, "from": lo, "to": hi} | profile(g))
    me_eras.append({"key": "psg", "from": 2021, "to": 2023} | profile(psg_me))
    # club et sélection, à la même époque
    me_club_recent = pd.concat(
        [barca[barca["season"].map(_season_start) >= 2017], psg_me], ignore_index=True
    )
    me_sel = me[me["comp"].isin(SELECTION_COMPS)]
    mb_sel = mb[mb["comp"].isin(SELECTION_COMPS)]
    return {
        "messi_seasons": seasons,
        "messi_eras": me_eras,
        "same_age": {"messi": profile(same_age_me), "mbappe": profile(psg_mb)},
        "psg": {"messi": profile(psg_me), "mbappe": profile(psg_mb)},
        "club_vs_selection": {
            "messi_club": profile(me_club_recent),
            "messi_selection": profile(me_sel),
            "mbappe_club": profile(psg_mb),
            "mbappe_selection": profile(mb_sel),
        },
        "messi_tournaments": spells(
            me,
            [("wc-2018", ("wc-2018",)), ("wc-2022", ("wc-2022",)), ("copa-2024", ("copa-2024",))],
        ),
        "mbappe_tournaments": spells(
            mb, [(c, (c,)) for c in ("wc-2018", "euro-2020", "wc-2022", "euro-2024")]
        ),
        "mbappe_psg_seasons": spells(
            mb, [("ligue1-2021", ("ligue1-2021",)), ("ligue1-2022", ("ligue1-2022",))]
        ),
        "messi_mls": profile(me[me["comp"] == "mls-2023"]),
    }

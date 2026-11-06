"""Enquêtes « hold-up », « pertes », « formations » et « Messi » : des cas construits à la main."""

from __future__ import annotations

import pandas as pd

from tableau_noir.enquetes import formations, holdups, messi, pertes


def _match(i: int, comp: str, kind: str, xg: float, xga: float, res: str, **kw: object) -> list:
    opp = {"W": "L", "L": "W", "D": "D"}[res]
    base = {
        "match_id": f"m{i}",
        "comp": comp,
        "kind": kind,
        "source": "statsbomb",
        "season": "2022",
        "year": 2022,
        "stage": "Final" if kw.get("knockout") else "Group A",
        "knockout": bool(kw.get("knockout", False)),
        "penalties": bool(kw.get("penalties", False)),
    }
    g = {"W": (2, 1), "D": (1, 1), "L": (0, 1)}[res]
    return [
        base
        | {
            "team": f"A{i}",
            "opponent": f"B{i}",
            "xg": xg,
            "xg_against": xga,
            "result": res,
            "goals": g[0],
            "goals_against": g[1],
        },
        base
        | {
            "team": f"B{i}",
            "opponent": f"A{i}",
            "xg": xga,
            "xg_against": xg,
            "result": opp,
            "goals": g[1],
            "goals_against": g[0],
        },
    ]


def holdup_corpus() -> pd.DataFrame:
    rows: list = []
    # club : 4 matchs, l'équipe à moins d'xG gagne 1 fois (le hold-up : 0,2 contre 2,6)
    rows += _match(0, "pl-2015", "club", 0.2, 2.6, "W")
    rows += _match(1, "pl-2015", "club", 0.5, 1.5, "L")
    rows += _match(2, "pl-2015", "club", 0.9, 1.0, "D")
    rows += _match(3, "pl-2015", "club", 0.3, 2.4, "L")
    # sélection : phase finale, une victoire aux tirs au but, une dans le jeu
    rows += _match(4, "wc-2022", "selection", 0.8, 1.2, "W", knockout=True, penalties=True)
    rows += _match(5, "wc-2022", "selection", 0.6, 1.9, "W", knockout=True)
    rows += _match(6, "wc-2022", "selection", 0.4, 1.0, "L")
    return pd.DataFrame(rows)


def test_holdups_taux() -> None:
    out = holdups.compute(holdup_corpus())
    assert out["matches"] == 7
    assert out["overall"]["n"] == 7
    assert out["club"]["win_pct"] == 25.0
    assert out["selection_knockout"]["win_pct"] == 100.0
    assert out["selection_knockout_pens_wins"] == 1
    assert out["selection_knockout_regular"] == 1
    # le plus gros hold-up en tête, écart positif
    assert out["heists"][0]["team"] == "A0"
    assert out["heists"][0]["gap"] == 2.4
    # au-delà de 2 xG d'écart, une victoire sur deux matchs
    big = [b for b in out["bins"] if b["lo"] == 2.0][0]
    assert big["n"] == 2 and big["win_pct"] == 50.0


def losses_table() -> pd.DataFrame:
    rows = []
    for i, (comp, year) in enumerate((("pl-2015", 2015), ("wc-2022", 2022))):
        for team in (f"A{i}", f"B{i}"):
            for band in range(6):
                rows.append(
                    {
                        "match_id": f"m{i}",
                        "comp": comp,
                        "year": year,
                        "team": team,
                        "band": band,
                        "losses": 10,
                        # une perte dans ses 17–35 m coûte 4 fois une perte à 70–87 m
                        "shots_against": 4 if band == 1 else 1,
                        "xg_against": 0.4 if band == 1 else 0.1,
                        "goals_against": 0,
                        "regained_5s": 3,
                    }
                )
    return pd.DataFrame(rows)


def test_pertes_profil() -> None:
    out = pertes.compute(pd.DataFrame(), pd.DataFrame(), losses_table())
    o = out["overall"]
    assert o["matches"] == 2
    assert o["losses_per_team"] == 60.0  # 6 bandes × 10 pertes, par équipe et par match
    assert o["own_half_pct"] == 50.0
    assert o["bands"][1]["xg_per_100"] == 4.0
    assert out["cost_ratio_band1_band4"] == 4.0
    assert out["by_kind"]["club"]["matches"] == 1
    assert out["by_kind"]["selection"]["matches"] == 1


def players_table() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Deux équipes annoncées à quatre (l'une bancale), une à trois, une incomplète."""
    rows = []
    shapes = []

    def defence(mid: str, team: str, ann: str, pts: list[tuple[float, float]]) -> None:
        shapes.append(
            {
                "match_id": mid,
                "team": team,
                "announced": ann,
                "comp": "pl-2015",
                "year": 2015,
                "season": "2015/2016",
            }
        )
        for i, (x, y) in enumerate(pts):
            rows.append(
                {
                    "match_id": mid,
                    "comp": "pl-2015",
                    "season": "2015/2016",
                    "year": 2015,
                    "team": team,
                    "player_id": f"{team}{i}",
                    "player": f"{team}{i}",
                    "position": "DF",
                    "minutes": 90,
                    "touch_x": x,
                    "touch_y": y,
                }
            )

    defence("m1", "A", "4-4-2", [(50, 5), (35, 20), (35, 48), (52, 63)])
    defence("m1", "B", "4-2-3-1", [(44, 5), (34, 20), (36, 48), (60, 63)])  # bancale
    defence("m2", "C", "3-5-2", [(58, 5), (38, 15), (35, 34), (38, 53), (60, 63)])
    defence("m2", "D", "4-3-3", [(50, 5), (35, 20), (35, 48)])  # trois défenseurs : ignorée
    return pd.DataFrame(rows), pd.DataFrame(shapes)


def test_formations_lignes() -> None:
    players, shapes = players_table()
    out = formations.compute(pd.DataFrame(), pd.DataFrame(), shapes, players)
    assert out["teams"] == 4
    assert out["overall"]["back_three_pct"] == 25.0
    assert out["four"]["n"] == 2  # D n'a que trois défenseurs : ignorée
    assert out["four"]["lopsided_pct"] == 50.0
    # le latéral le plus haut est ramené à droite
    assert out["shape_lopsided"][-1]["x"] == 60.0
    assert out["three"]["wide_x"] == 59.0


def test_messi_profils() -> None:
    def match(i: int, player: str, comp: str, season: str, **kw: float) -> dict:
        base = {
            "match_id": f"{comp}{i}",
            "comp": comp,
            "season": season,
            "player": player,
            "minutes": 90,
            "goals": 1,
            "npxg": 0.5,
            "shots": 4,
            "box_touches": 10,
            "dribbles": 3,
            "progressive": 2,
            "key_passes": 1,
            "touches": 100,
            "xt": 0.4,
            "touch_x": 70.0,
            "touch_y": 40.0,
            "passes": 50,
            "passes_ok": 40,
        }
        return base | kw

    rows = [match(i, "Lionel Messi", "liga-barca", "2010/2011", dribbles=7) for i in range(11)]
    rows += [match(i, "Kylian Mbappé", "ligue1-2022", "2022/2023", touches=80) for i in range(5)]
    rows += [match(i, "Kylian Mbappé", "wc-2022", "2022", npxg=0.25) for i in range(2)]
    out = messi.compute(pd.DataFrame(), pd.DataFrame(), pd.DataFrame(rows))
    assert out["messi_seasons"][0]["age"] == 23
    assert out["same_age"]["messi"]["dribbles"] == 7.0
    assert out["same_age"]["mbappe"]["touches"] == 80.0
    assert out["club_vs_selection"]["mbappe_selection"]["npxg"] == 0.25
    assert out["club_vs_selection"]["mbappe_club"]["pass_pct"] == 80.0

from __future__ import annotations

import re
from typing import Any

import numpy as np
import pandas as pd
import pytest

from tableau_noir import analyst, players, xt


def moves(rows: list[dict[str, Any]]) -> pd.DataFrame:
    base = {"set_piece": "open", "ok": True, "goal": False, "ex": None, "ey": None}
    return pd.DataFrame([base | r for r in rows])


def test_xt_la_menace_monte_vers_le_but() -> None:
    rows = []
    for _ in range(50):  # depuis le milieu, on joue vers la surface ; depuis la surface, on tire
        rows.append({"kind": "pass", "x": 50.0, "y": 34.0, "ex": 95.0, "ey": 34.0})
        rows.append({"kind": "pass", "x": 50.0, "y": 34.0, "ex": 95.0, "ey": 34.0, "ok": False})
        rows.append({"kind": "shot", "x": 95.0, "y": 34.0})
    rows += [{"kind": "shot", "x": 95.0, "y": 34.0, "goal": True}] * 25
    model = xt.fit(moves(rows))
    v_mid, v_box = model.value(np.array([50.0, 95.0]), np.array([34.0, 34.0]))
    assert v_box == pytest.approx(25 / 75)  # tir à chaque fois, un sur trois rentre
    assert v_mid == pytest.approx(v_box / 2)  # une passe sur deux arrive
    ev = moves(
        [
            {"kind": "pass", "x": 50.0, "y": 34.0, "ex": 95.0, "ey": 34.0},
            {"kind": "pass", "x": 50.0, "y": 34.0, "ex": 95.0, "ey": 34.0, "ok": False},
            {"kind": "pass", "x": 50.0, "y": 34.0, "ex": 95.0, "ey": 34.0, "set_piece": "corner"},
        ]
    )
    added = model.added(ev)
    assert added[0] == pytest.approx(v_box - v_mid) and added[1] == 0 and added[2] == 0


def test_zones_symetriques() -> None:
    z = players.zone(np.array([10.0, 10.0, 10.0, 100.0]), np.array([34.0, 5.0, 63.0, 30.0]))
    assert z[1] == z[2] and z[0] != z[1] and z[3] == 5 * 3


def test_postes() -> None:
    assert players.role("DF", [20, 22], [5, 6]) == "FB"
    assert players.role("DF", [20, 22], [30, 38]) == "CB"
    assert players.role("GK", [], []) == "GK"
    assert players.role("", [80], [34]) == "FW"


def player(pid: str, role: str, profile: list[float], name: str | None = None) -> dict[str, Any]:
    return {"id": pid, "name": name or pid, "team": "T", "role": role, "profile": profile}


def test_jumeaux() -> None:
    tables = {
        "a": {"players": {"1": player("1", "FW", [1, 0]), "2": player("2", "FW", [0, 1])}},
        "b": {
            "players": {
                "3": player("3", "FW", [0.9, 0.1]),
                "4": player("4", "FW", [1, 0], name="1"),  # le même joueur, ailleurs : exclu
                "5": player("5", "MF", [1, 0]),  # autre poste : exclu
            }
        },
    }
    players.twins(tables, n=2)
    tw = tables["a"]["players"]["1"]["twins"]
    assert [t["id"] for t in tw] == ["3", "2"]
    assert tw[0]["sim"] > 0.99 and tw[0]["comp"] == "b"


def test_classement_par_poste() -> None:
    table: dict[str, dict[str, Any]] = {
        str(i): {
            "id": str(i),
            "role": "FW",
            "per90": {"npxg": v, "goals": v, "shots": v, "xt": v, "key_passes": v, "dribbles": v},
        }
        for i, v in enumerate([0.1, 0.5, 0.3])
    }
    ranks = players._rank(table)
    assert ranks["FW"] == ["1", "2", "0"]
    assert table["1"]["rank"] == 1 and table["1"]["of"] == 3


def game() -> dict[str, Any]:
    side = {"home": "H", "away": "A"}

    def team(s: str) -> dict[str, Any]:
        return {
            "announced": "4-3-3",
            "shape": {
                "formation_with": "3-4-3" if s == "home" else "4-3-3",
                "formation_without": "4-4-2",
                "lanes": [[0.05] * 5, [0.06] * 5, [0.09] * 5],
                "block": None,
            },
            "network": [["h1", "h2", 12]] if s == "home" else [],
            "pressing": {
                "source": "pressures",
                "regain_5s": 0.4 if s == "home" else 0.2,
                "high_recoveries": 7,
                "counterpress_share": 0.2,
            },
            "relation": {"short_share": 0.6 if s == "home" else 0.4},
            "recovery": {
                "shots_against": 2 if s == "home" else 6,
                "xg_against": 0.2 if s == "home" else 0.9,
                "goal_minutes": [] if s == "home" else [55],
                "behind_ball": None,
            },
        }

    def p(pid: str, s: str, **kw: Any) -> dict[str, Any]:
        base = {
            "id": pid,
            "name": f"Joueur {pid}",
            "side": s,
            "team": side[s],
            "goals": 0,
            "assists": 0,
            "xg": 0.1,
            "key_passes": 1,
            "progressive": 3,
            "def_actions": 2,
            "xt": 0.1,
            "attention": 0.5,
        }
        return base | kw

    return {
        "meta": {
            "id": "m1",
            "has_360": False,
            "home": {"name": "Argentina", "score": 2, "penalties": None},
            "away": {"name": "France", "score": 1, "penalties": None},
        },
        "stats": {
            s: {
                "xg": 2.1 if s == "home" else 0.6,
                "possession": 0.65 if s == "home" else 0.35,
                "big_chances": 3,
                "shots": 18 if s == "home" else 6,
                "red": 0,
                "ppda": 8.0 if s == "home" else 14.0,
            }
            for s in ("home", "away")
        },
        "team": {s: team(s) for s in ("home", "away")},
        "players": [
            p("h1", "home", goals=2, xt=0.5, attention=2.0),
            p("h2", "home"),
            p("a1", "away"),
        ],
        "goals": [{"side": "home", "minute": 10}],
        "value": {"actions": {"home": [], "away": []}},
    }


def test_coin_de_l_analyste() -> None:
    ctx = {"stats": {"relation": {"short_share": {"mean": 0.5, "sd": 0.1}}}, "teams": []}
    notes = analyst.match_notes(game(), ctx, {"players": {}})
    assert set(notes) == {f"s{i}" for i in range(1, 10)}
    for sec, note in notes.items():
        for lang in ("fr", "en"):
            n = note[lang]
            assert n["lead"], (sec, lang)
            text = " ".join([n["lead"], n["impact"], *n["keys"]])
            # seuls les marqueurs d'équipe restent entre accolades
            assert not re.findall(r"\{(?!T:(home|away):\w+\}|TN:)[^}]*\}", text), (sec, text)
    s1 = notes["s1"]
    assert "{T:home:Sub} gagne 2–1." in s1["fr"]["lead"]
    assert "2,10" in s1["fr"]["lead"] and "2.10" in s1["en"]["lead"]
    assert "Joueur h1" in s1["fr"]["impact"]
    assert "55'" in " ".join(notes["s5"]["fr"]["keys"])
    # même match, même texte : le choix des tournures est reproductible
    assert analyst.match_notes(game(), ctx, {"players": {}}) == notes

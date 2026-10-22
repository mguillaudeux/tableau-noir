from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from tableau_noir import classic, xg
from tableau_noir.model import Match, Player, Team, frame


def row(**kw: object) -> dict[str, object]:
    base = {
        "match_id": "x",
        "period": 1,
        "t": 0.0,
        "minute": 0,
        "team": "A",
        "player": "a1",
        "set_piece": "open",
        "possession": None,
    }
    return base | kw


def tiny_match() -> Match:
    rows = [
        row(
            kind="pass", ok=True, x=20, y=34, ex=55, ey=34, t=0, possession="A"
        ),  # 35 m gagnés : progressive
        row(kind="pass", ok=True, x=60, y=34, ex=65, ey=34, t=5, possession="A"),  # 5 m : non
        row(kind="shot", ok=True, x=95, y=34, xg=0.4, goal=True, t=10, possession="A"),
        row(
            kind="pass",
            ok=False,
            team="B",
            player="b1",
            x=30,
            y=30,
            ex=40,
            ey=30,
            t=20,
            possession="B",
        ),
        row(kind="tackle", ok=True, x=70, y=30, t=24, possession="B"),
        row(kind="own_goal", team="B", player="b1", t=40),
        row(kind="foul", team="B", player="b1", card="red", t=50),
    ]
    players = {
        "a1": Player("a1", "Alpha", "A", "FW", True, 90),
        "b1": Player("b1", "Beta", "B", "DF", True, 50),
    }
    return Match(
        "x",
        "statsbomb",
        "C",
        "S",
        "2022-01-01",
        "Final",
        Team("A", "A", 2),
        Team("B", "B", 0),
        90,
        players,
        frame(rows),
    )


def test_stats_equipe() -> None:
    s = classic.team_stats(tiny_match())
    a, b = s["A"], s["B"]
    assert a["progressive"] == 1 and a["passes_ok"] == 2 and a["pass_rate"] == 1.0
    assert a["xg"] == 0.4 and a["big_chances"] == 1 and a["shots"] == 1 and a["on_target"] == 1
    assert b["red"] == 1 and b["fouls"] == 1
    assert a["possession"] + b["possession"] == pytest.approx(1)
    assert a["tackles_won"] == 1


def test_buts_contre_son_camp() -> None:
    goals = classic.goals_table(tiny_match())
    assert [g["team"] for g in goals] == ["A", "A"]
    assert goals[1]["own_goal"] and goals[1]["player"] == "b1"


def test_joueurs() -> None:
    p = {r["id"]: r for r in classic.player_stats(tiny_match())}
    assert p["a1"]["goals"] == 1 and p["a1"]["progressive"] == 1 and p["a1"]["xg"] == 0.4


def test_xg_logistique() -> None:
    rng = np.random.default_rng(0)
    n = 4000
    x = rng.uniform(70, 104, n)
    y = rng.uniform(10, 58, n)
    shots = pd.DataFrame({"x": x, "y": y, "body": "foot", "set_piece": "open"})
    dist, angle = xg.geometry(x, y)
    p = 1 / (1 + np.exp(-(-1 - 0.1 * dist + 1.5 * angle)))
    shots["goal"] = rng.random(n) < p
    pens = pd.DataFrame(
        {
            "x": [94.0] * 10,
            "y": [34.0] * 10,
            "body": "foot",
            "set_piece": "penalty",
            "goal": [True] * 7 + [False] * 3,
        }
    )
    m = xg.fit(pd.concat([shots, pens], ignore_index=True))
    assert m.coef[1] < 0 and m.coef[2] > 0  # plus loin : moins d'xG ; plus d'angle : plus d'xG
    assert m.penalty == 0.7
    pred = m.predict(pens.head(1))
    assert pred[0] == 0.7

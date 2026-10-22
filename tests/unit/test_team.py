from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
import pytest

from tableau_noir import team
from tableau_noir.model import Match, Player, Team, frame


def pos(xs: Sequence[float]) -> list[dict[str, Any]]:
    out = [{"position": "GK", "x": 5.0}]
    return out + [{"position": "X", "x": x} for x in xs]


def test_formation_433() -> None:
    xs = [20, 21, 22, 23, 45, 47, 46, 75, 76, 77]
    assert team.formation(pos(xs)) == "4-3-3"


def test_formation_4231_quand_la_4e_ligne_se_voit() -> None:
    xs = [20, 21, 22, 23, 40, 41, 60, 61, 62, 85]
    assert team.formation(pos(xs)) == "4-2-3-1"


def test_formation_ligne_arriere_de_3_a_5() -> None:
    # sans la contrainte, deux défenseurs isolés donneraient un « 2-… »
    xs = [10, 11, 30, 31, 32, 33, 34, 70, 71, 72]
    assert team.formation(pos(xs)).split("-")[0] in {"3", "4", "5"}  # type: ignore[union-attr]


def test_formation_trop_peu_de_joueurs() -> None:
    assert team.formation(pos([20, 40, 60])) is None


def test_couloirs() -> None:
    lanes = team.lane_of(np.array([1.0, 20.0, 34.0, 50.0, 67.0]))
    assert list(lanes) == [0, 1, 2, 3, 4]


def row(**kw: object) -> dict[str, object]:
    base = {"match_id": "x", "period": 1, "minute": 0, "set_piece": "open", "y": 34.0}
    return base | kw


def transition_match() -> Match:
    rows = [
        row(t=0.0, team="A", player="a1", kind="pass", ok=True, x=40.0, possession="A"),
        row(t=2.0, team="A", player="a2", kind="pass", ok=False, x=60.0, possession="A"),
        row(t=3.0, team="B", player="b1", kind="pass", ok=True, x=45.0, possession="B"),
        row(t=6.0, team="A", player="a1", kind="recovery", ok=True, x=55.0, possession="A"),
        row(t=8.0, team="A", player="a1", kind="pass", ok=False, x=70.0, possession="A"),
        row(t=9.0, team="B", player="b1", kind="carry", ok=True, x=35.0, possession="B"),
        row(t=19.0, team="B", player="b2", kind="shot", ok=False, x=90.0, xg=0.2, possession="B"),
        row(t=30.0, team="A", player="a1", kind="pass", ok=True, x=10.0, possession="A"),
    ]
    players = {
        p: Player(p, p, p[0].upper(), "MF", True, 90, None) for p in ("a1", "a2", "b1", "b2")
    }
    return Match(
        "x",
        "wyscout",
        "C",
        "S",
        "2022-01-01",
        "Final",
        Team("A", "A", 0),
        Team("B", "B", 0),
        90,
        players,
        frame(rows),
    )


def test_transitions() -> None:
    tr = team.transitions(transition_match())
    assert len(tr) == 2
    first, second = tr.iloc[0], tr.iloc[1]
    assert first["regain"] == pytest.approx(4.0) and first["shots_against"] == 0
    assert second["regain"] == pytest.approx(22.0) and second["shots_against"] == 1
    assert second["xg_against"] == pytest.approx(0.2)


def test_pressing_sans_evenement_de_pression() -> None:
    m = transition_match()
    p = team.pressing(m, "A", team.transitions(m))
    assert p["source"] == "defensive_actions" and p["counterpress_share"] is None
    assert p["regain_hist"] == [1, 0, 0, 1]
    assert p["regain_5s"] == pytest.approx(0.5)


def test_indice_relationniste() -> None:
    stats = {
        "short_share": {"mean": 0.5, "sd": 0.1},
        "lanes": {"mean": 4.0, "sd": 0.5},
        "roaming": {"mean": 8.0, "sd": 0.0},  # écart-type nul : ingrédient ignoré
    }
    rel = {"short_share": 0.6, "lanes": 3.5, "roaming": 12.0, "proximity": None}
    assert team.relation_index(rel, stats) == pytest.approx(1.0)
    assert team.relation_index({"short_share": None}, stats) is None


def test_contexte_de_competition() -> None:
    def analysis(short: float) -> dict[str, Any]:
        return {
            "relation": {"short_share": short},
            "pressing": {},
            "recovery": {},
            "shape": {"block": None},
        }

    ctx = team.context(
        [("A", "A", analysis(0.4)), ("B", "B", analysis(0.5)), ("C", "C", analysis(0.6))]
    )
    s = ctx["stats"]["relation"]["short_share"]
    assert s["mean"] == pytest.approx(0.5) and s["min"] == 0.4 and s["max"] == 0.6
    assert [t["id"] for t in ctx["teams"]] == ["A", "B", "C"]
    assert ctx["teams"][1]["index"] == pytest.approx(0.0)

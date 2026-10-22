from __future__ import annotations

from tableau_noir.sources import statsbomb as sb
from tableau_noir.sources import wyscout as wy


def sb_event(typ: str, **extra: object) -> dict[str, object]:
    return {
        "period": 1,
        "timestamp": "00:10:30.000",
        "minute": 10,
        "second": 30,
        "team": {"id": 1},
        "player": {"id": 9},
        "possession_team": {"id": 1},
        "location": [60.0, 40.0],
        "type": {"name": typ},
        **extra,
    }


def test_statsbomb_metres_et_passes() -> None:
    rows = sb.event_rows(
        "sb-1", [sb_event("Pass", **{"pass": {"end_location": [120, 80], "goal_assist": True}})]
    )
    r = rows[0]
    assert r["kind"] == "pass" and r["ok"] is True and r["assist"] is True and r["key_pass"] is True
    assert (r["x"], r["y"]) == (52.5, 34.0)
    assert (r["ex"], r["ey"]) == (105.0, 68.0)
    assert r["t"] == 630.0


def test_statsbomb_tir_carton_hors_jeu() -> None:
    shot = sb_event(
        "Shot",
        shot={
            "statsbomb_xg": 0.76,
            "outcome": {"name": "Goal"},
            "type": {"name": "Penalty"},
            "body_part": {"name": "Right Foot"},
        },
    )
    foul = sb_event("Foul Committed", foul_committed={"card": {"name": "Second Yellow"}})
    off = sb_event("Pass", **{"pass": {"outcome": {"name": "Pass Offside"}}})
    rows = sb.event_rows("sb-1", [shot, foul, off])
    kinds = [r["kind"] for r in rows]
    assert kinds == ["shot", "foul", "pass", "offside"]
    assert rows[0]["goal"] and rows[0]["set_piece"] == "penalty" and rows[0]["xg"] == 0.76
    assert rows[1]["card"] == "second_yellow"
    assert rows[2]["ok"] is False


def test_statsbomb_duels_aeriens() -> None:
    rows = sb.event_rows(
        "sb-1",
        [
            sb_event("Duel", duel={"type": {"name": "Aerial Lost"}}),
            sb_event("Clearance", clearance={"aerial_won": True}),
        ],
    )
    aerial = [r for r in rows if r.get("aerial")]
    assert [r["ok"] for r in aerial] == [False, True]


def wy_event(name: str, sub: str, tags: list[int], **extra: object) -> dict[str, object]:
    return {
        "eventName": name,
        "subEventName": sub,
        "tags": [{"id": t} for t in tags],
        "matchPeriod": "2H",
        "eventSec": 60.0,
        "teamId": 5,
        "playerId": 7,
        "positions": [{"x": 50, "y": 50}, {"x": 100, "y": 0}],
        **extra,
    }


def test_wyscout_codes() -> None:
    rows = wy.event_rows(
        "wy-1",
        [
            wy_event("Pass", "Simple pass", [1801, 302]),
            wy_event("Free Kick", "Penalty", [101, 1801]),
            wy_event("Duel", "Air duel", [703]),
            wy_event("Foul", "Foul", [1702]),
            wy_event("Pass", "Cross", [1802, 1401, 102]),
        ],
    )
    kinds = [r["kind"] for r in rows]
    assert kinds == ["pass", "shot", "duel", "foul", "pass", "own_goal", "interception"]
    assert rows[0]["key_pass"] and rows[0]["t"] == 45 * 60 + 60
    assert rows[1]["set_piece"] == "penalty" and rows[1]["goal"]
    assert rows[2]["aerial"] and rows[2]["ok"]
    assert rows[3]["card"] == "yellow"
    assert (rows[0]["ex"], rows[0]["ey"]) == (105.0, 0.0)


def test_wyscout_noms_et_phases() -> None:
    assert wy.fix_text(r"Š. Vrsaljko") == "Š. Vrsaljko"
    sizes = [(1, 8), (2, 4), (3, 2), (4, 1), (5, 1)]
    metas, i = [], 0
    for rid, n in sizes:
        for _ in range(n):
            i += 1
            metas.append(
                {
                    "wyId": i,
                    "roundId": rid,
                    "gameweek": 0,
                    "dateutc": f"2018-07-{rid:02d}",
                    "groupName": "",
                }
            )
    metas.append(
        {"wyId": 99, "roundId": 0, "gameweek": 2, "dateutc": "2018-06-20", "groupName": "Group C"}
    )
    st = wy._stages(metas)
    assert st[15] == "3rd Place Final" and st[16] == "Final"
    assert st[1] == "Round of 16" and st[9] == "Quarter-finals" and st[13] == "Semi-finals"
    assert st[99] == "Group C"

"""Wyscout public dataset (Pappalardo et al., 2019, CC BY 4.0) → format commun.

Les fichiers sont lus en local dans `data/raw/wyscout/` (figshare, collection 4415000) :
`events/events_<Compétition>.json`, `matches/matches_<Compétition>.json`, `players.json`,
`teams.json`, `competitions.json`.
"""

from __future__ import annotations

import json
import re
from functools import cache
from pathlib import Path
from typing import Any

from tableau_noir.model import PERIOD_OFFSET, Match, Player, Team, frame

RAW = Path("data/raw/wyscout")
SX, SY = 1.05, 0.68  # pourcentages → mètres (105 × 68)
PERIODS = {"1H": 1, "2H": 2, "E1": 3, "E2": 4, "P": 5}
ON_BALL = {"Pass", "Free Kick", "Shot", "Others on the ball"}
FREE_KICK = {
    "Corner": ("pass", "corner"),
    "Free Kick": ("pass", "free_kick"),
    "Free kick cross": ("pass", "free_kick"),
    "Free kick shot": ("shot", "free_kick"),
    "Goal kick": ("pass", "goal_kick"),
    "Penalty": ("shot", "penalty"),
    "Throw in": ("pass", "throw_in"),
}
CARDS = {1701: "red", 1703: "second_yellow", 1702: "yellow"}
POSITIONS = {"GK": "GK", "DF": "DF", "MD": "MF", "FW": "FW"}
NAMES = {  # nom du fichier → (nom de la compétition, saison)
    "World_Cup": ("FIFA World Cup", "2018"),
    "European_Championship": ("UEFA Euro", "2016"),
    "France": ("Ligue 1", "2017/2018"),
    "England": ("Premier League", "2017/2018"),
    "Spain": ("La Liga", "2017/2018"),
    "Italy": ("Serie A", "2017/2018"),
    "Germany": ("1. Bundesliga", "2017/2018"),
}


def fix_text(s: str) -> str:
    """Les noms du jeu de données contiennent des séquences « \\uXXXX » restées littérales."""
    return re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)


@cache
def _json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


@cache
def players_index(raw: Path = RAW) -> dict[int, dict[str, Any]]:
    return {int(p["wyId"]): p for p in _json(raw / "players.json")}


@cache
def teams_index(raw: Path = RAW) -> dict[int, dict[str, Any]]:
    return {int(t["wyId"]): t for t in _json(raw / "teams.json")}


def matches(key: str, raw: Path = RAW) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = _json(raw / "matches" / f"matches_{key}.json")
    return out


@cache
def _events_by_match(key: str, raw: Path = RAW) -> dict[int, list[dict[str, Any]]]:
    by: dict[int, list[dict[str, Any]]] = {}
    for e in _json(raw / "events" / f"events_{key}.json"):
        by.setdefault(int(e["matchId"]), []).append(e)
    return by


def _xy(pos: dict[str, float]) -> tuple[float, float]:
    return round(pos["x"] * SX, 2), round(pos["y"] * SY, 2)


def event_rows(match_id: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for e in events:
        period = PERIODS[e["matchPeriod"]]
        if period == 5:
            continue
        tags = {int(t["id"]) for t in e.get("tags", [])}
        t = PERIOD_OFFSET[period] + float(e["eventSec"])
        name, sub = e["eventName"], e["subEventName"]
        pos = e.get("positions") or []
        x, y = _xy(pos[0]) if pos else (None, None)
        ex, ey = _xy(pos[1]) if len(pos) > 1 else (None, None)
        base: dict[str, Any] = {
            "match_id": match_id,
            "period": period,
            "t": t,
            "minute": int(t // 60),
            "team": str(e["teamId"]),
            "player": str(e["playerId"]) if e.get("playerId") else None,
            "x": x,
            "y": y,
            "set_piece": "open",
            "possession": str(e["teamId"]) if name in ON_BALL else None,
        }
        accurate = True if 1801 in tags else False if 1802 in tags else None
        card = next((c for tag, c in CARDS.items() if tag in tags), None)
        row: dict[str, Any] | None = None

        if name == "Pass":
            row = base | {
                "kind": "pass",
                "ok": accurate,
                "ex": ex,
                "ey": ey,
                "body": "head" if sub == "Head pass" else "foot",
                "key_pass": 302 in tags or 301 in tags,
                "assist": 301 in tags,
            }
        elif name == "Free Kick":
            kind, sp = FREE_KICK.get(sub, ("pass", "free_kick"))
            if kind == "shot":
                row = base | {
                    "kind": "shot",
                    "ok": accurate,
                    "goal": 101 in tags,
                    "set_piece": sp,
                    "body": "foot",
                }
            else:
                row = base | {
                    "kind": "pass",
                    "ok": accurate,
                    "ex": ex,
                    "ey": ey,
                    "set_piece": sp,
                    "key_pass": 302 in tags or 301 in tags,
                    "assist": 301 in tags,
                }
        elif name == "Shot":
            row = base | {
                "kind": "shot",
                "ok": accurate,
                "goal": 101 in tags,
                "body": "head" if 403 in tags else "foot",
            }
        elif name == "Duel":
            won = True if 703 in tags else False if 701 in tags else None
            if sub == "Air duel":
                row = base | {"kind": "duel", "ok": won, "aerial": True}
            elif sub == "Ground attacking duel" and tags & {503, 504}:
                row = base | {"kind": "dribble", "ok": won}
            elif sub == "Ground defending duel":
                row = base | {"kind": "tackle", "ok": won}
            else:
                row = base | {"kind": "duel", "ok": won, "aerial": False}
        elif name == "Others on the ball":
            if sub == "Acceleration":
                row = base | {"kind": "carry", "ok": True, "ex": ex, "ey": ey}
            elif sub == "Clearance":
                row = base | {"kind": "clearance", "ok": True}
        elif name == "Foul":
            row = base | {"kind": "foul", "card": card}
            card = None
        elif name == "Offside":
            row = base | {"kind": "offside"}
        elif name == "Save attempt":
            row = base | {"kind": "save", "ok": 101 not in tags}
        if row is not None:
            rows.append(row)
        if 102 in tags:
            rows.append(base | {"kind": "own_goal"})
        if 1401 in tags:
            rows.append(base | {"kind": "interception", "ok": True})
        if card:
            rows.append(base | {"kind": "card", "card": card})
    return rows


def _stages(meta_all: list[dict[str, Any]]) -> dict[int, str]:
    """Phase de chaque match. Le jeu de données n'indique que la journée (`gameweek`, 0 pour les
    matchs à élimination) et un identifiant de tour : on nomme les tours d'après leur taille."""
    out: dict[int, str] = {}
    rounds: dict[int, list[dict[str, Any]]] = {}
    for m in meta_all:
        if int(m.get("gameweek") or 0) > 0:
            out[int(m["wyId"])] = (
                f"Group {str(m.get('groupName', '')).replace('Group ', '')}".strip()
            )
        else:
            rounds.setdefault(int(m["roundId"]), []).append(m)
    ordered = sorted(rounds.values(), key=lambda ms: min(x["dateutc"] for x in ms))
    names = {8: "Round of 16", 4: "Quarter-finals", 2: "Semi-finals"}
    for i, ms in enumerate(ordered):
        last = i == len(ordered) - 1
        name = names.get(len(ms), "Final" if last else "3rd Place Final")
        for m in ms:
            out[int(m["wyId"])] = name
    return out


def load_match(
    key: str, meta: dict[str, Any], raw: Path = RAW, stages: dict[int, str] | None = None
) -> Match:
    wid = int(meta["wyId"])
    competition, season = NAMES[key]
    players_db, teams_db = players_index(raw), teams_index(raw)
    duration = 90.0 if meta.get("duration") == "Regular" else 120.0
    events = _events_by_match(key, raw).get(wid, [])

    players: dict[str, Player] = {}
    teams: dict[str, Team] = {}
    for tid, td in meta["teamsData"].items():
        teams[td["side"]] = Team(
            id=str(tid),
            name=fix_text(teams_db.get(int(tid), {}).get("name", str(tid))),
            score=int(td["score"] if meta.get("duration") == "Regular" else td["scoreET"]),
            penalties=int(td["scoreP"]) if meta.get("duration") == "Penalties" else None,
        )
        form = td.get("formation") or {}
        subs = form.get("substitutions") or []
        if isinstance(subs, str):
            subs = []
        off = {int(s["playerOut"]): float(s["minute"]) for s in subs}
        on = {int(s["playerIn"]): float(s["minute"]) for s in subs}
        squad = [(p, True) for p in form.get("lineup") or []] + [
            (p, False) for p in form.get("bench") or []
        ]
        for p, starter in squad:
            pid = int(p["playerId"])
            if not starter and pid not in on:
                continue
            start = 0.0 if starter else on[pid]
            end = off.get(pid, duration)
            red = str(p.get("redCards", "0"))
            if red not in ("0", ""):
                end = min(end, float(red))
            info = players_db.get(pid, {})
            players[str(pid)] = Player(
                id=str(pid),
                name=fix_text(info.get("shortName", str(pid))),
                team=str(tid),
                position=POSITIONS.get(info.get("role", {}).get("code2", ""), ""),
                starter=starter,
                minutes=round(max(0.0, end - start), 1),
            )
    return Match(
        id=f"wy-{wid}",
        source="wyscout",
        competition=competition,
        season=season,
        date=meta["dateutc"][:10],
        stage=(stages or {}).get(wid, f"Matchday {meta.get('gameweek')}"),
        home=teams["home"],
        away=teams["away"],
        duration=duration,
        players=players,
        events=frame(event_rows(f"wy-{wid}", events)),
    )


def load_competition(key: str, raw: Path = RAW) -> list[Match]:
    metas = matches(key, raw)
    stages = _stages(metas) if NAMES[key][0] in ("FIFA World Cup", "UEFA Euro") else {}
    return [load_match(key, m, raw, stages) for m in metas]

"""Hudl StatsBomb Open Data → format commun.

Les fichiers sont téléchargés depuis https://github.com/hudl/open-data puis gardés en cache dans
`data/raw/statsbomb/` (jamais versionnés : le contrat StatsBomb interdit de les redistribuer).
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

import pandas as pd

from tableau_noir.model import PERIOD_OFFSET, PITCH_X, PITCH_Y, Match, Player, Team, frame

BASE = "https://raw.githubusercontent.com/hudl/open-data/master/data/"
CACHE = Path("data/raw/statsbomb")
SX, SY = PITCH_X / 120, PITCH_Y / 80

PASS_SET_PIECE = {
    "Corner": "corner",
    "Free Kick": "free_kick",
    "Throw-in": "throw_in",
    "Goal Kick": "goal_kick",
    "Kick Off": "kick_off",
}
SHOT_SET_PIECE = {"Penalty": "penalty", "Free Kick": "free_kick", "Corner": "corner"}
ON_TARGET = {"Goal", "Saved", "Saved To Post"}
WON = {"Won", "Success", "Success In Play", "Success Out", "Success To Team"}
SAVES = {"Shot Saved", "Shot Saved Off T", "Shot Saved to Post", "Penalty Saved", "Save"}
CARDS = {"Yellow Card": "yellow", "Second Yellow": "second_yellow", "Red Card": "red"}


def fetch(path: str, cache: Path = CACHE) -> Any:
    """Lit un fichier JSON du dépôt, en le téléchargeant une seule fois."""
    local = cache / path
    if not local.exists():
        local.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(BASE + path, timeout=60) as r:
            local.write_bytes(r.read())
    return json.loads(local.read_text(encoding="utf-8"))


def competitions(cache: Path = CACHE) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = fetch("competitions.json", cache)
    return out


def matches(competition_id: int, season_id: int, cache: Path = CACHE) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = fetch(f"matches/{competition_id}/{season_id}.json", cache)
    return out


def _xy(loc: list[float] | None) -> tuple[float | None, float | None]:
    if not loc:
        return None, None
    return round(loc[0] * SX, 2), round(loc[1] * SY, 2)


def _clock(s: str) -> float:
    """« 12:03.456 » ou « 00:12:03.456 » → secondes."""
    parts = [float(p) for p in s.split(":")]
    sec = 0.0
    for p in parts:
        sec = sec * 60 + p
    return sec


def _body(name: str | None) -> str | None:
    if not name:
        return None
    return "head" if name == "Head" else "foot" if "Foot" in name else "other"


def _position_group(name: str) -> str:
    if name == "Goalkeeper":
        return "GK"
    if "Back" in name:
        return "DF"
    if "Midfield" in name:
        return "MF"
    return "FW"


def event_rows(match_id: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Traduit les événements StatsBomb en lignes du format commun."""
    rows: list[dict[str, Any]] = []
    for e in events:
        period = int(e["period"])
        base: dict[str, Any] = {
            "match_id": match_id,
            "period": period,
            "t": PERIOD_OFFSET[period] + _clock(e["timestamp"]),
            "minute": int(e["minute"]),
            "team": str(e["team"]["id"]),
            "player": str(e["player"]["id"]) if "player" in e else None,
            "possession": str(e["possession_team"]["id"]) if "possession_team" in e else None,
            "set_piece": "open",
            "event_id": e["id"],
            "chain": int(e.get("possession", -1)),
            "counterpress": bool(e.get("counterpress", False)),
        }
        base["x"], base["y"] = _xy(e.get("location"))
        typ = e["type"]["name"]
        row: dict[str, Any] | None = None
        extra: list[dict[str, Any]] = []

        if typ == "Pass":
            p = e["pass"]
            ex, ey = _xy(p.get("end_location"))
            outcome = p.get("outcome", {}).get("name")
            row = base | {
                "kind": "pass",
                "ok": outcome is None,
                "ex": ex,
                "ey": ey,
                "set_piece": PASS_SET_PIECE.get(p.get("type", {}).get("name", ""), "open"),
                "body": _body(p.get("body_part", {}).get("name")),
                "key_pass": bool(p.get("shot_assist") or p.get("goal_assist")),
                "assist": bool(p.get("goal_assist")),
                "recipient": str(p["recipient"]["id"]) if "recipient" in p else None,
            }
            if outcome == "Pass Offside":
                extra.append(base | {"kind": "offside"})
            if p.get("aerial_won"):
                extra.append(base | {"kind": "duel", "ok": True, "aerial": True})
        elif typ == "Shot":
            s = e["shot"]
            end = s.get("end_location") or []
            ex, ey = _xy(end[:2])
            outcome = s.get("outcome", {}).get("name")
            row = base | {
                "kind": "shot",
                "ok": outcome in ON_TARGET,
                "ex": ex,
                "ey": ey,
                "xg": float(s.get("statsbomb_xg", 0.0)),
                "goal": outcome == "Goal",
                "set_piece": SHOT_SET_PIECE.get(s.get("type", {}).get("name", ""), "open"),
                "body": _body(s.get("body_part", {}).get("name")),
            }
            if s.get("aerial_won"):
                extra.append(base | {"kind": "duel", "ok": True, "aerial": True})
        elif typ == "Carry":
            ex, ey = _xy(e["carry"].get("end_location"))
            row = base | {"kind": "carry", "ok": True, "ex": ex, "ey": ey}
        elif typ == "Dribble":
            outcome = e.get("dribble", {}).get("outcome", {}).get("name")
            row = base | {"kind": "dribble", "ok": outcome == "Complete"}
        elif typ == "Dribbled Past":
            row = base | {"kind": "duel", "ok": False, "aerial": False}
        elif typ == "Duel":
            d = e.get("duel", {})
            dtype = d.get("type", {}).get("name")
            outcome = d.get("outcome", {}).get("name")
            if dtype == "Aerial Lost":
                row = base | {"kind": "duel", "ok": False, "aerial": True}
            else:
                row = base | {"kind": "tackle", "ok": outcome in WON}
        elif typ == "50/50":
            outcome = e.get("50_50", {}).get("outcome", {}).get("name")
            row = base | {"kind": "duel", "ok": outcome in WON, "aerial": False}
        elif typ == "Pressure":
            row = base | {"kind": "pressure"}
        elif typ == "Interception":
            outcome = e.get("interception", {}).get("outcome", {}).get("name")
            row = base | {"kind": "interception", "ok": outcome in WON}
        elif typ == "Ball Recovery":
            row = base | {
                "kind": "recovery",
                "ok": not e.get("ball_recovery", {}).get("recovery_failure"),
            }
        elif typ == "Clearance":
            row = base | {"kind": "clearance", "ok": True}
            if e.get("clearance", {}).get("aerial_won"):
                extra.append(base | {"kind": "duel", "ok": True, "aerial": True})
        elif typ == "Block":
            row = base | {"kind": "block", "ok": True}
        elif typ == "Foul Committed":
            card = CARDS.get(e.get("foul_committed", {}).get("card", {}).get("name", ""))
            row = base | {"kind": "foul", "card": card}
        elif typ == "Bad Behaviour":
            card = CARDS.get(e.get("bad_behaviour", {}).get("card", {}).get("name", ""))
            row = base | {"kind": "card", "card": card} if card else None
        elif typ == "Offside":
            row = base | {"kind": "offside"}
        elif typ == "Goal Keeper":
            gk = e["goalkeeper"].get("type", {}).get("name")
            row = base | {"kind": "save", "ok": True} if gk in SAVES else None
        elif typ == "Own Goal Against":
            row = base | {"kind": "own_goal"}
        elif typ in ("Miscontrol", "Dispossessed"):
            row = base | {"kind": "miscontrol", "ok": False}
            if e.get("miscontrol", {}).get("aerial_won"):
                extra.append(base | {"kind": "duel", "ok": True, "aerial": True})
        if row is not None:
            rows.append(row)
        rows.extend(extra)
    return rows


def _penalty_shootout(events: list[dict[str, Any]], team_id: int) -> int | None:
    pens = [e for e in events if e["period"] == 5 and e["type"]["name"] == "Shot"]
    if not pens:
        return None
    return sum(
        1 for e in pens if e["team"]["id"] == team_id and e["shot"]["outcome"]["name"] == "Goal"
    )


def load_match(meta: dict[str, Any], cache: Path = CACHE) -> Match:
    """Un match StatsBomb complet : métadonnées, joueurs (minutes jouées), événements."""
    mid = int(meta["match_id"])
    events: list[dict[str, Any]] = fetch(f"events/{mid}.json", cache)
    lineups: list[dict[str, Any]] = fetch(f"lineups/{mid}.json", cache)
    last = max(e["minute"] + e["second"] / 60 for e in events if e["period"] <= 4)
    duration = 120.0 if any(e["period"] in (3, 4) for e in events) else 90.0

    players: dict[str, Player] = {}
    for squad in lineups:
        for p in squad["lineup"]:
            spans = p.get("positions") or []
            if not spans:
                continue
            minutes = 0.0
            for s in spans:
                start = _clock(s["from"]) / 60
                end = _clock(s["to"]) / 60 if s.get("to") else last
                minutes += max(0.0, end - start)
            players[str(p["player_id"])] = Player(
                id=str(p["player_id"]),
                name=p.get("player_nickname") or p["player_name"],
                team=str(squad["team_id"]),
                position=_position_group(spans[0]["position"]),
                starter=spans[0].get("start_reason") == "Starting XI",
                minutes=round(min(minutes, last), 1),
                number=p.get("jersey_number"),
            )

    def team(side: str) -> Team:
        t = meta[f"{side}_team"]
        tid = t[f"{side}_team_id"]
        return Team(
            id=str(tid),
            name=t[f"{side}_team_name"],
            score=int(meta[f"{side}_score"]),
            penalties=_penalty_shootout(events, tid),
        )

    m = Match(
        id=f"sb-{mid}",
        source="statsbomb",
        competition=meta["competition"]["competition_name"],
        season=meta["season"]["season_name"],
        date=meta["match_date"],
        stage=meta.get("competition_stage", {}).get("name", ""),
        home=team("home"),
        away=team("away"),
        duration=duration,
        players=players,
        events=frame(event_rows(f"sb-{mid}", [e for e in events if e["period"] <= 4])),
        has_360=meta.get("match_status_360") == "available",
        formations=_formations(events),
    )
    return m


def _formations(events: list[dict[str, Any]]) -> dict[str, str]:
    """Formation annoncée au coup d'envoi (« 433 » → « 4-3-3 »)."""
    out: dict[str, str] = {}
    for e in events:
        if e["type"]["name"] == "Starting XI":
            f = str(e.get("tactics", {}).get("formation", ""))
            out[str(e["team"]["id"])] = "-".join(f)
    return out


def load_frames(match_id: int, cache: Path = CACHE) -> pd.DataFrame:
    """Les images 360 d'un match : pour chaque événement, les joueurs visibles (en mètres, dans le
    repère de l'équipe qui réalise l'action, qui attaque vers la droite)."""
    data: list[dict[str, Any]] = fetch(f"three-sixty/{match_id}.json", cache)
    rows = []
    for f in data:
        for p in f["freeze_frame"]:
            x, y = p["location"]
            rows.append(
                (
                    f["event_uuid"],
                    bool(p["teammate"]),
                    bool(p.get("actor")),
                    bool(p.get("keeper")),
                    round(x * SX, 2),
                    round(y * SY, 2),
                )
            )
    return pd.DataFrame(rows, columns=["event_id", "teammate", "actor", "keeper", "x", "y"])

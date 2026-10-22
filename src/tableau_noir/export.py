"""Export JSON pour le site : un catalogue des matchs, puis un fichier par match.

Le site ne reçoit que des résultats calculés (statistiques, tirs, joueurs), jamais les fichiers
d'événements bruts.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from tableau_noir import classic
from tableau_noir.model import Match

CREDITS = {
    "statsbomb": "Hudl StatsBomb Open Data",
    "wyscout": "Wyscout, via Pappalardo et al. (2019), CC BY 4.0",
}
XG_SOURCE = {"statsbomb": "statsbomb", "wyscout": "tableau-noir"}


def _team(m: Match, side: str) -> dict[str, Any]:
    t = m.home if side == "home" else m.away
    return {"id": t.id, "name": t.name, "score": t.score, "penalties": t.penalties}


def match_summary(m: Match) -> dict[str, Any]:
    return {
        "id": m.id,
        "date": m.date,
        "stage": m.stage,
        "home": _team(m, "home"),
        "away": _team(m, "away"),
        "duration": m.duration,
        "has_360": m.has_360,
    }


def match_json(m: Match) -> dict[str, Any]:
    stats = classic.team_stats(m)
    return {
        "meta": match_summary(m)
        | {
            "source": m.source,
            "credit": CREDITS[m.source],
            "xg_model": XG_SOURCE[m.source],
            "competition": m.competition,
            "season": m.season,
        },
        "stats": {"home": stats[m.home.id], "away": stats[m.away.id]},
        "shots": [
            s | {"side": "home" if s["team"] == m.home.id else "away"}
            for s in classic.shots_table(m)
        ],
        "goals": [
            g | {"side": "home" if g["team"] == m.home.id else "away"}
            for g in classic.goals_table(m)
        ],
        "players": [
            p | {"side": "home" if p["team"] == m.home.id else "away"}
            for p in classic.player_stats(m)
        ],
    }


def write_json(data: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def export(groups: Iterable[tuple[dict[str, Any], list[Match]]], out: Path) -> dict[str, Any]:
    """`groups` : (description de la compétition, matchs). Écrit le catalogue et les matchs."""
    catalogue: list[dict[str, Any]] = []
    for comp, ms in groups:
        ms = sorted(ms, key=lambda m: m.date)
        for m in ms:
            write_json(match_json(m), out / "matches" / f"{m.id}.json")
        catalogue.append(comp | {"matches": [match_summary(m) for m in ms]})
    data = {"competitions": catalogue}
    write_json(data, out / "catalogue.json")
    return data

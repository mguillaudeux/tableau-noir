"""Export JSON pour le site : un catalogue des matchs, puis un fichier par match.

Le site ne reçoit que des résultats calculés (statistiques, tirs, joueurs), jamais les fichiers
d'événements bruts.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from tableau_noir import classic, team
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


def match_json(m: Match, comp: str) -> dict[str, Any]:
    stats = classic.team_stats(m)
    side = {m.home.id: "home", m.away.id: "away"}
    analysis = team.team_analysis(m)
    return {
        "meta": match_summary(m)
        | {
            "comp": comp,
            "source": m.source,
            "credit": CREDITS[m.source],
            "xg_model": XG_SOURCE[m.source],
            "competition": m.competition,
            "season": m.season,
        },
        "stats": {"home": stats[m.home.id], "away": stats[m.away.id]},
        "shots": [s | {"side": side[s["team"]]} for s in classic.shots_table(m)],
        "goals": [g | {"side": side[g["team"]]} for g in classic.goals_table(m)],
        "players": [p | {"side": side[p["team"]]} for p in classic.player_stats(m)],
        "team": {side[tid]: a for tid, a in analysis.items()},
    }


def write_json(data: Any, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return path


def export_competition(comp: dict[str, Any], matches: Iterable[Match], out: Path) -> dict[str, Any]:
    """Écrit un fichier par match (au fil de l'eau, pour ne pas garder les images 360 en mémoire),
    puis le contexte de la compétition. Renvoie l'entrée du catalogue."""
    summaries, analyses = [], []
    for m in matches:
        data = match_json(m, comp["id"])
        write_json(data, out / "matches" / f"{m.id}.json")
        summaries.append(match_summary(m))
        for s in ("home", "away"):
            t = data["meta"][s]
            analyses.append((t["id"], t["name"], data["team"][s]))
    write_json(team.context(analyses), out / "context" / f"{comp['id']}.json")
    return comp | {"matches": sorted(summaries, key=lambda x: x["date"])}


def write_catalogue(entries: list[dict[str, Any]], out: Path) -> dict[str, Any]:
    data = {"competitions": entries}
    write_json(data, out / "catalogue.json")
    return data

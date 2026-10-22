"""Export JSON pour le site : un catalogue des matchs, puis un fichier par match.

Le site ne reçoit que des résultats calculés (statistiques, tirs, joueurs), jamais les fichiers
d'événements bruts.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from tableau_noir import analyst, classic, players, team
from tableau_noir.model import Match
from tableau_noir.xt import XTModel

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
    """Tout ce que le site affiche pour un match, sauf les sections joueurs (voir `match_data`)."""
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


def match_data(m: Match, comp: str, xt_model: XTModel) -> tuple[dict[str, Any], dict[str, Any]]:
    """Le JSON d'un match, enrichi des données joueurs (xT, poste), et les sommes internes de
    gravité, qui ne seront converties qu'une fois toute la compétition connue."""
    data = match_json(m, comp)
    mp = players.match_players(m, xt_model)
    for row in data["players"]:
        row |= mp["rows"].get(row["id"], {})
    data["value"] = {"actions": mp["actions"], "xt_minutes": mp["xt_minutes"]}
    return data, mp


def competition(
    comp: dict[str, Any], matches: Iterable[Match], xt_model: XTModel
) -> dict[str, Any]:
    """Calcule une compétition entière (en gardant les JSON en mémoire, pas les images 360) :
    matchs, contexte d'équipe, joueurs. Rien n'est écrit ici : voir `write_competition`."""
    done: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for m in matches:
        done.append(match_data(m, comp["id"], xt_model))
    analyses = [
        (d["meta"][s]["id"], d["meta"][s]["name"], d["team"][s])
        for d, _ in done
        for s in ("home", "away")
    ]
    table = players.tournament(comp, done)
    return {
        "comp": comp,
        "matches": [d for d, _ in done],
        "context": team.context(analyses),
        "players": table,
    }


def write_competition(c: dict[str, Any], out: Path) -> dict[str, Any]:
    """Écrit les matchs, le contexte et la table des joueurs ; renvoie l'entrée du catalogue."""
    comp: dict[str, Any] = c["comp"]
    for d in c["matches"]:
        write_json(d, out / "matches" / f"{d['meta']['id']}.json")
    write_json(c["context"], out / "context" / f"{comp['id']}.json")
    write_json(c["players"], out / "players" / f"{comp['id']}.json")
    summaries = [match_summary_from(d) for d in c["matches"]]
    return comp | {"matches": sorted(summaries, key=lambda x: x["date"])}


def match_summary_from(d: dict[str, Any]) -> dict[str, Any]:
    keys = ("id", "date", "stage", "home", "away", "duration", "has_360")
    meta: dict[str, Any] = d["meta"]
    return {k: meta[k] for k in keys}


def finish(computed: list[dict[str, Any]], out: Path) -> list[dict[str, Any]]:
    """Dernière étape, toutes compétitions connues : jumeaux, coin de l'analyste, écriture.
    Les tables de joueurs déjà publiées (compétitions non recalculées) servent aux jumeaux."""
    tables = {c["comp"]["id"]: c["players"] for c in computed}
    for f in sorted((out / "players").glob("*.json")) if (out / "players").exists() else []:
        if f.stem not in tables:
            tables[f.stem] = json.loads(f.read_text(encoding="utf-8"))
    players.twins(tables)
    entries = []
    for c in computed:
        for d in c["matches"]:
            d["analyst"] = analyst.match_notes(d, c["context"], c["players"])
        entries.append(write_competition(c, out))
    for cid, tab in tables.items():
        if cid not in {c["comp"]["id"] for c in computed}:
            write_json(tab, out / "players" / f"{cid}.json")
    return entries


def rewrite_notes(out: Path) -> int:
    """Réécrit le coin de l'analyste à partir des fichiers déjà publiés, sans tout recalculer
    (pour retoucher les textes en quelques secondes)."""
    n = 0
    for f in sorted((out / "matches").glob("*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        comp = d["meta"]["comp"]
        ctx = json.loads((out / "context" / f"{comp}.json").read_text(encoding="utf-8"))
        table = json.loads((out / "players" / f"{comp}.json").read_text(encoding="utf-8"))
        d["analyst"] = analyst.match_notes(d, ctx, table)
        write_json(d, f)
        n += 1
    return n


def write_catalogue(entries: list[dict[str, Any]], out: Path) -> dict[str, Any]:
    data = {"competitions": entries}
    write_json(data, out / "catalogue.json")
    return data

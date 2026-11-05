"""Le corpus : une ligne par équipe et par match, sur tous les matchs (poules comprises).

C'est la matière des enquêtes : on y répond à des questions qui traversent les compétitions
(« le pressing fait-il gagner ? »), là où les pages de match ne regardent qu'un match à la fois.
Rien du 360 ici : seulement les événements, pour que le corpus se calcule vite et partout.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

from tableau_noir import classic, team
from tableau_noir.model import Match

CORPUS = Path("data/processed/corpus.csv")
SELECTIONS = ("FIFA World Cup", "UEFA Euro", "Copa America", "African Cup of Nations")


def rows(m: Match, comp: str) -> list[dict[str, Any]]:
    stats = classic.team_stats(m)
    tr = team.transitions(m)
    out = []
    for us, them in ((m.home, m.away), (m.away, m.home)):
        s, o = stats[us.id], stats[them.id]
        pr = team.pressing(m, us.id, tr)
        rec = team.recovery_runs(m, us.id, tr)
        rel = team.relation_metrics(m, us.id)
        pens = us.penalties if us.penalties is not None else -1
        opens = them.penalties if them.penalties is not None else -1
        result = "W" if us.score > them.score else "L" if us.score < them.score else "D"
        if result == "D" and pens >= 0:
            result = "W" if pens > opens else "L"
        out.append(
            {
                "match_id": m.id,
                "comp": comp,
                "kind": "selection" if m.competition in SELECTIONS else "club",
                "year": int(str(m.date)[:4]),
                "competition": m.competition,
                "season": m.season,
                "stage": m.stage,
                "knockout": not str(m.stage).startswith("Group"),
                "date": m.date,
                "team": us.name,
                "opponent": them.name,
                "home": us.id == m.home.id,
                "goals": us.score,
                "goals_against": them.score,
                "result": result,
                "penalties": pens >= 0,
                "duration": m.duration,
                "xg": s["xg"],
                "xg_against": o["xg"],
                "npxg": s["npxg"],
                "shots": s["shots"],
                "shots_against": o["shots"],
                "possession": s["possession"],
                "ppda": s["ppda"],
                "ppda_opp": o["ppda"],
                "press_source": pr["source"],
                "press_per_min": pr["per_minute_out"],
                "counterpress": pr["counterpress_share"],
                "regain_5s": pr["regain_5s"],
                "regain_10s": pr["regain_10s"],
                "high_recoveries": pr["high_recoveries"],
                "def_height": pr["height"],
                "losses": rec["losses"],
                "tr_shots_against": rec["shots_against"],
                "tr_xg_against": rec["xg_against"],
                "tr_goals_against": rec["goals_against"],
                "short_share": rel["short_share"],
                "quick_share": rel["quick_share"],
                "has_360": m.has_360,
                "source": m.source,
            }
        )
    # ce que le pressing de l'un produit chez l'autre
    for r, o in ((out[0], out[1]), (out[1], out[0])):
        r["tr_shots_for"] = o["tr_shots_against"]
        r["tr_xg_for"] = o["tr_xg_against"]
        r["tr_goals_for"] = o["tr_goals_against"]
        r["opp_losses"] = o["losses"]
    return out


SHOTS = Path("data/processed/shots.csv")


def shot_rows(m: Match, comp: str) -> list[dict[str, Any]]:
    """Chaque tir, avec le score au moment du tir : la matière des occasions manquées."""
    ev = m.events
    shots = ev[ev["kind"] == "shot"].sort_values(["period", "t"])
    goals = ev[(ev["kind"].isin(("shot", "own_goal"))) & ev["goal"].fillna(False).astype(bool)]
    names = {m.home.id: m.home.name, m.away.id: m.away.name}
    out = []
    for rec in shots.to_dict("records"):
        r = _Row(rec)
        before = goals[goals["t"] < r.t]
        own = ev[(ev["kind"] == "own_goal") & (ev["t"] < r.t)]
        # un csc porte l'équipe qui le concède : il compte pour l'autre
        shots_b = before[before["kind"] == "shot"]
        gf = int((shots_b["team"] == r.team).sum()) + int((own["team"] != r.team).sum())
        ga = int((shots_b["team"] != r.team).sum()) + int((own["team"] == r.team).sum())
        p = m.players.get(str(r.player))
        out.append(
            {
                "match_id": m.id,
                "comp": comp,
                "kind": "selection" if m.competition in SELECTIONS else "club",
                "competition": m.competition,
                "season": m.season,
                "stage": m.stage,
                "knockout": not str(m.stage).startswith("Group"),
                "date": m.date,
                "team": names.get(str(r.team), str(r.team)),
                "opponent": names.get(m.away.id if r.team == m.home.id else m.home.id, "?"),
                "player": p.name if p else "?",
                "minute": int(r.minute) + 1,
                "period": int(r.period),
                "x": r.x,
                "y": r.y,
                "xg": r.xg,
                "goal": bool(r.goal) if pd.notna(r.goal) else False,
                "on_target": bool(r.ok) if pd.notna(r.ok) else False,
                "set_piece": r.set_piece,
                "body": r.body,
                "score_for": gf,
                "score_against": ga,
                "final_for": us_score(m, str(r.team)),
                "final_against": them_score(m, str(r.team)),
                "duration": m.duration,
            }
        )
    return out


class _Row:
    """Accès par attribut à une ligne (typé Any, pour mypy)."""

    def __init__(self, d: dict[Any, Any]) -> None:
        self.__dict__.update(d)

    def __getattr__(self, k: str) -> Any:
        return self.__dict__[k]


def us_score(m: Match, tid: str) -> int:
    return m.home.score if tid == m.home.id else m.away.score


def them_score(m: Match, tid: str) -> int:
    return m.away.score if tid == m.home.id else m.home.score


def build(
    matches: Iterable[tuple[str, Match]], out: Path = CORPUS, shots_out: Path = SHOTS
) -> pd.DataFrame:
    team_rows: list[dict[str, Any]] = []
    shot_list: list[dict[str, Any]] = []
    for comp, m in matches:
        try:
            team_rows += rows(m, comp)
            shot_list += shot_rows(m, comp)
        except Exception as e:  # noqa: BLE001 — un match cassé ne doit pas perdre les autres
            print(f"{comp} {m.id} ignoré : {e}", flush=True)
    df = pd.DataFrame(team_rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    pd.DataFrame(shot_list).to_csv(shots_out, index=False)
    return df


def load(path: Path = CORPUS) -> pd.DataFrame:
    return pd.read_csv(path)

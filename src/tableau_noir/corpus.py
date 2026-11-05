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


def build(matches: Iterable[tuple[str, Match]], out: Path = CORPUS) -> pd.DataFrame:
    df = pd.DataFrame([r for comp, m in matches for r in rows(m, comp)])
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return df


def load(path: Path = CORPUS) -> pd.DataFrame:
    return pd.read_csv(path)

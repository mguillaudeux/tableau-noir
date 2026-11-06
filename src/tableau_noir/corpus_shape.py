"""Deuxième passe du corpus : la forme des équipes et le lieu des pertes de balle.

Pour chaque équipe et chaque match (StatsBomb seulement, qui donne la composition annoncée) :
- la formation annoncée et celles qu'on déduit des positions moyennes, avec et sans ballon ;
- où l'équipe perd le ballon (6 bandes de 17,5 m, depuis son but) et ce que chaque zone de perte
  coûte (tirs et xG concédés dans les 15 s).
Matière des enquêtes « formations mensongères » et « où meurent les attaques ».
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from tableau_noir import team
from tableau_noir.model import PITCH_X, Match

SHAPES = Path("data/processed/shapes.csv")
LOSSES = Path("data/processed/losses.csv")
BANDS = 6


def shape_rows(m: Match, comp: str) -> list[dict[str, Any]]:
    out = []
    for us in (m.home, m.away):
        with_ball = team.average_positions(m, us.id, True)
        without = team.average_positions(m, us.id, False)
        out.append(
            {
                "match_id": m.id,
                "comp": comp,
                "season": m.season,
                "date": m.date,
                "year": int(str(m.date)[:4]),
                "team": us.name,
                "announced": m.formations.get(us.id),
                "with_ball": team.formation(with_ball),
                "without_ball": team.formation(without),
                "n_with": len(with_ball),
            }
        )
    return out


def loss_rows(m: Match, comp: str) -> list[dict[str, Any]]:
    tr = team.transitions(m)
    if tr.empty:
        return []
    tr["band"] = np.clip((tr["x_loss"].to_numpy(float) / PITCH_X * BANDS).astype(int), 0, BANDS - 1)
    names = {m.home.id: m.home.name, m.away.id: m.away.name}
    out = []
    for key, g in tr.groupby(["team", "band"]):
        tid, band = str(key[0]), int(str(key[1]))
        out.append(
            {
                "match_id": m.id,
                "comp": comp,
                "year": int(str(m.date)[:4]),
                "team": names.get(str(tid), str(tid)),
                "band": band,
                "losses": int(len(g)),
                "shots_against": int(g["shots_against"].sum()),
                "xg_against": float(g["xg_against"].sum()),
                "goals_against": int(g["goals_against"].sum()),
                "regained_5s": int((g["regain"] <= 5).sum()),
            }
        )
    return out


def build(
    matches: Iterable[tuple[str, Match]], shapes_out: Path = SHAPES, losses_out: Path = LOSSES
) -> tuple[pd.DataFrame, pd.DataFrame]:
    shapes: list[dict[str, Any]] = []
    losses: list[dict[str, Any]] = []
    for comp, m in matches:
        try:
            losses += loss_rows(m, comp)
            if m.source == "statsbomb":
                shapes += shape_rows(m, comp)
        except Exception as e:  # noqa: BLE001
            print(f"{comp} {m.id} ignoré : {e}", flush=True)
    s, lo = pd.DataFrame(shapes), pd.DataFrame(losses)
    shapes_out.parent.mkdir(parents=True, exist_ok=True)
    s.to_csv(shapes_out, index=False)
    lo.to_csv(losses_out, index=False)
    return s, lo

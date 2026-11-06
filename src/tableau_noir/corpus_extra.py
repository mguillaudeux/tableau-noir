"""Troisième passe du corpus : les joueurs.

`players.csv` : une ligne par joueur et par match (StatsBomb), avec ses chiffres (buts, xG, tirs,
passes clés, passes progressives, dribbles, actions défensives, touches, xT) et l'endroit où il
touche le ballon (médiane). Matière des enquêtes « Messi et Mbappé » et « formations ».
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any

import pandas as pd

from tableau_noir import classic
from tableau_noir.model import Match
from tableau_noir.xt import XTModel

PLAYERS = Path("data/processed/players.csv")
TOUCH = ("pass", "carry", "shot", "dribble")


def player_rows(m: Match, comp: str, model: XTModel) -> list[dict[str, Any]]:
    ev = m.events
    xt = pd.Series(model.added(ev), index=ev.index)
    names = {m.home.id: m.home.name, m.away.id: m.away.name}
    out = []
    for p in classic.player_stats(m):
        e = ev[ev["player"] == p["id"]]
        t = e[e["kind"].isin(TOUCH)].dropna(subset=["x", "y"])
        shots = e[(e["kind"] == "shot") & (e["set_piece"] != "penalty")]
        out.append(
            {
                "match_id": m.id,
                "comp": comp,
                "season": m.season,
                "date": m.date,
                "year": int(str(m.date)[:4]),
                "team": names.get(p["team"], p["team"]),
                "player_id": p["id"],
                "player": p["name"],
                "position": p["position"],
                "minutes": p["minutes"],
                "goals": p["goals"],
                "assists": p["assists"],
                "shots": p["shots"],
                "xg": p["xg"],
                "npxg": round(float(shots["xg"].fillna(0).sum()), 3),
                "key_passes": p["key_passes"],
                "passes": p["passes"],
                "passes_ok": p["passes_ok"],
                "progressive": p["progressive"],
                "dribbles": p["dribbles"],
                "def_actions": p["def_actions"],
                "touches": p["touches"],
                "xt": round(float(xt[e.index].sum()), 3),
                "touch_x": round(float(t["x"].median()), 1) if len(t) else None,
                "touch_y": round(float(t["y"].median()), 1) if len(t) else None,
                "box_touches": int(((t["x"] >= 88.5) & (t["y"].between(13.84, 54.16))).sum()),
            }
        )
    return out


def build_players(
    matches: Iterable[tuple[str, Match]], model: XTModel, out: Path = PLAYERS
) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for i, (comp, m) in enumerate(matches):
        if m.source != "statsbomb":
            continue
        try:
            rows += player_rows(m, comp, model)
        except Exception as e:  # noqa: BLE001
            print(f"{comp} {m.id} ignoré : {e}", flush=True)
        if i % 200 == 0:
            print(i, comp, flush=True)
    df = pd.DataFrame(rows)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return df

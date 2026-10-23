"""Rejouer les buts, vus du dessus : des points sur un terrain, jamais d'images du match.

Pour chaque but (hors contre son camp), on garde l'action qui y mène : les événements de la même
possession, au plus les 25 dernières secondes et 14 événements. Tout est ramené dans le repère de
l'équipe qui marque (elle attaque vers la droite).

Avec le 360, chaque événement porte les joueurs visibles à cet instant. Le 360 ne dit pas qui est
qui (sauf le porteur du ballon) : pour animer, on apparie les points d'une image à l'autre, équipe
par équipe, en minimisant la distance parcourue (algorithme hongrois). Les points qui n'ont pas de
partenaire dans l'image suivante apparaissent ou disparaissent en fondu.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment

from tableau_noir.model import PITCH_X, PITCH_Y, Match

MOVES = ("pass", "carry", "dribble", "shot", "miscontrol", "duel", "tackle", "interception")
WINDOW, MAX_EVENTS = 25.0, 14
MAX_STEP = 18.0  # au-delà, deux points d'images voisines ne sont pas le même joueur


def _r(v: float) -> float:
    return round(float(v), 1)


def goals(m: Match) -> list[dict[str, Any]]:
    ev = m.events.reset_index(drop=True)
    shots = ev[(ev["kind"] == "shot") & ev["goal"].fillna(False).astype(bool)]
    frames: dict[str, pd.DataFrame] | None = None
    if m.frames is not None:
        frames = {str(k): g for k, g in m.frames.groupby("event_id")}
    out = []
    for i, shot in shots.iterrows():
        tid = shot["team"]
        same = ev[
            (ev.index <= i)
            & (ev["period"] == shot["period"])
            & (ev["t"] >= shot["t"] - WINDOW)
            & (ev["chain"] == shot["chain"])
            & ev["kind"].isin(MOVES)
            & ev["x"].notna()
        ]
        if shot["set_piece"] == "penalty":
            same = same.loc[[i]]
        seq = same.tail(MAX_EVENTS)
        steps = [_step(m, r, tid, frames) for _, r in seq.iterrows()]
        _link(steps)
        p = m.players.get(str(shot["player"]))
        out.append(
            {
                "minute": int(shot["minute"]) + 1,
                "t": round(float(shot["t"]), 2),
                "side": "home" if tid == m.home.id else "away",
                "scorer": p.name if p else "?",
                "xg": None if pd.isna(shot["xg"]) else round(float(shot["xg"]), 2),
                "penalty": shot["set_piece"] == "penalty",
                "has_360": frames is not None and any(s["dots"] for s in steps),
                "steps": steps,
            }
        )
    return out


def _step(
    m: Match, r: pd.Series, tid: str, frames: dict[str, pd.DataFrame] | None
) -> dict[str, Any]:
    """Un événement dans le repère de l'équipe qui marque, avec les joueurs visibles du 360."""
    ours = r["team"] == tid

    def flip(x: float, y: float) -> tuple[float, float]:
        return (x, y) if ours else (PITCH_X - x, PITCH_Y - y)

    x, y = flip(float(r["x"]), float(r["y"]))
    ex, ey = (None, None)
    if pd.notna(r["ex"]):
        ex, ey = flip(float(r["ex"]), float(r["ey"]))
    elif r["kind"] == "shot":
        ex, ey = PITCH_X, PITCH_Y / 2
    p = m.players.get(str(r["player"]))
    dots: list[list[Any]] = []
    f = frames.get(str(r["event_id"])) if frames else None
    if f is not None:
        for fx, fy, mate, actor, keeper in zip(
            f["x"].to_numpy(float),
            f["y"].to_numpy(float),
            f["teammate"].to_numpy(bool),
            f["actor"].to_numpy(bool),
            f["keeper"].to_numpy(bool),
            strict=True,
        ):
            us = bool(mate) == bool(ours)  # coéquipier de l'acteur ⇔ même équipe que l'acteur
            gx, gy = flip(fx, fy)
            dots.append([_r(gx), _r(gy), 1 if us else 0, 1 if actor else 0, 1 if keeper else 0])
    return {
        "t": round(float(r["t"]), 2),
        "kind": str(r["kind"]),
        "ours": bool(ours),
        "ok": None if pd.isna(r["ok"]) else bool(r["ok"]),
        "name": p.name if p else "",
        "x": _r(x),
        "y": _r(y),
        "ex": None if ex is None else _r(ex),
        "ey": None if ey is None else _r(ey),
        "dots": dots,
    }


def _link(steps: list[dict[str, Any]]) -> None:
    """Numérote les points pour qu'un même joueur garde son numéro d'une image à l'autre."""
    next_id = 0
    prev: list[list[Any]] = []
    for s in steps:
        cur = s["dots"]
        if not cur:
            continue
        for team in (0, 1):
            a = [d for d in prev if d[2] == team]
            b = [d for d in cur if d[2] == team]
            if a and b:
                cost = np.array([[np.hypot(p[0] - q[0], p[1] - q[1]) for q in b] for p in a])
                rows, cols = linear_sum_assignment(cost)
                for i, j in zip(rows, cols, strict=True):
                    if cost[i, j] <= MAX_STEP:
                        b[j].append(a[i][5])
        for d in cur:
            if len(d) == 5:
                d.append(next_id)
                next_id += 1
        prev = cur

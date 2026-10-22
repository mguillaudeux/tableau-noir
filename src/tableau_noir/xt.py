"""Expected Threat (xT) : ce que vaut le ballon selon l'endroit où il se trouve.

Méthode de Karun Singh (2018). Le terrain est découpé en 16 × 12 cases. Pour chaque case, on mesure
sur les cinq grands championnats 2017/18 (Wyscout) :
- la probabilité de tirer plutôt que de jouer le ballon (s), et de marquer quand on tire (g) ;
- la probabilité de jouer le ballon (m), et où il arrive quand le geste réussit (T).
La menace d'une case se résout par itérations : xT(z) = s·g + m·Σ T(z→z')·xT(z').

Une passe ou une conduite réussie vaut alors xT(arrivée) − xT(départ) : positive quand elle
rapproche le ballon d'un but probable, négative quand elle recule. Un geste raté vaut 0.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd

from tableau_noir.model import PITCH_X, PITCH_Y

Array = npt.NDArray[np.float64]
NX, NY = 16, 12
MOVES = ("pass", "carry")


def cell(x: Array, y: Array) -> npt.NDArray[np.int64]:
    """Indice de case (colonne × NY + ligne) pour des coordonnées en mètres."""
    cx = np.clip((np.asarray(x, float) / PITCH_X * NX).astype(int), 0, NX - 1)
    cy = np.clip((np.asarray(y, float) / PITCH_Y * NY).astype(int), 0, NY - 1)
    out: npt.NDArray[np.int64] = (cx * NY + cy).astype(np.int64)
    return out


@dataclass(frozen=True)
class XTModel:
    grid: tuple[tuple[float, ...], ...]  # [colonne][ligne], colonne 0 = notre but
    n_actions: int

    def value(self, x: Array, y: Array) -> Array:
        g = np.array(self.grid).ravel()
        out: Array = g[cell(x, y)]
        return out

    def added(self, events: pd.DataFrame) -> Array:
        """xT ajouté par chaque événement : passes et conduites réussies dans le jeu, 0 sinon."""
        ok = (
            events["kind"].isin(MOVES).to_numpy()
            & events["ok"].fillna(False).astype(bool).to_numpy()
            & (events["set_piece"] == "open").to_numpy()
            & events[["x", "y", "ex", "ey"]].notna().all(axis=1).to_numpy()
        )
        out = np.zeros(len(events))
        if ok.any():
            e = events[ok]
            out[ok] = self.value(e["ex"].to_numpy(float), e["ey"].to_numpy(float)) - self.value(
                e["x"].to_numpy(float), e["y"].to_numpy(float)
            )
        return out

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        grid = [[round(v, 5) for v in col] for col in self.grid]
        path.write_text(json.dumps({"grid": grid, "n_actions": self.n_actions}), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> XTModel:
        d = json.loads(path.read_text(encoding="utf-8"))
        return cls(tuple(tuple(c) for c in d["grid"]), d["n_actions"])


def fit(events: pd.DataFrame, iterations: int = 40) -> XTModel:
    """`events` : passes, conduites et tirs au format commun. Les penaltys et les coups de pied
    arrêtés joués à la passe (corners, touches…) sont écartés : on mesure le jeu courant."""
    ev = events.dropna(subset=["x", "y"])
    ev = ev[ev["set_piece"] != "penalty"]
    shots = ev[ev["kind"] == "shot"]
    moves = ev[ev["kind"].isin(MOVES) & (ev["set_piece"] == "open")]
    n = NX * NY
    z_shot = cell(shots["x"].to_numpy(float), shots["y"].to_numpy(float))
    z_move = cell(moves["x"].to_numpy(float), moves["y"].to_numpy(float))
    n_shot = np.bincount(z_shot, minlength=n).astype(float)
    n_goal = np.bincount(
        z_shot, weights=shots["goal"].fillna(False).astype(float).to_numpy(), minlength=n
    )
    n_move = np.bincount(z_move, minlength=n).astype(float)
    total = np.maximum(n_shot + n_move, 1)
    s, m = n_shot / total, n_move / total
    g = np.divide(n_goal, n_shot, out=np.zeros(n), where=n_shot > 0)
    done = moves[moves["ok"].fillna(False).astype(bool)].dropna(subset=["ex", "ey"])
    a = cell(done["x"].to_numpy(float), done["y"].to_numpy(float))
    b = cell(done["ex"].to_numpy(float), done["ey"].to_numpy(float))
    trans = np.zeros((n, n))
    np.add.at(trans, (a, b), 1)
    trans /= np.maximum(n_move, 1)[:, None]
    xt = np.zeros(n)
    for _ in range(iterations):
        xt = s * g + m * (trans @ xt)
    grid = xt.reshape(NX, NY)
    return XTModel(tuple(tuple(float(v) for v in col) for col in grid), int(len(ev)))

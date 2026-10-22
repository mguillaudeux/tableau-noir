"""Un modèle d'xG simple pour les données Wyscout (qui n'en fournissent pas).

Régression logistique sur ~40 000 tirs des cinq grands championnats 2017/18, avec quatre
variables : distance au but, angle d'ouverture du but, tir de la tête, coup franc direct.
Les penaltys valent une constante (taux de réussite observé dans les mêmes données).
StatsBomb fournit son propre xG : ce modèle ne sert qu'aux matchs Wyscout.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import numpy.typing as npt
import pandas as pd
from scipy.optimize import minimize

from tableau_noir.model import PITCH_X, PITCH_Y

Array = npt.NDArray[np.float64]
GOAL_W = 7.32


def geometry(x: Array, y: Array) -> tuple[Array, Array]:
    """Distance au centre du but (m) et angle sous lequel le tireur voit le but (radians)."""
    dx = PITCH_X - x
    dy = np.abs(y - PITCH_Y / 2)
    dist = np.hypot(dx, dy)
    a1 = np.arctan2(dy + GOAL_W / 2, dx)
    a2 = np.arctan2(dy - GOAL_W / 2, dx)
    return dist, np.abs(a1 - a2)


def features(shots: pd.DataFrame) -> Array:
    dist, angle = geometry(shots["x"].to_numpy(float), shots["y"].to_numpy(float))
    return np.column_stack(
        [
            np.ones(len(shots)),
            dist,
            angle,
            (shots["body"] == "head").to_numpy(float),
            (shots["set_piece"] == "free_kick").to_numpy(float),
        ]
    )


@dataclass(frozen=True)
class XGModel:
    coef: tuple[float, ...]
    penalty: float
    n_shots: int

    def predict(self, shots: pd.DataFrame) -> Array:
        z = features(shots) @ np.array(self.coef)
        p = 1 / (1 + np.exp(-z))
        out: Array = np.where(shots["set_piece"].to_numpy() == "penalty", self.penalty, p)
        return out

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"coef": self.coef, "penalty": self.penalty, "n_shots": self.n_shots}, indent=1
            ),
            encoding="utf-8",
        )

    @staticmethod
    def load(path: Path) -> XGModel:
        d = json.loads(path.read_text(encoding="utf-8"))
        return XGModel(tuple(d["coef"]), float(d["penalty"]), int(d["n_shots"]))


def fit(shots: pd.DataFrame) -> XGModel:
    """Régression logistique (maximum de vraisemblance, légère pénalité L2)."""
    open_ = shots[(shots["set_piece"] != "penalty") & shots["x"].notna()]
    x = features(open_)
    y = open_["goal"].astype(bool).to_numpy(float)

    def loss(w: Array) -> tuple[float, Array]:
        z = x @ w
        p = 1 / (1 + np.exp(-z))
        eps = 1e-12
        ll = (
            -(y * np.log(p + eps) + (1 - y) * np.log(1 - p + eps)).mean()
            + 1e-4 * (w[1:] ** 2).sum()
        )
        grad = x.T @ (p - y) / len(y)
        grad[1:] += 2e-4 * w[1:]
        return float(ll), grad

    w0 = np.zeros(x.shape[1])
    res = minimize(loss, w0, jac=True, method="L-BFGS-B")
    pens = shots[shots["set_piece"] == "penalty"]
    pen_rate = float(pens["goal"].astype(bool).mean()) if len(pens) else 0.76
    return XGModel(tuple(float(v) for v in res.x), round(pen_rate, 3), int(len(open_)))

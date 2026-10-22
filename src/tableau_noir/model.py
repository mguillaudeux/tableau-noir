"""Le format commun de Tableau Noir : un match = des métadonnées + une table d'événements.

Conventions, quelle que soit la source :
- coordonnées en mètres sur un terrain de 105 × 68 ;
- chaque événement est vu depuis l'équipe qui le réalise, qui attaque vers la droite
  (x = 105 : but adverse) ;
- y = 0 est la ligne de touche à gauche de l'équipe qui attaque ;
- `t` : secondes depuis le coup d'envoi, avec un décalage fixe par période (45', 90', 105') ;
- la séance de tirs au but (période 5) est gardée à part et ne compte dans aucune statistique.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd

PITCH_X = 105.0
PITCH_Y = 68.0
PERIOD_OFFSET = {1: 0.0, 2: 45 * 60.0, 3: 90 * 60.0, 4: 105 * 60.0, 5: 120 * 60.0}

KINDS = (
    "pass",
    "shot",
    "carry",
    "dribble",
    "duel",
    "pressure",
    "interception",
    "tackle",
    "clearance",
    "block",
    "recovery",
    "foul",
    "offside",
    "save",
    "miscontrol",
    "card",
    "own_goal",
    "other",
)
SET_PIECES = ("open", "corner", "free_kick", "penalty", "throw_in", "goal_kick", "kick_off")

COLUMNS: dict[str, str] = {
    "match_id": "string",
    "period": "int64",
    "t": "float64",
    "minute": "int64",
    "team": "string",
    "player": "string",
    "kind": "string",
    "ok": "boolean",
    "x": "float64",
    "y": "float64",
    "ex": "float64",
    "ey": "float64",
    "xg": "float64",
    "goal": "boolean",
    "set_piece": "string",
    "body": "string",
    "key_pass": "boolean",
    "assist": "boolean",
    "card": "string",
    "possession": "string",
    "aerial": "boolean",
    "event_id": "string",  # identifiant de l'événement chez le fournisseur (jointure avec le 360)
    "recipient": "string",  # receveur d'une passe (StatsBomb seulement)
    "chain": "int64",  # numéro de la possession (séquence de jeu d'une même équipe)
    "counterpress": "boolean",  # pression dans les 5 s après une perte (StatsBomb seulement)
}


def frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Table d'événements typée, colonnes dans l'ordre de COLUMNS."""
    df = pd.DataFrame(rows, columns=list(COLUMNS))
    for col, dtype in COLUMNS.items():
        if dtype == "int64":
            df[col] = df[col].fillna(-1)
        df[col] = df[col].astype(dtype)  # type: ignore[call-overload]
    df = df.sort_values(["period", "t"], kind="stable").reset_index(drop=True)
    if (df["chain"] < 0).all() and len(df):
        df["chain"] = chains(df)
    return df


def chains(df: pd.DataFrame) -> pd.Series:
    """Numérote les possessions quand la source ne le fait pas : une nouvelle possession commence
    chaque fois que l'équipe qui a le ballon change (ou à chaque nouvelle période)."""
    team = df["possession"].ffill()
    new = (team != team.shift()) | (df["period"] != df["period"].shift())
    return new.cumsum().astype("int64")


@dataclass
class Player:
    id: str
    name: str
    team: str
    position: str  # GK, DF, MF, FW (ou "" si inconnu)
    starter: bool
    minutes: float = 0.0
    number: int | None = None


@dataclass
class Team:
    id: str
    name: str
    score: int
    penalties: int | None = None  # tirs au but réussis, s'il y a eu une séance


@dataclass
class Match:
    id: str  # "sb-3869685", "wy-2058017"
    source: str  # "statsbomb" | "wyscout"
    competition: str
    season: str
    date: str
    stage: str
    home: Team
    away: Team
    duration: float  # minutes jouées (90, 120…)
    players: dict[str, Player] = field(default_factory=dict)
    events: pd.DataFrame = field(default_factory=lambda: frame([]))
    has_360: bool = False
    frames: pd.DataFrame | None = None  # positions 360 : event_id, teammate, actor, keeper, x, y
    formations: dict[str, str] = field(default_factory=dict)  # formation de départ annoncée

    def team(self, team_id: str) -> Team:
        return self.home if team_id == self.home.id else self.away

    def opponent(self, team_id: str) -> Team:
        return self.away if team_id == self.home.id else self.home

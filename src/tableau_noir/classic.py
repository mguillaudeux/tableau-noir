"""Section 1 · les stats classiques d'un match : ce que l'on retrouve sur toutes les feuilles
de match, calculé de la même façon pour les deux sources."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.model import PITCH_X, PITCH_Y, Match

FINAL_THIRD = PITCH_X * 2 / 3
BIG_CHANCE = 0.3  # xG à partir duquel on parle de grosse occasion


def progressive(df: pd.DataFrame) -> pd.Series:
    """Passe progressive (définition Wyscout) : elle rapproche le ballon du but adverse d'au moins
    30 m si elle reste dans son camp, 15 m si elle franchit la ligne médiane, 10 m dans le camp
    adverse.
    Les corners et les touches sont exclus."""
    gx, gy = PITCH_X, PITCH_Y / 2
    d0 = np.hypot(gx - df["x"], gy - df["y"])
    d1 = np.hypot(gx - df["ex"], gy - df["ey"])
    gain = d0 - d1
    half = PITCH_X / 2
    own_own = (df["x"] < half) & (df["ex"] < half)
    crosses = (df["x"] < half) & (df["ex"] >= half)
    need = np.where(own_own, 30.0, np.where(crosses, 15.0, 10.0))
    ok = df["ok"].fillna(False).astype(bool)
    sp = ~df["set_piece"].isin(["corner", "throw_in"])
    return (ok & sp & (gain >= need)).fillna(False)


def possession_share(ev: pd.DataFrame, home: str, away: str) -> dict[str, float]:
    """Possession au temps : chaque événement donne le ballon à l'équipe en possession jusqu'à
    l'événement suivant (10 s au plus, pour ne pas compter les arrêts de jeu)."""
    e = ev[ev["possession"].notna()].sort_values(["period", "t"])
    dt = e.groupby("period")["t"].diff(-1).abs().fillna(0).clip(upper=10)
    tot = dt.groupby(e["possession"]).sum()
    s = float(tot.get(home, 0) + tot.get(away, 0)) or 1.0
    return {home: float(tot.get(home, 0)) / s, away: float(tot.get(away, 0)) / s}


def _rate(num: int, den: int) -> float | None:
    return round(num / den, 3) if den else None


def team_stats(m: Match) -> dict[str, dict[str, Any]]:
    ev = m.events
    poss = possession_share(ev, m.home.id, m.away.id)
    prog = progressive(ev[ev["kind"] == "pass"])
    out: dict[str, dict[str, Any]] = {}
    for team in (m.home, m.away):
        e = ev[ev["team"] == team.id]
        opp = ev[ev["team"] == m.opponent(team.id).id]
        shots = e[e["kind"] == "shot"]
        passes = e[e["kind"] == "pass"]
        p_ok = passes["ok"].fillna(False).astype(bool)
        open_passes = passes[
            ~passes["set_piece"].isin(["corner", "throw_in", "goal_kick", "kick_off"])
        ]
        duels = e[e["kind"].isin(["duel", "tackle", "dribble"]) & e["ok"].notna()]
        aerial = duels[duels["aerial"].fillna(False).astype(bool)]
        cards = e["card"].dropna()
        xg = shots["xg"].fillna(0)
        f3 = passes[p_ok & (passes["x"] < FINAL_THIRD) & (passes["ex"] >= FINAL_THIRD)]
        out[team.id] = {
            "goals": team.score,
            "xg": round(float(xg.sum()), 2),
            "npxg": round(float(xg[shots["set_piece"] != "penalty"].sum()), 2),
            "shots": int(len(shots)),
            "on_target": int(shots["ok"].fillna(False).astype(bool).sum()),
            "big_chances": int((xg >= BIG_CHANCE).sum()),
            "possession": round(poss[team.id], 3),
            "passes": int(len(passes)),
            "passes_ok": int(p_ok.sum()),
            "pass_rate": _rate(int(p_ok.sum()), len(passes)),
            "open_pass_rate": _rate(
                int(open_passes["ok"].fillna(False).astype(bool).sum()), len(open_passes)
            ),
            "progressive": int(prog[passes.index].sum()),
            "final_third": int(len(f3)),
            "key_passes": int(passes["key_pass"].fillna(False).astype(bool).sum()),
            "duels": int(len(duels)),
            "duels_won": int(duels["ok"].astype(bool).sum()),
            "aerials": int(len(aerial)),
            "aerials_won": int(aerial["ok"].astype(bool).sum()),
            "tackles": int((e["kind"] == "tackle").sum()),
            "tackles_won": int(
                ((e["kind"] == "tackle") & e["ok"].fillna(False).astype(bool)).sum()
            ),
            "interceptions": int((e["kind"] == "interception").sum()),
            "recoveries": int((e["kind"] == "recovery").sum()) if m.source == "statsbomb" else None,
            "clearances": int((e["kind"] == "clearance").sum()),
            "saves": int((e["kind"] == "save").sum()),
            "fouls": int((e["kind"] == "foul").sum()),
            "yellow": int(cards.isin(["yellow"]).sum()),
            "red": int(cards.isin(["red", "second_yellow"]).sum()),
            "corners": int((passes["set_piece"] == "corner").sum()),
            "offsides": int((e["kind"] == "offside").sum()),
            # PPDA : passes adverses dans leurs 60 % de terrain / nos actions défensives là
            "ppda": _ppda(e, opp),
        }
    return out


def _ppda(e: pd.DataFrame, opp: pd.DataFrame) -> float | None:
    """Passes autorisées par action défensive, sur les 60 % de terrain adverses (pressing)."""
    opp_passes = opp[(opp["kind"] == "pass") & (opp["x"] < PITCH_X * 0.6)]
    defensive = e[e["kind"].isin(["tackle", "interception", "foul"]) & (e["x"] > PITCH_X * 0.4)]
    return round(len(opp_passes) / len(defensive), 1) if len(defensive) else None


def shots_table(m: Match) -> list[dict[str, Any]]:
    """Tous les tirs, dans l'ordre : de quoi tracer la course aux xG et la carte des tirs."""
    s = m.events[m.events["kind"] == "shot"].sort_values("t")
    out = []
    for _, r in s.iterrows():
        out.append(
            {
                "t": round(float(r["t"]) / 60, 2),
                "minute": int(r["minute"]),
                "team": r["team"],
                "player": r["player"] if pd.notna(r["player"]) else None,
                "x": round(float(r["x"]), 1) if pd.notna(r["x"]) else None,
                "y": round(float(r["y"]), 1) if pd.notna(r["y"]) else None,
                "xg": round(float(r["xg"]), 3) if pd.notna(r["xg"]) else 0.0,
                "goal": bool(r["goal"]) if pd.notna(r["goal"]) else False,
                "on_target": bool(r["ok"]) if pd.notna(r["ok"]) else False,
                "body": r["body"] if pd.notna(r["body"]) else None,
                "set_piece": r["set_piece"],
            }
        )
    return out


def goals_table(m: Match) -> list[dict[str, Any]]:
    """Les buts dans l'ordre, buts contre son camp compris (attribués à l'équipe qui en profite)."""
    ev = m.events
    g = ev[
        ((ev["kind"] == "shot") & ev["goal"].fillna(False).astype(bool))
        | (ev["kind"] == "own_goal")
    ]
    out = []
    for _, r in g.sort_values("t").iterrows():
        own = r["kind"] == "own_goal"
        team = m.opponent(str(r["team"])).id if own else str(r["team"])
        out.append(
            {
                "t": round(float(r["t"]) / 60, 2),
                "minute": int(r["minute"]),
                "team": team,
                "player": r["player"] if pd.notna(r["player"]) else None,
                "own_goal": bool(own),
                "penalty": r["set_piece"] == "penalty",
            }
        )
    return out


def player_stats(m: Match) -> list[dict[str, Any]]:
    ev = m.events
    prog = progressive(ev[ev["kind"] == "pass"])
    rows = []
    for p in m.players.values():
        if p.minutes <= 0:
            continue
        e = ev[ev["player"] == p.id]
        shots = e[e["kind"] == "shot"]
        passes = e[e["kind"] == "pass"]
        ok = passes["ok"].fillna(False).astype(bool)
        duels = e[e["kind"].isin(["duel", "tackle", "dribble"]) & e["ok"].notna()]
        rows.append(
            {
                "id": p.id,
                "name": p.name,
                "team": p.team,
                "position": p.position,
                "starter": p.starter,
                "minutes": p.minutes,
                "number": p.number,
                "goals": int(shots["goal"].fillna(False).astype(bool).sum()),
                "assists": int(passes["assist"].fillna(False).astype(bool).sum()),
                "shots": int(len(shots)),
                "xg": round(float(shots["xg"].fillna(0).sum()), 2),
                "key_passes": int(passes["key_pass"].fillna(False).astype(bool).sum()),
                "passes": int(len(passes)),
                "passes_ok": int(ok.sum()),
                "progressive": int(prog[passes.index].sum()),
                "dribbles": int(
                    ((e["kind"] == "dribble") & e["ok"].fillna(False).astype(bool)).sum()
                ),
                "def_actions": int(
                    e["kind"].isin(["tackle", "interception", "clearance", "block"]).sum()
                ),
                "recoveries": int((e["kind"] == "recovery").sum()),
                "duels": int(len(duels)),
                "duels_won": int(duels["ok"].astype(bool).sum()),
                "touches": int(
                    e["kind"].isin(["pass", "shot", "carry", "dribble", "miscontrol"]).sum()
                ),
            }
        )
    return sorted(rows, key=lambda r: (r["team"], not r["starter"], -r["minutes"]))

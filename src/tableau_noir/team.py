"""Sections 2 à 5 · l'équipe : structure et couloirs, pressing, relationnisme, replis.

Deux niveaux de données :
- les **événements** (toutes les sources) : positions des actions, possessions, passes ;
- les images **360** (StatsBomb, Euro 2020, Coupe du monde 2022, Euro 2024) : la position des
  joueurs *visibles* à l'écran au moment de chaque action. Elles ne disent pas qui est qui (sauf le
  joueur qui a le ballon) et ne montrent jamais tout le terrain : les comptes de joueurs sont donc
  des comptes de joueurs visibles, à lire comme des tendances.

Repère : pour l'équipe étudiée, x va de son but (0) au but adverse (105).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.model import PITCH_X, PITCH_Y, Match

LANES = (0.0, 13.84, 24.84, 43.16, 54.16, PITCH_Y)  # 5 couloirs, bornés par les surfaces
THIRDS = (0.0, 35.0, 70.0, PITCH_X)
ON_BALL = ("pass", "shot", "carry", "dribble", "miscontrol")
OFF_BALL = ("pressure", "tackle", "interception", "recovery", "block", "clearance", "foul")
SET_PIECE_START = ("corner", "free_kick", "throw_in", "goal_kick", "kick_off", "penalty")
ZONE_35 = 35.0


def _r(v: float | None, d: int = 2) -> float | None:
    return None if v is None or (isinstance(v, float) and np.isnan(v)) else round(float(v), d)


def lane_of(y: np.ndarray | pd.Series) -> np.ndarray:
    return np.clip(np.searchsorted(LANES, np.asarray(y, float), side="right") - 1, 0, 4)


# --- Pertes de balle ---------------------------------------------------------------------------


def transitions(m: Match) -> pd.DataFrame:
    """Chaque perte de balle en jeu : passe ratée, contrôle manqué, dribble perdu.

    On garde les pertes où l'adversaire touche réellement le ballon (et pas celles qui finissent en
    touche ou en sortie de but). Pour chacune : le temps mis à récupérer le ballon (première action
    avec ballon, récupération ou interception de l'équipe), et les tirs adverses dans les 15 s.
    """
    ev = m.events.reset_index(drop=True)
    lost = (
        ((ev["kind"] == "pass") & (ev["ok"] == False) & (ev["set_piece"] == "open"))  # noqa: E712
        | (ev["kind"] == "miscontrol")
        | ((ev["kind"] == "dribble") & (ev["ok"] == False))  # noqa: E712
    )
    gain_kinds = set(ON_BALL) | {"recovery", "interception"}
    touch_kinds = set(ON_BALL) | {
        "recovery",
        "interception",
        "clearance",
        "block",
        "tackle",
        "save",
    }
    rows = []
    t_all, team_all, kind_all = ev["t"].to_numpy(), ev["team"].to_numpy(), ev["kind"].to_numpy()
    period_all, sp_all = ev["period"].to_numpy(), ev["set_piece"].to_numpy()
    minute_all = ev["minute"].to_numpy(int)
    for i in np.flatnonzero(lost.fillna(False).to_numpy(bool)):
        tid, t0, per = team_all[i], t_all[i], period_all[i]
        j, opp_touched, regain, dead = i + 1, False, np.nan, False
        while j < len(ev) and period_all[j] == per and t_all[j] - t0 <= 60:
            if team_all[j] != tid and kind_all[j] in touch_kinds:
                if sp_all[j] in SET_PIECE_START and not opp_touched:
                    dead = True
                    break
                opp_touched = True
            elif team_all[j] == tid and kind_all[j] in gain_kinds:
                if opp_touched:
                    regain = t_all[j] - t0
                    break
                if sp_all[j] in SET_PIECE_START:
                    dead = True
                    break
            j += 1
        if dead or not opp_touched:
            continue
        shots = ev[
            (ev["team"] != tid)
            & (ev["kind"] == "shot")
            & (ev["t"] > t0)
            & (ev["t"] <= t0 + 15)
            & (ev["period"] == per)
        ]
        rows.append(
            {
                "team": tid,
                "t": float(t0),
                "period": int(per),
                "x_loss": ev.at[i, "x"],
                # où l'adversaire récupère : la fin de la passe ratée, sinon le lieu de la perte
                "x_turn": ev.at[i, "ex"]
                if kind_all[i] == "pass" and pd.notna(ev.at[i, "ex"])
                else ev.at[i, "x"],
                "regain": float(regain),
                "shots_against": int(len(shots)),
                "xg_against": float(shots["xg"].fillna(0).sum()),
                "goals_against": int(shots["goal"].fillna(False).astype(bool).sum()),
                "minute": int(minute_all[i]),
            }
        )
    return pd.DataFrame(rows)


# --- Section 2 · structure et couloirs ----------------------------------------------------------


def _pass_pairs(m: Match, tid: str) -> pd.DataFrame:
    """Passes réussies avec leur receveur : donné par StatsBomb, sinon déduit (le joueur de la
    même équipe qui fait l'action suivante)."""
    ev = m.events
    ok = ev["ok"].fillna(False).astype(bool)
    passes = ev[(ev["team"] == tid) & (ev["kind"] == "pass") & ok]
    if passes["recipient"].notna().any():
        rec = passes[passes["recipient"].notna()]
        return pd.DataFrame(
            {"passer": rec["player"], "receiver": rec["recipient"], "x": rec["ex"], "y": rec["ey"]}
        )
    nxt = ev[ev["kind"].isin(ON_BALL)].copy()
    nxt["receiver"] = nxt["player"].shift(-1)
    nxt["next_team"] = nxt["team"].shift(-1)
    sel = nxt[
        (nxt["kind"] == "pass")
        & (nxt["team"] == tid)
        & (nxt["next_team"] == tid)
        & nxt["ok"].fillna(False).astype(bool)
        & (nxt["receiver"] != nxt["player"])
    ]
    return pd.DataFrame(
        {"passer": sel["player"], "receiver": sel["receiver"], "x": sel["ex"], "y": sel["ey"]}
    )


def _receptions(m: Match, tid: str) -> pd.DataFrame:
    pairs = _pass_pairs(m, tid)
    return pd.DataFrame({"player": pairs["receiver"], "x": pairs["x"], "y": pairs["y"]})


def average_positions(m: Match, tid: str, with_ball: bool) -> list[dict[str, Any]]:
    """Positions moyennes des titulaires : avec le ballon (touches et réceptions), ou sans
    (pressions, tacles, interceptions, récupérations, contres, dégagements, fautes)."""
    ev = m.events[m.events["team"] == tid]
    if with_ball:
        pts = pd.concat(
            [ev.loc[ev["kind"].isin(ON_BALL), ["player", "x", "y"]], _receptions(m, tid)]
        )
    else:
        pts = ev.loc[
            ev["kind"].isin(OFF_BALL) | ((ev["kind"] == "duel") & ~ev["aerial"].fillna(False)),
            ["player", "x", "y"],
        ]
    pts = pts.dropna()
    out = []
    for p in m.players.values():
        if p.team != tid or not p.starter:
            continue
        mine = pts[pts["player"] == p.id]
        if len(mine) < 3:
            continue
        out.append(
            {
                "id": p.id,
                "name": p.name,
                "number": p.number,
                "position": p.position,
                "x": _r(mine["x"].median(), 1),
                "y": _r(mine["y"].median(), 1),
                "n": int(len(mine)),
            }
        )
    return out


def _partition(xs: list[float], k: int) -> tuple[float, list[int]]:
    """Découpe optimale d'une liste triée en k groupes contigus (somme des variances minimale)."""
    n = len(xs)
    cost = [[0.0] * (n + 1) for _ in range(n + 1)]
    for i in range(n):
        for j in range(i + 1, n + 1):
            seg = xs[i:j]
            mu = sum(seg) / len(seg)
            cost[i][j] = sum((v - mu) ** 2 for v in seg)
    best: dict[tuple[int, int], tuple[float, list[int]]] = {}

    def solve(i: int, g: int) -> tuple[float, list[int]]:
        if g == 1:
            return cost[i][n], [n - i]
        if (i, g) in best:
            return best[(i, g)]
        out: tuple[float, list[int]] = (float("inf"), [])
        lo, hi = (i + 3, i + 5) if i == 0 else (i + 1, n - g + 1)  # la ligne arrière : 3 à 5
        for j in range(lo, min(hi, n - g + 1) + 1):
            c, sizes = solve(j, g - 1)
            if cost[i][j] + c < out[0]:
                out = (cost[i][j] + c, [j - i, *sizes])
        best[(i, g)] = out
        return out

    return solve(0, k)


def formation(positions: list[dict[str, Any]]) -> str | None:
    """Formation réelle déduite des positions moyennes : les joueurs de champ, triés de l'arrière
    vers l'avant, sont regroupés en 3 ou 4 lignes (la 4e seulement si elle se voit nettement)."""
    xs = sorted(float(p["x"]) for p in positions if p["position"] != "GK")
    if len(xs) < 9:
        return None
    sse3, s3 = _partition(xs, 3)
    sse4, s4 = _partition(xs, 4)
    sizes = s4 if sse4 < 0.55 * sse3 else s3
    return "-".join(str(s) for s in sizes)


def lane_grid(m: Match, tid: str) -> list[list[float]]:
    """Part des touches de balle par couloir (5) et par tiers (3), en possession."""
    ev = m.events[(m.events["team"] == tid) & m.events["kind"].isin(ON_BALL)].dropna(
        subset=["x", "y"]
    )
    grid = np.zeros((3, 5))
    if len(ev):
        third = np.clip(np.searchsorted(THIRDS, ev["x"].to_numpy(float), side="right") - 1, 0, 2)
        lane = lane_of(ev["y"])
        np.add.at(grid, (third, lane), 1)
        grid /= grid.sum()
    return np.round(grid, 4).tolist()


def _frames_by_side(m: Match, tid: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Images 360 où l'équipe a le ballon (ses joueurs = teammate) ou ne l'a pas (ses joueurs =
    adversaires de l'acteur, ramenés dans son repère). Gardiens exclus."""
    assert m.frames is not None
    ev = m.events[m.events["event_id"].notna() & m.events["kind"].isin(ON_BALL)][
        ["event_id", "team", "x", "y", "period", "t", "chain"]
    ]
    fr = m.frames[~m.frames["keeper"]].merge(ev, on="event_id", suffixes=("", "_ball"))
    with_ball = fr[(fr["team"] == tid) & fr["teammate"]].copy()
    without = fr[(fr["team"] != tid) & ~fr["teammate"]].copy()
    without["x"] = PITCH_X - without["x"]
    without["y"] = PITCH_Y - without["y"]
    return with_ball, without


def block_metrics(m: Match, tid: str) -> dict[str, Any] | None:
    """Forme du bloc (360) : largeur, profondeur, hauteur, couloirs occupés, avec et sans ballon.
    Calculée image par image, sur les images où au moins 8 joueurs de champ sont visibles."""
    if m.frames is None:
        return None
    wb, wo = _frames_by_side(m, tid)

    def per_frame(df: pd.DataFrame) -> pd.DataFrame:
        g = df.groupby("event_id")
        stats = pd.DataFrame(
            {
                "n": g.size(),
                "width": g["y"].quantile(0.9) - g["y"].quantile(0.1),
                "depth": g["x"].max() - g["x"].min(),
                "last_line": g["x"].min(),
                "height": g["x"].mean(),
            }
        )
        lanes = df.assign(lane=lane_of(df["y"]), opp_half=df["x"] >= PITCH_X / 2)
        stats["lanes"] = lanes[lanes["opp_half"]].groupby("event_id")["lane"].nunique()
        return stats[stats["n"] >= 8].fillna({"lanes": 0})

    a, b = per_frame(wb), per_frame(wo)
    if a.empty or b.empty:
        return None
    return {
        "with_ball": {
            k: _r(a[k].mean(), 1) for k in ("width", "depth", "last_line", "height", "lanes")
        }
        | {"frames": int(len(a))},
        "without_ball": {k: _r(b[k].mean(), 1) for k in ("width", "depth", "last_line", "height")}
        | {"frames": int(len(b))},
    }


# --- Section 3 · pressing ----------------------------------------------------------------------


def pressing(m: Match, tid: str, tr: pd.DataFrame) -> dict[str, Any]:
    ev = m.events[m.events["team"] == tid]
    has_pressure = bool((m.events["kind"] == "pressure").any())
    kinds = ("pressure",) if has_pressure else ("tackle", "interception", "foul")
    acts = ev[ev["kind"].isin(kinds)].dropna(subset=["x", "y"])
    rng = np.random.default_rng(len(acts))
    pts = acts[["x", "y"]].to_numpy()
    if len(pts) > 450:
        pts = pts[rng.choice(len(pts), 450, replace=False)]
    mine = tr[tr["team"] == tid] if not tr.empty else tr
    regains = mine["regain"].dropna() if len(mine) else pd.Series(dtype=float)
    bins = [0, 5, 10, 20, np.inf]
    hist = np.histogram(regains, bins=bins)[0] if len(regains) else np.zeros(4)
    opp = tr[tr["team"] != tid] if not tr.empty else tr  # pertes adverses = nos récupérations
    high = opp[opp["x_turn"].notna() & (opp["x_turn"] <= PITCH_X - 70)] if len(opp) else opp
    defensive = ev[ev["kind"].isin(("tackle", "interception", "pressure", "foul", "recovery"))]
    out_minutes = _minutes_without_ball(m, tid)
    return {
        "source": "pressures" if has_pressure else "defensive_actions",
        "points": np.round(pts, 1).tolist(),
        "count": int(len(acts)),
        "per_minute_out": _r(len(acts) / out_minutes, 2) if out_minutes else None,
        "counterpress_share": _r(acts["counterpress"].fillna(False).astype(bool).mean(), 3)
        if has_pressure and len(acts)
        else None,
        "height": _r(defensive["x"].mean(), 1),
        "losses": int(len(mine)),
        "regain_hist": [int(v) for v in hist],
        "regain_5s": _r((regains <= 5).mean(), 3) if len(regains) else None,
        "regain_10s": _r((regains <= 10).mean(), 3) if len(regains) else None,
        "high_recoveries": int(len(high)),
    }


def _minutes_without_ball(m: Match, tid: str) -> float:
    """Temps passé sans le ballon, au même compte que la possession (classic.possession_share)."""
    e = m.events[m.events["possession"].notna()].sort_values(["period", "t"])
    dt = e.groupby("period")["t"].diff(-1).abs().fillna(0).clip(upper=10)
    return float(dt[e["possession"] != tid].sum()) / 60


# --- Section 4 · relationnisme ------------------------------------------------------------------


def pass_network(m: Match, tid: str, min_passes: int = 4) -> list[list[Any]]:
    """Liens du réseau de passes entre titulaires (au moins `min_passes` passes réussies,
    dans un sens ou dans l'autre)."""
    pairs = _pass_pairs(m, tid).dropna(subset=["passer", "receiver"])
    starters = {p.id for p in m.players.values() if p.team == tid and p.starter}
    pairs = pairs[pairs["passer"].isin(starters) & pairs["receiver"].isin(starters)]
    counts: dict[tuple[str, str], int] = {}
    for a, b in zip(pairs["passer"], pairs["receiver"], strict=True):
        k = (str(a), str(b)) if str(a) < str(b) else (str(b), str(a))
        counts[k] = counts.get(k, 0) + 1
    return [
        [a, b, n] for (a, b), n in sorted(counts.items(), key=lambda kv: -kv[1]) if n >= min_passes
    ]


def relation_metrics(m: Match, tid: str) -> dict[str, Any]:
    """Les ingrédients du relationnisme : passes courtes, combinaisons rapides, joueurs qui
    sortent de leur couloir ; avec le 360 : proximité autour du ballon et couloirs occupés."""
    ev = m.events
    passes = ev[(ev["team"] == tid) & (ev["kind"] == "pass") & (ev["set_piece"] == "open")]
    ok = passes[passes["ok"].fillna(False).astype(bool)].dropna(subset=["x", "ex"])
    length = np.hypot(ok["ex"] - ok["x"], ok["ey"] - ok["y"])
    short = float((length < 15).mean()) if len(ok) else np.nan
    seq = passes.sort_values("t")
    dt = seq["t"].diff()
    same = (seq["chain"] == seq["chain"].shift()) & (seq["player"] != seq["player"].shift())
    quick = float(((dt <= 2.5) & same).sum() / max(1, len(seq)))
    touches = ev[(ev["team"] == tid) & ev["kind"].isin(ON_BALL)].dropna(subset=["y"])
    starters = [
        p.id for p in m.players.values() if p.team == tid and p.starter and p.position != "GK"
    ]
    spread = touches[touches["player"].isin(starters)].groupby("player")["y"].agg(["std", "size"])
    roaming = float(spread.loc[spread["size"] >= 15, "std"].mean()) if len(spread) else np.nan
    out: dict[str, Any] = {
        "short_share": _r(short, 3),
        "quick_share": _r(quick, 3),
        "roaming": _r(roaming, 1),
        "proximity": None,
        "lanes": None,
    }
    if m.frames is not None:
        wb, _ = _frames_by_side(m, tid)
        att = wb[wb["x_ball"] >= PITCH_X / 2]
        if len(att):
            d = np.hypot(att["x"] - att["x_ball"], att["y"] - att["y_ball"])
            near = att.assign(near=(d < 15) & ~att["actor"]).groupby("event_id")["near"].sum()
            lanes = (
                att[att["x"] >= PITCH_X / 2]
                .assign(lane=lambda f: lane_of(f["y"]))
                .groupby("event_id")["lane"]
                .nunique()
            )
            out["proximity"] = _r(near.mean(), 2)
            out["lanes"] = _r(lanes.mean(), 2)
    return out


# --- Section 5 · replis et rest defense ---------------------------------------------------------


def recovery_runs(m: Match, tid: str, tr: pd.DataFrame) -> dict[str, Any]:
    """Après une perte en jeu : combien de joueurs (visibles) sont entre le ballon et leur but
    au moment de la perte, puis 6 à 10 s plus tard.
    Sans 360, on garde ce que disent les événements : les tirs concédés en transition."""
    mine = tr[tr["team"] == tid] if not tr.empty else tr
    base: dict[str, Any] = {
        "losses": int(len(mine)),
        "shots_against": int(mine["shots_against"].sum()) if len(mine) else 0,
        "xg_against": _r(mine["xg_against"].sum(), 2) if len(mine) else 0.0,
        "goals_against": int(mine["goals_against"].sum()) if len(mine) else 0,
        "goal_minutes": sorted({int(v) + 1 for v in mine.loc[mine["goals_against"] > 0, "minute"]})
        if len(mine)
        else [],
        "behind_ball": None,
        "behind_8s": None,
        "gain": None,
        "back_7plus": None,
        "samples": 0,
        "example": None,
    }
    if m.frames is None or mine.empty:
        return base
    ev = m.events[m.events["event_id"].notna() & m.events["kind"].isin(ON_BALL)]
    ev = ev[ev["team"] != tid].sort_values("t")
    fr = m.frames
    them = fr[~fr["teammate"] & ~fr["keeper"]]
    by_event = {k: g for k, g in them.groupby("event_id")}
    times, periods = ev["t"].to_numpy(), ev["period"].to_numpy()
    ids, xs = ev["event_id"].to_numpy(), ev["x"].to_numpy(float)
    samples: list[dict[str, Any]] = []
    rows = zip(
        mine["t"].to_numpy(float),
        mine["regain"].to_numpy(float),
        mine["period"].to_numpy(int),
        strict=True,
    )
    for t0, regain, period in rows:
        limit = t0 + (regain if not np.isnan(regain) else 60.0)
        lo = int(np.searchsorted(times, t0, side="right"))
        hi = int(np.searchsorted(times, limit))
        idx = [k for k in range(lo, hi) if periods[k] == period]
        if not idx:
            continue
        k0 = idx[0]
        f0 = by_event.get(ids[k0])
        k1 = next(
            (
                k
                for k in idx
                if t0 + 6 <= times[k] <= t0 + 10 and len(by_event.get(ids[k], ())) >= 4
            ),
            None,
        )
        if f0 is None or len(f0) < 4 or k1 is None:
            continue
        f1 = by_event[ids[k1]]
        # repère de l'adversaire (qui attaque vers la droite) : notre but est en x = 105
        samples.append(
            {
                "behind": int((f0["x"] > xs[k0]).sum()),
                "behind_after": int((f1["x"] > xs[k1]).sum()),
                "n1": len(f1),
                "first": ev.iloc[k0],
                "e1": ev.iloc[k1],
            }
        )
    if not samples:
        return base
    behind = np.array([s["behind"] for s in samples])
    after = np.array([s["behind_after"] for s in samples])
    best = max(samples, key=lambda s: (s["behind_after"] - s["behind"], s["n1"]))
    base.update(
        {
            "behind_ball": _r(behind.mean(), 2),
            "behind_8s": _r(after.mean(), 2),
            "gain": _r((after - behind).mean(), 2),
            "back_7plus": _r((after >= 7).mean(), 3),
            "samples": len(samples),
            "example": _example(m, tid, best),
        }
    )
    return base


def _flip(df: pd.DataFrame) -> list[list[float]]:
    """Passe du repère de l'adversaire au nôtre (demi-tour du terrain)."""
    out: list[list[float]] = np.round(
        np.column_stack([PITCH_X - df["x"].to_numpy(float), PITCH_Y - df["y"].to_numpy(float)]), 1
    ).tolist()
    return out


def _example(m: Match, tid: str, s: dict[str, Any]) -> dict[str, Any]:
    """Deux images d'une perte de balle, dans le repère de l'équipe étudiée (elle attaque vers la
    droite) : à la perte, puis 6 à 10 s plus tard."""
    fr = m.frames
    assert fr is not None

    def snap(e: pd.Series) -> dict[str, Any]:
        f = fr[fr["event_id"] == e["event_id"]]
        carrier = m.players.get(str(e["player"]))
        return {
            "t": round(float(e["t"]), 1),
            "minute": int(e["minute"]),
            "us": _flip(f[~f["teammate"]]),
            "them": _flip(f[f["teammate"] & ~f["actor"]]),
            "ball": [round(PITCH_X - float(e["x"]), 1), round(PITCH_Y - float(e["y"]), 1)],
            "carrier": carrier.name if carrier else None,
        }

    return {
        "before": snap(s["first"]),
        "after": snap(s["e1"]),
        "behind": s["behind"],
        "behind_after": s["behind_after"],
    }


# --- Tout pour un match -------------------------------------------------------------------------


def team_analysis(m: Match) -> dict[str, dict[str, Any]]:
    tr = transitions(m)
    out = {}
    for t in (m.home, m.away):
        with_ball = average_positions(m, t.id, True)
        without = average_positions(m, t.id, False)
        out[t.id] = {
            "announced": m.formations.get(t.id),
            "shape": {
                "with_ball": with_ball,
                "without_ball": without,
                "formation_with": formation(with_ball),
                "formation_without": formation(without),
                "lanes": lane_grid(m, t.id),
                "block": block_metrics(m, t.id),
            },
            "network": pass_network(m, t.id),
            "pressing": pressing(m, t.id, tr),
            "relation": relation_metrics(m, t.id),
            "recovery": recovery_runs(m, t.id, tr),
        }
    return out


# --- Contexte d'une compétition -----------------------------------------------------------------

RELATION_KEYS = (
    ("short_share", 1),
    ("quick_share", 1),
    ("roaming", 1),
    ("proximity", 1),
    ("lanes", -1),
)
COMPARE = {
    "pressing": (
        "per_minute_out",
        "counterpress_share",
        "height",
        "regain_5s",
        "regain_10s",
        "high_recoveries",
    ),
    "relation": tuple(k for k, _ in RELATION_KEYS),
    "recovery": ("behind_ball", "behind_8s", "gain", "back_7plus", "shots_against", "xg_against"),
    "block_with": ("width", "depth", "last_line", "height", "lanes"),
    "block_without": ("width", "depth", "last_line", "height"),
}


def _block(d: dict[str, Any], phase: str) -> dict[str, Any]:
    b = d["shape"]["block"]
    return (b or {}).get(phase, {}) if b else {}


def _values(d: dict[str, Any], group: str) -> dict[str, Any]:
    if group == "block_with":
        return _block(d, "with_ball")
    if group == "block_without":
        return _block(d, "without_ball")
    out: dict[str, Any] = d[group]
    return out


def relation_index(rel: dict[str, Any], stats: dict[str, dict[str, float]]) -> float | None:
    """Moyenne des écarts réduits (z) des ingrédients disponibles, orientés « relationniste »."""
    zs = []
    for k, sign in RELATION_KEYS:
        v, s = rel.get(k), stats.get(k)
        if v is None or not s or not s.get("sd"):
            continue
        zs.append(sign * (v - s["mean"]) / s["sd"])
    return round(float(np.mean(zs)), 3) if zs else None


def context(analyses: list[tuple[str, str, dict[str, Any]]]) -> dict[str, Any]:
    """`analyses` : (identifiant d'équipe, nom, analyse d'une équipe sur un match).
    Renvoie les moyennes et écarts-types de la compétition, et l'indice moyen de chaque équipe."""
    stats: dict[str, dict[str, dict[str, float]]] = {}
    for group, keys in COMPARE.items():
        stats[group] = {}
        for k in keys:
            vals = [v for _, _, d in analyses if (v := _values(d, group).get(k)) is not None]
            if len(vals) >= 3:
                stats[group][k] = {
                    "mean": round(float(np.mean(vals)), 4),
                    "sd": round(float(np.std(vals)), 4),
                    "min": round(float(np.min(vals)), 4),
                    "max": round(float(np.max(vals)), 4),
                }
    teams: dict[str, dict[str, Any]] = {}
    for tid, name, d in analyses:
        idx = relation_index(d["relation"], stats["relation"])
        t = teams.setdefault(tid, {"id": tid, "name": name, "matches": 0, "index": []})
        t["matches"] += 1
        if idx is not None:
            t["index"].append(idx)
    points = [
        {
            "id": t["id"],
            "name": t["name"],
            "matches": t["matches"],
            "index": round(float(np.mean(t["index"])), 3),
        }
        for t in teams.values()
        if t["index"]
    ]
    return {"stats": stats, "teams": sorted(points, key=lambda p: p["index"])}

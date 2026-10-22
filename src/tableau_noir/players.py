"""Sections 6 à 9 · les joueurs : gravité, valeur des actions, classements par poste, jumeaux.

Trois étages :
1. `match_players` : sur un match, la valeur (xT) de chaque passe et conduite, et les données
   brutes de gravité (adversaires autour de chaque touche de balle) ;
2. `tournament` : sur une compétition, la gravité corrigée de la zone, les cumuls par 90 minutes,
   les classements par poste et les profils ;
3. `twins` : les jumeaux statistiques, toutes compétitions confondues.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np
import pandas as pd

from tableau_noir.model import PITCH_X, PITCH_Y, Match
from tableau_noir.xt import XTModel

ROLES = ("GK", "CB", "FB", "MF", "FW")
TOUCH = ("pass", "carry", "shot", "dribble")
DEFENSIVE = ("pressure", "tackle", "foul", "interception", "block", "duel")
RADIUS_360 = 10.0  # adversaires « autour » d'une touche, sur l'image 360
RADIUS_EV, WINDOW_EV = 5.0, (-1.0, 2.0)  # actions défensives adverses près d'une touche
NZ = 18  # 6 bandes de 17,5 m × 3 couloirs (axe, intérieur, côté), symétriques


def _r(v: float | None, d: int = 2) -> float | None:
    if v is None or not np.isfinite(v):
        return None
    return round(float(v), d)


def zone(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    band = np.clip((np.asarray(x, float) / PITCH_X * 6).astype(int), 0, 5)
    off = np.abs(np.asarray(y, float) - PITCH_Y / 2)
    lane = np.where(off < 9.16, 0, np.where(off < 20.16, 1, 2))
    out: np.ndarray = band * 3 + lane
    return out


def role(position: str, xs: list[float], ys: list[float]) -> str:
    """Poste de jeu : la source donne GK / DF / MF / FW ; on sépare les défenseurs centraux des
    latéraux d'après l'endroit où ils touchent le ballon."""
    if position == "GK":
        return "GK"
    mx = float(np.median(xs)) if xs else 52.5
    wide = float(np.median(np.abs(np.array(ys) - PITCH_Y / 2))) if ys else 0.0
    if position == "DF":
        return "FB" if wide > 15 else "CB"
    if position in ("MF", "FW"):
        return position
    return "CB" if mx < 35 else "MF" if mx < 70 else "FW"


# --- 1. Le match ---------------------------------------------------------------------------------


def _gravity_360(m: Match, touches: pd.DataFrame) -> pd.Series:
    """Nombre d'adversaires (hors gardien) à moins de 10 m, pour chaque touche qui a une image."""
    if m.frames is None:
        return pd.Series(dtype=float)
    opp = m.frames[~m.frames["teammate"] & ~m.frames["keeper"]]
    t = touches.reset_index()[["index", "event_id", "x", "y"]].rename(
        columns={"x": "bx", "y": "by"}
    )
    j = opp.merge(t, on="event_id")
    j["near"] = np.hypot(j["x"] - j["bx"], j["y"] - j["by"]) <= RADIUS_360
    seen = touches.index[touches["event_id"].isin(set(m.frames["event_id"]))]
    out = j.groupby("index")["near"].sum().reindex(seen, fill_value=0)
    return out.astype(float)


def _gravity_events(m: Match, touches: pd.DataFrame) -> pd.Series:
    """Actions défensives adverses (pressions, tacles, fautes…) à moins de 5 m et 2 s d'une
    touche : l'« attention » reçue, mesurable pour toutes les sources."""
    ev = m.events
    out = pd.Series(0.0, index=touches.index)
    for tid in (m.home.id, m.away.id):
        mine = touches[touches["team"] == tid]
        d = ev[(ev["team"] != tid) & ev["kind"].isin(DEFENSIVE)].dropna(subset=["x", "y"])
        d = d.sort_values("t")
        dt, dx, dy = d["t"].to_numpy(), PITCH_X - d["x"].to_numpy(), PITCH_Y - d["y"].to_numpy()
        lo = np.searchsorted(dt, mine["t"].to_numpy() + WINDOW_EV[0])
        hi = np.searchsorted(dt, mine["t"].to_numpy() + WINDOW_EV[1], side="right")
        xs, ys = mine["x"].to_numpy(), mine["y"].to_numpy()
        counts = [
            int((np.hypot(dx[a:b] - x, dy[a:b] - y) <= RADIUS_EV).sum()) if b > a else 0
            for a, b, x, y in zip(lo, hi, xs, ys, strict=True)
        ]
        out.loc[mine.index] = np.array(counts, dtype=float)
    return out


def _zone_sums(z: np.ndarray, v: np.ndarray) -> list[list[float]]:
    n = np.bincount(z, minlength=NZ)
    s = np.bincount(z, weights=v, minlength=NZ)
    return [[int(a), round(float(b), 2)] for a, b in zip(n, s, strict=True)]


def match_players(m: Match, model: XTModel) -> dict[str, Any]:
    """Pour chaque joueur : xT apporté, poste, et sommes brutes de gravité par zone (internes)."""
    ev = m.events.copy()
    ev["xt"] = model.added(ev)
    touches = ev[ev["kind"].isin(TOUCH) & ev["player"].notna()].dropna(subset=["x", "y"])
    g360 = _gravity_360(m, touches)
    gev = _gravity_events(m, touches)
    side = {m.home.id: "home", m.away.id: "away"}
    rows: dict[str, dict[str, Any]] = {}
    zones: dict[str, dict[str, list[list[float]]]] = {}
    for p in m.players.values():
        if p.minutes <= 0:
            continue
        e = ev[ev["player"] == p.id]
        t = touches[touches["player"] == p.id]
        shots = e[e["kind"] == "shot"]
        np_shots = shots[shots["set_piece"] != "penalty"]
        rows[p.id] = {
            "role": role(p.position, t["x"].tolist(), t["y"].tolist()),
            "npxg": _r(float(np_shots["xg"].fillna(0).sum()), 2),
            "xt": _r(float(e["xt"].sum()), 3),
            "xt_pass": _r(float(e.loc[e["kind"] == "pass", "xt"].sum()), 3),
            "xt_carry": _r(float(e.loc[e["kind"] == "carry", "xt"].sum()), 3),
            "saves": int(((e["kind"] == "save") & e["ok"].fillna(False).astype(bool)).sum()),
            "x": _r(float(t["x"].median()), 1) if len(t) else None,
            "y": _r(float(t["y"].median()), 1) if len(t) else None,
        }
        if rows[p.id]["role"] == "GK":
            rows[p.id] |= _keeper(m, p.team, p.minutes)
        tz = zone(t["x"].to_numpy(), t["y"].to_numpy())
        z360 = t.index.isin(g360.index)
        zones[p.id] = {
            "g360": _zone_sums(tz[z360], g360.reindex(t.index[z360]).to_numpy(float)),
            "gev": _zone_sums(tz, gev.reindex(t.index).to_numpy(float)),
        }
    return {
        "rows": rows,
        "zones": zones,
        "actions": {side[tid]: _top_actions(ev, m, tid) for tid in side},
        "xt_minutes": {side[tid]: _xt_minutes(ev, m, tid) for tid in side},
    }


def _keeper(m: Match, tid: str, minutes: float) -> dict[str, Any]:
    """Gardien : tirs adverses et buts encaissés, au prorata de son temps de jeu."""
    ev = m.events
    share = min(1.0, minutes / max(m.duration, 1))
    shots = ev[(ev["team"] != tid) & (ev["kind"] == "shot")]
    on_target = shots[shots["ok"].fillna(False).astype(bool) | shots["goal"].fillna(False)]
    conceded = (m.away if m.home.id == tid else m.home).score
    return {
        "xg_faced": _r(float(on_target["xg"].fillna(0).sum()) * share, 2),
        "conceded": _r(conceded * share, 2),
    }


def _top_actions(ev: pd.DataFrame, m: Match, tid: str, n: int = 6) -> list[dict[str, Any]]:
    a = ev[(ev["team"] == tid) & (ev["xt"] > 0)].nlargest(n, "xt")
    out = []
    for r in a.to_dict("records"):
        pid = str(r["player"])
        out.append(
            {
                "player": pid,
                "name": m.players[pid].name if pid in m.players else "?",
                "kind": str(r["kind"]),
                "minute": int(r["minute"]) + 1,
                "x": _r(r["x"], 1),
                "y": _r(r["y"], 1),
                "ex": _r(r["ex"], 1),
                "ey": _r(r["ey"], 1),
                "xt": _r(r["xt"], 3),
            }
        )
    return out


def _xt_minutes(ev: pd.DataFrame, m: Match, tid: str) -> list[float]:
    """xT apporté minute par minute (pour la course à la menace)."""
    e = ev[(ev["team"] == tid) & (ev["xt"] != 0)]
    n = int(m.duration)
    s = np.bincount(np.clip(e["minute"].to_numpy(int), 0, n - 1), weights=e["xt"], minlength=n)
    return [round(float(v), 3) for v in s]


# --- 2. La compétition ---------------------------------------------------------------------------

PER90 = (
    "goals",
    "assists",
    "npxg",
    "shots",
    "xt",
    "key_passes",
    "progressive",
    "dribbles",
    "def_actions",
    "touches",
    "saves",
    "prevented",
)
ROLE_METRICS = {
    "FW": ("npxg", "goals", "shots", "xt", "key_passes", "dribbles"),
    "MF": ("xt", "progressive", "key_passes", "pass_rate", "def_actions", "duel_rate"),
    "FB": ("xt", "progressive", "key_passes", "def_actions", "duel_rate", "dribbles"),
    "CB": ("def_actions", "duel_rate", "progressive", "pass_rate", "xt"),
    "GK": ("prevented", "save_pct", "saves", "pass_rate"),
}
PROFILE = {
    "outfield": (
        "npxg",
        "shots",
        "xt",
        "key_passes",
        "progressive",
        "dribbles",
        "def_actions",
        "touches",
        "pass_rate",
        "duel_rate",
    ),
    "GK": ("prevented", "save_pct", "saves", "pass_rate", "touches"),
}
MIN_MATCH_TOUCHES = 15


def _baseline(zones: list[dict[str, list[list[float]]]], key: str) -> np.ndarray:
    n = np.zeros(NZ)
    s = np.zeros(NZ)
    for z in zones:
        a = np.array(z[key], float)
        n += a[:, 0]
        s += a[:, 1]
    out: np.ndarray = np.divide(s, n, out=np.zeros(NZ), where=n > 0)
    return out


def _excess(z: list[list[float]], base: np.ndarray) -> tuple[float, int]:
    a = np.array(z, float)
    n = a[:, 0].sum()
    if n == 0:
        return 0.0, 0
    return float((a[:, 1] - a[:, 0] * base).sum()), int(n)


def gravity(
    matches: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, tuple[np.ndarray, np.ndarray]]:
    """Ajoute à chaque joueur de chaque match sa gravité : adversaires en plus de la moyenne
    de la compétition autour d'une touche dans la même zone (360), et attention reçue
    (actions défensives adverses de plus que la moyenne, pour 10 touches)."""
    allz = [z for _, mp in matches for z in mp["zones"].values()]
    base = {k: _baseline(allz, k) for k in ("g360", "gev")}
    for data, mp in matches:
        for row in data["players"]:
            z = mp["zones"].get(row["id"])
            if not z:
                continue
            e360, n360 = _excess(z["g360"], base["g360"])
            eev, nev = _excess(z["gev"], base["gev"])
            row["gravity"] = _r(e360 / n360, 2) if n360 >= MIN_MATCH_TOUCHES else None
            row["gravity_n"] = n360
            row["attention"] = _r(10 * eev / nev, 2) if nev >= MIN_MATCH_TOUCHES else None
    return {"base": (base["g360"], base["gev"])}


def _percentile(values: np.ndarray, v: float) -> float:
    return float((values < v).mean() + 0.5 * (values == v).mean())


def tournament(
    comp: dict[str, Any], matches: list[tuple[dict[str, Any], dict[str, Any]]]
) -> dict[str, Any]:
    """Cumuls par joueur, classements par poste et profils d'une compétition."""
    gravity(matches)
    acc: dict[str, dict[str, Any]] = {}
    role_minutes: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    grav: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0, 0.0])
    for data, mp in matches:
        team_names = {data["meta"][s]["id"]: data["meta"][s]["name"] for s in ("home", "away")}
        for row in data["players"]:
            extra = mp["rows"].get(row["id"], {})
            a = acc.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "name": row["name"],
                    "team": team_names.get(row["team"], row["team"]),
                    "matches": 0,
                    "minutes": 0.0,
                }
                | dict.fromkeys(
                    (
                        "goals",
                        "assists",
                        "npxg",
                        "shots",
                        "xt",
                        "key_passes",
                        "progressive",
                        "dribbles",
                        "def_actions",
                        "touches",
                        "passes",
                        "passes_ok",
                        "duels",
                        "duels_won",
                        "saves",
                        "xg_faced",
                        "conceded",
                    ),
                    0.0,
                ),
            )
            a["matches"] += 1
            a["minutes"] += row["minutes"]
            for k in (
                "goals",
                "assists",
                "shots",
                "key_passes",
                "progressive",
                "dribbles",
                "def_actions",
                "touches",
                "passes",
                "passes_ok",
                "duels",
                "duels_won",
            ):
                a[k] += row[k]
            for k in ("npxg", "xt", "saves", "xg_faced", "conceded"):
                a[k] += extra.get(k) or 0.0
            role_minutes[row["id"]][extra.get("role", "MF")] += row["minutes"]
            g = grav[row["id"]]
            if row.get("gravity") is not None:
                g[0] += row["gravity"] * row["gravity_n"]
                g[1] += row["gravity_n"]
            if row.get("attention") is not None:
                g[2] += row["attention"] * row["minutes"]
                g[3] += row["minutes"]
    min_minutes = 180.0 if comp.get("kind") == "tournament" else 90.0
    players: dict[str, dict[str, Any]] = {}
    for pid, a in acc.items():
        if a["minutes"] < min_minutes:
            continue
        r = max(role_minutes[pid].items(), key=lambda kv: kv[1])[0]
        p90 = 90.0 / a["minutes"]
        a["prevented"] = a["xg_faced"] - a["conceded"]
        out = {
            "id": pid,
            "name": a["name"],
            "team": a["team"],
            "role": r,
            "matches": a["matches"],
            "minutes": round(a["minutes"]),
            "totals": {
                k: _r(a[k], 2) for k in ("goals", "assists", "npxg", "xt", "shots", "key_passes")
            },
            "per90": {k: _r(a[k] * p90, 3) for k in PER90},
        }
        out["per90"]["pass_rate"] = _r(a["passes_ok"] / a["passes"], 3) if a["passes"] else None
        out["per90"]["duel_rate"] = _r(a["duels_won"] / a["duels"], 3) if a["duels"] else None
        shots_on = a["saves"] + a["conceded"]
        out["per90"]["save_pct"] = _r(a["saves"] / shots_on, 3) if shots_on else None
        g = grav[pid]
        out["gravity"] = _r(g[0] / g[1], 2) if g[1] >= 40 else None
        out["attention"] = _r(g[2] / g[3], 2) if g[3] else None
        players[pid] = out
    rankings = _rank(players)
    _profiles(players)
    return {
        "comp": comp["id"],
        "min_minutes": min_minutes,
        "rankings": rankings,
        "players": players,
    }


def _rank(players: dict[str, dict[str, Any]], top: int = 15) -> dict[str, list[str]]:
    """Note de poste = moyenne des centiles (dans le poste, dans la compétition) des
    indicateurs du poste."""
    out: dict[str, list[str]] = {}
    for r in ROLES:
        group = [p for p in players.values() if p["role"] == r]
        if not group:
            out[r] = []
            continue
        pct: dict[str, dict[str, float]] = defaultdict(dict)
        for k in ROLE_METRICS[r]:
            vals = np.array([p["per90"].get(k) for p in group if p["per90"].get(k) is not None])
            for p in group:
                v = p["per90"].get(k)
                if v is not None and len(vals):
                    pct[p["id"]][k] = _percentile(vals, v)
        for p in group:
            got = pct[p["id"]]
            p["pct"] = {k: round(v, 3) for k, v in got.items()}
            p["score"] = round(float(np.mean(list(got.values()))), 3) if got else 0.0
        ranked = sorted(group, key=lambda p: -p["score"])
        for i, p in enumerate(ranked, 1):
            p["rank"] = i
            p["of"] = len(ranked)
        out[r] = [p["id"] for p in ranked[:top]]
    return out


def _profiles(players: dict[str, dict[str, Any]]) -> None:
    """Profil = indicateurs réduits (z) dans la compétition, ce qui gomme en partie les
    différences de comptage entre StatsBomb et Wyscout."""
    for family, keys in PROFILE.items():
        group = [p for p in players.values() if (p["role"] == "GK") == (family == "GK")]
        if len(group) < 3:
            continue
        mat = np.array([[p["per90"].get(k) for k in keys] for p in group], dtype=float)
        mu = np.nanmean(mat, axis=0)
        sd = np.nanstd(mat, axis=0)
        sd[sd == 0] = 1
        z = np.nan_to_num((mat - mu) / sd)
        for p, row in zip(group, z, strict=True):
            p["profile"] = [round(float(v), 3) for v in row]


# --- 3. Les jumeaux ------------------------------------------------------------------------------


def twins(tables: dict[str, dict[str, Any]], n: int = 3) -> None:
    """Pour chaque joueur de chaque compétition, les `n` profils les plus proches (similarité
    cosinus), au même poste, toutes compétitions confondues, en excluant le joueur lui-même."""
    pool = [
        (cid, p)
        for cid, tab in tables.items()
        for p in tab["players"].values()
        if p.get("profile") is not None
    ]
    for r in ROLES:
        items = [(c, p) for c, p in pool if p["role"] == r]
        if len(items) < 2:
            continue
        mat = np.array([p["profile"] for _, p in items], float)
        norm = np.linalg.norm(mat, axis=1)
        norm[norm == 0] = 1
        unit = mat / norm[:, None]
        sim = unit @ unit.T
        names = [p["name"] for _, p in items]
        for i, (_, p) in enumerate(items):
            order = np.argsort(-sim[i])
            found = []
            for j in order:
                if j == i or names[j] == names[i]:
                    continue
                c2, q = items[j]
                found.append(
                    {
                        "comp": c2,
                        "id": q["id"],
                        "name": q["name"],
                        "team": q["team"],
                        "sim": round(float(sim[i, j]), 3),
                    }
                )
                if len(found) == n:
                    break
            p["twins"] = found

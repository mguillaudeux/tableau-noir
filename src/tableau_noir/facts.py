"""La fiche de faits d'un match : tout ce que le coin de l'analyste a le droit de citer.

Les textes du coin de l'analyste sont écrits à la main, match par match, à partir de cette fiche.
Elle rassemble les chiffres déjà publiés sur le site, arrondis comme on les écrit (parts en
pourcentage entier, xG à deux décimales…), plus quelques écarts précalculés. `check` vérifie
ensuite que chaque nombre d'un texte figure dans la fiche : on ne raconte que ce qui est mesuré.
"""

from __future__ import annotations

import re
from typing import Any

from tableau_noir.team import relation_index

SIDES = ("home", "away")
OTHER = {"home": "away", "away": "home"}
LANES = ("couloir gauche", "demi-espace gauche", "axe", "demi-espace droit", "couloir droit")


def _pct(v: float | None) -> int | None:
    return None if v is None else round(v * 100)


def _r(v: float | None, d: int = 2) -> float | None:
    return None if v is None else round(float(v), d)


def _mean(ctx: dict[str, Any], group: str, key: str, d: int = 2) -> float | None:
    v = ctx.get("stats", {}).get(group, {}).get(key)
    return None if v is None else round(float(v["mean"]), d)


def facts(
    d: dict[str, Any],
    ctx: dict[str, Any],
    table: dict[str, Any],
    catalogue: dict[str, Any] | None = None,
) -> dict[str, Any]:
    m = d["meta"]
    names = {s: m[s]["name"] for s in SIDES}
    pname = {p["id"]: p["name"] for p in d["players"]}
    side_of = {p["id"]: p["side"] for p in d["players"]}
    st = d["stats"]
    tm = d["team"]

    # --- le match
    shots = d["shots"]
    goals = []
    for g in d["goals"]:
        shot = next(
            (s for s in shots if s["goal"] and s["player"] == g["player"] and s["t"] == g["t"]),
            None,
        )
        goals.append(
            {
                "minute": g["minute"] + 1,
                "team": names[g["side"]],
                "scorer": pname.get(g["player"], "?"),
                "penalty": bool(g.get("penalty")),
                "own_goal": bool(g.get("own_goal")),
                "xg": _r(shot["xg"]) if shot else None,
                "in_transition": (g["minute"] + 1)
                in (tm[OTHER[g["side"]]]["recovery"].get("goal_minutes") or []),
            }
        )
    missed = sorted((s for s in shots if not s["goal"]), key=lambda s: -s["xg"])[:4]
    match = {
        "competition": m["competition"],
        "season": m["season"],
        "stage": m["stage"],
        "date": m["date"],
        "home": names["home"],
        "away": names["away"],
        "score": f"{m['home']['score']}-{m['away']['score']}",
        "penalties": f"{m['home']['penalties']}-{m['away']['penalties']}"
        if m["home"].get("penalties") is not None
        else None,
        "extra_time": m["duration"] > 90,
        "data": "StatsBomb 360"
        if m.get("has_360")
        else ("Wyscout" if m["source"] == "wyscout" else "StatsBomb"),
        "goals": goals,
        "biggest_misses": [
            {
                "minute": s["minute"] + 1,
                "team": names[s["side"]],
                "player": pname.get(s["player"], "?"),
                "xg": _r(s["xg"]),
                "on_target": s["on_target"],
                "penalty": s["set_piece"] == "penalty",
            }
            for s in missed
            if s["xg"] >= 0.1
        ],
        "red_cards": {names[s]: st[s]["red"] for s in SIDES if st[s]["red"]},
    }
    if catalogue:
        match["paths"] = _paths(catalogue, m)

    # --- section 1
    keys1 = (
        "goals",
        "shots",
        "on_target",
        "big_chances",
        "passes",
        "progressive",
        "final_third",
        "key_passes",
        "duels_won",
        "aerials_won",
        "tackles_won",
        "interceptions",
        "recoveries",
        "clearances",
        "saves",
        "fouls",
        "yellow",
        "red",
        "corners",
        "offsides",
    )
    s1: dict[str, Any] = {
        names[s]: {k: st[s].get(k) for k in keys1}
        | {
            "xg": _r(st[s]["xg"]),
            "npxg": _r(st[s]["npxg"]),
            "possession_pct": _pct(st[s]["possession"]),
            "pass_rate_pct": _pct(st[s]["pass_rate"]),
            "ppda": _r(st[s]["ppda"], 1),
        }
        for s in SIDES
    }
    s1["xg_gap"] = _r(abs(st["home"]["xg"] - st["away"]["xg"]))
    s1["standouts"] = [
        _player(p) for p in sorted(d["players"], key=_standout_score, reverse=True)[:5]
    ]

    # --- section 2
    s2 = {}
    for s in SIDES:
        sh = tm[s]["shape"]
        grid = sh["lanes"]
        lanes = [sum(grid[t][i] for t in range(3)) for i in range(5)]
        block = sh.get("block") or {}
        s2[names[s]] = {
            "announced": tm[s].get("announced"),
            "formation_with_ball": sh.get("formation_with"),
            "formation_without_ball": sh.get("formation_without"),
            "touches_by_lane_pct": {LANES[i]: _pct(v) for i, v in enumerate(lanes)},
            "touches_by_third_pct": {
                "own": _pct(sum(grid[0])),
                "middle": _pct(sum(grid[1])),
                "final": _pct(sum(grid[2])),
            },
            "block_360": {
                ph: {k: _r(v, 1) for k, v in vals.items() if k != "frames"}
                for ph, vals in block.items()
            }
            or None,
            "average_positions_with_ball": [
                {"name": p["name"], "x_m": _r(p["x"], 0), "y_m": _r(p["y"], 0)}
                for p in sorted(sh["with_ball"], key=lambda p: p["x"])
            ],
        }
    s2["competition_mean_block"] = {
        "with_ball": {
            k: _mean(ctx, "block_with", k, 1) for k in ("width", "height", "last_line", "lanes")
        },
        "without_ball": {
            k: _mean(ctx, "block_without", k, 1) for k in ("width", "depth", "last_line")
        },
    }

    # --- section 3
    s3 = {}
    for s in SIDES:
        pr = tm[s]["pressing"]
        hist = pr["regain_hist"]
        tot = sum(hist) or 1
        s3[names[s]] = {
            "source": pr["source"],
            "ppda": _r(st[s]["ppda"], 1),
            "pressures_or_actions": pr["count"],
            "per_minute_out_of_possession": _r(pr["per_minute_out"], 1),
            "counterpress_pct": _pct(pr["counterpress_share"]),
            "defensive_height_m": _r(pr["height"], 1),
            "open_play_losses": pr["losses"],
            "regained_under_5s_pct": _pct(pr["regain_5s"]),
            "regained_under_10s_pct": _pct(pr["regain_10s"]),
            "regain_time_split_pct": {
                "<5s": round(100 * hist[0] / tot),
                "5-10s": round(100 * hist[1] / tot),
                "10-20s": round(100 * hist[2] / tot),
                ">20s": round(100 * hist[3] / tot),
            },
            "high_recoveries": pr["high_recoveries"],
        }
    s3["competition_mean"] = {
        "per_minute_out_of_possession": _mean(ctx, "pressing", "per_minute_out", 1),
        "counterpress_pct": _pct(_mean(ctx, "pressing", "counterpress_share", 3)),
        "regained_under_5s_pct": _pct(_mean(ctx, "pressing", "regain_5s", 3)),
        "high_recoveries": _mean(ctx, "pressing", "high_recoveries", 1),
        "defensive_height_m": _mean(ctx, "pressing", "height", 1),
    }

    # --- section 4
    rel_stats = ctx.get("stats", {}).get("relation", {})
    s4: dict[str, Any] = {}
    for s in SIDES:
        r = tm[s]["relation"]
        net = tm[s].get("network") or []
        deg: dict[str, int] = {}
        for a, b, n in net:
            deg[a] = deg.get(a, 0) + n
            deg[b] = deg.get(b, 0) + n
        s4[names[s]] = {
            "relational_index": _r(relation_index(r, rel_stats)),
            "short_passes_pct": _pct(r.get("short_share")),
            "quick_combinations_pct": _pct(r.get("quick_share")),
            "lateral_freedom_m": _r(r.get("roaming"), 1),
            "teammates_near_ball_360": _r(r.get("proximity")),
            "lanes_occupied_360": _r(r.get("lanes")),
            "network_hubs": [
                {"name": pname.get(k, "?"), "passes_involved": v}
                for k, v in sorted(deg.items(), key=lambda kv: -kv[1])[:3]
            ],
            "strongest_links": [
                {"pair": f"{pname.get(a, '?')} – {pname.get(b, '?')}", "passes": n}
                for a, b, n in net[:3]
            ],
        }
    s4["competition_mean"] = {
        "short_passes_pct": _pct(_mean(ctx, "relation", "short_share", 3)),
        "quick_combinations_pct": _pct(_mean(ctx, "relation", "quick_share", 3)),
        "lateral_freedom_m": _mean(ctx, "relation", "roaming", 1),
    }
    teams = ctx.get("teams", [])
    s4["competition_axis"] = {
        "most_positional": [{"team": t["name"], "index": t["index"]} for t in teams[:3]],
        "most_relational": [{"team": t["name"], "index": t["index"]} for t in teams[-3:]],
        "teams_ranked": len(teams),
    }
    ranked = [t["name"] for t in teams]
    for s in SIDES:
        if names[s] in ranked:
            s4[names[s]]["tournament_rank_most_relational"] = len(ranked) - ranked.index(names[s])

    # --- section 5
    s5 = {}
    for s in SIDES:
        r = tm[s]["recovery"]
        ex = r.get("example")
        s5[names[s]] = {
            "open_play_losses": r["losses"],
            "shots_conceded_within_15s_of_loss": r["shots_against"],
            "xg_conceded_in_transition": _r(r["xg_against"]),
            "goals_conceded_in_transition_minutes": r.get("goal_minutes") or [],
            "players_behind_ball_at_loss_360": _r(r.get("behind_ball"), 1),
            "players_behind_ball_6_10s_later_360": _r(r.get("behind_8s"), 1),
            "block_rebuilt_7plus_pct_360": _pct(r.get("back_7plus")),
            "example_360": {
                "minute": ex["before"]["minute"] + 1,
                "behind_at_loss": ex["behind"],
                "behind_after": ex["behind_after"],
            }
            if ex
            else None,
        }
    s5["competition_mean"] = {
        "shots_conceded_within_15s_of_loss": _mean(ctx, "recovery", "shots_against", 1),
        "xg_conceded_in_transition": _mean(ctx, "recovery", "xg_against"),
        "players_behind_ball_6_10s_later_360": _mean(ctx, "recovery", "behind_8s", 1),
        "block_rebuilt_7plus_pct_360": _pct(_mean(ctx, "recovery", "back_7plus", 3)),
    }

    # --- section 6
    key = "gravity" if m.get("has_360") else "attention"
    gp = [p for p in d["players"] if p.get(key) is not None and p.get("role") != "GK"]
    gp.sort(key=lambda p: -p[key])
    tab = table.get("players", {})
    comp_top = sorted(
        (p for p in tab.values() if p.get(key) is not None and p["role"] != "GK"),
        key=lambda p: -p[key],
    )[:5]
    s6 = {
        "measure": "extra opponents within 10 m per touch, vs same-zone tournament average (360)"
        if key == "gravity"
        else "extra opponent defensive actions per 10 touches, vs same-zone average",
        "top": [{"name": p["name"], "team": names[p["side"]], "value": _r(p[key])} for p in gp[:6]],
        "bottom": [
            {"name": p["name"], "team": names[p["side"]], "value": _r(p[key])} for p in gp[-3:]
        ],
        "tournament_top": [
            {"name": p["name"], "team": p["team"], "value": _r(p[key])} for p in comp_top
        ],
    }

    # --- section 7
    xt = {s: sum(p.get("xt") or 0 for p in d["players"] if p["side"] == s) for s in SIDES}
    mins = d.get("value", {}).get("xt_minutes", {})
    s7: dict[str, Any] = {
        names[s]: {
            "xt_total": _r(xt[s]),
            "xt_first_half": _r(sum(mins.get(s, [])[:45])),
            "xt_second_half": _r(sum(mins.get(s, [])[45:90])),
            "xt_extra_time": _r(sum(mins.get(s, [])[90:])) if m["duration"] > 90 else None,
            "top_actions": [
                {
                    "player": a["name"],
                    "minute": a["minute"],
                    "kind": a["kind"],
                    "xt": _r(a["xt"]),
                    "from_x_m": _r(a["x"], 0),
                    "to_x_m": _r(a["ex"], 0),
                }
                for a in d.get("value", {}).get("actions", {}).get(s, [])[:4]
            ],
        }
        for s in SIDES
    }
    s7["creators"] = [
        {
            "name": p["name"],
            "team": names[p["side"]],
            "xt": _r(p["xt"]),
            "xt_passes": _r(p.get("xt_pass")),
            "xt_carries": _r(p.get("xt_carry")),
        }
        for p in sorted(d["players"], key=lambda p: -(p.get("xt") or 0))[:6]
    ]
    for c in s7["creators"]:
        tot = xt[side_of[next(p["id"] for p in d["players"] if p["name"] == c["name"])]]
        c["share_of_team_pct"] = _pct(c["xt"] / tot) if tot > 0 and c["xt"] else None

    # --- sections 8 et 9
    here = [tab[p["id"]] | {"side": p["side"]} for p in d["players"] if p["id"] in tab]
    here.sort(key=lambda p: p["rank"] / max(p["of"], 1))
    s8 = {
        "min_minutes": table.get("min_minutes"),
        "players": [
            {
                "name": p["name"],
                "team": names[p["side"]],
                "role": p["role"],
                "rank": p["rank"],
                "of": p["of"],
                "score_pct": round(p["score"] * 100),
                "tournament_minutes": p["minutes"],
                "tournament_goals": p["totals"]["goals"],
                "tournament_assists": p["totals"]["assists"],
            }
            for p in here[:12]
        ],
        "role_leaders": {
            r: [tab[i]["name"] for i in ids[:3]] for r, ids in table.get("rankings", {}).items()
        },
    }
    s9 = {
        "players": [
            {
                "name": p["name"],
                "team": names[p["side"]],
                "role": p["role"],
                "twins": [
                    {
                        "name": t["name"],
                        "team": t["team"],
                        "competition": t["comp"],
                        "similarity_pct": round(max(0.0, t["sim"]) * 100),
                    }
                    for t in p.get("twins", [])[:3]
                ],
            }
            for p in sorted(here, key=lambda p: -p.get("score", 0))[:10]
            if p.get("twins")
        ]
    }
    return {
        "match": match,
        "s1": s1,
        "s2": s2,
        "s3": s3,
        "s4": s4,
        "s5": s5,
        "s6": s6,
        "s7": s7,
        "s8": s8,
        "s9": s9,
    }


def _standout_score(p: dict[str, Any]) -> float:
    return float(
        p["goals"] * 2.5
        + p["assists"] * 1.6
        + p["xg"] * 0.8
        + p["key_passes"] * 0.15
        + p["progressive"] * 0.03
        + p["def_actions"] * 0.04
        + (p.get("xt") or 0) * 1.5
    )


def _player(p: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": p["name"],
        "minutes": round(p["minutes"]),
        "goals": p["goals"],
        "assists": p["assists"],
        "shots": p["shots"],
        "xg": _r(p["xg"]),
        "key_passes": p["key_passes"],
        "progressive_passes": p["progressive"],
        "dribbles": p["dribbles"],
        "defensive_actions": p["def_actions"],
        "xt": _r(p.get("xt")),
    }


def _paths(catalogue: dict[str, Any], meta: dict[str, Any]) -> dict[str, list[str]]:
    """Le parcours de chaque équipe dans les matchs à élimination directe précédents."""
    comp = next((c for c in catalogue["competitions"] if c["id"] == meta["comp"]), None)
    out: dict[str, list[str]] = {}
    if not comp or comp.get("kind") != "tournament":
        return out
    for s in SIDES:
        name = meta[s]["name"]
        rows = []
        for x in comp["matches"]:
            if x["date"] >= meta["date"] or name not in (x["home"]["name"], x["away"]["name"]):
                continue
            pens = (
                f" ({x['home']['penalties']}-{x['away']['penalties']} tab)"
                if x["home"].get("penalties") is not None
                else ""
            )
            rows.append(
                f"{x['stage']}: {x['home']['name']} {x['home']['score']}-"
                f"{x['away']['score']} {x['away']['name']}{pens}"
            )
        out[name] = rows
    return out


# --- Vérification des textes ----------------------------------------------------------------------

# constantes du jeu et de la méthode : durées, distances de référence, nom des données
CONSTANTS = {"15", "20", "35", "45", "60", "90", "105", "120", "360"}
NUM = re.compile(r"(?<![\w.,])[−-]?\d+(?:[.,]\d+)?")


def _flatten(x: Any) -> list[Any]:
    if isinstance(x, dict):
        return [v for k, val in x.items() for v in _flatten(k) + _flatten(val)]
    if isinstance(x, list):
        return [v for item in x for v in _flatten(item)]
    return [x]


def allowed_numbers(f: dict[str, Any]) -> set[str]:
    """Les nombres qu'un texte peut citer, écrits comme dans la fiche (et leurs entiers)."""
    out: set[str] = set()
    for v in _flatten(f):
        if isinstance(v, bool) or v is None:
            continue
        if isinstance(v, int | float):
            fv = float(v)
            for d in (0, 1, 2):
                out.add(f"{abs(fv):.{d}f}")
        elif isinstance(v, str):
            for n in NUM.findall(v):
                out.add(n.lstrip("−-").replace(",", "."))
    return out


def check(note: dict[str, Any], f: dict[str, Any]) -> list[str]:
    """Les nombres d'un texte absents de la fiche (petits entiers de 0 à 11 tolérés)."""
    ok = allowed_numbers(f)
    bad: list[str] = []
    for sec, by_lang in note.items():
        for lang, n in by_lang.items():
            text = " ".join([n["lead"], n["impact"], *n["keys"]])
            for raw in NUM.findall(text):
                v = raw.lstrip("−-").replace(",", ".")
                if v in ok or v in CONSTANTS or (v.isdigit() and int(v) <= 11):
                    continue
                if "." in v and any(o.startswith(v) for o in ok):  # 0,4 pour 0,40
                    continue
                bad.append(f"{sec}/{lang}: {raw}")
    return bad

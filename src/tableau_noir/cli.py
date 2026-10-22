"""Ligne de commande : `tableau-noir xg` puis `tableau-noir export`."""

from __future__ import annotations

import argparse
import gc
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pandas as pd

from tableau_noir import export as ex
from tableau_noir import xg, xt
from tableau_noir.model import Match
from tableau_noir.sources import statsbomb as sb
from tableau_noir.sources import wyscout as wy

XG_PATH = Path("data/processed/xg_wyscout.json")
XT_PATH = Path("data/processed/xt_wyscout.json")
WEB_DATA = Path("web/data")
LEAGUES = ("England", "France", "Germany", "Italy", "Spain")

# (identifiant, compétition StatsBomb, saisons, libellé de groupe)
STATSBOMB = [
    ("wc-2022", 43, [106], "tournament"),
    ("euro-2024", 55, [282], "tournament"),
    ("euro-2020", 55, [43], "tournament"),
    ("wc-2018", 43, [3], "tournament"),
    ("ucl-finals", 16, [41, 21, 22, 23, 24, 25, 26, 27, 2, 1, 4], "archives"),
]
WYSCOUT = [("euro-2016", "European_Championship", "tournament")]


def train_xg(raw: Path = wy.RAW) -> xg.XGModel:
    shots: list[pd.DataFrame] = []
    for key in LEAGUES:
        events = json.loads((raw / "events" / f"events_{key}.json").read_text(encoding="utf-8"))
        rows = wy.event_rows(key, [e for e in events if e["eventName"] in ("Shot", "Free Kick")])
        df = pd.DataFrame(rows)
        shots.append(df[df["kind"] == "shot"])
        del events, rows
        gc.collect()
    model = xg.fit(pd.concat(shots, ignore_index=True))
    model.save(XG_PATH)
    return model


def train_xt(raw: Path = wy.RAW) -> xt.XTModel:
    names = ("Pass", "Shot", "Free Kick", "Others on the ball")
    parts: list[pd.DataFrame] = []
    for key in LEAGUES:
        events = json.loads((raw / "events" / f"events_{key}.json").read_text(encoding="utf-8"))
        rows = wy.event_rows(key, [e for e in events if e["eventName"] in names])
        df = pd.DataFrame(rows)
        parts.append(df[df["kind"].isin(("pass", "carry", "shot"))])
        del events, rows
        gc.collect()
    model = xt.fit(pd.concat(parts, ignore_index=True))
    model.save(XT_PATH)
    return model


def with_xg(m: Match, model: xg.XGModel) -> Match:
    shots = m.events["kind"] == "shot"
    if shots.any():
        m.events.loc[shots, "xg"] = model.predict(m.events[shots])
    return m


def _statsbomb_matches(cid: int, seasons: list[int]) -> Iterator[Match]:
    for sid in seasons:
        for meta in sb.matches(cid, sid):
            m = sb.load_match(meta)
            if m.has_360:
                m.frames = sb.load_frames(int(meta["match_id"]))
            yield m
            m.frames = None


def build(out: Path = WEB_DATA, only: set[str] | None = None) -> dict[str, Any]:
    model = xg.XGModel.load(XG_PATH)
    xt_model = xt.XTModel.load(XT_PATH)
    computed: list[dict[str, Any]] = []
    for gid, cid, seasons, kind in STATSBOMB:
        if only and gid not in only:
            continue
        first = sb.load_match(sb.matches(cid, seasons[0])[0])
        last = sb.load_match(sb.matches(cid, seasons[-1])[0])
        label = first.season if kind == "tournament" else f"{first.season[:4]}–{last.season[-4:]}"
        has_360 = any(
            m.get("match_status_360") == "available" for s in seasons for m in sb.matches(cid, s)
        )
        comp = {
            "id": gid,
            "name": first.competition,
            "season": label,
            "kind": kind,
            "source": "statsbomb",
            "has_360": has_360,
        }
        computed.append(ex.competition(comp, _statsbomb_matches(cid, seasons), xt_model))
        print(f"{gid} : {len(computed[-1]['matches'])} matchs", flush=True)
    for gid, key, kind in WYSCOUT:
        if only and gid not in only:
            continue
        name, season = wy.NAMES[key]
        comp = {
            "id": gid,
            "name": name,
            "season": season,
            "kind": kind,
            "source": "wyscout",
            "has_360": False,
        }
        ms = (with_xg(m, model) for m in wy.load_competition(key))
        computed.append(ex.competition(comp, ms, xt_model))
        print(f"{gid} : {len(computed[-1]['matches'])} matchs", flush=True)
    entries = ex.finish(computed, out)
    ex.write_json({"grid": [[round(v, 5) for v in col] for col in xt_model.grid]}, out / "xt.json")
    if only:
        old = json.loads((out / "catalogue.json").read_text(encoding="utf-8"))["competitions"]
        new = {e["id"]: e for e in entries}
        entries = [new.get(c["id"], c) for c in old]
    return ex.write_catalogue(entries, out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tableau-noir")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("xg", help="entraîne le modèle d'xG sur les tirs Wyscout")
    sub.add_parser("notes", help="réécrit le coin de l'analyste sans tout recalculer")
    sub.add_parser("xt", help="calcule la grille d'expected threat sur les championnats Wyscout")
    e = sub.add_parser("export", help="calcule les stats et écrit web/data/")
    e.add_argument("--only", nargs="*", help="ne recalculer que ces compétitions (ex. wc-2022)")
    args = parser.parse_args(argv)
    if args.command == "xg":
        m = train_xg()
        print(f"xG : {m.n_shots} tirs, coefficients {m.coef}, penalty {m.penalty}")
    elif args.command == "notes":
        print(f"{ex.rewrite_notes(WEB_DATA)} matchs commentés")
    elif args.command == "xt":
        t = train_xt()
        print(f"xT : {t.n_actions} actions, case la plus menaçante {max(map(max, t.grid)):.3f}")
    elif args.command == "export":
        data = build(only=set(args.only) if args.only else None)
        print(f"{sum(len(c['matches']) for c in data['competitions'])} matchs exportés")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

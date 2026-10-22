"""Ligne de commande : `tableau-noir xg` puis `tableau-noir export`."""

from __future__ import annotations

import argparse
import gc
import json
from pathlib import Path
from typing import Any

import pandas as pd

from tableau_noir import export as ex
from tableau_noir import xg
from tableau_noir.model import Match
from tableau_noir.sources import statsbomb as sb
from tableau_noir.sources import wyscout as wy

XG_PATH = Path("data/processed/xg_wyscout.json")
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


def with_xg(m: Match, model: xg.XGModel) -> Match:
    shots = m.events["kind"] == "shot"
    if shots.any():
        m.events.loc[shots, "xg"] = model.predict(m.events[shots])
    return m


def build(out: Path = WEB_DATA) -> dict[str, Any]:
    model = xg.XGModel.load(XG_PATH)
    groups: list[tuple[dict[str, Any], list[Match]]] = []
    for gid, cid, seasons, kind in STATSBOMB:
        ms: list[Match] = []
        name = season = ""
        for sid in seasons:
            for meta in sb.matches(cid, sid):
                m = sb.load_match(meta)
                name, season = m.competition, m.season
                ms.append(m)
        label = season if kind == "tournament" else f"{ms[0].season[:4]}–{ms[-1].season[-4:]}"
        groups.append(
            (
                {
                    "id": gid,
                    "name": name,
                    "season": label,
                    "kind": kind,
                    "source": "statsbomb",
                    "has_360": any(m.has_360 for m in ms),
                },
                ms,
            )
        )
        print(f"{gid} : {len(ms)} matchs")
    for gid, key, kind in WYSCOUT:
        ms = [with_xg(m, model) for m in wy.load_competition(key)]
        comp, season = wy.NAMES[key]
        groups.append(
            (
                {
                    "id": gid,
                    "name": comp,
                    "season": season,
                    "kind": kind,
                    "source": "wyscout",
                    "has_360": False,
                },
                ms,
            )
        )
        print(f"{gid} : {len(ms)} matchs")
    return ex.export(groups, out)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tableau-noir")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("xg", help="entraîne le modèle d'xG sur les tirs Wyscout")
    sub.add_parser("export", help="calcule les stats et écrit web/data/")
    args = parser.parse_args(argv)
    if args.command == "xg":
        m = train_xg()
        print(f"xG : {m.n_shots} tirs, coefficients {m.coef}, penalty {m.penalty}")
    elif args.command == "export":
        data = build()
        print(f"{sum(len(c['matches']) for c in data['competitions'])} matchs exportés")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

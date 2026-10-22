"""Vérifie web/data (généré par `tableau-noir export`) contre des faits connus."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "web" / "data"
pytestmark = pytest.mark.integration


def load(mid: str) -> dict[str, Any]:
    return json.loads((DATA / "matches" / f"{mid}.json").read_text(encoding="utf-8"))


def test_catalogue() -> None:
    cat = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    sizes = {c["id"]: len(c["matches"]) for c in cat["competitions"]}
    assert sizes == {
        "wc-2022": 64,
        "euro-2024": 51,
        "euro-2020": 51,
        "wc-2018": 64,
        "ucl-finals": 11,
        "euro-2016": 51,
    }


def test_les_buts_collent_au_score() -> None:
    for f in (DATA / "matches").glob("*.json"):
        d = json.loads(f.read_text(encoding="utf-8"))
        for side in ("home", "away"):
            assert sum(g["side"] == side for g in d["goals"]) == d["meta"][side]["score"], f.name


def test_finale_2022() -> None:
    d = load("sb-3869685")
    m, s = d["meta"], d["stats"]
    assert (m["home"]["name"], m["away"]["name"]) == ("Argentina", "France")
    assert (m["home"]["penalties"], m["away"]["penalties"]) == (4, 2)
    assert (s["home"]["shots"], s["away"]["shots"]) == (20, 10)  # chiffres officiels de la FIFA
    assert (s["home"]["on_target"], s["away"]["on_target"]) == (10, 5)
    mbappe = next(p for p in d["players"] if p["name"] == "Kylian Mbappé")
    assert mbappe["goals"] == 3


def test_finale_2016_wyscout_et_xg_maison() -> None:
    cat = json.loads((DATA / "catalogue.json").read_text(encoding="utf-8"))
    final = next(
        m
        for c in cat["competitions"]
        if c["id"] == "euro-2016"
        for m in c["matches"]
        if m["stage"] == "Final"
    )
    d = load(final["id"])
    assert {d["meta"]["home"]["name"], d["meta"]["away"]["name"]} == {"Portugal", "France"}
    assert d["meta"]["xg_model"] == "tableau-noir"
    assert all(0 < s["xg"] < 1 for s in d["shots"])


def test_pas_de_donnees_brutes_publiees() -> None:
    d = load("sb-3869685")
    assert set(d) == {"meta", "stats", "shots", "goals", "players"}

from __future__ import annotations

import pandas as pd

from tableau_noir.enquetes import pressing


def corpus() -> pd.DataFrame:
    rows = []
    # 8 matchs : l'équipe A presse toujours plus (PPDA plus bas) ; elle gagne 5, nul 1, perd 2
    results = ["W", "W", "W", "W", "W", "D", "L", "L"]
    for i, r in enumerate(results):
        opp = {"W": "L", "L": "W", "D": "D"}[r]
        for team, res, ppda, poss, xg, xga in (
            (f"A{i}", r, 8.0 + i, 0.6, 1.5, 0.8),
            (f"B{i}", opp, 20.0 + i, 0.4, 0.8, 1.5),
        ):
            g = 2 if res == "W" else 1 if res == "D" else 0
            rows.append(
                {
                    "match_id": f"m{i}",
                    "comp": "wc-2022",
                    "stage": "Final" if i % 2 else "Group A",
                    "knockout": bool(i % 2),
                    "team": team,
                    "result": res,
                    "goals": g,
                    "goals_against": 2 - g if res != "D" else 1,
                    "xg": xg,
                    "xg_against": xga,
                    "possession": poss,
                    "ppda": ppda,
                    "press_per_min": 10 - ppda / 4,
                    "counterpress": 0.3 - ppda / 100,
                    "high_recoveries": 20 - ppda / 2,
                    "tr_xg_against": 0.2,
                    "source": "statsbomb",
                }
            )
    df = pd.DataFrame(rows)
    # un « champion » nommé comme dans compute
    df.loc[df["team"] == "A1", "team"] = "Argentina"
    for name in ("Spain", "Italy", "France"):
        df.loc[len(df)] = df.iloc[0].to_dict() | {"team": name, "match_id": f"x{name}"}
        df.loc[len(df)] = df.iloc[1].to_dict() | {"team": f"Z{name}", "match_id": f"x{name}"}
    df.loc[df["team"].isin(["Spain", "Italy", "France"]) & (df["comp"] == "wc-2022"), "comp"] = [
        "euro-2024",
        "euro-2020",
        "wc-2018",
    ]
    df.loc[df["team"].str.startswith("Z"), "comp"] = ["euro-2024", "euro-2020", "wc-2018"]
    return df


def test_resultat_du_presseur() -> None:
    out = pressing.compute(corpus())
    o = out["outcomes"]["ppda"]
    assert (o["n"], o["win"], o["draw"], o["loss"]) == (11, 8, 1, 2)
    assert out["outcomes"]["possession"]["win"] == o["win"]  # A a aussi plus le ballon
    assert out["outcomes_knockout"]["ppda"]["n"] == 4


def test_quarts_et_effet() -> None:
    out = pressing.compute(corpus())
    q = out["ppda_quartiles"]
    assert len(q) == 4 and q[0]["value"] < q[3]["value"]
    assert q[0]["xg"] > q[3]["xg"]
    assert out["xg_gap_q1_q4"] == round(q[0]["xg"] - q[3]["xg"], 2)
    assert out["corr_ppda_possession"] < 0
    assert {c["team"] for c in out["champions"]} == {"Argentina", "Spain", "Italy", "France"}

import assert from "node:assert/strict";
import { test } from "node:test";

import { byStage, chalkPath, orient, rng, scoreLine, share, sortPlayers, standouts, winner, xgRace } from "../js/logic.js";

test("le hasard de la craie est reproductible", () => {
  const a = rng(4); const b = rng(4);
  assert.equal(a(), b());
  assert.equal(chalkPath([[0, 0], [100, 0]], { seed: 2 }), chalkPath([[0, 0], [100, 0]], { seed: 2 }));
  assert.match(chalkPath([[0, 0], [100, 0]]), /^M0\.0 0\.0.*L100\.0 0\.0$/);
});

test("orientation : l'équipe à l'extérieur attaque vers la gauche", () => {
  assert.deepEqual(orient(100, 30, "home"), [100, 30]);
  assert.deepEqual(orient(100, 30, "away"), [5, 38]);
});

test("course aux xG", () => {
  const { steps, total } = xgRace([{ t: 10, xg: 0.5, side: "home" }, { t: 20, xg: 0.25, side: "away" }, { t: 30, xg: 0.1, side: "home" }], 90);
  assert.equal(total.home, 0.6);
  assert.equal(total.away, 0.25);
  assert.deepEqual(steps.home.at(-1), [90, 0.6]);
});

test("score, vainqueur, tirs au but", () => {
  const m = { home: { score: 3, penalties: 4 }, away: { score: 3, penalties: 2 } };
  assert.equal(winner(m), "home");
  assert.equal(scoreLine(m), "3 – 3 (4 – 2 tab)");
  assert.equal(winner({ home: { score: 1 }, away: { score: 1 } }), null);
  assert.equal(share(0, 0), 0.5);
});

test("phases dans l'ordre inverse du tournoi", () => {
  const g = byStage([{ stage: "Group A" }, { stage: "Final" }, { stage: "Round of 16" }]);
  assert.deepEqual(g.map(([k]) => k), ["Final", "Round of 16", "Group Stage"]);
});

test("tri des joueurs", () => {
  const rows = [{ name: "B", minutes: 10 }, { name: "A", minutes: 90 }, { name: "C", minutes: null }];
  assert.deepEqual(sortPlayers(rows, "minutes", -1).map((r) => r.name), ["A", "B", "C"]);
  assert.deepEqual(sortPlayers(rows, "minutes", 1).map((r) => r.name), ["B", "A", "C"]);
  assert.deepEqual(sortPlayers(rows, "name", 1).map((r) => r.name), ["A", "B", "C"]);
});

test("les hommes forts", () => {
  const p = (name, goals, xg) => ({ name, goals, assists: 0, xg, key_passes: 0, progressive: 0, def_actions: 0 });
  assert.equal(standouts([p("a", 0, 0.1), p("b", 2, 1.2), p("c", 1, 0.3)], 1)[0].name, "b");
});

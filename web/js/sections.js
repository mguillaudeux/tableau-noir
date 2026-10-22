// Sections 2 à 5 : structure et couloirs, pressing, relationnisme, replis.

import { HAND, HEX, compareRows, el, hatchRect, pitchSvg } from "./draw.js";
import { chalkCircle, chalkPath, relationIndex, scale, seedOf } from "./logic.js";

const $ = (s, root = document) => root.querySelector(s);
const SIDES = ["home", "away"];

/** Point d'entrée : `ctx` apporte l'état, la traduction et les formats de app.js. */
export function renderTeamSection(body, section, ctx) {
  const d = ctx.state.match;
  const head = (key) => `<div class="section-head"><h2>${ctx.esc(ctx.t(`${key}_title`))}</h2><span class="note">${ctx.esc(ctx.t(`${key}_note`))}</span></div>`;
  const no360 = !d.meta.has_360 ? `<p class="caveat">${ctx.esc(ctx.t("no_360"))}</p>` : "";
  ctx.side ??= "home";
  const R = { s2: structure, s3: pressing, s4: relation, s5: recovery }[section];
  body.innerHTML = `<section>${head(section)}${no360}<div id="sec"></div>
    <div class="method"><h3>${ctx.esc(ctx.t("method_title"))}</h3><p>${ctx.esc(ctx.t(`${section}_method`))}</p></div></section>`;
  R($("#sec", body), d, ctx);
}

/** Moyenne et étendue de la compétition, à fusionner dans une ligne de comparaison. */
const ref = (ctx, group, key) => {
  const s = ctx.state.context?.stats?.[group]?.[key];
  return s ? { mean: s.mean, lo: s.min, hi: s.max } : { mean: null };
};
const teamName = (d, side, ctx) => ctx.team(d.meta[side].name);

function sideTabs(host, d, ctx, redraw) {
  host.innerHTML = SIDES.map((s) => `<button type="button" role="tab" class="${s}" aria-selected="${ctx.side === s}" data-side="${s}">${ctx.esc(teamName(d, s, ctx))}</button>`).join("");
  host.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { ctx.side = b.dataset.side; redraw(); }));
}

// --- Section 2 · structure et couloirs ----------------------------------------------------------

function structure(root, d, ctx) {
  const { t, esc } = ctx;
  root.innerHTML = `
    <div class="tabs" role="tablist" id="t2"></div>
    <p class="formations" id="forms"></p>
    <div class="grid">
      <div class="panel"><p class="fig">${esc(t("fig_shape_with"))}</p><svg class="chart" id="shape-with"></svg></div>
      <div class="panel"><p class="fig">${esc(t("fig_shape_without"))}</p><svg class="chart" id="shape-without"></svg></div>
      <div class="panel"><p class="fig">${esc(t("fig_lanes"))}</p><svg class="chart" id="lanes"></svg><p class="legend">${esc(t("lanes_legend"))}</p></div>
      <div class="panel"><p class="fig">${esc(t("fig_block"))}</p><ul class="sheet" id="block"></ul></div>
    </div>`;
  const draw = () => {
    sideTabs($("#t2", root), d, ctx, draw);
    const a = d.team[ctx.side];
    const sh = a.shape;
    $("#forms", root).innerHTML = `${esc(t("announced"))} <b>${esc(a.announced ?? "–")}</b> · ${esc(t("with_ball"))} <b>${esc(sh.formation_with ?? "–")}</b> · ${esc(t("without_ball"))} <b>${esc(sh.formation_without ?? "–")}</b>`;
    drawShape($("#shape-with", root), sh.with_ball, sh.formation_with, ctx.side, d.meta.id + "w");
    drawShape($("#shape-without", root), sh.without_ball, sh.formation_without, ctx.side, d.meta.id + "o");
    drawLanes($("#lanes", root), sh.lanes, ctx.side, ctx);
  };
  draw();
  const rows = [];
  const fmtm = (v) => `${ctx.num(v, 1)} m`;
  const b = (s, phase) => d.team[s].shape.block?.[phase];
  const add = (label, phase, key, fmt, help) => rows.push({
    label: t(label), help: help ? t(help) : null, fmt,
    home: b("home", phase)?.[key] ?? null, away: b("away", phase)?.[key] ?? null,
    ...ref(ctx, phase === "with_ball" ? "block_with" : "block_without", key),
  });
  add("b_width_with", "with_ball", "width", fmtm);
  add("b_height_with", "with_ball", "height", fmtm, "b_height_h");
  add("b_lanes", "with_ball", "lanes", (v) => ctx.num(v, 1), "b_lanes_h");
  add("b_width_without", "without_ball", "width", fmtm);
  add("b_depth_without", "without_ball", "depth", fmtm, "b_depth_h");
  add("b_line_without", "without_ball", "last_line", fmtm, "b_line_h");
  if (rows.some((r) => r.home != null)) compareRows($("#block", root), rows, esc);
  else $("#block", root).innerHTML = `<li class="group"><span>${esc(t("needs_360"))}</span></li>`;
}

/** Positions moyennes, reliées ligne par ligne selon la formation déduite. */
function drawShape(svg, players, form, side, seed) {
  const P = pitchSvg(svg, { seed: seedOf(seed) });
  if (!players?.length) return;
  const color = HEX[side];
  const outfield = players.filter((p) => p.position !== "GK").sort((a, b) => a.x - b.x);
  if (form) {
    let i = 0;
    for (const size of form.split("-").map(Number)) {
      const line = outfield.slice(i, i + size).sort((a, b) => a.y - b.y);
      i += size;
      if (line.length > 1) svg.append(el("path", { class: "chalk", d: chalkPath(line.map((p) => P(p.x, p.y)), { amp: 1.5, seed: seedOf(`${seed}${i}`) }), stroke: color, "stroke-width": 1.6, fill: "none", opacity: 0.45, "stroke-dasharray": "6 5" }));
    }
  }
  for (const p of players) {
    const [cx, cy] = P(p.x, p.y);
    svg.append(el("path", { class: "chalk", d: chalkCircle(cx, cy, 15, { seed: seedOf(p.id) }), stroke: color, "stroke-width": 2.6, fill: "#1c2421", "fill-opacity": 0.85 }));
    if (p.number != null) svg.append(el("text", { x: cx, y: cy + 5, "text-anchor": "middle", "font-size": 14, fill: color, "font-family": "DM Mono, monospace" }, String(p.number)));
    svg.append(el("text", { x: cx, y: cy + 33, "text-anchor": "middle", "font-size": 15, fill: "#ece7dc", "font-family": HAND, class: "chalk" }, p.name.split(" ").slice(-1)[0]));
  }
  svg.append(el("text", { x: P(103, 2)[0], y: P(103, 2)[1] + 14, "text-anchor": "end", "font-size": 13, fill: HEX.gris, "font-family": "DM Mono, monospace" }, "→"));
}

/** Touches de balle par couloir et par tiers : un nuage de points de craie, dense où l'on joue. */
function drawLanes(svg, grid, side, ctx) {
  const P = pitchSvg(svg, { seed: 11 });
  const lanes = [0, 13.84, 24.84, 43.16, 54.16, 68];
  const thirds = [0, 35, 70, 105];
  const g = el("g", { class: "chalk" });
  for (const y of lanes.slice(1, -1)) g.append(el("path", { d: chalkPath([P(0, y), P(105, y)], { seed: y }), stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "3 6", fill: "none", opacity: 0.6 }));
  for (const x of thirds.slice(1, -1)) g.append(el("path", { d: chalkPath([P(x, 0), P(x, 68)], { seed: x }), stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "3 6", fill: "none", opacity: 0.6 }));
  svg.append(g);
  const max = Math.max(...grid.flat(), 0.01);
  let seed = 7;
  for (let th = 0; th < 3; th++) {
    for (let ln = 0; ln < 5; ln++) {
      const v = grid[th][ln];
      const [x0, y0] = P(thirds[th], lanes[ln]);
      const [x1, y1] = P(thirds[th + 1], lanes[ln + 1]);
      const n = Math.round((v / max) * 140);
      const dots = el("g", { class: "chalk" });
      for (let i = 0; i < n; i++) {
        seed = (seed * 1664525 + 1013904223) >>> 0;
        const rx = (seed / 2 ** 32);
        seed = (seed * 1664525 + 1013904223) >>> 0;
        const ry = (seed / 2 ** 32);
        dots.append(el("circle", { cx: x0 + 6 + rx * (x1 - x0 - 12), cy: y0 + 4 + ry * (y1 - y0 - 8), r: 1.8, fill: HEX[side], opacity: 0.8 }));
      }
      svg.append(dots);
      svg.append(el("text", { x: (x0 + x1) / 2, y: (y0 + y1) / 2 + 6, "text-anchor": "middle", "font-size": 17, fill: "#ece7dc", "font-family": "DM Mono, monospace", "paint-order": "stroke", stroke: "#1c2421", "stroke-width": 4 }, ctx.pct(v)));
    }
  }
}

// --- Section 3 · pressing ---------------------------------------------------------------------

function pressing(root, d, ctx) {
  const { t, esc } = ctx;
  root.innerHTML = `
    <div class="tabs" role="tablist" id="t3"></div>
    <div class="grid">
      <div class="panel"><p class="fig" id="press-title"></p><svg class="chart" id="press-map"></svg><p class="legend" id="press-legend"></p></div>
      <div class="panel"><p class="fig">${esc(t("fig_regain"))}</p><svg class="chart" id="regain"></svg></div>
      <div class="panel full"><p class="fig">${esc(t("fig_press_sheet"))}</p><ul class="sheet" id="press-sheet"></ul></div>
    </div>`;
  const draw = () => {
    sideTabs($("#t3", root), d, ctx, draw);
    const pr = d.team[ctx.side].pressing;
    $("#press-title", root).textContent = t(pr.source === "pressures" ? "fig_press_map" : "fig_def_map");
    const P = pitchSvg($("#press-map", root), { seed: 23 });
    const dots = el("g", { class: "chalk" });
    for (const [x, y] of pr.points) {
      const [cx, cy] = P(x, y);
      dots.append(el("circle", { cx, cy, r: 3.2, fill: HEX[ctx.side], opacity: 0.75 }));
    }
    $("#press-map", root).append(dots);
    const thirds = [0, 0, 0];
    for (const [x] of pr.points) thirds[Math.min(2, Math.floor(x / 35))]++;
    const tot = pr.points.length || 1;
    $("#press-legend", root).textContent = t("press_thirds", { a: ctx.pct(thirds[0] / tot), b: ctx.pct(thirds[1] / tot), c: ctx.pct(thirds[2] / tot) });
  };
  draw();
  drawRegain($("#regain", root), d, ctx);
  const rows = [
    ["p_ppda", (s) => d.stats[s].ppda, (v) => ctx.num(v, 1), "p_ppda_h", null],
    [d.team.home.pressing.source === "pressures" ? "p_per_min" : "p_per_min_def", (s) => d.team[s].pressing.per_minute_out, (v) => ctx.num(v, 1), "p_per_min_h", ["pressing", "per_minute_out"]],
    ["p_counter", (s) => d.team[s].pressing.counterpress_share, ctx.pct, "p_counter_h", ["pressing", "counterpress_share"]],
    ["p_height", (s) => d.team[s].pressing.height, (v) => `${ctx.num(v, 1)} m`, "p_height_h", ["pressing", "height"]],
    ["p_regain5", (s) => d.team[s].pressing.regain_5s, ctx.pct, "p_regain5_h", ["pressing", "regain_5s"]],
    ["p_regain10", (s) => d.team[s].pressing.regain_10s, ctx.pct, null, ["pressing", "regain_10s"]],
    ["p_high", (s) => d.team[s].pressing.high_recoveries, (v) => ctx.num(v), "p_high_h", ["pressing", "high_recoveries"]],
  ].map(([label, get, fmt, help, mean]) => ({ label: t(label), help: help ? t(help) : null, fmt, home: get("home"), away: get("away"), ...(mean ? ref(ctx, ...mean) : { mean: null }) }));
  compareRows($("#press-sheet", root), rows, esc);
}

/** Temps de récupération après une perte : barres de craie par tranche, les deux équipes. */
function drawRegain(svg, d, ctx) {
  const W = 640; const H = 300; const m = { l: 40, r: 20, t: 30, b: 50 };
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.replaceChildren();
  const labels = ["< 5 s", "5–10 s", "10–20 s", ctx.t("regain_late")];
  const share = (s) => { const h = d.team[s].pressing.regain_hist; const n = h.reduce((a, b) => a + b, 0) || 1; return h.map((v) => v / n); };
  const sh = { home: share("home"), away: share("away") };
  const max = Math.max(...sh.home, ...sh.away, 0.01);
  const y = scale(0, max * 1.15, H - m.b, m.t);
  const bw = (W - m.l - m.r) / 4;
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[m.l, H - m.b], [W - m.r, H - m.b]], { seed: 2 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none", opacity: 0.7 }));
  labels.forEach((lab, i) => {
    const cx = m.l + bw * (i + 0.5);
    SIDES.forEach((s, j) => {
      const x = cx + (j ? 6 : -6 - bw * 0.3);
      const top = y(sh[s][i]);
      g.append(el("rect", { x, y: top, width: bw * 0.3, height: H - m.b - top, fill: `url(#hachures)`, color: HEX[s], stroke: HEX[s], "stroke-width": 2 }));
      g.append(el("text", { x: x + bw * 0.15, y: top - 8, "text-anchor": "middle", "font-size": 14, fill: HEX[s], "font-family": "DM Mono, monospace" }, ctx.pct(sh[s][i])));
    });
    g.append(el("text", { x: cx, y: H - m.b + 24, "text-anchor": "middle", "font-size": 14, fill: HEX.gris, "font-family": "DM Mono, monospace" }, lab));
  });
  svg.append(g);
}

// --- Section 4 · relationnisme -------------------------------------------------------------------

function relation(root, d, ctx) {
  const { t, esc } = ctx;
  root.innerHTML = `
    <div class="grid">
      <div class="panel full"><p class="fig">${esc(t("fig_axis"))}</p><svg class="chart" id="axis"></svg></div>
      <div class="panel"><p class="fig">${esc(t("fig_network"))} · ${esc(teamName(d, "home", ctx))}</p><svg class="chart" id="net-home"></svg></div>
      <div class="panel"><p class="fig">${esc(t("fig_network"))} · ${esc(teamName(d, "away", ctx))}</p><svg class="chart" id="net-away"></svg></div>
      <div class="panel full"><p class="fig">${esc(t("fig_ingredients"))}</p><ul class="sheet" id="ingr"></ul></div>
    </div>`;
  drawAxis($("#axis", root), d, ctx);
  for (const s of SIDES) drawNetwork($(`#net-${s}`, root), d, s);
  const rows = [
    ["r_short", "short_share", ctx.pct, "r_short_h"],
    ["r_quick", "quick_share", ctx.pct, "r_quick_h"],
    ["r_roaming", "roaming", (v) => `${ctx.num(v, 1)} m`, "r_roaming_h"],
    ["r_proximity", "proximity", (v) => ctx.num(v, 2), "r_proximity_h"],
    ["r_lanes", "lanes", (v) => ctx.num(v, 2), "r_lanes_h"],
  ].map(([label, key, fmt, help]) => ({ label: t(label), help: t(help), fmt, home: d.team.home.relation[key], away: d.team.away.relation[key], ...ref(ctx, "relation", key) }));
  compareRows($("#ingr", root), rows, esc);
}

function drawAxis(svg, d, ctx) {
  const W = 1000; const H = 220; const m = { l: 60, r: 60 };
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.replaceChildren();
  const stats = ctx.state.context?.stats?.relation ?? {};
  const teams = ctx.state.context?.teams ?? [];
  const mine = Object.fromEntries(SIDES.map((s) => [s, relationIndex(d.team[s].relation, stats)]));
  const all = [...teams.map((p) => p.index), ...Object.values(mine).filter((v) => v != null)];
  const lim = Math.max(1, ...all.map(Math.abs)) * 1.1;
  const x = scale(-lim, lim, m.l, W - m.r);
  const y0 = 120;
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[m.l, y0], [W - m.r, y0]], { amp: 1, seed: 4 }), stroke: HEX.craie, "stroke-width": 2.4, fill: "none" }));
  g.append(el("path", { d: chalkPath([[x(0), y0 - 10], [x(0), y0 + 10]], { seed: 5 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none" }));
  g.append(el("text", { x: m.l, y: y0 + 54, "font-size": 24, fill: "#ece7dc", "font-family": HAND }, `← ${ctx.t("positionist")}`));
  g.append(el("text", { x: W - m.r, y: y0 + 54, "text-anchor": "end", "font-size": 24, fill: "#ece7dc", "font-family": HAND }, `${ctx.t("relationist")} →`));
  svg.append(g);
  for (const p of teams) {
    const c = el("circle", { cx: x(p.index), cy: y0, r: 5, fill: HEX.gris, opacity: 0.55 });
    c.append(el("title", {}, `${ctx.team(p.name)} · ${ctx.num(p.index, 2)}`));
    svg.append(c);
  }
  let lastX = -999;
  SIDES.forEach((s, i) => {
    const v = mine[s];
    if (v == null) return;
    const cx = x(v);
    const up = Math.abs(cx - lastX) < 120 ? 2 : 1;
    lastX = cx;
    svg.append(el("path", { class: "chalk", d: chalkCircle(cx, y0, 12, { seed: i + 3 }), stroke: HEX[s], "stroke-width": 3, fill: HEX[s], "fill-opacity": 0.5 }));
    svg.append(el("path", { class: "chalk", d: chalkPath([[cx, y0 - 14], [cx, y0 - 30 * up]], { seed: i }), stroke: HEX[s], "stroke-width": 1.6, fill: "none" }));
    svg.append(el("text", { x: cx, y: y0 - 36 * up, "text-anchor": "middle", "font-size": 22, fill: HEX[s], "font-family": HAND, class: "chalk" }, `${teamName(d, s, ctx)} ${ctx.num(v, 2)}`));
  });
}

/** Réseau de passes : positions moyennes avec ballon, liens d'autant plus épais qu'ils servent. */
function drawNetwork(svg, d, side) {
  const a = d.team[side];
  const P = pitchSvg(svg, { seed: seedOf(side + d.meta.id) });
  const pos = Object.fromEntries(a.shape.with_ball.map((p) => [p.id, p]));
  const max = Math.max(1, ...a.network.map((l) => l[2]));
  const g = el("g", { class: "chalk" });
  for (const [i, j, n] of a.network) {
    const p = pos[i]; const q = pos[j];
    if (!p || !q) continue;
    g.append(el("path", { d: chalkPath([P(p.x, p.y), P(q.x, q.y)], { amp: 0.8, seed: n + i.length }), stroke: HEX.craie, "stroke-width": 1 + 9 * (n / max), opacity: 0.25 + 0.55 * (n / max), fill: "none", "stroke-linecap": "round" }));
  }
  svg.append(g);
  const nmax = Math.max(1, ...a.shape.with_ball.map((p) => p.n));
  for (const p of a.shape.with_ball) {
    const [cx, cy] = P(p.x, p.y);
    const r = 8 + 12 * Math.sqrt(p.n / nmax);
    svg.append(el("path", { class: "chalk", d: chalkCircle(cx, cy, r, { seed: seedOf(p.id) }), stroke: HEX[side], "stroke-width": 2.6, fill: "#1c2421", "fill-opacity": 0.9 }));
    if (p.number != null) svg.append(el("text", { x: cx, y: cy + 5, "text-anchor": "middle", "font-size": 13, fill: HEX[side], "font-family": "DM Mono, monospace" }, String(p.number)));
  }
}

// --- Section 5 · replis ----------------------------------------------------------------------------

function recovery(root, d, ctx) {
  const { t, esc } = ctx;
  root.innerHTML = `
    <div class="tabs" role="tablist" id="t5"></div>
    <p class="formations" id="ex-title"></p>
    <div class="grid">
      <div class="panel"><p class="fig" id="ex-before-title"></p><svg class="chart" id="ex-before"></svg></div>
      <div class="panel"><p class="fig" id="ex-after-title"></p><svg class="chart" id="ex-after"></svg></div>
      <div class="panel full"><p class="fig">${esc(t("fig_recovery_sheet"))}</p><ul class="sheet" id="rec-sheet"></ul></div>
    </div>`;
  const draw = () => {
    sideTabs($("#t5", root), d, ctx, draw);
    const r = d.team[ctx.side].recovery;
    const ex = r.example;
    for (const id of ["#ex-before", "#ex-after"]) $(id, root).parentElement.hidden = !ex;
    if (!ex) {
      $("#ex-title", root).textContent = t("needs_360");
      $("#ex-before", root).replaceChildren(); $("#ex-after", root).replaceChildren();
      $("#ex-before-title", root).textContent = ""; $("#ex-after-title", root).textContent = "";
      return;
    }
    $("#ex-title", root).innerHTML = esc(t("ex_title", { n0: ex.behind, n1: ex.behind_after, min: ex.before.minute + 1 }));
    $("#ex-before-title", root).textContent = t("ex_before", { who: ex.before.carrier ?? "?" });
    $("#ex-after-title", root).textContent = t("ex_after", { s: ctx.num(ex.after.t - ex.before.t, 0) });
    drawSnap($("#ex-before", root), ex.before, ctx.side);
    drawSnap($("#ex-after", root), ex.after, ctx.side);
  };
  draw();
  const rows = [
    ["rr_behind", "behind_ball", (v) => ctx.num(v, 1), "rr_behind_h"],
    ["rr_behind8", "behind_8s", (v) => ctx.num(v, 1), "rr_behind8_h"],
    ["rr_gain", "gain", (v) => (v > 0 ? "+" : "") + ctx.num(v, 1), "rr_gain_h"],
    ["rr_seven", "back_7plus", ctx.pct, "rr_seven_h"],
    ["rr_shots", "shots_against", (v) => ctx.num(v), "rr_shots_h"],
    ["rr_xg", "xg_against", (v) => ctx.num(v, 2), null],
  ].map(([label, key, fmt, help]) => ({ label: t(label), help: help ? t(help) : null, fmt, home: d.team.home.recovery[key], away: d.team.away.recovery[key], ...ref(ctx, "recovery", key) }));
  compareRows($("#rec-sheet", root), rows, esc);
}

/** Une image 360 : nos joueurs (couleur de l'équipe), les adversaires (craie), le ballon. */
function drawSnap(svg, snap, side) {
  const P = pitchSvg(svg, { seed: 31 });
  hatchRect(svg, P, 0, 0, 35, 68, HEX.craie, 0.16);
  svg.append(el("text", { x: P(34, 66)[0], y: P(34, 66)[1], "text-anchor": "end", "font-size": 18, fill: "#ece7dc", "font-family": HAND, opacity: 0.8 }, "35 m"));
  const other = side === "home" ? "away" : "home";
  for (const [x, y] of snap.them) {
    const [cx, cy] = P(x, y);
    svg.append(el("path", { class: "chalk", d: chalkPath([[cx - 7, cy - 7], [cx + 7, cy + 7]], { seed: x }) + chalkPath([[cx + 7, cy - 7], [cx - 7, cy + 7]], { seed: y }), stroke: HEX[other], "stroke-width": 2.6, fill: "none" }));
  }
  for (const [x, y] of snap.us) {
    const [cx, cy] = P(x, y);
    svg.append(el("path", { class: "chalk", d: chalkCircle(cx, cy, 9, { seed: seedOf(`${x}${y}`) }), stroke: HEX[side], "stroke-width": 3, fill: HEX[side], "fill-opacity": 0.35 }));
  }
  const [bx, by] = P(...snap.ball);
  svg.append(el("path", { class: "chalk", d: chalkCircle(bx, by, 14, { seed: 5 }), stroke: HEX.corail, "stroke-width": 2.6, fill: "none" }));
  svg.append(el("circle", { cx: bx, cy: by, r: 4, fill: HEX.corail }));
}

// Sections 6 à 9 : gravité, valeur des actions (xT), classements par poste, jumeaux.

import { HAND, HEX, el, pitchSvg } from "./draw.js";
import { chalkCircle, chalkPath, scale, seedOf } from "./logic.js";
import { analystBlock } from "./analyst.js";

const $ = (s, root = document) => root.querySelector(s);
const SIDES = ["home", "away"];
const ROLES = ["GK", "CB", "FB", "MF", "FW"];
const ROLE_METRICS = {
  FW: ["npxg", "goals", "shots", "xt", "key_passes", "dribbles"],
  MF: ["xt", "progressive", "key_passes", "pass_rate", "def_actions", "duel_rate"],
  FB: ["xt", "progressive", "key_passes", "def_actions", "duel_rate", "dribbles"],
  CB: ["def_actions", "duel_rate", "progressive", "pass_rate", "xt"],
  GK: ["prevented", "save_pct", "saves", "pass_rate"],
};
const PROFILE = {
  outfield: ["npxg", "shots", "xt", "key_passes", "progressive", "dribbles", "def_actions", "touches", "pass_rate", "duel_rate"],
  GK: ["prevented", "save_pct", "saves", "pass_rate", "touches"],
};
const RATES = new Set(["pass_rate", "duel_rate", "save_pct"]);
const lastName = (n) => n.split(" ").slice(-1)[0];

export function renderPlayerSection(body, section, ctx) {
  const d = ctx.state.match;
  const { t, esc } = ctx;
  const head = `<div class="section-head"><h2>${esc(t(`${section}_title`))}</h2><span class="note">${esc(t(`${section}_note`))}</span></div>`;
  const caveat = section === "s6" && !d.meta.has_360 ? `<p class="caveat">${esc(t("no_360_gravity"))}</p>` : "";
  const noTable = (section === "s8" || section === "s9") && !ctx.state.players ? `<p class="caveat">${esc(t("no_table"))}</p>` : "";
  body.innerHTML = `<section>${head}${caveat}${noTable}<div id="sec"></div>
    ${analystBlock(d, section, ctx.state.lang, t, esc)}
    <div class="method"><h3>${esc(t("method_title"))}</h3><p>${esc(t(`${section}_method`))}</p></div></section>`;
  const root = $("#sec", body);
  ({ s6: gravity, s7: value, s8: rankings, s9: twins })[section](root, d, ctx);
}

const fmtMetric = (ctx, k, v) => (v == null ? "–" : RATES.has(k) ? ctx.pct(v) : ctx.num(v, k === "touches" || k === "def_actions" ? 1 : 2));

/** Lignes de barres signées (autour de zéro) : [{ label, sub, side, v, text }]. */
function signedRows(ul, rows, esc) {
  const lim = Math.max(0.01, ...rows.map((r) => Math.abs(r.v)));
  for (const r of rows) {
    const li = document.createElement("li");
    li.className = r.side ?? "";
    li.innerHTML = `<span class="who">${esc(r.label)}${r.sub ? `<small>${esc(r.sub)}</small>` : ""}</span><svg aria-hidden="true"></svg><span class="v">${esc(r.text)}</span>`;
    ul.append(li);
    const svg = li.querySelector("svg");
    svg.setAttribute("viewBox", "0 0 200 14");
    svg.setAttribute("preserveAspectRatio", "none");
    const g = el("g", { class: "chalk" });
    g.append(el("rect", { x: 0, y: 0, width: 200, height: 14, fill: "none" }));
    g.append(el("path", { d: "M100 0V14", stroke: HEX.gris, "stroke-width": 1.2, opacity: 0.7 }));
    const len = (Math.abs(r.v) / lim) * 96;
    if (len >= 1) {
      const x1 = r.v >= 0 ? 100 + len : 100 - len;
      g.append(el("path", { d: chalkPath([[100, 7], [x1, 7]], { amp: 0.6, step: 16, seed: seedOf(r.label) }), stroke: HEX[r.side] ?? HEX.craie, "stroke-width": 9, "stroke-linecap": "round", fill: "none", opacity: 0.9 }));
    }
    svg.append(g);
  }
}

// --- Section 6 · gravité ---------------------------------------------------------------------------

function gravity(root, d, ctx) {
  const { t, esc } = ctx;
  const key = d.meta.has_360 ? "gravity" : "attention";
  root.innerHTML = `
    <div class="grid">
      <div class="panel full"><p class="fig">${esc(t(key === "gravity" ? "fig_magnets" : "fig_magnets_ev"))}</p><svg class="chart" id="magnets"></svg>
        <p class="legend">${esc(t("magnets_legend"))}</p></div>
      <div class="panel"><p class="fig">${esc(t("fig_gravity_match"))}</p><ul class="srows" id="g-match"></ul></div>
      <div class="panel"><p class="fig">${esc(t("fig_gravity_comp"))}</p><ul class="srows" id="g-comp"></ul></div>
    </div>`;
  const ps = d.players.filter((p) => p[key] != null && p.x != null && p.role !== "GK");
  drawMagnets($("#magnets", root), ps, key);
  const fmt = (v) => (v > 0 ? "+" : "") + ctx.num(v, 2);
  const sorted = [...ps].sort((a, b) => b[key] - a[key]);
  const pick = sorted.length > 10 ? [...sorted.slice(0, 6), ...sorted.slice(-4)] : sorted;
  signedRows($("#g-match", root), pick.map((p) => ({ label: p.name, sub: ctx.team(d.meta[p.side].name), side: p.side, v: p[key], text: fmt(p[key]) })), esc);
  const table = ctx.state.players?.players ?? {};
  const here = new Map(d.players.map((p) => [p.id, p.side]));
  const comp = Object.values(table).filter((p) => p[key] != null && p.role !== "GK").sort((a, b) => b[key] - a[key]).slice(0, 10);
  if (comp.length) signedRows($("#g-comp", root), comp.map((p) => ({ label: p.name, sub: ctx.team(p.team), side: here.get(p.id) ?? null, v: p[key], text: fmt(p[key]) })), esc);
  else $("#g-comp", root).innerHTML = `<li><span class="who">${esc(t("no_table"))}</span></li>`;
}

/** Les aimants : chaque joueur à sa position médiane (les deux équipes sur le même terrain),
 * entouré d'autant de cercles de craie qu'il attire d'adversaires en plus. */
function drawMagnets(svg, ps, key) {
  const P = pitchSvg(svg, { k: 8, seed: 41 });
  const max = Math.max(0.01, ...ps.map((p) => p[key]));
  const boxes = [];
  const free = (b) => !boxes.some((o) => b.x0 < o.x1 && b.x1 > o.x0 && b.y0 < o.y1 && b.y1 > o.y0);
  const order = [...ps].sort((a, b) => b[key] - a[key]);
  for (const p of order) {
    const [x, y] = p.side === "home" ? [p.x, p.y] : [105 - p.x, 68 - p.y];
    const [cx, cy] = P(x, y);
    const v = p[key];
    const rings = v > 0 ? Math.max(1, Math.round((v / max) * 4)) : 0;
    for (let i = 1; i <= rings; i++) {
      svg.append(el("path", { class: "chalk", d: chalkCircle(cx, cy, 10 + i * 9, { seed: seedOf(p.id + i), amp: 0.06 }), stroke: HEX[p.side], "stroke-width": 1.6, fill: "none", opacity: 0.75 - i * 0.13 }));
    }
    svg.append(el("circle", { cx, cy, r: 6, fill: HEX[p.side], opacity: v > 0 ? 0.95 : 0.45 }));
    if (v <= 0) continue;
    // étiquette au-dessus des cercles, sinon en dessous, sinon on renonce (le classement la donne)
    const name = lastName(p.name);
    const w = name.length * 9 + 6;
    const r = 10 + rings * 9;
    for (const ty of [cy - r - 6, cy + r + 18]) {
      const b = { x0: cx - w / 2, x1: cx + w / 2, y0: ty - 16, y1: ty + 4 };
      if (!free(b)) continue;
      boxes.push(b);
      svg.append(el("text", { x: cx, y: ty, "text-anchor": "middle", "font-size": 19, fill: "#ece7dc", "font-family": HAND, class: "chalk" }, name));
      break;
    }
  }
}

// --- Section 7 · valeur des actions --------------------------------------------------------------

function value(root, d, ctx) {
  const { t, esc } = ctx;
  root.innerHTML = `
    <div class="tabs" role="tablist" id="t7"></div>
    <div class="grid">
      <div class="panel"><p class="fig">${esc(t("fig_xt_map"))}</p><svg class="chart" id="xt-map"></svg><p class="legend">${esc(t("xt_legend"))}</p></div>
      <div class="panel"><p class="fig">${esc(t("fig_xt_race"))}</p><svg class="chart" id="xt-race"></svg></div>
      <div class="panel full"><p class="fig">${esc(t("fig_creators"))}</p><div class="table-wrap"><table class="players" id="creators"></table></div></div>
    </div>`;
  ctx.side ??= "home";
  const draw = () => {
    const host = $("#t7", root);
    host.innerHTML = SIDES.map((s) => `<button type="button" role="tab" class="${s}" aria-selected="${ctx.side === s}" data-side="${s}">${esc(ctx.team(d.meta[s].name))}</button>`).join("");
    host.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { ctx.side = b.dataset.side; draw(); }));
    drawXtMap($("#xt-map", root), ctx.state.xt?.grid, d.value?.actions?.[ctx.side] ?? [], ctx.side, ctx);
  };
  draw();
  drawXtRace($("#xt-race", root), d, ctx);
  const rows = [...d.players].filter((p) => p.xt != null).sort((a, b) => b.xt - a.xt).slice(0, 10);
  const max = Math.max(0.01, ...rows.map((p) => p.xt));
  $("#creators", root).innerHTML = `<thead><tr><th>${esc(t("col_player"))}</th><th>${esc(t("col_min"))}</th><th>xT</th><th>${esc(t("col_xt_pass"))}</th><th>${esc(t("col_xt_carry"))}</th><th></th></tr></thead>
    <tbody>${rows.map((p) => `<tr class="${p.side}"><td class="name">${esc(p.name)}</td><td>${ctx.num(p.minutes)}</td><td><b>${ctx.num(p.xt, 2)}</b></td><td>${ctx.num(p.xt_pass ?? 0, 2)}</td><td>${ctx.num(p.xt_carry ?? 0, 2)}</td>
      <td class="barcell"><span style="width:${Math.max(0, (p.xt / max) * 100)}%"></span></td></tr>`).join("")}</tbody>`;
}

/** La grille d'xT (plus la case est claire, plus le ballon y est dangereux) et les gestes qui ont
 * le plus fait monter la menace. L'équipe attaque toujours vers la droite. */
function drawXtMap(svg, grid, actions, side, ctx) {
  const P = pitchSvg(svg, { seed: 51 });
  if (grid) {
    const nx = grid.length;
    const ny = grid[0].length;
    const max = Math.max(...grid.flat());
    const g = el("g", {});
    for (let i = 0; i < nx; i++) {
      for (let j = 0; j < ny; j++) {
        const [x0, y0] = P((i * 105) / nx, (j * 68) / ny);
        const [x1, y1] = P(((i + 1) * 105) / nx, ((j + 1) * 68) / ny);
        g.append(el("rect", { x: x0, y: y0, width: x1 - x0, height: y1 - y0, fill: HEX.craie, opacity: 0.03 + 0.4 * Math.sqrt(grid[i][j] / max) }));
      }
    }
    svg.insertBefore(g, svg.firstChild);
  }
  actions.forEach((a, i) => {
    if (a.ex == null) return;
    const p0 = P(a.x, a.y);
    const p1 = P(a.ex, a.ey);
    svg.append(el("path", { class: "chalk", d: chalkPath([p0, p1], { amp: 0.8, seed: i + 3 }), stroke: HEX[side], "stroke-width": 3, fill: "none", "stroke-dasharray": a.kind === "carry" ? "7 5" : null }));
    const ang = Math.atan2(p1[1] - p0[1], p1[0] - p0[0]);
    const head = [[p1[0] - 11 * Math.cos(ang - 0.45), p1[1] - 11 * Math.sin(ang - 0.45)], p1, [p1[0] - 11 * Math.cos(ang + 0.45), p1[1] - 11 * Math.sin(ang + 0.45)]];
    svg.append(el("path", { d: `M${head.map((q) => q.join(" ")).join("L")}`, stroke: HEX[side], "stroke-width": 3, fill: "none" }));
    svg.append(el("circle", { cx: p0[0], cy: p0[1], r: 9, fill: "#1c2421", stroke: HEX[side], "stroke-width": 1.6 }));
    svg.append(el("text", { x: p0[0], y: p0[1] + 4.5, "text-anchor": "middle", "font-size": 12, fill: HEX[side], "font-family": "DM Mono, monospace" }, String(i + 1)));
  });
  const list = svg.parentElement.querySelector("ol.actions") ?? svg.parentElement.insertBefore(document.createElement("ol"), svg.nextSibling);
  list.className = `actions ${side}`;
  list.innerHTML = actions.map((a) => `<li><b>${ctx.esc(a.name)}</b> ${a.minute}' · ${ctx.esc(ctx.t(a.kind === "carry" ? "kind_carry" : "kind_pass"))} · +${ctx.num(a.xt, 2)} xT</li>`).join("");
}

/** Course à la menace : xT cumulé minute par minute, buts en corail. */
function drawXtRace(svg, d, ctx) {
  const W = 640; const H = 300; const m = { l: 40, r: 84, t: 24, b: 40 };
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.replaceChildren();
  const mins = d.value?.xt_minutes;
  if (!mins) return;
  const cum = {};
  for (const s of SIDES) { let a = 0; cum[s] = mins[s].map((v) => (a += v)); }
  const n = mins.home.length;
  const ymax = Math.max(0.5, ...cum.home, ...cum.away) * 1.12;
  const x = scale(0, n, m.l, W - m.r);
  const y = scale(Math.min(0, ...cum.home, ...cum.away), ymax, H - m.b, m.t);
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[m.l, y(0)], [W - m.r, y(0)]], { seed: 3 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none", opacity: 0.7 }));
  for (const mark of [45, 90, 105].filter((v) => v < n)) {
    g.append(el("path", { d: chalkPath([[x(mark), m.t], [x(mark), H - m.b]], { seed: mark }), stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "4 5", fill: "none", opacity: 0.6 }));
    g.append(el("text", { x: x(mark), y: H - m.b + 20, "text-anchor": "middle", "font-size": 14, fill: HEX.gris }, `${mark}'`));
  }
  g.append(el("text", { x: m.l, y: H - 4, "font-size": 13, fill: HEX.gris }, ctx.t("race_axis")));
  const ends = {};
  for (const s of SIDES) {
    const pts = cum[s].map((v, i) => [x(i + 1), y(v)]);
    g.append(el("path", { d: chalkPath([[x(0), y(0)], ...pts], { amp: 0.5, step: 12, seed: seedOf(s) }), stroke: HEX[s], "stroke-width": 3.2, fill: "none", "stroke-linejoin": "round" }));
    ends[s] = pts[pts.length - 1];
  }
  const gap = ends.home[1] - ends.away[1];
  if (Math.abs(gap) < 20) { const sh = ((20 - Math.abs(gap)) / 2) * (gap < 0 ? 1 : -1); ends.home[1] -= sh; ends.away[1] += sh; }
  for (const s of SIDES) g.append(el("text", { x: ends[s][0] + 8, y: ends[s][1] + 5, "font-size": 16, fill: HEX[s] }, `${ctx.num(cum[s][n - 1], 2)} xT`));
  svg.append(g);
  for (const goal of d.goals) {
    const i = Math.min(n - 1, goal.minute);
    svg.append(el("path", { class: "chalk", d: chalkCircle(x(i + 1), y(cum[goal.side][i]), 7, { seed: goal.minute }), stroke: HEX.corail, "stroke-width": 2.4, fill: HEX.corail, "fill-opacity": 0.25 }));
  }
}

// --- Section 8 · classements -----------------------------------------------------------------------

function rankings(root, d, ctx) {
  const { t, esc } = ctx;
  const tab = ctx.state.players;
  if (!tab) return;
  const here = new Map(d.players.map((p) => [p.id, p.side]));
  const mine = d.players.map((p) => tab.players[p.id]).filter(Boolean);
  ctx.role ??= mine.sort((a, b) => a.rank / a.of - b.rank / b.of)[0]?.role ?? "FW";
  root.innerHTML = `<div class="tabs roles" role="tablist" id="t8"></div>
    <p class="formations">${esc(t("rank_intro", { n: ctx.num(tab.min_minutes) }))}</p>
    <div class="table-wrap"><table class="players rank" id="rank"></table></div>`;
  const draw = () => {
    $("#t8", root).innerHTML = ROLES.map((r) => `<button type="button" role="tab" aria-selected="${ctx.role === r}" data-role="${r}">${esc(t(`role_${r}`))}</button>`).join("");
    $("#t8", root).querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { ctx.role = b.dataset.role; draw(); }));
    const metrics = ROLE_METRICS[ctx.role];
    const ids = tab.rankings[ctx.role] ?? [];
    const extra = Object.values(tab.players).filter((p) => p.role === ctx.role && here.has(p.id) && !ids.includes(p.id)).sort((a, b) => a.rank - b.rank);
    const row = (p) => `<tr class="${here.get(p.id) ?? ""}"><td>${p.rank}</td><td class="name">${esc(p.name)}<small>${esc(ctx.team(p.team))} · ${ctx.num(p.minutes)} min</small></td>
      <td class="barcell score"><span style="width:${p.score * 100}%"></span><b>${ctx.num(p.score * 100)}</b></td>
      ${metrics.map((k) => `<td style="--p:${p.pct?.[k] ?? 0}">${fmtMetric(ctx, k, p.per90[k])}</td>`).join("")}</tr>`;
    $("#rank", root).innerHTML = `<thead><tr><th>#</th><th>${esc(t("col_player"))}</th><th>${esc(t("col_score"))}</th>${metrics.map((k) => `<th title="${esc(t(`mh_${k}`))}">${esc(t(`m_${k}`))}</th>`).join("")}</tr></thead>
      <tbody>${ids.map((id) => row(tab.players[id])).join("")}${extra.length ? `<tr class="gap"><td colspan="${3 + metrics.length}">…</td></tr>${extra.map(row).join("")}` : ""}</tbody>`;
  };
  draw();
}

// --- Section 9 · jumeaux -----------------------------------------------------------------------------

function twins(root, d, ctx) {
  const { t, esc } = ctx;
  const tab = ctx.state.players;
  if (!tab) return;
  const mine = d.players.map((p) => tab.players[p.id] && { ...tab.players[p.id], side: p.side }).filter((p) => p?.profile && p.twins?.length);
  if (!mine.length) { root.innerHTML = `<p class="formations">${esc(t("no_twins"))}</p>`; return; }
  mine.sort((a, b) => b.score - a.score);
  ctx.twinOf = mine.some((p) => p.id === ctx.twinOf) ? ctx.twinOf : mine[0].id;
  ctx.twinIdx ??= 0;
  root.innerHTML = `<div class="chips" id="who"></div>
    <div class="grid">
      <div class="panel"><p class="fig" id="prof-title"></p><ul class="srows twin" id="prof"></ul><p class="legend">${esc(t("profile_legend"))}</p></div>
      <div class="panel"><p class="fig">${esc(t("fig_twins"))}</p><ol class="twins" id="twins"></ol></div>
    </div>`;
  const draw = async () => {
    $("#who", root).innerHTML = mine.map((p) => `<button type="button" class="${p.side}" aria-pressed="${p.id === ctx.twinOf}" data-id="${p.id}">${esc(p.name)}</button>`).join("");
    $("#who", root).querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { ctx.twinOf = b.dataset.id; ctx.twinIdx = 0; draw(); }));
    const me = mine.find((p) => p.id === ctx.twinOf);
    $("#twins", root).innerHTML = me.twins.map((tw, i) => `<li><button type="button" aria-pressed="${i === ctx.twinIdx}" data-i="${i}"><b>${esc(tw.name)}</b><small>${esc(ctx.team(tw.team))} · ${esc(t(`comp_${tw.comp}`))}</small><span class="sim">${ctx.pct(Math.max(0, tw.sim))}</span></button></li>`).join("");
    $("#twins", root).querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { ctx.twinIdx = Number(b.dataset.i); draw(); }));
    const tw = me.twins[ctx.twinIdx];
    const other = tw.comp === tab.comp ? tab : await ctx.json(`data/players/${tw.comp}.json`).catch(() => null);
    const twin = other?.players?.[tw.id];
    $("#prof-title", root).textContent = t("fig_profile", { a: me.name, b: tw.name });
    const keys = PROFILE[me.role === "GK" ? "GK" : "outfield"];
    const ul = $("#prof", root);
    ul.replaceChildren();
    keys.forEach((k, i) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="who">${esc(t(`m_${k}`))}<small>${esc(fmtMetric(ctx, k, me.per90[k]))} · ${esc(fmtMetric(ctx, k, twin?.per90?.[k]))}</small></span><svg aria-hidden="true"></svg>`;
      ul.append(li);
      const svg = li.querySelector("svg");
      svg.setAttribute("viewBox", "0 0 200 22");
      svg.setAttribute("preserveAspectRatio", "none");
      const g = el("g", { class: "chalk" });
      g.append(el("rect", { x: 0, y: 0, width: 200, height: 22, fill: "none" }));
      g.append(el("path", { d: "M100 0V22", stroke: HEX.gris, "stroke-width": 1.2, opacity: 0.7 }));
      const z = (v) => 100 + Math.max(-2.5, Math.min(2.5, v)) * 38;
      g.append(el("path", { d: chalkPath([[100, 6], [z(me.profile[i]), 6]], { amp: 0.5, seed: i }), stroke: HEX[me.side], "stroke-width": 7, "stroke-linecap": "round", fill: "none" }));
      if (twin?.profile) g.append(el("path", { d: chalkPath([[100, 16], [z(twin.profile[i]), 16]], { amp: 0.5, seed: i + 9 }), stroke: HEX.craie, "stroke-width": 5, "stroke-linecap": "round", fill: "none", opacity: 0.8 }));
      svg.append(g);
    });
  };
  draw();
}

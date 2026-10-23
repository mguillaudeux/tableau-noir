// Tableau Noir : catalogue des matchs et page de match (section 1 : les stats classiques).

import { PITCH, byStage, chalkCircle, chalkPath, orient, scale, scoreLine, seedOf, share, sortPlayers, standouts, winner, xgRace } from "./logic.js";
import { compName, makeT, stageName, teamName } from "./i18n.js";
import { HEX, bar, drawPitch, el } from "./draw.js";
import { renderTeamSection as teamSection } from "./sections.js";
import { renderPlayerSection as playerSection } from "./players.js";
import { analystBlock } from "./analyst.js";
import { mountReplay } from "./replay.js";
import { mountRace } from "./anim.js";
import { showArchives, showDossier } from "./editorial.js";

const $ = (s, root = document) => root.querySelector(s);
const app = $("#app");
const tip = $("#tip");

const state = { lang: initialLang(), catalogue: null, comp: null, match: null, tab: "home", sort: { key: "minutes", dir: -1 } };
let t = makeT(state.lang);
const cache = new Map();

function initialLang() {
  const q = new URLSearchParams(location.search).get("lang");
  if (q === "fr" || q === "en") return q;
  try {
    const s = localStorage.getItem("tableau-noir-lang");
    if (s === "fr" || s === "en") return s;
  } catch { /* stockage indisponible */ }
  return navigator.language?.startsWith("fr") ? "fr" : "en";
}

const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const num = (x, d = 0) => (x == null ? "–" : x.toLocaleString(state.lang === "fr" ? "fr-FR" : "en-GB", { minimumFractionDigits: d, maximumFractionDigits: d }));
const pct = (x) => (x == null ? "–" : state.lang === "fr" ? `${Math.round(x * 100)} %` : `${Math.round(x * 100)}%`);
const team = (name) => teamName(name, state.lang);
const COLORS = { home: "var(--jaune)", away: "var(--bleu)" };


function applyI18n() {
  document.documentElement.lang = state.lang;
  document.querySelectorAll("[data-i18n]").forEach((n) => { n.textContent = t(n.dataset.i18n); });
  document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === state.lang)));
}

async function json(url) {
  if (!cache.has(url)) cache.set(url, fetch(url).then((r) => { if (!r.ok) throw new Error(`${url} : ${r.status}`); return r.json(); }));
  return cache.get(url);
}

// --- Routeur ----------------------------------------------------------------------------------

function route() {
  const h = location.hash.replace(/^#\/?/, "");
  const [kind, id, section] = h.split("/");
  if (kind === "m" && id) return showMatch(id, SECTIONS.includes(section) ? section : "s1");
  const ectx = () => ({ state, t, esc, json, team, num, pct, masthead, stageName });
  if (kind === "dossier") { state.match = null; return showDossier(app, ectx()); }
  if (kind === "archives") { state.match = null; return showArchives(app, ectx()); }
  return showCatalogue(kind === "c" ? id : null);
}

// --- Catalogue --------------------------------------------------------------------------------

function masthead(compact = false) {
  return `<section class="masthead${compact ? " compact" : ""}">
    <h1><a href="#/">Tableau Noir</a></h1>
    <p class="sub">${esc(t("tagline"))}</p>
  </section>`;
}

function compCard(c, active) {
  const n = c.matches.length;
  const badges = [`<span class="badge">${esc(t("matches_n", { n }))}</span>`];
  if (c.has_360) badges.push('<span class="badge b360">360</span>');
  badges.push(`<span class="badge">${esc(c.source === "wyscout" ? t("wyscout") : "StatsBomb")}</span>`);
  return `<button type="button" class="comp" data-comp="${c.id}" aria-pressed="${active}">
    <svg class="cadre chalk" aria-hidden="true"></svg>
    <span><span class="name">${esc(compName(c.name, state.lang))}</span><br><span class="season">${esc(c.season)}</span></span>
    <span class="meta">${badges.join("")}</span>
  </button>`;
}

function drawFrames(root) {
  root.querySelectorAll("svg.cadre").forEach((svg) => {
    const { width: w, height: h } = svg.getBoundingClientRect();
    if (!w) return;
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.setAttribute("preserveAspectRatio", "none");
    svg.replaceChildren();
    const seed = seedOf(svg.parentElement.dataset.comp || "x");
    const active = svg.parentElement.getAttribute("aria-pressed") === "true";
    svg.append(el("path", {
      d: chalkPath([[2, 2], [w - 2, 2], [w - 2, h - 2], [2, h - 2], [2, 2]], { amp: 1.4, seed }),
      fill: "none", stroke: active ? HEX.home : HEX.craie, "stroke-width": active ? 2.4 : 1.6, opacity: active ? 1 : 0.55,
      "stroke-linecap": "round", "stroke-linejoin": "round",
    }));
  });
}

async function showCatalogue(compId) {
  state.catalogue ??= await json("data/catalogue.json");
  const comps = state.catalogue.competitions;
  const comp = comps.find((c) => c.id === compId) ?? comps[0];
  state.comp = comp.id;
  const stages = byStage(comp.matches).map(([stage, ms]) => `
    <section class="stage"><h2>${esc(stageName(stage, state.lang))}</h2>
      <div class="matches">${ms.map(matchRow).join("")}</div>
    </section>`).join("");
  app.innerHTML = `${masthead()}
    <p class="masthead lead">${esc(t("lead"))}</p>
    <div class="features">
      <a class="feature" href="#/dossier"><span class="kicker">${esc(t("feature_dossier_kicker"))}</span><b>${esc(t("feature_dossier_title"))}</b><span>${esc(t("feature_dossier_text"))}</span></a>
      <a class="feature" href="#/archives"><span class="kicker">${esc(t("feature_archives_kicker"))}</span><b>${esc(t("feature_archives_title"))}</b><span>${esc(t("feature_archives_text"))}</span></a>
    </div>
    <p class="fig" style="margin-top:30px">${esc(t("pick_comp"))}</p>
    <div class="competitions">${comps.map((c) => compCard(c, c.id === comp.id)).join("")}</div>
    ${stages}`;
  app.querySelectorAll(".comp").forEach((b) => b.addEventListener("click", () => { location.hash = `#/c/${b.dataset.comp}`; }));
  requestAnimationFrame(() => drawFrames(app));
  document.title = "Tableau Noir · l'analyse tactique à la craie";
}

function matchRow(m) {
  const w = winner(m);
  const cls = (side) => (w == null ? "" : w === side ? "w" : "l");
  const pens = m.home.penalties != null ? `<span class="tab">${m.home.penalties} – ${m.away.penalties} ${esc(t("tab"))}</span>` : "";
  return `<a class="match-row" href="#/m/${m.id}">
    <span class="h ${cls("home")}">${esc(team(m.home.name))}</span>
    <span class="s">${m.home.score} – ${m.away.score}${pens}</span>
    <span class="a ${cls("away")}">${esc(team(m.away.name))}</span>
  </a>`;
}

// --- Match ------------------------------------------------------------------------------------

const SECTIONS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"];
const READY = new Set(SECTIONS);

async function showMatch(id, section = "s1") {
  const same = state.match?.meta.id === id;
  if (!same) app.innerHTML = `${masthead(true)}<p class="loading">${esc(t("loading"))}</p>`;
  const [d] = await Promise.all([json(`data/matches/${id}.json`), state.catalogue ?? json("data/catalogue.json").then((c) => { state.catalogue = c; })]);
  [state.context, state.players, state.xt] = await Promise.all([
    json(`data/context/${d.meta.comp}.json`).catch(() => null),
    json(`data/players/${d.meta.comp}.json`).catch(() => null),
    json("data/xt.json").catch(() => null),
  ]);
  state.match = d;
  state.section = section;
  renderMatch();
  if (!same) window.scrollTo({ top: 0 });
  else document.querySelector(".sections")?.scrollIntoView({ block: "start" });
}

function renderMatch() {
  const d = state.match;
  const m = d.meta;
  const comp = state.catalogue?.competitions.find((c) => c.matches.some((x) => x.id === m.id));
  const replays = d.replays ?? [];
  const scorers = (side) => d.goals.filter((g) => g.side === side).map((g) => {
    const p = d.players.find((x) => x.id === g.player);
    const tag = g.penalty ? ` (${t("pen_short")})` : g.own_goal ? ` (${t("own_goal")})` : "";
    const r = g.own_goal ? -1 : replays.findIndex((x) => x.side === side && x.minute === g.minute + 1 && x.scorer === p?.name);
    const btn = r >= 0 ? `<button type="button" class="rp" data-r="${r}" title="${esc(t("replay_open"))}" aria-label="${esc(t("replay_open"))}">▶</button>` : "";
    return `<span>${side === "home" ? btn : ""}${esc(p ? p.name : "?")} ${g.minute + 1}'${esc(tag)}${side === "away" ? btn : ""}</span>`;
  }).join("");
  const data = m.source === "wyscout" ? t("wyscout") : m.has_360 ? "StatsBomb 360" : `StatsBomb · ${t("events_only")}`;
  document.title = `${team(m.home.name)} – ${team(m.away.name)} · Tableau Noir`;
  app.innerHTML = `${masthead(true)}
    <p class="crumbs"><a href="#/c/${comp?.id ?? ""}">${esc(compName(m.competition, state.lang))} ${esc(comp?.season ?? m.season)}</a> · ${esc(stageName(m.stage, state.lang))} · ${esc(m.date)}</p>
    <section class="board" aria-label="Score">
      <div class="team home">${esc(team(m.home.name))}</div>
      <div><div class="score">${m.home.score} – ${m.away.score}</div>${m.home.penalties != null ? `<span class="pens">${m.home.penalties} – ${m.away.penalties} ${esc(t("tab"))}</span>` : ""}</div>
      <div class="team away">${esc(team(m.away.name))}</div>
    </section>
    <p class="board-meta">${m.duration > 90 ? `${esc(t("aet"))} · ` : ""}<span class="badge${m.has_360 ? " b360" : ""}">${esc(data)}</span></p>
    <div class="scorers"><div class="home">${scorers("home")}</div><div class="away">${scorers("away")}</div></div>
    ${replays.length ? `<p class="replay-hint">${esc(t("replay_hint"))}</p>` : ""}
    <div id="replay" class="replay" hidden></div>
    <ul class="sections" aria-label="${esc(t("sections_title"))}">${SECTIONS.map((s) => (READY.has(s)
      ? `<li><a href="#/m/${m.id}/${s}"${state.section === s ? ' aria-current="page"' : ""}>${esc(t(s))}</a></li>`
      : `<li><span title="${esc(t("soon"))}">${esc(t(s))}</span></li>`)).join("")}</ul>
    <div id="section-body"></div>`;
  app.querySelectorAll("button.rp").forEach((b) => b.addEventListener("click", () => openReplay(Number(b.dataset.r))));
  const body = $("#section-body");
  if (state.section === "s1") renderClassic(body);
  else {
    const ctx = { state, t, esc, num, pct, team, showTip, moveTip, hideTip, json };
    (["s6", "s7", "s8", "s9"].includes(state.section) ? playerSection : teamSection)(body, state.section, ctx);
  }
}

let stopReplay = null;
function openReplay(i) {
  const d = state.match;
  const g = d.replays[i];
  const host = $("#replay");
  stopReplay?.();
  host.hidden = false;
  const m = d.meta;
  const title = `${g.scorer} ${g.minute}'${g.penalty ? ` (${t("pen_short")})` : ""}`;
  const sub = `${team(m.home.name)} ${m.home.score}–${m.away.score} ${team(m.away.name)} · ${compName(m.competition, state.lang)} ${m.season}`;
  const file = `tableau-noir-${m.id}-${g.minute}-${g.scorer.split(" ").slice(-1)[0]}`.toLowerCase().normalize("NFD").replace(/[^a-z0-9-]/g, "");
  stopReplay = mountReplay(host, g, { t, title, sub, file });
  host.insertAdjacentHTML("afterbegin", `<button type="button" class="close" aria-label="${esc(t("replay_close"))}">×</button>`);
  host.querySelector(".close").addEventListener("click", () => { stopReplay?.(); stopReplay = null; host.hidden = true; host.innerHTML = ""; });
  host.scrollIntoView({ behavior: "smooth", block: "center" });
}

function renderClassic(body) {
  const m = state.match.meta;
  body.innerHTML = `
    <section aria-labelledby="s1-title">
      <div class="section-head"><h2 id="s1-title">${esc(t("s1_title"))}</h2><span class="note">${esc(t("s1_note"))}</span></div>
      <div class="grid">
        <div class="panel"><p class="fig">${esc(t("fig_sheet"))}</p><ul class="sheet" id="sheet"></ul></div>
        <div class="panel">
          <p class="fig">${esc(t("fig_race"))} <button type="button" class="animate" id="animate-race">▶ ${esc(t("animate"))}</button></p><div id="race-host"><svg class="chart" id="race" role="img" aria-label="${esc(t("fig_race"))}"></svg></div>
          <p class="fig" style="margin-top:34px">${esc(t("fig_shots"))}</p><svg class="chart" id="shots" role="img" aria-label="${esc(t("fig_shots"))}"></svg>
          <div class="legend"><span><i style="background:${HEX.craie}"></i>${esc(t("shots_goal"))}</span><span><i style="border:2px solid ${HEX.craie}"></i>${esc(t("shots_on"))}</span><span><i style="border:1px dashed ${HEX.gris}"></i>${esc(t("shots_off"))}</span><span>${esc(t("shots_size"))}</span></div>
        </div>
        <div class="panel full"><p class="fig">${esc(t("fig_players"))}</p><div id="standouts" class="standouts"></div>
          <div class="tabs" role="tablist" id="tabs"></div><div class="table-wrap"><table class="players" id="players"></table></div></div>
      </div>
      ${analystBlock(state.match, "s1", state.lang, t, esc)}
      <div class="method"><h3>${esc(t("method_title"))}</h3><p>${esc(m.source === "wyscout" ? t("method_wy") : t("method_sb"))} ${esc(t("method_common"))}</p></div>
    </section>`;
  drawSheet();
  drawRace();
  $("#animate-race").addEventListener("click", (e) => {
    e.currentTarget.remove();
    const d = state.match;
    const sub = `${team(d.meta.home.name)} – ${team(d.meta.away.name)} · ${compName(d.meta.competition, state.lang)} ${d.meta.season}`;
    mountRace($("#race-host"), d, "xg", { t, title: t("race_xg"), sub, decimal: state.lang === "fr" ? "," : ".", autoplay: false });
  });
  drawShots();
  drawPlayers();
}

// Fig. 1 — feuille de match
const SHEET = [
  ["g_attack", [["k_xg", "xg", 2, "k_xg_h"], ["k_npxg", "npxg", 2], ["k_shots", "shots"], ["k_on_target", "on_target"], ["k_big", "big_chances", 0, "k_big_h"]]],
  ["g_ball", [["k_possession", "possession", "pct"], ["k_passes", "passes_ok"], ["k_pass_rate", "pass_rate", "pct"], ["k_progressive", "progressive", 0, "k_progressive_h"], ["k_final_third", "final_third"], ["k_key", "key_passes", 0, "k_key_h"]]],
  ["g_fight", [["k_duels", "duels_won", "rate:duels"], ["k_aerials", "aerials_won", "rate:aerials"]]],
  ["g_defend", [["k_tackles", "tackles_won"], ["k_interceptions", "interceptions"], ["k_recoveries", "recoveries"], ["k_clearances", "clearances"], ["k_ppda", "ppda", 1, "k_ppda_h"], ["k_saves", "saves"]]],
  ["g_discipline", [["k_corners", "corners"], ["k_fouls", "fouls"], ["k_yellow", "yellow"], ["k_red", "red"], ["k_offsides", "offsides"]]],
];

function drawSheet() {
  const s = state.match.stats;
  const ul = $("#sheet");
  for (const [group, rows] of SHEET) {
    ul.insertAdjacentHTML("beforeend", `<li class="group"><span>${esc(t(group))}</span></li>`);
    for (const [label, key, fmt = 0, help] of rows) {
      const a = s.home[key];
      const b = s.away[key];
      if (a == null && b == null) continue;
      const show = (v, side) => {
        if (fmt === "pct") return pct(v);
        if (typeof fmt === "string" && fmt.startsWith("rate:")) {
          const tot = s[side][fmt.slice(5)];
          return `${num(v)}<small style="color:var(--gris-2)"> /${num(tot)}</small>`;
        }
        return num(v, fmt);
      };
      const li = document.createElement("li");
      li.innerHTML = `<span class="v home">${show(a, "home")}</span><svg aria-hidden="true"></svg>
        <span class="k">${esc(t(label))}${help ? `<small>${esc(t(help))}</small>` : ""}</span>
        <svg aria-hidden="true"></svg><span class="v away">${show(b, "away")}</span>`;
      ul.append(li);
      const [l, r] = li.querySelectorAll("svg");
      const max = Math.max(a || 0, b || 0) || 1;
      bar(l, (a || 0) / max, "home", seedOf(label + "h"), true);
      bar(r, (b || 0) / max, "away", seedOf(label + "a"), false);
    }
  }
}


// Fig. 2 — course aux xG
function drawRace() {
  const d = state.match;
  const svg = $("#race");
  const W = 640;
  const H = 300;
  const m = { l: 40, r: 84, t: 24, b: 40 };
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const dur = d.meta.duration;
  const { steps, total } = xgRace(d.shots, dur);
  const end = Math.max(dur, ...steps.home.map((p) => p[0]), ...steps.away.map((p) => p[0]));
  const ymax = Math.max(1, total.home, total.away) * 1.12;
  const x = scale(0, end, m.l, W - m.r);
  const y = scale(0, ymax, H - m.b, m.t);
  const g = el("g", { class: "chalk" });
  // axes et repères
  g.append(el("path", { d: chalkPath([[m.l, H - m.b], [W - m.r, H - m.b]], { seed: 3 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none", opacity: 0.7 }));
  for (const mark of [45, 90, 105].filter((v) => v < end)) {
    g.append(el("path", { d: chalkPath([[x(mark), m.t], [x(mark), H - m.b]], { seed: mark }), stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "4 5", fill: "none", opacity: 0.6 }));
    g.append(el("text", { x: x(mark), y: H - m.b + 20, "text-anchor": "middle", "font-size": 14, fill: HEX.gris }, `${mark}'`));
  }
  for (let v = 1; v < ymax; v += 1) {
    g.append(el("text", { x: m.l - 10, y: y(v) + 5, "text-anchor": "end", "font-size": 14, fill: HEX.gris }, num(v)));
    g.append(el("path", { d: `M${m.l} ${y(v)}H${W - m.r}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.12 }));
  }
  g.append(el("text", { x: m.l, y: H - 4, "font-size": 13, fill: HEX.gris }, t("race_axis")));
  const ends = {};
  for (const side of ["home", "away"]) {
    const pts = steps[side].map(([tt, v]) => [x(tt), y(v)]);
    g.append(el("path", { d: chalkPath(pts, { amp: 0.7, step: 10, seed: seedOf(side) }), stroke: HEX[side], "stroke-width": 3.4, fill: "none", "stroke-linejoin": "round" }));
    ends[side] = pts[pts.length - 1];
  }
  const gap = ends.home[1] - ends.away[1];
  if (Math.abs(gap) < 20) {
    const shift = (20 - Math.abs(gap)) / 2 * (gap < 0 ? 1 : -1);
    ends.home = [ends.home[0], ends.home[1] - shift];
    ends.away = [ends.away[0], ends.away[1] + shift];
  }
  for (const side of ["home", "away"]) {
    g.append(el("text", { x: ends[side][0] + 8, y: ends[side][1] + 5, "font-size": 16, fill: HEX[side] }, `${num(total[side], 2)} xG`));
  }
  svg.replaceChildren(g);
  // buts : cercle de craie et nom du buteur (à la main)
  let lastY = { home: -99, away: -99 };
  for (const s of d.shots.filter((s) => s.goal)) {
    const before = d.shots.filter((o) => o.side === s.side && o.t < s.t).reduce((a, o) => a + o.xg, 0);
    const cx = x(s.t);
    const cy = y(before + s.xg);
    svg.append(el("path", { class: "chalk", d: chalkCircle(cx, cy, 7, { seed: seedOf(String(s.t)) }), stroke: HEX.corail, "stroke-width": 2.4, fill: HEX.corail, "fill-opacity": 0.25 }));
    const p = state.match.players.find((pp) => pp.id === s.player);
    let ly = cy - 12;
    if (Math.abs(ly - lastY[s.side]) < 16) ly -= 16;
    lastY[s.side] = ly;
    svg.append(el("text", { x: cx + 6, y: ly, "font-size": 17, fill: HEX.craie, "font-family": "Nothing You Could Do, cursive", class: "chalk" }, p ? p.name.split(" ").slice(-1)[0] : ""));
  }
}

// Fig. 3 — carte des tirs

function drawShots() {
  const d = state.match;
  const svg = $("#shots");
  const k = 6;
  const pad = 10;
  svg.setAttribute("viewBox", `0 0 ${PITCH.x * k + pad * 2} ${PITCH.y * k + pad * 2}`);
  const g = el("g", { class: "chalk" });
  drawPitch(g, k, pad, pad, seedOf(d.meta.id));
  svg.replaceChildren(g);
  const marks = el("g");
  for (const s of [...d.shots].sort((a, b) => b.xg - a.xg)) {
    if (s.x == null) continue;
    const [x, y] = orient(s.x, s.y, s.side);
    const cx = pad + x * k;
    const cy = pad + y * k;
    const r = 4 + 26 * Math.sqrt(s.xg || 0.01);
    const color = HEX[s.side];
    const c = el("path", {
      d: chalkCircle(cx, cy, r, { seed: seedOf(`${s.t}${s.side}`), amp: 0.08 }),
      stroke: color, "stroke-width": s.goal ? 2.5 : s.on_target ? 2.2 : 1.3,
      "stroke-dasharray": s.goal || s.on_target ? null : "3 3",
      fill: s.goal ? color : "transparent", "fill-opacity": s.goal ? 0.85 : 0, opacity: s.goal || s.on_target ? 1 : 0.75,
      class: "chalk", tabindex: 0,
    });
    const p = d.players.find((pp) => pp.id === s.player);
    const extra = [s.set_piece === "penalty" ? t("pen") : s.set_piece === "free_kick" ? t("fk") : null, s.body === "head" ? t("head") : null].filter(Boolean).join(" · ");
    const html = `<b>${esc(p ? p.name : "?")}</b><br>${esc(t("shots_tip", { min: s.minute + 1, xg: num(s.xg, 2) }))}${extra ? `<br>${esc(extra)}` : ""}<br>${esc(s.goal ? t("shots_goal") : s.on_target ? t("shots_on") : t("shots_off"))}`;
    c.addEventListener("pointerenter", (e) => showTip(html, e));
    c.addEventListener("pointermove", (e) => moveTip(e));
    c.addEventListener("pointerleave", hideTip);
    c.addEventListener("focus", () => { const b = c.getBoundingClientRect(); showTip(html, { clientX: b.right, clientY: b.top }); });
    c.addEventListener("blur", hideTip);
    marks.append(c);
  }
  svg.append(marks);
  // sens du jeu
  svg.append(el("text", { x: pad + 52.5 * k - 14, y: pad + PITCH.y * k - 12, "text-anchor": "end", "font-size": 22, fill: HEX.home, "font-family": "Nothing You Could Do, cursive", class: "chalk" }, `${team(d.meta.home.name)} →`));
  svg.append(el("text", { x: pad + 52.5 * k + 14, y: pad + 30, "font-size": 22, fill: HEX.away, "font-family": "Nothing You Could Do, cursive", class: "chalk" }, `← ${team(d.meta.away.name)}`));
}

function showTip(html, e) { tip.innerHTML = html; tip.hidden = false; moveTip(e); }
function moveTip(e) {
  const x = Math.min(window.innerWidth - tip.offsetWidth - 8, e.clientX + 14);
  const y = Math.max(8, e.clientY - tip.offsetHeight - 10);
  tip.style.left = `${x}px`;
  tip.style.top = `${y}px`;
}
function hideTip() { tip.hidden = true; }

// Fig. 4 — joueurs
const COLS = [
  ["name", "col_player"], ["minutes", "col_min"], ["goals", "col_goals"], ["assists", "col_assists"], ["shots", "col_shots"],
  ["xg", "col_xg", 2], ["key_passes", "col_key"], ["passes_ok", "col_passes"], ["progressive", "col_prog"],
  ["dribbles", "col_drib"], ["def_actions", "col_def"], ["duels_won", "col_duels"],
];

function drawPlayers() {
  const d = state.match;
  const best = standouts(d.players, 3);
  $("#standouts").innerHTML = best.map((p) => {
    const why = [
      p.goals ? t("why_goals", { g: p.goals }) : null,
      p.assists ? t("why_assists", { a: p.assists }) : null,
      p.xg >= 0.3 ? t("why_xg", { xg: num(p.xg, 2) }) : null,
      p.key_passes >= 2 ? t("why_key", { k: p.key_passes }) : null,
      p.progressive >= 5 ? t("why_prog", { p: p.progressive }) : null,
      p.def_actions >= 5 ? t("why_def", { d: p.def_actions }) : null,
    ].filter(Boolean).slice(0, 3).join(" · ");
    return `<div class="standout"><div class="who ${p.side}">${esc(p.name)}</div>
      <div class="line">${esc(team(p.side === "home" ? d.meta.home.name : d.meta.away.name))} · ${num(p.minutes)}'</div>
      <div class="why">${esc(why)}</div></div>`;
  }).join("");
  const tabs = $("#tabs");
  tabs.innerHTML = ["home", "away"].map((side) => `<button type="button" role="tab" class="${side}" data-side="${side}" aria-selected="${state.tab === side}">${esc(team(d.meta[side].name))}</button>`).join("");
  tabs.querySelectorAll("button").forEach((b) => b.addEventListener("click", () => { state.tab = b.dataset.side; drawPlayers(); }));
  const rows = sortPlayers(d.players.filter((p) => p.side === state.tab), state.sort.key, state.sort.dir);
  const tops = Object.fromEntries(COLS.slice(1).map(([k]) => [k, Math.max(...d.players.filter((p) => p.side === state.tab).map((p) => p[k] ?? 0))]));
  const head = COLS.map(([k, label]) => `<th scope="col" data-k="${k}"${state.sort.key === k ? ` aria-sort="${state.sort.dir < 0 ? "descending" : "ascending"}"` : ""}>${esc(t(label))}</th>`).join("");
  const body = rows.map((p) => `<tr>${COLS.map(([k, , dd]) => {
    if (k === "name") return `<td class="name${p.starter ? "" : " sub"}">${esc(p.name)}<span class="pos">${esc(p.position)}</span></td>`;
    if (k === "passes_ok") return `<td>${num(p.passes_ok)}/${num(p.passes)}</td>`;
    if (k === "duels_won") return `<td>${num(p.duels_won)}/${num(p.duels)}</td>`;
    const v = p[k];
    return `<td class="${v && v === tops[k] && k !== "minutes" ? "hi" : ""}">${num(v, dd ?? 0)}</td>`;
  }).join("")}</tr>`).join("");
  $("#players").innerHTML = `<thead><tr>${head}</tr></thead><tbody>${body}</tbody>`;
  $("#players").querySelectorAll("th").forEach((th) => th.addEventListener("click", () => {
    const k = th.dataset.k;
    state.sort = { key: k, dir: state.sort.key === k ? -state.sort.dir : k === "name" ? 1 : -1 };
    drawPlayers();
  }));
}

// --- Démarrage --------------------------------------------------------------------------------

function bind() {
  document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => {
    state.lang = b.dataset.lang;
    t = makeT(state.lang);
    try { localStorage.setItem("tableau-noir-lang", state.lang); } catch { /* ignore */ }
    applyI18n();
    route();
  }));
  window.addEventListener("hashchange", route);
  let rt;
  window.addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => drawFrames(app), 150); });
}

applyI18n();
bind();
route().catch((err) => {
  console.error(err);
  app.innerHTML = `<p class="loading">${esc(String(err))}</p>`;
});

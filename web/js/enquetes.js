// Les enquêtes : une question, une réponse chiffrée, trois ou quatre figures qu'on peut emporter.

import { HEX, el } from "./draw.js";
import { chalkPath, seedOf } from "./logic.js";

const $ = (s, root = document) => root.querySelector(s);
const MONO = "DM Mono, monospace";
const HAND = "Nothing You Could Do, cursive";
const TITRE = "Big Shoulders Display, sans-serif";

export async function showEnquete(app, slug, ctx) {
  const { t, esc, json, state } = ctx;
  const all = await json("data/enquetes.json");
  const e = all.find((x) => x.slug === slug) ?? all[0];
  const L = state.lang;
  state.enquetes = all;
  document.title = `${e.title[L]} · Tableau Noir`;
  app.innerHTML = `${ctx.masthead(true)}
    <article class="enquete">
      <p class="kicker">${esc(t("enquete_kicker", { n: e.number }))}</p>
      <h1>${esc(e.title[L])}</h1>
      <div class="qa"><p class="q">${esc(e.question[L])}</p><p class="a">${esc(e.answer[L])}</p></div>
      <p class="standfirst">${esc(e.standfirst[L])}</p>
      ${e.chapters.map((c, i) => `<section class="chapter">
          <h2>${esc(c.title[L])}</h2>
          ${c.text[L].map((p) => `<p>${esc(p)}</p>`).join("")}
          <figure class="fig-card" data-fig="${c.figure}" data-i="${i}">
            <figcaption><span></span><button type="button" class="dl">${esc(t("fig_download"))}</button></figcaption>
            <svg class="chart"></svg>
          </figure>
        </section>`).join("")}
      <section class="chapter boxes">
        <div class="box take"><h3>${esc(t("takeaways"))}</h3><ul>${e.takeaways[L].map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
        <div class="box limits"><h3>${esc(t("limits"))}</h3><ul>${e.limits[L].map((x) => `<li>${esc(x)}</li>`).join("")}</ul></div>
      </section>
      <p class="credit-line">${esc(t("enquete_credit"))}</p>
    </article>`;
  app.querySelectorAll("figure.fig-card").forEach((fig) => {
    const kind = fig.dataset.fig;
    const svg = fig.querySelector("svg");
    const caption = FIGURES[kind](svg, e, ctx);
    fig.querySelector("figcaption span").textContent = caption;
    fig.querySelector(".dl").addEventListener("click", () => download(svg, `tableau-noir-${e.slug}-${kind}`, caption, ctx));
  });
  window.scrollTo({ top: 0 });
}

// --- Figures ----------------------------------------------------------------------------------

const W = 1200;
const H = 675; // 16:9, pour être emporté tel quel
const text = (x, y, s, o = {}) => el("text", { x, y, fill: HEX.craie, "font-family": MONO, "font-size": 20, ...o }, s);

function frame(svg, title, source) {
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  svg.replaceChildren();
  svg.append(el("rect", { x: 0, y: 0, width: W, height: H, fill: "#1c2421" }));
  svg.append(text(50, 64, title, { "font-family": HAND, "font-size": 40 }));
  svg.append(text(50, H - 28, source, { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(W - 50, 60, "TABLEAU NOIR", { fill: HEX.gris, "font-size": 18, "text-anchor": "end", "font-family": TITRE, "font-weight": 600, "letter-spacing": 3 }));
}

/** Fig. 1 — l'équipe qui a « plus de … » : victoires, nuls, défaites, en barres empilées. */
function outcomes(svg, e, ctx) {
  const { t, state } = ctx;
  const d = e.data.outcomes;
  const keys = ["xg", "possession", "high_recoveries", "counterpress", "press_per_min", "ppda"];
  frame(svg, t("fig_outcomes_title"), t("fig_source", { n: e.data.n_matches }));
  const x0 = 330; const x1 = W - 60; const y0 = 120; const rowH = 78;
  const g = el("g", { class: "chalk" });
  keys.forEach((k, i) => {
    const o = d[k];
    const y = y0 + i * rowH;
    const w = (v) => ((x1 - x0) * v) / o.n;
    const seg = [["win", HEX.home], ["draw", HEX.gris], ["loss", HEX.away]];
    let x = x0;
    for (const [s, col] of seg) {
      const ww = w(o[s]);
      g.append(el("path", { d: chalkPath([[x, y + 22], [x + ww, y + 22]], { amp: 0.8, step: 14, seed: seedOf(k + s) }), stroke: col, "stroke-width": 30, fill: "none", opacity: s === "draw" ? 0.45 : 0.9, "stroke-linecap": "butt" }));
      if (ww > 60) svg.append(text(x + ww / 2, y + 29, `${Math.round((100 * o[s]) / o.n)} %`, { "text-anchor": "middle", fill: HEX.craie, "font-size": 20, "font-weight": 600, "paint-order": "stroke", stroke: "#1c2421", "stroke-width": 5 }));
      x += ww;
    }
    const bold = k === "xg" || k === "ppda";
    svg.append(text(x0 - 18, y + 20, t(`more_${k}`), { "text-anchor": "end", "font-size": bold ? 22 : 19, "font-family": bold ? TITRE : MONO, "font-weight": 600, fill: bold ? HEX.craie : HEX.gris }));
    svg.append(text(x0 - 18, y + 42, t("outcome_n", { n: o.n }), { "text-anchor": "end", fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(g);
  // ligne du hasard : 50 % du total hors nuls, à titre de repère
  const legend = [["win", t("o_win"), HEX.home], ["draw", t("o_draw"), HEX.gris], ["loss", t("o_loss"), HEX.away]];
  legend.forEach(([, lab, col], i) => {
    svg.append(el("rect", { x: x0 + i * 170, y: 88, width: 16, height: 16, fill: col, opacity: 0.9 }));
    svg.append(text(x0 + i * 170 + 24, 102, lab, { fill: HEX.gris, "font-size": 15 }));
  });
  svg.append(text(x0, y0 + keys.length * rowH + 8, t("fig_outcomes_note"), { "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_outcomes_caption", { n: e.data.n_matches });
}

/** Fig. 2 — les champions : leur PPDA contre celui de leur tournoi. */
function champions(svg, e, ctx) {
  const { t, state } = ctx;
  frame(svg, t("fig_champions_title"), t("fig_source", { n: e.data.n_matches }));
  const rows = e.data.champions;
  const x0 = 90; const x1 = W - 90; const y0 = 150; const rowH = 110;
  const max = 26;
  const X = (v) => x0 + ((x1 - x0) * v) / max;
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[x0, y0 - 30], [x0, y0 + rows.length * rowH - 20]], { seed: 1 }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
  for (const v of [5, 10, 15, 20, 25]) {
    g.append(el("path", { d: `M${X(v)} ${y0 - 30}V${y0 + rows.length * rowH - 20}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.15 }));
    svg.append(text(X(v), y0 - 40, String(v), { "text-anchor": "middle", fill: HEX.gris, "font-size": 15 }));
  }
  svg.append(text(x0, H - 62, t("ppda_axis"), { fill: HEX.gris, "font-size": 15 }));
  rows.forEach((r, i) => {
    const y = y0 + i * rowH;
    g.append(el("path", { d: chalkPath([[x0, y + 18], [X(r.ppda), y + 18]], { amp: 0.8, step: 14, seed: seedOf(r.team) }), stroke: HEX.home, "stroke-width": 26, fill: "none", opacity: 0.9 }));
    g.append(el("path", { d: chalkPath([[X(r.ppda_comp), y - 4], [X(r.ppda_comp), y + 40]], { seed: i }), stroke: HEX.craie, "stroke-width": 3, fill: "none" }));
    svg.append(text(X(r.ppda) + 12, y + 25, ctx.num(r.ppda, 1), { fill: HEX.home, "font-size": 22 }));
    svg.append(text(X(r.ppda_comp) + 8, y - 10, `⌀ ${ctx.num(r.ppda_comp, 1)}`, { fill: HEX.gris, "font-size": 14 }));
    svg.append(text(x0 + 10, y + 70, `${ctx.team(r.team)} ${e.data.champions[i].comp.slice(-4)}`, { "font-family": TITRE, "font-size": 28, "font-weight": 600, "letter-spacing": 1 }));
    svg.append(text(x0 + 10 + 18 * (ctx.team(r.team).length + 5) + 10, y + 70, t("champion_rank", { r: r.rank, n: r.of }), { "font-family": HAND, "font-size": 22, fill: HEX.gris }));
  });
  svg.append(g);
  svg.append(text(x1, H - 62, t("ppda_hint"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_champions_caption");
}

/** Fig. 3 — quarts de pressing : xG créés, concédés, et points. */
function quartiles(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_quartiles_title"), t("fig_source_rows", { n: e.data.n_rows }));
  const q = e.data.ppda_quartiles;
  const panels = [
    { key: "xg", label: t("q_xg"), color: HEX.home, min: 0.8, max: 1.8 },
    { key: "xg_against", label: t("q_xga"), color: HEX.away, min: 0.8, max: 1.8 },
    { key: "pts", label: t("q_pts"), color: HEX.craie, min: 0.8, max: 1.8 },
  ];
  const pw = 340; const left = 70; const top = 130; const ph = 380;
  panels.forEach((p, pi) => {
    const x0 = left + pi * (pw + 40);
    const X = (i) => x0 + 30 + (i * (pw - 60)) / 3;
    const Y = (v) => top + ph - ((v - p.min) / (p.max - p.min)) * ph;
    const g = el("g", { class: "chalk" });
    g.append(el("path", { d: chalkPath([[x0, top + ph], [x0 + pw, top + ph]], { seed: pi }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
    const pts = q.map((r, i) => [X(i), Y(r[p.key])]);
    g.append(el("path", { d: chalkPath(pts, { amp: 1, step: 10, seed: seedOf(p.key) }), stroke: p.color, "stroke-width": 5, fill: "none", "stroke-linejoin": "round" }));
    q.forEach((r, i) => {
      g.append(el("circle", { cx: X(i), cy: Y(r[p.key]), r: 7, fill: p.color }));
      svg.append(text(X(i), Y(r[p.key]) - 16, ctx.num(r[p.key], 2), { "text-anchor": "middle", fill: p.color, "font-size": 18 }));
      svg.append(text(X(i), top + ph + 26, t(`q_${r.quartile}`), { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
    });
    svg.append(g);
    svg.append(text(x0, top - 20, p.label, { "font-family": TITRE, "font-size": 26, "font-weight": 600, fill: p.color, "letter-spacing": 1 }));
  });
  svg.append(text(left, top + ph + 62, t("q_axis"), { fill: HEX.gris, "font-size": 15 }));
  svg.append(text(W - 60, top + ph + 100, t("fig_quartiles_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_quartiles_caption");
}

/** Fig. 4 — les blocs bas qui ont gagné : PPDA des deux équipes, face à face. */
function cases(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_cases_title"), t("fig_source_ko", { n: e.data.n_knockout }));
  const rows = e.data.low_block_wins.slice(0, 7);
  const x0 = 420; const x1 = W - 80; const y0 = 110; const rowH = 70;
  const max = 52;
  const X = (v) => x0 + ((x1 - x0) * v) / max;
  const g = el("g", { class: "chalk" });
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + 20;
    g.append(el("path", { d: chalkPath([[X(r.ppda_high), y], [X(r.ppda_low), y]], { amp: 0.6, step: 16, seed: seedOf(r.match_id) }), stroke: HEX.craie, "stroke-width": 2, fill: "none", opacity: 0.35, "stroke-dasharray": "4 6" }));
    g.append(el("circle", { cx: X(r.ppda_high), cy: y, r: 11, fill: HEX.away, opacity: 0.9 }));
    g.append(el("circle", { cx: X(r.ppda_low), cy: y, r: 11, fill: HEX.home }));
    svg.append(text(X(r.ppda_high), y - 18, ctx.num(r.ppda_high, 1), { "text-anchor": "middle", fill: HEX.away, "font-size": 15 }));
    svg.append(text(X(r.ppda_low), y - 18, ctx.num(r.ppda_low, 1), { "text-anchor": "middle", fill: HEX.home, "font-size": 15 }));
    svg.append(text(x0 - 20, y - 4, `${ctx.team(r.low_block)} ${r.score_low}–${r.score_high} ${ctx.team(r.presser)}`, { "text-anchor": "end", "font-family": TITRE, "font-size": 24, "font-weight": 600, "letter-spacing": 1 }));
    svg.append(text(x0 - 20, y + 18, `${ctx.compName(r.comp)} · ${ctx.stageName(r.stage)} · ${t("poss_short", { p: r.possession_low })}`, { "text-anchor": "end", fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(g);
  svg.append(el("circle", { cx: x0, cy: 92, r: 7, fill: HEX.home }));
  svg.append(text(x0 + 14, 97, t("legend_low_block"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(el("circle", { cx: x0 + 300, cy: 92, r: 7, fill: HEX.away }));
  svg.append(text(x0 + 314, 97, t("legend_presser"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(x1, y0 + rows.length * rowH + 30, t("ppda_axis"), { "text-anchor": "end", fill: HEX.gris, "font-size": 14 }));
  return t("fig_cases_caption");
}

const FIGURES = { outcomes, champions, quartiles, cases };

// --- Export PNG ---------------------------------------------------------------------------------

/** Rend le SVG en PNG 1920 × 1080, polices incorporées, pour une vidéo ou un réseau social. */
async function download(svg, name, caption, ctx) {
  const clone = svg.cloneNode(true);
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  clone.querySelectorAll("[class]").forEach((n) => n.removeAttribute("class")); // pas de filtre craie hors page
  const css = await fontCss();
  clone.insertBefore(el("style", {}, css), clone.firstChild);
  const blob = new Blob([new XMLSerializer().serializeToString(clone)], { type: "image/svg+xml" });
  const url = URL.createObjectURL(blob);
  const img = new Image();
  await new Promise((ok, ko) => { img.onload = ok; img.onerror = ko; img.src = url; });
  const canvas = document.createElement("canvas");
  canvas.width = 1920;
  canvas.height = 1080;
  canvas.getContext("2d").drawImage(img, 0, 0, 1920, 1080);
  URL.revokeObjectURL(url);
  const a = document.createElement("a");
  a.href = canvas.toDataURL("image/png");
  a.download = `${name}.png`;
  a.click();
}

let fontCache = null;
async function fontCss() {
  if (fontCache) return fontCache;
  const families = ["Nothing+You+Could+Do", "DM+Mono", "Big+Shoulders+Display:wght@600"];
  try {
    const css = await (await fetch(`https://fonts.googleapis.com/css2?${families.map((f) => `family=${f}`).join("&")}&display=swap`)).text();
    const urls = [...css.matchAll(/url\(([^)]+)\)/g)].map((m) => m[1]);
    let out = css;
    for (const u of urls) {
      const b = await (await fetch(u)).blob();
      const data = await new Promise((ok) => { const r = new FileReader(); r.onload = () => ok(r.result); r.readAsDataURL(b); });
      out = out.replace(u, data);
    }
    fontCache = out;
  } catch { fontCache = ""; }
  return fontCache;
}

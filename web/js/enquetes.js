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
  svg.append(text(50, 64, title, { "font-family": HAND, "font-size": title.length > 48 ? 34 : 40 }));
  svg.append(text(50, H - 28, source, { fill: HEX.gris, "font-size": 13 }));
  svg.append(text(W - 50, H - 28, "TABLEAU NOIR", { fill: HEX.gris, "font-size": 15, "text-anchor": "end", "font-family": TITRE, "font-weight": 600, "letter-spacing": 3 }));
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


/** Fig. — en championnat : favori, force égale, outsider × presse plus / presse moins. */
function favourite(svg, e, ctx) {
  const { t } = ctx;
  const L = e.data.leagues_sb;
  frame(svg, t("fig_fav_title"), t("fig_source_leagues", { n: L.n_matches }));
  const groups = [
    { label: t("fav_favourite"), more: L.favourite_pressing_more, less: L.favourite_pressing_less },
    { label: t("fav_equal"), more: L.equal_presser, less: null },
    { label: t("fav_outsider"), more: L.outsider_pressing_more, less: L.outsider_pressing_less },
  ];
  const x0 = 330; const x1 = W - 70; const y0 = 130;
  const X = (v) => x0 + ((x1 - x0) * v) / 100;
  const g = el("g", { class: "chalk" });
  for (const v of [25, 50, 75]) {
    g.append(el("path", { d: `M${X(v)} ${y0 - 20}V${y0 + 3 * 150}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.18 }));
    svg.append(text(X(v), y0 - 28, `${v} %`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 14 }));
  }
  groups.forEach((gr, i) => {
    const y = y0 + i * 150;
    svg.append(text(x0 - 20, y, gr.label, { "text-anchor": "end", "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
    const bars = gr.less ? [["more", t("fav_more"), HEX.home], ["less", t("fav_less"), HEX.away]] : [["more", t("fav_equal_sub"), HEX.home]];
    bars.forEach(([k, lab, col], j) => {
      const o = gr[k];
      const yy = y + 16 + j * 42;
      g.append(el("path", { d: chalkPath([[x0, yy + 12], [X(o.win_pct), yy + 12]], { amp: 0.8, step: 14, seed: seedOf(gr.label + k) }), stroke: col, "stroke-width": 26, fill: "none", opacity: 0.9 }));
      svg.append(text(x0 - 20, yy + 17, lab, { "text-anchor": "end", fill: HEX.gris, "font-size": 14 }));
      svg.append(text(X(o.win_pct) + 12, yy + 19, `${o.win_pct} %`, { fill: col, "font-size": 21, "font-weight": 600 }));
      svg.append(text(X(o.win_pct) + 82, yy + 19, t("outcome_n", { n: o.n }), { fill: HEX.gris, "font-size": 13 }));
    });
  });
  svg.append(g);
  svg.append(text(x0, H - 62, t("fig_fav_note"), { "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_fav_caption", { n: L.n_matches });
}

/** Fig. — le temps : le Barça saison par saison, et les tournois 2018–2024. */
function time(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_time_title"), t("fig_source_time"));
  const b = e.data.barca;
  // panneau gauche : PPDA du Barça par saison
  const lx0 = 70; const lx1 = 640; const ty = 130; const by = 520;
  const X = (i) => lx0 + ((lx1 - lx0) * i) / (b.length - 1);
  const Y = (v) => by - ((v - 8) / (18 - 8)) * (by - ty);
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[lx0, by], [lx1, by]], { seed: 3 }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
  g.append(el("path", { d: chalkPath(b.map((r, i) => [X(i), Y(r.ppda)]), { amp: 1, step: 10, seed: 7 }), stroke: HEX.home, "stroke-width": 5, fill: "none", "stroke-linejoin": "round" }));
  b.forEach((r, i) => {
    g.append(el("circle", { cx: X(i), cy: Y(r.ppda), r: 5, fill: HEX.home }));
    if (i % 4 === 0 || i === b.length - 1) {
      svg.append(text(X(i), by + 24, r.season.slice(0, 4), { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
      svg.append(text(X(i), Y(r.ppda) - 14, ctx.num(r.ppda, 1), { "text-anchor": "middle", fill: HEX.home, "font-size": 16 }));
    }
  });
  svg.append(g);
  svg.append(text(lx0, ty - 24, t("time_barca"), { "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
  svg.append(text(lx0, by + 50, t("time_barca_sub"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(lx0, by + 90, t("time_barca_note"), { "font-family": HAND, "font-size": 22, fill: HEX.home }));
  // panneau droit : presseur gagne, tournoi par tournoi
  const T = e.data.tournaments.filter((x) => ["wc-2018", "euro-2020", "wc-2022", "euro-2024"].includes(x.comp));
  const rx0 = 760; const rx1 = W - 60;
  const RX = (i) => rx0 + ((rx1 - rx0) * i) / (T.length - 1);
  const RY = (v) => by - ((v - 20) / (70 - 20)) * (by - ty);
  const g2 = el("g", { class: "chalk" });
  g2.append(el("path", { d: chalkPath([[rx0 - 20, RY(50)], [rx1 + 20, RY(50)]], { seed: 9 }), stroke: HEX.gris, "stroke-width": 1.2, fill: "none", "stroke-dasharray": "5 7", opacity: 0.7 }));
  g2.append(el("path", { d: chalkPath(T.map((r, i) => [RX(i), RY(r.presser_win_pct)]), { amp: 1, step: 10, seed: 11 }), stroke: HEX.craie, "stroke-width": 5, fill: "none", "stroke-linejoin": "round" }));
  T.forEach((r, i) => {
    g2.append(el("circle", { cx: RX(i), cy: RY(r.presser_win_pct), r: 7, fill: HEX.craie }));
    svg.append(text(RX(i), RY(r.presser_win_pct) - 16, `${r.presser_win_pct} %`, { "text-anchor": "middle", fill: HEX.craie, "font-size": 18 }));
    svg.append(text(RX(i), by + 24, t(`comp_${r.comp}`), { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(text(rx1 + 22, RY(50) + 5, "50 %", { fill: HEX.gris, "font-size": 13 }));
  svg.append(g2);
  svg.append(text(rx0, ty - 24, t("time_tournaments"), { "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
  svg.append(text(rx0, by + 50, t("time_tournaments_sub"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(rx0, by + 90, t("time_tournaments_note"), { "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_time_caption");
}


// --- Outils de figures génériques ----------------------------------------------------------------

/** Deux colonnes de valeurs face à face (club | sélection), une ligne par indicateur. */
function compareRowsFig(svg, rows, left, right, ctx) {
  const lx = 300; const colW = 380; const gap = 90; const y0 = 125; const rowH = Math.min(78, (H - 210) / rows.length);
  const cols = [[lx, HEX.home, left, "a"], [lx + colW + gap, HEX.away, right, "b"]];
  const g = el("g", { class: "chalk" });
  for (const [x, col, title] of cols) svg.append(text(x, 100, title, { fill: col, "font-family": TITRE, "font-size": 22, "font-weight": 600, "letter-spacing": 1 }));
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + 20;
    const max = Math.max(r.a, r.b) || 1;
    for (const [x, col, , k] of cols) {
      const w = ((colW - 90) * r[k]) / max;
      g.append(el("path", { d: chalkPath([[x, y], [x + w, y]], { amp: 0.7, step: 14, seed: seedOf(r.label + k) }), stroke: col, "stroke-width": 24, fill: "none", opacity: 0.9 }));
      svg.append(text(x + w + 10, y + 7, r.fmt(r[k]), { fill: col, "font-size": 20, "font-weight": 600 }));
    }
    svg.append(text(lx - 22, y + 5, r.label, { "text-anchor": "end", "font-size": 17, fill: HEX.craie }));
    if (r.sub) svg.append(text(lx - 22, y + 24, r.sub, { "text-anchor": "end", "font-size": 12, fill: HEX.gris }));
  });
  svg.append(g);
}

/** Petits multiples : une courbe par panneau, x = étiquettes, y = valeurs. */
function panels(svg, items, panelsSpec, ctx, opts = {}) {
  const n = panelsSpec.length;
  const left = 70; const gap = 40; const pw = (W - 2 * left - gap * (n - 1)) / n; const top = opts.top ?? 140; const ph = opts.height ?? 360;
  panelsSpec.forEach((p, pi) => {
    const x0 = left + pi * (pw + gap);
    const vals = items.map((it) => p.get(it)).filter((v) => v != null);
    const lo = p.min ?? Math.min(...vals) - (Math.max(...vals) - Math.min(...vals)) * 0.5;
    const hi = p.max ?? Math.max(...vals) + (Math.max(...vals) - Math.min(...vals)) * 0.3;
    const X = (i) => x0 + 24 + (i * (pw - 48)) / Math.max(1, items.length - 1);
    const Y = (v) => top + ph - ((v - lo) / (hi - lo || 1)) * ph;
    const g = el("g", { class: "chalk" });
    g.append(el("path", { d: chalkPath([[x0, top + ph], [x0 + pw, top + ph]], { seed: pi }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
    const pts = items.map((it, i) => [X(i), Y(p.get(it))]).filter((q) => !Number.isNaN(q[1]));
    g.append(el("path", { d: chalkPath(pts, { amp: 1, step: 10, seed: seedOf(p.label) }), stroke: p.color ?? HEX.home, "stroke-width": 5, fill: "none", "stroke-linejoin": "round" }));
    items.forEach((it, i) => {
      const v = p.get(it);
      if (v == null) return;
      g.append(el("circle", { cx: X(i), cy: Y(v), r: 6, fill: p.color ?? HEX.home }));
      const show = opts.labelEvery ? i % opts.labelEvery === 0 || i === items.length - 1 : true;
      const showValue = opts.values === "ends" ? i === 0 || i === items.length - 1 : show;
      if (showValue) svg.append(text(X(i), Y(v) - 14, p.fmt ? p.fmt(v) : ctx.num(v, 1), { "text-anchor": "middle", fill: p.color ?? HEX.home, "font-size": 16 }));
      if (show) svg.append(text(X(i), top + ph + 24, opts.xlabel(it), { "text-anchor": "middle", fill: HEX.gris, "font-size": 12 }));
    });
    svg.append(g);
    svg.append(text(x0, top - 20, p.label, { "font-family": TITRE, "font-size": 24, "font-weight": 600, fill: p.color ?? HEX.home, "letter-spacing": 1 }));
    if (p.sub) svg.append(text(x0, top - 2, p.sub, { fill: HEX.gris, "font-size": 12 }));
  });
}

// --- Enquête 2 · club et sélection ------------------------------------------------------------------

function same(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.club; const s = e.data.selection;
  frame(svg, t("fig_same_title"), t("fig_source_cs", { a: c.matches, b: s.matches }));
  const rows = [
    { label: t("cs_goals"), a: c.goals_per_match, b: s.goals_per_match, fmt: (v) => ctx.num(v, 2) },
    { label: t("cs_xg"), a: c.xg_per_match, b: s.xg_per_match, fmt: (v) => ctx.num(v, 2) },
    { label: t("cs_shots"), a: c.shots_per_match, b: s.shots_per_match, fmt: (v) => ctx.num(v, 1) },
    { label: t("cs_xg_shot"), a: c.shots.xg_per_shot, b: s.shots.xg_per_shot, fmt: (v) => ctx.num(v, 3) },
    { label: t("cs_dist"), a: c.shots.distance_m, b: s.shots.distance_m, fmt: (v) => `${ctx.num(v, 1)} m` },
    { label: t("cs_headers"), a: c.shots.header_pct, b: s.shots.header_pct, fmt: (v) => ctx.pct(v / 100) },
  ];
  compareRowsFig(svg, rows, t("cs_club"), t("cs_selection"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_same_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_same_caption");
}

function handbrake(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.club; const s = e.data.selection;
  frame(svg, t("fig_hb_title"), t("fig_source_cs", { a: c.matches, b: s.matches }));
  const rows = [
    { label: t("cs_losses"), sub: t("cs_losses_sub"), a: c.losses_per_team, b: s.losses_per_team, fmt: (v) => ctx.num(v, 1) },
    { label: t("cs_press"), sub: t("cs_press_sub"), a: c.press_per_min, b: s.press_per_min, fmt: (v) => ctx.num(v, 2) },
    { label: t("cs_cp"), sub: t("cs_cp_sub"), a: c.counterpress_pct, b: s.counterpress_pct, fmt: (v) => ctx.pct(v / 100) },
    { label: t("cs_tr"), sub: t("cs_tr_sub"), a: c.transition_goals_pct, b: s.transition_goals_pct, fmt: (v) => ctx.pct(v / 100) },
    { label: t("cs_short"), a: c.short_pass_pct, b: s.short_pass_pct, fmt: (v) => ctx.pct(v / 100) },
    { label: t("cs_gap"), sub: t("cs_gap_sub"), a: c.possession_gap, b: s.possession_gap, fmt: (v) => ctx.num(v, 1) },
  ];
  compareRowsFig(svg, rows, t("cs_club"), t("cs_selection"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_hb_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_hb_caption");
}

function deciders(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.club; const s = e.data.selection;
  frame(svg, t("fig_dec_title"), t("fig_source_cs", { a: c.matches, b: s.matches }));
  const keys = [["more_xg", t("more_xg")], ["more_possession", t("more_possession")], ["more_pressing", t("more_ppda")]];
  const x0 = 320; const x1 = W - 70; const X = (v) => x0 + ((x1 - x0) * v) / 70;
  const g = el("g", { class: "chalk" });
  for (const v of [25, 50]) { g.append(el("path", { d: `M${X(v)} 110V${110 + 3 * 160}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.18 })); svg.append(text(X(v), 100, `${v} %`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 14 })); }
  keys.forEach(([k, lab], i) => {
    const y = 130 + i * 160;
    svg.append(text(x0 - 20, y + 4, lab, { "text-anchor": "end", "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
    [[c[k], t("cs_club"), HEX.home], [s[k], t("cs_selection"), HEX.away]].forEach(([o, sub, col], j) => {
      const yy = y + 22 + j * 44;
      g.append(el("path", { d: chalkPath([[x0, yy + 12], [X(o.win_pct), yy + 12]], { amp: 0.8, step: 14, seed: seedOf(k + sub) }), stroke: col, "stroke-width": 26, fill: "none", opacity: 0.9 }));
      svg.append(text(X(o.win_pct) + 12, yy + 19, `${o.win_pct} %`, { fill: col, "font-size": 21, "font-weight": 600 }));
      svg.append(text(X(o.win_pct) + 82, yy + 19, t("dec_loss", { p: o.loss_pct }), { fill: HEX.gris, "font-size": 13 }));
      svg.append(text(x0 - 20, yy + 17, sub, { "text-anchor": "end", fill: HEX.gris, "font-size": 14 }));
    });
  });
  svg.append(g);
  svg.append(text(x0, H - 62, t("fig_dec_note"), { "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_dec_caption");
}

function tournaments(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_tour_title"), t("fig_source_tour"));
  const items = e.data.tournaments;
  panels(svg, items, [
    { label: t("p_losses"), sub: t("p_losses_sub"), get: (x) => x.losses_per_team, fmt: (v) => ctx.num(v, 0) },
    { label: t("p_goals"), sub: t("p_goals_sub"), get: (x) => x.goals_per_match, fmt: (v) => ctx.num(v, 2), color: HEX.craie },
    { label: t("p_draws"), sub: t("p_draws_sub"), get: (x) => x.draws_pct, fmt: (v) => `${v} %`, color: HEX.away },
    { label: t("p_ppda"), sub: t("p_ppda_sub"), get: (x) => x.ppda, fmt: (v) => ctx.num(v, 1), color: HEX.corail },
  ], ctx, { xlabel: (x) => t(`short_${x.comp}`), top: 150, height: 360, values: "ends" });
  svg.append(text(W - 60, H - 62, t("fig_tour_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_tour_caption");
}

// --- Enquête 3 · le temps --------------------------------------------------------------------------

function shotsFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_shots_title"), t("fig_source_barca"));
  const b = e.data.barca;
  panels(svg, b, [
    { label: t("p_outside"), sub: t("p_outside_barca"), get: (x) => x.barca.outside_box_pct, fmt: (v) => `${ctx.num(v, 0)} %` },
    { label: t("p_outside_opp"), sub: t("p_outside_opp_sub"), get: (x) => x.opponents.outside_box_pct, fmt: (v) => `${ctx.num(v, 0)} %`, color: HEX.away },
    { label: t("p_distance"), sub: t("p_distance_sub"), get: (x) => x.barca.shot_distance_m, fmt: (v) => `${ctx.num(v, 1)} m`, color: HEX.craie },
  ], ctx, { xlabel: (x) => x.season.slice(0, 4), labelEvery: 4, top: 150, height: 360 });
  svg.append(text(W - 60, H - 62, t("fig_shots_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_shots_caption");
}

function lossesFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_losses_title"), t("fig_source_barca_tour"));
  const b = e.data.barca; const T = e.data.tournaments;
  const left = 70; const pw = 520; const top = 150; const ph = 360;
  const draw = (items, x0, spec, xlabel, every) => {
    const vals = items.map(spec.get);
    const lo = Math.min(...vals) - 8; const hi = Math.max(...vals) + 8;
    const X = (i) => x0 + 24 + (i * (pw - 48)) / Math.max(1, items.length - 1);
    const Y = (v) => top + ph - ((v - lo) / (hi - lo)) * ph;
    const g = el("g", { class: "chalk" });
    g.append(el("path", { d: chalkPath([[x0, top + ph], [x0 + pw, top + ph]], { seed: 1 }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
    g.append(el("path", { d: chalkPath(items.map((it, i) => [X(i), Y(spec.get(it))]), { amp: 1, step: 10, seed: seedOf(spec.label) }), stroke: spec.color, "stroke-width": 5, fill: "none", "stroke-linejoin": "round" }));
    items.forEach((it, i) => {
      g.append(el("circle", { cx: X(i), cy: Y(spec.get(it)), r: 6, fill: spec.color }));
      if (i % every === 0 || i === items.length - 1) {
        svg.append(text(X(i), Y(spec.get(it)) - 14, ctx.num(spec.get(it), 1), { "text-anchor": "middle", fill: spec.color, "font-size": 16 }));
        svg.append(text(X(i), top + ph + 24, xlabel(it), { "text-anchor": "middle", fill: HEX.gris, "font-size": 12 }));
      }
    });
    svg.append(g);
    svg.append(text(x0, top - 20, spec.label, { "font-family": TITRE, "font-size": 24, "font-weight": 600, fill: spec.color, "letter-spacing": 1 }));
    svg.append(text(x0, top - 2, spec.sub, { fill: HEX.gris, "font-size": 12 }));
  };
  draw(b, left, { label: t("p_losses_barca"), sub: t("p_losses_barca_sub"), get: (x) => x.barca.losses, color: HEX.home }, (x) => x.season.slice(0, 4), 4);
  draw(T, left + pw + 40, { label: t("p_losses_tour"), sub: t("p_losses_sub"), get: (x) => x.losses_per_team, color: HEX.away }, (x) => t(`short_${x.comp}`), 1);
  svg.append(text(W - 60, H - 62, t("fig_losses_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_losses_caption");
}

function pressingFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_press_time_title"), t("fig_source_barca_tour"));
  const b = e.data.barca; const T = e.data.tournaments;
  panels(svg, b, [
    { label: t("p_ppda_barca"), sub: t("p_ppda_barca_sub"), get: (x) => x.barca.ppda, fmt: (v) => ctx.num(v, 1) },
    { label: t("p_cp_barca"), sub: t("p_cp_sub"), get: (x) => x.barca.counterpress_pct, fmt: (v) => `${ctx.num(v, 0)} %`, color: HEX.craie },
  ], ctx, { xlabel: (x) => x.season.slice(0, 4), labelEvery: 4, top: 150, height: 300 });
  // les tournois, en dessous : une petite table
  const y0 = H - 118;
  svg.append(text(70, y0, t("p_tour_line"), { "font-family": TITRE, "font-size": 22, "font-weight": 600, fill: HEX.away, "letter-spacing": 1 }));
  T.forEach((x, i) => {
    const cx = 70 + i * 200;
    svg.append(text(cx, y0 + 28, t(`short_${x.comp}`), { fill: HEX.gris, "font-size": 13 }));
    svg.append(text(cx, y0 + 50, `PPDA ${ctx.num(x.ppda, 1)} · CP ${ctx.num(x.counterpress_pct, 0)} %`, { fill: HEX.away, "font-size": 16 }));
  });
  svg.append(text(W - 60, y0 + 50, t("fig_press_time_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_press_time_caption");
}

function steady(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_steady_title"), t("fig_source_barca_tour"));
  const T = e.data.tournaments;
  panels(svg, T, [
    { label: t("p_xg_shot"), sub: t("p_xg_shot_sub"), get: (x) => x.shots.xg_per_shot, fmt: (v) => ctx.num(v, 3), min: 0, max: 0.16 },
    { label: t("p_goals"), sub: t("p_goals_sub"), get: (x) => x.goals_per_match, fmt: (v) => ctx.num(v, 2), color: HEX.craie, min: 0, max: 3.5 },
    { label: t("p_draws"), sub: t("p_draws_sub"), get: (x) => x.draws_pct, fmt: (v) => `${v} %`, color: HEX.away, min: 0, max: 40 },
  ], ctx, { xlabel: (x) => t(`short_${x.comp}`), top: 150, height: 360 });
  svg.append(text(W - 60, H - 62, t("fig_steady_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_steady_caption");
}

const FIGURES = { outcomes, champions, quartiles, cases, favourite, time, same, handbrake, deciders, tournaments, shots: shotsFig, losses: lossesFig, pressing: pressingFig, steady };

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

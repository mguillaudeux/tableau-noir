// Les enquêtes : une question, une réponse chiffrée, trois ou quatre figures qu'on peut emporter.

import { HEX, el, drawPitch } from "./draw.js";
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
          ${c.figure ? `<figure class="fig-card" data-fig="${c.figure}" data-i="${i}">
            <figcaption><span></span><button type="button" class="dl">${esc(t("fig_download"))}</button></figcaption>
            <svg class="chart"></svg>
          </figure>` : ""}
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
  svg.append(text(50, H - 28, source, { fill: HEX.gris, "font-size": 12 }));
  svg.append(text(W - 50, H - 28, "TABLEAU NOIR", { fill: HEX.gris, "font-size": 14, "text-anchor": "end", "font-family": TITRE, "font-weight": 600, "letter-spacing": 3 }));
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
function compareRowsFig(svg, rows, left, right, ctx, { lx = 300, colW = 380 } = {}) { const gap = 90; const y0 = 125; const rowH = Math.min(78, (H - 210) / rows.length);
  const cols = [[lx, HEX.home, left, "a"], [lx + colW + gap, HEX.away, right, "b"]];
  const g = el("g", { class: "chalk" });
  for (const [x, col, title] of cols) svg.append(text(x, 100, title, { fill: col, "font-family": TITRE, "font-size": 22, "font-weight": 600, "letter-spacing": 1 }));
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + 20;
    const max = Math.max(r.a ?? 0, r.b ?? 0) || 1;
    for (const [x, col, , k] of cols) {
      if (r[k] == null) { svg.append(text(x, y + 7, "–", { fill: HEX.gris, "font-size": 20 })); continue; }
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


// --- Enquête 4 · la possession ------------------------------------------------------------------------

function bandsFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_bands_title"), t("fig_source_cs", { a: e.data.clubs_matches, b: e.data.selections_matches }));
  const sets = [["bands_club", t("cs_club"), HEX.home], ["bands_selection", t("cs_selection"), HEX.away]];
  const left = 90; const pw = 480; const top = 150; const ph = 330;
  sets.forEach(([key, title, col], si) => {
    const x0 = left + si * (pw + 70);
    const b = e.data[key];
    const X = (i) => x0 + 30 + (i * (pw - 60)) / 5;
    const Y = (v) => top + ph - ((v - 20) / 40) * ph;
    const g = el("g", { class: "chalk" });
    g.append(el("path", { d: chalkPath([[x0, top + ph], [x0 + pw, top + ph]], { seed: si }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
    g.append(el("path", { d: chalkPath([[x0, Y(50)], [x0 + pw, Y(50)]], { seed: 9 }), stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "5 7", fill: "none", opacity: 0.6 }));
    for (const [k, colr, dash] of [["win_pct", col, null], ["loss_pct", HEX.corail, "6 6"]]) {
      g.append(el("path", { d: chalkPath(b.map((r, i) => [X(i), Y(r[k])]), { amp: 1, step: 10, seed: seedOf(key + k) }), stroke: colr, "stroke-width": 5, fill: "none", "stroke-linejoin": "round", "stroke-dasharray": dash }));
      b.forEach((r, i) => {
        g.append(el("circle", { cx: X(i), cy: Y(r[k]), r: 6, fill: colr }));
        svg.append(text(X(i), Y(r[k]) + (k === "win_pct" ? -14 : 24), `${r[k]} %`, { "text-anchor": "middle", fill: colr, "font-size": 15 }));
      });
    }
    b.forEach((r, i) => svg.append(text(X(i), top + ph + 24, `${r.band} %`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 })));
    svg.append(g);
    svg.append(text(x0, top - 24, title, { "font-family": TITRE, "font-size": 26, "font-weight": 600, fill: col, "letter-spacing": 1 }));
    svg.append(text(x0 + pw, top - 24, `${t("o_win")} ●  ${t("o_loss")} ◌`, { "text-anchor": "end", fill: HEX.gris, "font-size": 14 }));
    svg.append(text(x0, top + ph + 48, t("bands_axis"), { fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(text(W - 60, H - 62, t("fig_bands_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_bands_caption");
}

function equalFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_equal_title"), t("fig_source_leagues", { n: e.data.clubs_matches }));
  const rows = [["favourite", t("fav_favourite")], ["equal_strength", t("fav_equal")], ["outsider", t("fav_outsider")]];
  const x0 = 360; const x1 = W - 70; const X = (v) => x0 + ((x1 - x0) * v) / 70;
  const g = el("g", { class: "chalk" });
  for (const v of [25, 50]) { g.append(el("path", { d: `M${X(v)} 110V${110 + 3 * 150}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.18 })); svg.append(text(X(v), 100, `${v} %`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 14 })); }
  rows.forEach(([k, lab], i) => {
    const o = e.data[k];
    const y = 130 + i * 150;
    svg.append(text(x0 - 20, y + 4, lab, { "text-anchor": "end", "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
    svg.append(text(x0 - 20, y + 26, t("outcome_n", { n: o.n }), { "text-anchor": "end", fill: HEX.gris, "font-size": 13 }));
    [["win_pct", t("o_win"), HEX.home], ["loss_pct", t("o_loss"), HEX.corail]].forEach(([kk, sub, col], j) => {
      const yy = y + 22 + j * 44;
      g.append(el("path", { d: chalkPath([[x0, yy + 12], [X(o[kk]), yy + 12]], { amp: 0.8, step: 14, seed: seedOf(k + kk) }), stroke: col, "stroke-width": 26, fill: "none", opacity: 0.9 }));
      svg.append(text(X(o[kk]) + 12, yy + 19, `${sub} ${o[kk]} %`, { fill: col, "font-size": 20, "font-weight": 600 }));
    });
  });
  svg.append(g);
  svg.append(text(x0, H - 62, t("fig_equal_note"), { "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_equal_caption");
}

function bycompFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_bycomp_title"), t("fig_source_cs", { a: e.data.clubs_matches, b: e.data.selections_matches }));
  const rows = e.data.by_competition;
  const x0 = 360; const x1 = W - 80; const y0 = 105; const rowH = 46;
  const X = (v) => x0 + ((x1 - x0) * (v - 10)) / 60;
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: `M${X(50)} ${y0 - 10}V${y0 + rows.length * rowH}`, stroke: HEX.gris, "stroke-width": 1, "stroke-dasharray": "5 7", opacity: 0.6 }));
  svg.append(text(X(50), y0 - 16, "50 %", { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + 16;
    const isClub = r.comp.includes("2015");
    g.append(el("path", { d: chalkPath([[X(r.loss_pct), y], [X(r.win_pct), y]], { amp: 0.5, step: 16, seed: seedOf(r.comp) }), stroke: HEX.craie, "stroke-width": 2, fill: "none", opacity: 0.35 }));
    g.append(el("circle", { cx: X(r.loss_pct), cy: y, r: 9, fill: HEX.corail, opacity: 0.9 }));
    g.append(el("circle", { cx: X(r.win_pct), cy: y, r: 9, fill: isClub ? HEX.home : HEX.away }));
    svg.append(text(X(r.win_pct) + (r.win_pct >= r.loss_pct ? 16 : -16), y + 5, `${r.win_pct} %`, { "text-anchor": r.win_pct >= r.loss_pct ? "start" : "end", fill: isClub ? HEX.home : HEX.away, "font-size": 15 }));
    svg.append(text(x0 - 20, y + 5, r.label.replace("Coupe du monde", "CM"), { "text-anchor": "end", "font-size": 16, fill: isClub ? HEX.home : HEX.away }));
  });
  svg.append(g);
  svg.append(el("circle", { cx: x0, cy: H - 70, r: 7, fill: HEX.corail }));
  svg.append(text(x0 + 14, H - 65, t("bycomp_legend"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(W - 60, H - 65, t("fig_bycomp_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 24, fill: HEX.home }));
  return t("fig_bycomp_caption");
}

// --- Enquête 5 · le but le plus cher jamais raté --------------------------------------------------

/** Les occasions décisives manquées en phase finale : une barre par tir, longueur = xG. */
function missesFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_misses_title"), t("fig_source_misses", { n: e.data.n_decisive_tournaments }));
  const rows = e.data.top_tournaments.slice(0, 8);
  const x0 = 560; const x1 = W - 170; const y0 = 115; const rowH = 62;
  const X = (v) => x0 + ((x1 - x0) * v) / 0.7;
  const g = el("g", { class: "chalk" });
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + 18;
    g.append(el("path", { d: chalkPath([[x0, y], [X(r.xg), y]], { amp: 0.7, step: 14, seed: seedOf(r.match_id + r.minute) }), stroke: r.on_target ? HEX.home : HEX.corail, "stroke-width": 22, fill: "none", opacity: 0.9 }));
    svg.append(text(X(r.xg) + 10, y + 7, `${ctx.num(r.xg, 2)} xG`, { fill: r.on_target ? HEX.home : HEX.corail, "font-size": 19, "font-weight": 600 }));
    svg.append(text(x0 - 16, y - 4, `${r.player} · ${r.minute}'`, { "text-anchor": "end", "font-family": TITRE, "font-size": 23, "font-weight": 600, "letter-spacing": 1 }));
    svg.append(text(x0 - 16, y + 17, `${ctx.team(r.team)} – ${ctx.team(r.opponent)}, ${t(`comp_${r.comp}`)} · ${t("score_then", { s: r.score.replace("-", "–"), f: r.final.replace("-", "–") })}`, { "text-anchor": "end", fill: HEX.gris, "font-size": 12 }));
  });
  svg.append(g);
  [[HEX.corail, t("miss_off")], [HEX.home, t("miss_on")]].forEach(([c, lab], i) => {
    svg.append(el("rect", { x: x0 + i * 230, y: 86, width: 14, height: 14, fill: c }));
    svg.append(text(x0 + i * 230 + 22, 98, lab, { fill: HEX.gris, "font-size": 14 }));
  });
  svg.append(text(x1, H - 62, t("fig_misses_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_misses_caption");
}

function conversionFig(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.conversion.club; const s = e.data.conversion.selection;
  frame(svg, t("fig_conversion_title"), t("fig_source_conv", { a: c.shots, b: s.shots }));
  compareRowsFig(svg, [
    { label: t("cv_goals_xg"), sub: t("cv_goals_xg_sub"), a: c.goals_per_xg, b: s.goals_per_xg, fmt: (v) => ctx.num(v, 2) },
    { label: t("cv_big"), sub: t("cv_big_sub", { a: c.big_chances, b: s.big_chances }), a: c.big_chance_pct, b: s.big_chance_pct, fmt: (v) => `${v} %` },
    { label: t("cv_pen"), sub: t("cv_pen_sub", { a: c.penalties, b: s.penalties }), a: c.penalty_pct, b: s.penalty_pct, fmt: (v) => `${v} %` },
    { label: t("cv_big_xg"), sub: t("cv_big_xg_sub"), a: c.big_chance_xg, b: s.big_chance_xg, fmt: (v) => ctx.num(v, 2) },
    { label: t("cv_ko"), sub: t("cv_ko_sub", { n: e.data.conversion.selection_knockout.big_chances }), a: null, b: e.data.conversion.selection_knockout.big_chance_pct, fmt: (v) => `${v} %` },
  ], t("cv_club"), t("cv_selection"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_conversion_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_conversion_caption");
}

function erasFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_eras_title"), t("fig_source_eras"));
  panels(svg, e.data.eras, [
    { label: t("er_big"), sub: t("er_big_sub"), get: (x) => x.big_chance_pct, fmt: (v) => `${v} %`, min: 35, max: 62 },
    { label: t("er_goals_xg"), sub: t("er_goals_xg_sub"), get: (x) => x.goals_per_xg, fmt: (v) => ctx.num(v, 2), min: 0.75, max: 1.2, color: HEX.craie },
    { label: t("er_pen"), sub: t("er_pen_sub"), get: (x) => x.penalty_pct, fmt: (v) => `${v} %`, min: 55, max: 90, color: HEX.away },
  ], ctx, { xlabel: (x) => x.era, top: 150, height: 340 });
  svg.append(text(W - 60, H - 62, t("fig_eras_note", { b: e.data.barca_big_chance_pct }), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_eras_caption");
}

/** Les finales où le perdant avait plus d'xG : une paire de points par finale. */
function finalsFig(svg, e, ctx) {
  const { t } = ctx;
  const f = e.data.finals;
  frame(svg, t("fig_finals_title", { k: f.xg_lied, n: f.n }), t("fig_source_finals", { n: f.n }));
  const x0 = 440; const x1 = W - 90; const y0 = 170; const rowH = 135;
  const X = (v) => x0 + ((x1 - x0) * v) / 3.6;
  const g = el("g", { class: "chalk" });
  f.rows.forEach((r, i) => {
    const y = y0 + i * rowH;
    g.append(el("path", { d: chalkPath([[X(r.xg_winner), y], [X(r.xg_loser), y]], { amp: 0.6, step: 16, seed: seedOf(r.match_id) }), stroke: HEX.craie, "stroke-width": 2, fill: "none", opacity: 0.35, "stroke-dasharray": "4 6" }));
    g.append(el("circle", { cx: X(r.xg_loser), cy: y, r: 12, fill: HEX.away, opacity: 0.9 }));
    g.append(el("circle", { cx: X(r.xg_winner), cy: y, r: 12, fill: HEX.home }));
    svg.append(text(X(r.xg_loser), y - 20, ctx.num(r.xg_loser, 2), { "text-anchor": "middle", fill: HEX.away, "font-size": 17 }));
    svg.append(text(X(r.xg_winner), y - 20, ctx.num(r.xg_winner, 2), { "text-anchor": "middle", fill: HEX.home, "font-size": 17 }));
    svg.append(text(x0 - 24, y - 6, `${ctx.team(r.winner)} ${r.score.replace("-", "–")} ${ctx.team(r.loser)}${r.penalties ? ` (${t("tab")})` : ""}`, { "text-anchor": "end", "font-family": TITRE, "font-size": 26, "font-weight": 600, "letter-spacing": 1 }));
    svg.append(text(x0 - 24, y + 18, t(`comp_${r.comp}`), { "text-anchor": "end", fill: HEX.gris, "font-size": 14 }));
  });
  svg.append(g);
  for (const v of [0, 1, 2, 3]) svg.append(text(X(v), y0 + f.rows.length * rowH - 40, `${v} xG`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 14 }));
  svg.append(el("circle", { cx: x0, cy: 108, r: 7, fill: HEX.home }));
  svg.append(text(x0 + 14, 113, t("legend_winner"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(el("circle", { cx: x0 + 220, cy: 108, r: 7, fill: HEX.away }));
  svg.append(text(x0 + 234, 113, t("legend_loser"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(W - 60, H - 62, t("fig_finals_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_finals_caption");
}

// --- Enquête 6 · formations mensongères ------------------------------------------------------------

/** Ce que devient chaque schéma annoncé, avec le ballon : trois barres par schéma. */
// --- Enquête 6 · la défense à trois, et les formations qui mentent ----------------------------------

const pctFmt = (ctx) => (v) => `${ctx.num(v, v < 10 ? 1 : 0)} %`;
const compBar = (ctx, c, value, extra = {}) => ({ label: ctx.t(`comp_short_${c.comp}`), sub: seasonOf(ctx.t(`comp_label_${c.comp}`)), value, ...extra });
const seasonOf = (label) => (label.match(/\d{4}(\/\d{2})?/) ?? [""])[0];

function backThreeFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  const comp = (c) => d.by_comp.find((x) => x.comp === c);
  frame(svg, t("fig_backthree_title"), t("fig_source_shapes", { n: ctx.num(d.teams, 0) }));
  groupedBars(svg, [
    { label: t("bt_barca"), color: HEX.home, items: d.barca.map((x) => ({ label: x.era, value: x.opp.back_three_pct })) },
    { label: t("bt_leagues"), color: HEX.craie, items: ["pl-2015", "liga-2015", "seriea-2015", "ligue1-2015"].map((c) => compBar(ctx, comp(c), comp(c).back_three_pct)) },
    { label: t("bt_elite"), color: HEX.corail, items: ["bundesliga-2015", "bundesliga-2023", "ligue1-2021", "ligue1-2022"].map((c) => compBar(ctx, comp(c), comp(c).back_three_pct, { dim: c.endsWith("2015"), label: c.startsWith("bundes") ? "Lev." : "PSG" })) },
    { label: t("bt_sel"), color: HEX.away, items: ["wc-2018", "euro-2020", "wc-2022", "euro-2024"].map((c) => compBar(ctx, comp(c), comp(c).back_three_pct)) },
  ], null, ctx, { max: 85, fmt: pctFmt(ctx), top: 170, height: 330 });
  svg.append(text(W - 60, H - 62, t("fig_backthree_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_backthree_caption");
}

function topShapesFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_topshapes_title"), t("fig_source_shapes", { n: ctx.num(d.leagues_2015.n + d.tournaments.n, 0) }));
  const rows = d.shapes_compare.map((x) => ({ label: x.shape, sub: t("ts_sub"), a: x.leagues_pct, b: x.tournaments_pct, fmt: (v) => `${ctx.num(v, 1)} %` }));
  compareRowsFig(svg, rows, t("ts_leagues"), t("ts_tournaments"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_topshapes_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_topshapes_caption");
}

/** Trois petits terrains : la défense « médiane », symétrique, bancale, à trois. */
function lopsidedFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_lopsided_title"), t("fig_source_lines", { n: ctx.num(d.four.n + d.three.n, 0) }));
  const k = 3.3; const top = 190; const pw = 105 * k; const gap = (W - 120 - 3 * pw) / 2;
  const cases = [
    [d.shape_level, t("ls_level"), t("ls_level_sub"), HEX.home],
    [d.shape_lopsided, t("ls_lop"), t("ls_lop_sub", { p: ctx.num(d.four.lopsided_pct, 1) }), HEX.corail],
    [d.shape_three, t("ls_three"), t("ls_three_sub", { n: ctx.num(d.three.n, 0) }), HEX.away],
  ];
  cases.forEach(([pts, title, sub, col], i) => {
    const ox = 60 + i * (pw + gap);
    const g = el("g", { class: "chalk" });
    drawPitch(g, k, ox, top, 11 + i);
    svg.append(g);
    const P = (p) => [ox + p.x * k, top + p.y * k];
    const line = el("g", { class: "chalk" });
    line.append(el("path", { d: chalkPath(pts.map(P), { amp: 0.8, step: 10, seed: 40 + i }), stroke: col, "stroke-width": 3, fill: "none", opacity: 0.8 }));
    svg.append(line);
    pts.forEach((p) => {
      const [x, y] = P(p);
      svg.append(el("circle", { cx: x, cy: y, r: 9, fill: col, stroke: "#1c2421", "stroke-width": 2 }));
      svg.append(text(x + 14, y + 5, `${ctx.num(p.x, 0)} m`, { "text-anchor": "start", "font-size": 13, fill: HEX.craie, "paint-order": "stroke", stroke: "#1c2421", "stroke-width": 4 }));
    });
    svg.append(text(ox, top - 38, title, { "font-family": TITRE, "font-size": 24, "font-weight": 600, fill: col, "letter-spacing": 1 }));
    svg.append(text(ox, top - 16, sub, { fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(text(60, top + 68 * k + 26, t("ls_goal"), { fill: HEX.gris, "font-size": 13 }));
  svg.append(text(W - 60, H - 62, t("fig_lopsided_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_lopsided_caption");
}

function lopsideTimeFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  const comp = (c) => d.four_by_comp.find((x) => x.comp === c);
  frame(svg, t("fig_lopsidetime_title"), t("fig_source_lines", { n: ctx.num(d.four.n, 0) }));
  groupedBars(svg, [
    { label: t("lt2_barca"), color: HEX.home, items: d.four_barca.map((x) => ({ label: x.era, value: x.barca.lopsided_pct })) },
    { label: t("lt2_opp"), color: HEX.craie, items: d.four_barca.map((x) => ({ label: x.era, value: x.opp.lopsided_pct })) },
    { label: t("lt2_leagues"), color: HEX.corail, items: ["pl-2015", "liga-2015", "seriea-2015", "ligue1-2015"].map((c) => compBar(ctx, comp(c), comp(c).lopsided_pct)) },
    { label: t("lt2_sel"), color: HEX.away, items: ["wc-2018", "euro-2020", "wc-2022", "euro-2024"].map((c) => compBar(ctx, comp(c), comp(c).lopsided_pct)) },
  ], { value: d.four.lopsided_pct, label: t("lt2_ref", { v: ctx.num(d.four.lopsided_pct, 1) }) }, ctx, { max: 42, fmt: pctFmt(ctx), top: 170, height: 320 });
  svg.append(text(W - 60, H - 62, t("fig_lopsidetime_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_lopsidetime_caption");
}

// --- Enquête 7 · où meurent les attaques ------------------------------------------------------------

/** Six bandes de terrain : part des pertes, et coût de chaque perte. */
function bandsLossFig(svg, e, ctx) {
  const { t } = ctx;
  const b = e.data.overall.bands;
  frame(svg, t("fig_bandsloss_title"), t("fig_source_losses", { n: e.data.overall.matches }));
  const left = 90; const pw = 1020; const top = 140; const ph = 180;
  const draw = (key, yTop, color, label, fmt, max) => {
    const g = el("g", { class: "chalk" });
    const bw = pw / 6;
    b.forEach((r, i) => {
      const x = left + i * bw;
      const h = (r[key] / max) * ph;
      g.append(el("path", { d: chalkPath([[x + bw / 2, yTop + ph], [x + bw / 2, yTop + ph - h]], { amp: 0.8, step: 12, seed: seedOf(key + i) }), stroke: color, "stroke-width": bw * 0.55, fill: "none", opacity: 0.85 }));
      svg.append(text(x + bw / 2, yTop + ph - h - 10, fmt(r[key]), { "text-anchor": "middle", fill: color, "font-size": 18, "font-weight": 600 }));
      if (key === "xg_per_100") svg.append(text(x + bw / 2, yTop + ph + 24, r.label, { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
    });
    g.append(el("path", { d: chalkPath([[left, yTop + ph], [left + pw, yTop + ph]], { seed: 2 }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
    svg.append(g);
    svg.append(text(left, yTop - 10, label, { "font-family": TITRE, "font-size": 24, "font-weight": 600, fill: color, "letter-spacing": 1 }));
  };
  draw("share_pct", top, HEX.craie, t("bl_share"), (v) => `${ctx.num(v, 0)} %`, 40);
  draw("xg_per_100", top + ph + 70, HEX.corail, t("bl_cost"), (v) => ctx.num(v, 2), Math.max(...b.map((r) => r.xg_per_100)) * 1.15);
  svg.append(text(left, H - 52, t("bl_axis"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(text(W - 60, 104, t("fig_bandsloss_note", { r: ctx.num(e.data.cost_ratio_band1_band4, 1) }), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_bandsloss_caption");
}

function lossKindFig(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.by_kind.club; const s = e.data.by_kind.selection;
  frame(svg, t("fig_losskind_title"), t("fig_source_losskind", { a: c.matches, b: s.matches }));
  const rows = [
    { label: t("lk_losses"), sub: t("lk_losses_sub"), a: c.losses_per_team, b: s.losses_per_team, fmt: (v) => ctx.num(v, 1) },
    { label: t("lk_own_half"), sub: t("lk_own_half_sub"), a: c.own_half_pct, b: s.own_half_pct, fmt: (v) => `${ctx.num(v, 0)} %` },
    { label: t("lk_cost1"), sub: t("lk_cost1_sub"), a: c.bands[1].xg_per_100, b: s.bands[1].xg_per_100, fmt: (v) => ctx.num(v, 2) },
    { label: t("lk_cost4"), sub: t("lk_cost4_sub"), a: c.bands[4].xg_per_100, b: s.bands[4].xg_per_100, fmt: (v) => ctx.num(v, 2) },
    { label: t("lk_regain"), sub: t("lk_regain_sub"), a: c.bands[4].regained_5s_pct, b: s.bands[4].regained_5s_pct, fmt: (v) => `${ctx.num(v, 0)} %` },
  ];
  compareRowsFig(svg, rows, t("cv_club"), t("cv_selection"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_losskind_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_losskind_caption");
}

function lossTimeFig(svg, e, ctx) {
  const { t } = ctx;
  frame(svg, t("fig_losstime_title"), t("fig_source_barca"));
  panels(svg, e.data.barca_years, [
    { label: t("lt_losses"), sub: t("lt_losses_sub"), get: (x) => x.losses_per_team, fmt: (v) => ctx.num(v, 0) },
    { label: t("lt_own_half"), sub: t("lt_own_half_sub"), get: (x) => x.own_half_pct, fmt: (v) => `${ctx.num(v, 0)} %`, color: HEX.away },
  ], ctx, { xlabel: (x) => String(x.year), labelEvery: 4, top: 150, height: 340 });
  const er = e.data.eras;
  if (er.length) svg.append(text(70, H - 70, t("lt_eras", { a: ctx.num(er[0].own_half_pct, 1), b: ctx.num(er[er.length - 1].own_half_pct, 1) }), { "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_losstime_caption");
}

/** Barres groupées : plusieurs fils de comparaison côte à côte, avec une ligne de référence. */
function groupedBars(svg, groups, ref, ctx, { max, fmt, top = 150, height = 330 }) {
  const left = 70; const right = W - 50; const gap = 50;
  const n = groups.reduce((a, g) => a + g.items.length, 0);
  const bw = (right - left - gap * (groups.length - 1)) / n;
  const Y = (v) => top + height - (v / max) * height;
  let x = left;
  const g = el("g", { class: "chalk" });
  groups.forEach((grp, gi) => {
    const x0 = x;
    grp.items.forEach((it, i) => {
      const cx = x + bw / 2;
      g.append(el("path", { d: chalkPath([[cx, top + height], [cx, Y(it.value)]], { amp: 0.7, step: 12, seed: seedOf(grp.label + i) }), stroke: it.color ?? grp.color, "stroke-width": bw * 0.58, fill: "none", opacity: it.dim ? 0.45 : 0.9 }));
      svg.append(text(cx, Y(it.value) - 10, fmt(it.value), { "text-anchor": "middle", fill: it.color ?? grp.color, "font-size": bw < 72 ? 15 : 18, "font-weight": 600 }));
      svg.append(text(cx, top + height + 22, it.label, { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
      if (it.sub) svg.append(text(cx, top + height + 40, it.sub, { "text-anchor": "middle", fill: HEX.gris, "font-size": 11 }));
      x += bw;
    });
    svg.append(text(x0, top - 22, grp.label, { "font-family": TITRE, "font-size": 22, "font-weight": 600, fill: grp.color, "letter-spacing": 1 }));
    x += gap;
  });
  g.append(el("path", { d: chalkPath([[left, top + height], [right, top + height]], { seed: 3 }), stroke: HEX.craie, "stroke-width": 1.4, fill: "none", opacity: 0.6 }));
  if (ref) {
    g.append(el("path", { d: `M${left} ${Y(ref.value)}H${right}`, stroke: HEX.craie, "stroke-width": 1.2, "stroke-dasharray": "6 6", opacity: 0.5 }));
    // la légende de la ligne, sous le titre (jamais sur les barres)
    svg.append(el("path", { d: `M60 ${H - 62}H100`, stroke: HEX.craie, "stroke-width": 1.2, "stroke-dasharray": "6 6", opacity: 0.7 }));
    svg.append(text(110, H - 57, ref.label, { fill: HEX.gris, "font-size": 14 }));
  }
  svg.append(g);
}

/** Le coût d'une perte dans ses 17–35 m : chez les adversaires du Barça, en club, en sélection. */
function costTimeFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_costtime_title"), t("fig_source_costtime"));
  const short = (label) => label.replace("Coupe du monde", t("short_wc")).replace("Copa América", "Copa").replace("Bundesliga", "Bundes.");
  const clubs = d.clubs_then_now.map((c) => ({ label: short(c.label.split(" ").slice(0, -1).join(" ")), sub: c.label.split(" ").slice(-1)[0], value: c.xg_per_100, dim: c.label.endsWith("2015/16") }));
  const groups = [
    { label: t("ct_barca"), color: HEX.home, items: d.barca_opp.map((x) => ({ label: x.era, value: x.opp_xg_per_100 })) },
    { label: t("ct_clubs"), color: HEX.corail, items: clubs },
    { label: t("ct_sel"), color: HEX.away, items: d.selections.slice(0, 4).map((c) => ({ label: short(c.label.split(" ").slice(0, -1).join(" ")), sub: c.label.split(" ").slice(-1)[0], value: c.xg_per_100 })) },
  ];
  const max = Math.max(...groups.flatMap((g) => g.items.map((i) => i.value))) * 1.18;
  groupedBars(svg, groups, { value: d.leagues_2015.xg_per_100, label: t("ct_ref", { v: ctx.num(d.leagues_2015.xg_per_100, 2) }) }, ctx, { max, fmt: (v) => ctx.num(v, 2) });
  svg.append(text(W - 50, H - 62, t("fig_costtime_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_costtime_caption");
}

/** Fig. hold-up 1 — selon l'écart d'xG, le résultat de l'équipe qui en a le moins. */
function gapFig(svg, e, ctx) {
  const { t } = ctx;
  const bins = e.data.bins;
  frame(svg, t("fig_gap_title"), t("fig_source_holdups", { n: e.data.matches }));
  const x0 = 300; const x1 = W - 60; const y0 = 130; const rowH = 76;
  const g = el("g", { class: "chalk" });
  bins.forEach((r, i) => {
    const y = y0 + i * rowH;
    let x = x0;
    for (const [k, col] of [["win_pct", HEX.home], ["draw_pct", HEX.gris], ["loss_pct", HEX.away]]) {
      const ww = ((x1 - x0) * r[k]) / 100;
      g.append(el("path", { d: chalkPath([[x, y + 22], [x + ww, y + 22]], { amp: 0.8, step: 14, seed: seedOf(k + i) }), stroke: col, "stroke-width": 30, fill: "none", opacity: k === "draw_pct" ? 0.45 : 0.9, "stroke-linecap": "butt" }));
      if (ww > 56) svg.append(text(x + ww / 2, y + 29, `${ctx.num(r[k], 0)} %`, { "text-anchor": "middle", fill: HEX.craie, "font-size": 19, "font-weight": 600, "paint-order": "stroke", stroke: "#1c2421", "stroke-width": 5 }));
      x += ww;
    }
    const lab = r.hi == null ? t("gap_more", { a: ctx.num(r.lo, 1) }) : t("gap_range", { a: ctx.num(r.lo, 2), b: ctx.num(r.hi, 2) });
    svg.append(text(x0 - 18, y + 20, lab, { "text-anchor": "end", "font-family": TITRE, "font-size": 22, "font-weight": 600 }));
    svg.append(text(x0 - 18, y + 42, t("outcome_n", { n: r.n }), { "text-anchor": "end", fill: HEX.gris, "font-size": 13 }));
  });
  svg.append(g);
  [["win", t("o_win"), HEX.home], ["draw", t("o_draw"), HEX.gris], ["loss", t("o_loss"), HEX.away]].forEach(([, lab, col], i) => {
    svg.append(el("rect", { x: x0 + i * 170, y: 92, width: 16, height: 16, fill: col, opacity: 0.9 }));
    svg.append(text(x0 + i * 170 + 24, 106, lab, { fill: HEX.gris, "font-size": 15 }));
  });
  svg.append(text(60, 106, t("gap_axis"), { fill: HEX.gris, "font-size": 15 }));
  return t("fig_gap_caption");
}

/** Fig. hold-up 2 — compétition par compétition, la part des hold-up. */
function holdCompFig(svg, e, ctx) {
  const { t } = ctx;
  const rows = e.data.by_comp;
  frame(svg, t("fig_holdcomp_title"), t("fig_source_holdups", { n: e.data.matches }));
  const x0 = 360; const x1 = W - 90; const y0 = 110; const rowH = (H - 190) / rows.length;
  const max = 35;
  const X = (v) => x0 + ((x1 - x0) * v) / max;
  const g = el("g", { class: "chalk" });
  for (const v of [0, 10, 20, 30]) {
    g.append(el("path", { d: `M${X(v)} ${y0 - 10}V${y0 + rows.length * rowH}`, stroke: HEX.craie, "stroke-width": 0.6, opacity: 0.15 }));
    svg.append(text(X(v), y0 + rows.length * rowH + 20, `${v} %`, { "text-anchor": "middle", fill: HEX.gris, "font-size": 13 }));
  }
  rows.forEach((r, i) => {
    const y = y0 + i * rowH + rowH / 2;
    const col = r.kind === "selection" ? HEX.away : HEX.home;
    g.append(el("path", { d: chalkPath([[x0, y], [X(r.win_pct), y]], { amp: 0.5, step: 14, seed: seedOf(r.comp) }), stroke: col, "stroke-width": Math.min(18, rowH * 0.6), fill: "none", opacity: 0.85 }));
    svg.append(text(X(r.win_pct) + 10, y + 6, `${ctx.num(r.win_pct, 1)} %`, { fill: col, "font-size": 15 }));
    svg.append(text(x0 - 14, y + 5, t(`comp_label_${r.comp}`) || r.label, { "text-anchor": "end", "font-size": 15, fill: HEX.craie }));
  });
  svg.append(g);
  svg.append(el("rect", { x: x0, y: 84, width: 14, height: 14, fill: HEX.home }));
  svg.append(text(x0 + 22, 96, t("cv_club"), { fill: HEX.gris, "font-size": 14 }));
  svg.append(el("rect", { x: x0 + 120, y: 84, width: 14, height: 14, fill: HEX.away }));
  svg.append(text(x0 + 142, 96, t("cv_selection"), { fill: HEX.gris, "font-size": 14 }));
  return t("fig_holdcomp_caption");
}

/** Fig. hold-up 3 — les dix plus gros hold-up du corpus. */
function heistsFig(svg, e, ctx) {
  const { t } = ctx;
  const rows = e.data.heists.slice(0, 8);
  frame(svg, t("fig_heists_title"), t("fig_source_holdups", { n: e.data.matches }));
  const y0 = 120; const rowH = 62; const xb = 760; const max = Math.max(...rows.map((r) => r.gap));
  const g = el("g", { class: "chalk" });
  rows.forEach((r, i) => {
    const y = y0 + i * rowH;
    svg.append(text(60, y + 14, `${ctx.team(r.team)} ${r.goals}–${r.goals_against} ${ctx.team(r.opponent)}${r.penalties ? ` (${t("tab")})` : ""}`, { "font-family": TITRE, "font-size": 24, "font-weight": 600, "letter-spacing": 1, fill: i === 0 ? HEX.home : HEX.craie }));
    svg.append(text(60, y + 36, `${t(`comp_label_${r.comp}`) || r.label} · ${ctx.stageName(r.stage)}`, { fill: HEX.gris, "font-size": 13 }));
    g.append(el("path", { d: chalkPath([[xb, y + 12], [xb + (360 * r.gap) / max, y + 12]], { amp: 0.6, step: 14, seed: seedOf(r.match_id) }), stroke: HEX.corail, "stroke-width": 16, fill: "none", opacity: 0.85 }));
    svg.append(text(xb - 14, y + 18, `${ctx.num(r.xg, 2)} – ${ctx.num(r.xg_against, 2)}`, { "text-anchor": "end", fill: HEX.gris, "font-size": 15 }));
    svg.append(text(xb + (360 * r.gap) / max + 10, y + 18, `−${ctx.num(r.gap, 2)}`, { fill: HEX.corail, "font-size": 16 }));
  });
  svg.append(g);
  svg.append(text(xb - 14, 96, t("heists_xg"), { "text-anchor": "end", fill: HEX.gris, "font-size": 13 }));
  svg.append(text(xb, 96, t("heists_gap"), { fill: HEX.gris, "font-size": 13 }));
  return t("fig_heists_caption");
}


/** Fig. hold-up 4 — le temps : le Barça par période, les tournois, les clubs. */
function holdTimeFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_holdtime_title"), t("fig_source_holdups", { n: d.matches }));
  const comp = (c) => d.by_comp.find((x) => x.comp === c);
  const short = (c) => t(`comp_short_${c}`);
  const groups = [
    { label: t("ht_barca"), color: HEX.home, items: d.barca.map((x) => ({ label: x.era, value: x.win_pct })) },
    { label: t("ht_clubs"), color: HEX.corail, items: ["pl-2015", "liga-2015", "seriea-2015", "ligue1-2015", "ligue1-2022", "bundesliga-2023"].map(comp).filter(Boolean).map((x) => ({ label: short(x.comp), sub: seasonOf(t(`comp_label_${x.comp}`)), value: x.win_pct, dim: x.year < 2020 })) },
    { label: t("ht_sel"), color: HEX.away, items: ["wc-2018", "euro-2020", "wc-2022", "euro-2024"].map(comp).filter(Boolean).map((x) => ({ label: short(x.comp), sub: seasonOf(t(`comp_label_${x.comp}`)), value: x.win_pct })) },
  ];
  groupedBars(svg, groups, { value: d.overall.win_pct, label: t("ht_ref", { v: ctx.num(d.overall.win_pct, 1) }) }, ctx, { max: 36, fmt: (v) => `${ctx.num(v, 0)} %` });
  svg.append(text(W - 50, H - 62, t("fig_holdtime_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_holdtime_caption");
}

// --- Enquête 8 · Messi et Mbappé ------------------------------------------------------------------

const METRICS = [["npxg", "mm_m_npxg", 2], ["shots", "mm_m_shots", 2], ["box", "mm_m_box", 1], ["touches", "mm_m_touches", 1], ["dribbles", "mm_m_dribbles", 2], ["progressive", "mm_m_prog", 2], ["key_passes", "mm_m_kp", 2]];

function twinsFig(svg, e, ctx) {
  const { t } = ctx;
  const { messi, mbappe } = e.data.same_age;
  frame(svg, t("fig_twins_title"), t("fig_source_twins", { a: messi.matches, b: mbappe.matches }));
  const rows = METRICS.map(([k, lab, dec]) => ({ label: t(lab), sub: t("mm_per90"), a: messi[k], b: mbappe[k], fmt: (v) => ctx.num(v, dec) }));
  compareRowsFig(svg, rows, t("tw_messi"), t("tw_mbappe"), ctx);
  svg.append(text(W - 60, H - 62, t("fig_twins_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_twins_caption");
}

function messiTimeFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_messitime_title"), t("fig_source_messi"));
  panels(svg, d.messi_seasons, [
    { label: t("mt_dribbles"), sub: t("mt_sub"), get: (x) => x.dribbles, fmt: (v) => ctx.num(v, 1), min: 0, max: 10 },
    { label: t("mt_prog"), sub: t("mt_sub"), get: (x) => x.progressive, fmt: (v) => ctx.num(v, 1), min: 0, max: 9, color: HEX.away },
  ], ctx, { xlabel: (x) => `${x.season.slice(2, 4)}/${x.season.slice(7, 9)}`, labelEvery: 3, top: 150, height: 330 });
  const psg = d.psg.messi;
  svg.append(text(70, H - 70, t("mt_psg", { d: ctx.num(psg.dribbles, 2), p: ctx.num(psg.progressive, 2) }), { "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_messitime_caption");
}

/** Un terrain : la médiane des ballons touchés, saison après saison. */
function touchMapFig(svg, e, ctx) {
  const { t } = ctx;
  const d = e.data;
  frame(svg, t("fig_touchmap_title"), t("fig_source_messi"));
  const k = 7; const ox = 50; const oy = 120;
  const g = el("g", { class: "chalk" });
  drawPitch(g, k, ox, oy, 21);
  svg.append(g);
  const P = (p) => [ox + p.touch_x * k, oy + p.touch_y * k];
  // Messi au Barça : un chemin, du plus pâle (2005) au plus vif (2021)
  const seasons = d.messi_seasons;
  const path = el("g", { class: "chalk" });
  path.append(el("path", { d: chalkPath(seasons.map(P), { amp: 0.6, step: 8, seed: 5 }), stroke: HEX.home, "stroke-width": 2.5, fill: "none", opacity: 0.6 }));
  svg.append(path);
  seasons.forEach((s, i) => {
    const [x, y] = P(s);
    svg.append(el("circle", { cx: x, cy: y, r: 7, fill: HEX.home, opacity: 0.35 + (0.65 * i) / (seasons.length - 1) }));
  });
  const lab = (p, s, col, dx = 12, dy = 5, anchor = "start") => {
    const [x, y] = P(p);
    svg.append(text(x + dx, y + dy, s, { fill: col, "font-size": 14, "text-anchor": anchor, "paint-order": "stroke", stroke: "#1c2421", "stroke-width": 4 }));
  };
  lab(seasons[0], seasons[0].season.replace(/^20(\d\d)\/20(\d\d)$/, "$1/$2"), HEX.home);
  lab(seasons[seasons.length - 1], seasons[seasons.length - 1].season.replace(/^20(\d\d)\/20(\d\d)$/, "$1/$2"), HEX.home, 12, -8);
  const psgMe = d.psg.messi;
  const [mx, my] = P(psgMe);
  svg.append(el("circle", { cx: mx, cy: my, r: 9, fill: "none", stroke: HEX.home, "stroke-width": 3 }));
  lab(psgMe, "PSG", HEX.home, -14, 5, "end");
  // Mbappé : PSG et France
  const mb = [...d.mbappe_psg_seasons.map((x) => [x, `PSG ${t(`comp_label_${x.key}`).match(/\d{4}\/\d{2}/)[0].slice(2)}`]),
    ...d.mbappe_tournaments.map((x) => [x, t(`short_${x.key}`)])];
  // étiquettes placées à la main : les points de Mbappé se serrent sur le couloir gauche
  const at = { "ligue1-2021": [-12, 16, "end"], "ligue1-2022": [-12, -6, "end"], "euro-2020": [12, 14], "wc-2022": [-12, -4, "end"], "euro-2024": [12, 2], "wc-2018": [12, 5] };
  mb.forEach(([p, s]) => {
    svg.append(el("circle", { cx: P(p)[0], cy: P(p)[1], r: 7, fill: HEX.away }));
    lab(p, s, HEX.away, ...(at[p.key] ?? [12, 5]));
  });
  svg.append(text(ox + 4, oy + 68 * k + 22, `${t("ls_goal")}   ·   ${t("tm_attack")}`, { fill: HEX.gris, "font-size": 13 }));
  // légende
  const lx = ox + 105 * k + 40;
  [[HEX.home, t("tm_messi"), 0.7], [HEX.home, t("tm_messi_psg"), 0], [HEX.away, t("tm_mbappe"), 1]].forEach(([c, s, o], i) => {
    const y = 150 + i * 34;
    svg.append(el("circle", { cx: lx + 7, cy: y - 5, r: 7, fill: o ? c : "none", stroke: c, "stroke-width": o ? 0 : 3, opacity: o || 1 }));
    svg.append(text(lx + 24, y, s, { fill: HEX.craie, "font-size": 14 }));
  });
  svg.append(text(lx, 270, t("tm_how"), { fill: HEX.gris, "font-size": 12 }));
  const note = el("text", { x: lx, y: 330, "font-family": HAND, "font-size": 20, fill: HEX.home });
  wrap(t("tm_note"), 22).forEach((ln, i) => note.append(el("tspan", { x: lx, dy: i ? 30 : 0 }, ln)));
  svg.append(note);
  return t("fig_touchmap_caption");
}

const wrap = (s, n) => s.split(" ").reduce((lines, w) => {
  const last = lines[lines.length - 1];
  if (last && (last + " " + w).length <= n) lines[lines.length - 1] = `${last} ${w}`; else lines.push(w);
  return lines;
}, []);

function clubSelFig(svg, e, ctx) {
  const { t } = ctx;
  const c = e.data.club_vs_selection;
  frame(svg, t("fig_clubsel_title"), t("fig_source_twins", { a: c.messi_club.matches + c.messi_selection.matches, b: c.mbappe_club.matches + c.mbappe_selection.matches }));
  const row = (who, sub, a, b, k, lab, dec) => ({ label: t(who, { m: t(lab) }), sub: t(sub), a: a[k], b: b[k], fmt: (v) => ctx.num(v, dec) });
  const rows = [
    row("mm_cs_messi", "mm_cs_messi_sub", c.messi_club, c.messi_selection, "npxg", "mm_m_npxg", 2),
    row("mm_cs_messi", "mm_cs_messi_sub", c.messi_club, c.messi_selection, "touches", "mm_m_touches", 1),
    row("mm_cs_messi", "mm_cs_messi_sub", c.messi_club, c.messi_selection, "key_passes", "mm_m_kp", 2),
    row("mm_cs_mbappe", "mm_cs_mbappe_sub", c.mbappe_club, c.mbappe_selection, "npxg", "mm_m_npxg", 2),
    row("mm_cs_mbappe", "mm_cs_mbappe_sub", c.mbappe_club, c.mbappe_selection, "box", "mm_m_box", 1),
    row("mm_cs_mbappe", "mm_cs_mbappe_sub", c.mbappe_club, c.mbappe_selection, "dribbles", "mm_m_dribbles", 2),
  ];
  compareRowsFig(svg, rows, t("mm_cs_club"), t("mm_cs_sel"), ctx, { lx: 410, colW: 330 });
  svg.append(text(W - 60, H - 62, t("fig_clubsel_note"), { "text-anchor": "end", "font-family": HAND, "font-size": 22, fill: HEX.home }));
  return t("fig_clubsel_caption");
}

const FIGURES = { gap: gapFig, holdcomp: holdCompFig, heists: heistsFig, holdtime: holdTimeFig, costtime: costTimeFig, backthree: backThreeFig, topshapes: topShapesFig, lopsided: lopsidedFig, lopsidetime: lopsideTimeFig, twins: twinsFig, messitime: messiTimeFig, touchmap: touchMapFig, clubsel: clubSelFig, bandsloss: bandsLossFig, losskind: lossKindFig, losstime: lossTimeFig, outcomes, champions, quartiles, cases, favourite, time, same, handbrake, deciders, tournaments, shots: shotsFig, losses: lossesFig, pressing: pressingFig, steady, bands: bandsFig, equal: equalFig, bycomp: bycompFig, misses: missesFig, conversion: conversionFig, eras: erasFig, finals: finalsFig };

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

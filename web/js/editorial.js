// La salle des archives : les finales de Ligue des champions, fiche par fiche.

import { HEX, el } from "./draw.js";
import { chalkPath, seedOf } from "./logic.js";
import { fillTeams } from "./i18n.js";

const $ = (s, root = document) => root.querySelector(s);


// --- La salle des archives ----------------------------------------------------------------------

export async function showArchives(app, ctx) {
  const { t, esc, json, state, team } = ctx;
  const cat = state.catalogue ?? (await json("data/catalogue.json"));
  state.catalogue = cat;
  const comp = cat.competitions.find((c) => c.kind === "archives");
  const finals = [...comp.matches].sort((a, b) => a.date.localeCompare(b.date));
  const [details, table] = await Promise.all([
    Promise.all(finals.map((x) => json(`data/matches/${x.id}.json`))),
    json(`data/players/${comp.id}.json`).catch(() => null),
  ]);
  const L = state.lang;
  document.title = `${t("archives_title")} · Tableau Noir`;
  const winnerSide = (d) => {
    const { home: h, away: a } = d.meta;
    if (h.score !== a.score) return h.score > a.score ? "home" : "away";
    return h.penalties > a.penalties ? "home" : "away";
  };
  const xgWins = details.filter((d) => { const w = winnerSide(d); const o = w === "home" ? "away" : "home"; return d.stats[w].xg > d.stats[o].xg; }).length;
  const goals = details.reduce((a, d) => a + d.meta.home.score + d.meta.away.score, 0);
  const poss = details.reduce((a, d) => a + d.stats[winnerSide(d)].possession, 0) / details.length;
  const leaders = (key) => Object.values(table?.players ?? {}).sort((a, b) => (b.totals[key] ?? 0) - (a.totals[key] ?? 0)).slice(0, 5);
  // l'accroche : la première phrase du coin de l'analyste, ou les deux premières si elle est courte
  const firstSentence = (s) => {
    const parts = s.match(/[^.!?]+[.!?]+(\s|$)/g) ?? [s];
    return (parts[0].length < 70 && parts[1] ? parts[0] + parts[1] : parts[0]).trim();
  };
  app.innerHTML = `${ctx.masthead(true)}
    <article class="archives">
      <p class="kicker">${esc(t("archives_kicker"))}</p>
      <h1>${esc(t("archives_title"))}</h1>
      <p class="standfirst">${esc(t("archives_lead"))}</p>
      <div class="big-numbers">
        <div><b>${xgWins}<small>/${details.length}</small></b><span>${esc(t("archives_xg_wins"))}</span></div>
        <div><b>${goals}</b><span>${esc(t("archives_goals"))}</span></div>
        <div><b>${ctx.pct(poss)}</b><span>${esc(t("archives_poss"))}</span></div>
      </div>
      <p class="fig">${esc(t("archives_fig_xg"))}</p>
      <svg class="chart" id="arch-xg"></svg>
      <p class="legend">${esc(t("archives_xg_legend"))}</p>
      <ol class="cards">${details.map((d, i) => {
        const w = winnerSide(d);
        const lose = w === "home" ? "away" : "home";
        const hook = d.analyst?.s1?.[L]?.lead ? fillTeams(firstSentence(d.analyst.s1[L].lead), d.meta, L) : "";
        return `<li class="card">
          <p class="season">${esc(d.meta.season.replace("/", " – "))}</p>
          <h2><span class="w">${esc(team(d.meta[w].name))}</span> <b>${d.meta[w].score} – ${d.meta[lose].score}</b> <span class="l">${esc(team(d.meta[lose].name))}</span>
            ${d.meta.home.penalties != null ? `<small>${d.meta[w].penalties} – ${d.meta[lose].penalties} ${esc(t("tab"))}</small>` : ""}</h2>
          <p class="hook">${esc(hook)}</p>
          <p class="mini">xG ${ctx.num(d.stats[w].xg, 2)} – ${ctx.num(d.stats[lose].xg, 2)} · ${esc(t("k_possession"))} ${ctx.pct(d.stats[w].possession)}</p>
          <a class="go" href="#/m/${d.meta.id}">${esc(t("archives_open"))} →</a>
        </li>`;
      }).join("")}</ol>
      ${table ? `<div class="grid legends">
        <div class="panel"><p class="fig">${esc(t("archives_scorers"))}</p><ol class="legend-list">${leaders("goals").map((p) => `<li><b>${esc(p.name)}</b> <small>${esc(team(p.team))}</small><span>${ctx.num(p.totals.goals)}</span></li>`).join("")}</ol></div>
        <div class="panel"><p class="fig">${esc(t("archives_creators"))}</p><ol class="legend-list">${leaders("xt").map((p) => `<li><b>${esc(p.name)}</b> <small>${esc(team(p.team))}</small><span>${ctx.num(p.totals.xt, 2)} xT</span></li>`).join("")}</ol></div>
      </div>` : ""}
      <div class="method"><h3>${esc(t("method_title"))}</h3><p>${esc(t("archives_method"))}</p></div>
    </article>`;
  drawArchiveXg($("#arch-xg", app), details, winnerSide, ctx);
  window.scrollTo({ top: 0 });
}

/** Une barre de craie par finale : xG du vainqueur (jaune) contre xG du perdant (bleu). */
function drawArchiveXg(svg, details, winnerSide, ctx) {
  const W = 1100; const H = 300; const m = { l: 30, r: 20, t: 20, b: 60 };
  svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
  const max = Math.max(...details.flatMap((d) => [d.stats.home.xg, d.stats.away.xg]), 1);
  const bw = (W - m.l - m.r) / details.length;
  const y = (v) => H - m.b - (v / max) * (H - m.t - m.b);
  const g = el("g", { class: "chalk" });
  g.append(el("path", { d: chalkPath([[m.l, H - m.b], [W - m.r, H - m.b]], { seed: 2 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none", opacity: 0.7 }));
  details.forEach((d, i) => {
    const w = winnerSide(d);
    const l = w === "home" ? "away" : "home";
    const cx = m.l + bw * (i + 0.5);
    for (const [side, dx, col] of [[w, -bw * 0.17, HEX.home], [l, bw * 0.17, HEX.away]]) {
      const v = d.stats[side].xg;
      g.append(el("path", { d: chalkPath([[cx + dx, H - m.b], [cx + dx, y(v)]], { amp: 0.6, seed: seedOf(d.meta.id + side) }), stroke: col, "stroke-width": bw * 0.26, fill: "none", opacity: 0.85 }));
      g.append(el("text", { x: cx + dx, y: y(v) - 8, "text-anchor": "middle", "font-size": 13, fill: col, "font-family": "DM Mono, monospace" }, ctx.num(v, 1)));
    }
    g.append(el("text", { x: cx, y: H - m.b + 22, "text-anchor": "middle", "font-size": 14, fill: HEX.gris, "font-family": "DM Mono, monospace" }, d.meta.date.slice(0, 4)));
    g.append(el("text", { x: cx, y: H - m.b + 44, "text-anchor": "middle", "font-size": 17, fill: HEX.craie, "font-family": "Nothing You Could Do, cursive" }, ctx.team(d.meta[w].name).split(" ").slice(-1)[0]));
  });
  svg.replaceChildren(g);
}

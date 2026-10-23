// Les pages éditoriales : le dossier Argentine–France et la salle des archives des finales de LDC.

import { HEX, el } from "./draw.js";
import { chalkPath, seedOf } from "./logic.js";
import { fillTeams } from "./i18n.js";
import { mountReplay } from "./replay.js";
import { mountRace } from "./anim.js";

const $ = (s, root = document) => root.querySelector(s);
const SECTIONS = ["s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9"];

/** Démarre une animation seulement quand elle devient visible (une à la fois). */
function whenVisible(node, fn) {
  const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { io.disconnect(); fn(); } }, { threshold: 0.35 });
  io.observe(node);
}

function goalTitle(g, ctx) {
  return `${g.scorer} ${g.minute}'${g.penalty ? ` (${ctx.t("pen_short")})` : ""}`;
}

// --- Le dossier -----------------------------------------------------------------------------------

export async function showDossier(app, ctx) {
  const { t, esc, json, state, team } = ctx;
  const dossier = await json("data/dossier.json");
  const [d, cat] = await Promise.all([json(`data/matches/${dossier.match}.json`), state.catalogue ?? json("data/catalogue.json")]);
  state.catalogue = cat;
  const L = state.lang;
  const m = d.meta;
  document.title = `${dossier.title[L]} · Tableau Noir`;
  const media = dossier.media.map((x) => `<li><span>${esc(t(`media_${x.kind}`, { label: x.kind === "goal" ? goalTitle(d.replays.find((g) => g.minute === x.minute), ctx) : t(`race_${x.race}`) }))}</span>
      <a href="media/${x.file}.mp4" download>MP4</a><a href="media/${x.file}.gif" download>GIF</a></li>`).join("");
  app.innerHTML = `${ctx.masthead(true)}
    <article class="dossier">
      <p class="kicker">${esc(dossier.kicker[L])}</p>
      <h1>${esc(dossier.title[L])}</h1>
      <div class="mini-board"><span class="home">${esc(team(m.home.name))}</span><b>${m.home.score} – ${m.away.score}</b><span class="away">${esc(team(m.away.name))}</span>
        <small>${esc(t("aet"))} · ${m.home.penalties} – ${m.away.penalties} ${esc(t("tab"))}</small></div>
      <p class="standfirst">${esc(dossier.standfirst[L])}</p>
      ${dossier.chapters.map((c, i) => `<section class="chapter">
          <h2>${esc(c.title[L])}</h2>
          ${c.text[L].map((p) => `<p>${esc(p)}</p>`).join("")}
          <div class="figure" data-i="${i}"></div>
        </section>`).join("")}
      <section class="chapter downloads">
        <h2>${esc(t("media_title"))}</h2>
        <p>${esc(t("media_lead"))}</p>
        <ul class="media">${media}</ul>
      </section>
      <p class="back-link"><a href="#/m/${m.id}">${esc(t("dossier_open_match"))} →</a></p>
    </article>`;
  dossier.chapters.forEach((c, i) => figure($(`.figure[data-i="${i}"]`, app), c.figure, d, ctx));
  window.scrollTo({ top: 0 });
}

function figure(host, f, d, ctx) {
  const { t, esc, team, state } = ctx;
  const m = d.meta;
  if (!f) return;
  if (f.type === "paths") {
    const comp = state.catalogue.competitions.find((c) => c.id === m.comp);
    const col = (side) => {
      const name = m[side].name;
      const rows = comp.matches.filter((x) => x.date < m.date && [x.home.name, x.away.name].includes(name));
      return `<div class="path ${side}"><h3>${esc(team(name))}</h3><ol>${rows.map((x) => `<li><a href="#/m/${x.id}"><small>${esc(ctx.stageName(x.stage, state.lang))}</small>
        ${esc(team(x.home.name))} ${x.home.score} – ${x.away.score} ${esc(team(x.away.name))}${x.home.penalties != null ? ` <small>(${x.home.penalties} – ${x.away.penalties} ${esc(t("tab"))})</small>` : ""}</a></li>`).join("")}</ol></div>`;
    };
    host.innerHTML = `<div class="paths">${col("home")}${col("away")}</div>`;
  } else if (f.type === "replay") {
    const i = d.replays.findIndex((g) => g.minute === f.minute);
    const g = d.replays[i];
    const sub = `${team(m.home.name)} ${m.home.score}–${m.away.score} ${team(m.away.name)}`;
    const box = document.createElement("div");
    host.append(box);
    whenVisible(box, () => mountReplay(box, g, { t, title: goalTitle(g, ctx), sub, file: `tableau-noir-${m.id}-${g.minute}` }));
    box.style.minHeight = "300px";
  } else if (f.type === "race") {
    const sub = `${team(m.home.name)} – ${team(m.away.name)} · ${t("race_minutes")}`;
    mountRace(host, d, f.kind, { t, title: t(`race_${f.kind}`), sub, decimal: state.lang === "fr" ? "," : "." });
  } else if (f.type === "link") {
    host.innerHTML = `<a class="go" href="#/m/${m.id}/${f.section}">${esc(t("dossier_see_section", { s: t(f.section) }))} →</a>`;
  } else if (f.type === "sections") {
    host.innerHTML = `<ul class="sections dossier-sections">${SECTIONS.map((s) => `<li><a href="#/m/${m.id}/${s}">${esc(t(s))}</a></li>`).join("")}</ul>`;
  }
}

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
        const reps = (d.replays ?? []).filter((g) => g.steps.length > 1);
        return `<li class="card">
          <p class="season">${esc(d.meta.season.replace("/", " – "))}</p>
          <h2><span class="w">${esc(team(d.meta[w].name))}</span> <b>${d.meta[w].score} – ${d.meta[lose].score}</b> <span class="l">${esc(team(d.meta[lose].name))}</span>
            ${d.meta.home.penalties != null ? `<small>${d.meta[w].penalties} – ${d.meta[lose].penalties} ${esc(t("tab"))}</small>` : ""}</h2>
          <p class="hook">${esc(hook)}</p>
          <p class="mini">xG ${ctx.num(d.stats[w].xg, 2)} – ${ctx.num(d.stats[lose].xg, 2)} · ${esc(t("k_possession"))} ${ctx.pct(d.stats[w].possession)}</p>
          ${reps.length ? `<div class="chips">${reps.map((g, j) => `<button type="button" data-f="${i}" data-g="${j}">▶ ${esc(goalTitle(g, ctx))}</button>`).join("")}</div><div class="card-replay" hidden></div>` : ""}
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
  app.querySelectorAll(".cards .chips button").forEach((b) => b.addEventListener("click", () => {
    const d = details[Number(b.dataset.f)];
    const g = d.replays.filter((x) => x.steps.length > 1)[Number(b.dataset.g)];
    const host = b.closest(".card").querySelector(".card-replay");
    host.hidden = false;
    mountReplay(host, g, { t, title: goalTitle(g, ctx), sub: `${team(d.meta.home.name)} – ${team(d.meta.away.name)} · ${d.meta.season}`, file: `tableau-noir-${d.meta.id}-${g.minute}` });
  }));
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

// Figures animées : la course aux xG et la course à la menace qui se dessinent minute par minute.
// Même principe que les buts rejoués : render(t) dessine l'instant t, pour la lecture comme pour
// les exports vidéo.

import { xgRace } from "./logic.js";
import { recordAnimation } from "./replay.js";

const C = { home: "#e8c268", away: "#8db8d8", craie: "#ece7dc", gris: "#9aa39e", corail: "#e2786a", ardoise: "#1c2421" };
const HAND = '"Nothing You Could Do", cursive';
const MONO = '"DM Mono", monospace';
export const RUN = 14; // secondes pour dérouler le match
export const HOLD = 2.5;

/** Écrit un texte sur une ligne, en réduisant la police jusqu'à ce qu'il tienne. */
function fitText(ctx, text, x, y, maxW, size, family) {
  let s = size;
  do { ctx.font = `${s}px ${family}`; s -= 1; } while (ctx.measureText(text).width > maxW && s > 8);
  ctx.fillText(text, x, y);
}

function rand(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 2 ** 32; };
}

/** Les deux courbes (minute, valeur cumulée) et les buts, pour « xg » ou « xt ». */
export function series(d, kind) {
  const dur = d.meta.duration;
  if (kind === "xg") {
    const { steps } = xgRace(d.shots, dur);
    return { dur, steps, unit: "xG", goals: d.goals.map((g) => ({ side: g.side, minute: g.t ?? g.minute + 0.5, name: d.players.find((p) => p.id === g.player)?.name ?? "" })) };
  }
  const steps = {};
  for (const s of ["home", "away"]) {
    let a = 0;
    steps[s] = [[0, 0], ...d.value.xt_minutes[s].map((v, i) => [i + 1, (a += v)])];
  }
  return { dur, steps, unit: "xT", goals: d.goals.map((g) => ({ side: g.side, minute: g.minute + 1, name: d.players.find((p) => p.id === g.player)?.name ?? "" })) };
}

function valueAt(pts, minute) {
  let v = 0;
  for (const [m, y] of pts) { if (m > minute) break; v = y; }
  return v;
}

export function renderRace(canvas, d, kind, t, labels = {}) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  const S = series(d, kind);
  const minute = Math.min(S.dur, (t / RUN) * S.dur);
  const m = { l: W * 0.08, r: W * 0.14, t: H * 0.2, b: H * 0.12 };
  const ymax = Math.max(1, ...["home", "away"].map((s) => S.steps[s][S.steps[s].length - 1][1])) * 1.1;
  const X = (v) => m.l + (v / S.dur) * (W - m.l - m.r);
  const Y = (v) => H - m.b - (v / ymax) * (H - m.t - m.b);
  ctx.fillStyle = C.ardoise;
  ctx.fillRect(0, 0, W, H);
  const g = rand(3);
  ctx.fillStyle = "rgba(236,231,220,0.035)";
  for (let i = 0; i < 900; i++) ctx.fillRect(g() * W, g() * H, 1.2, 1.2);
  // axes
  ctx.strokeStyle = C.craie;
  ctx.globalAlpha = 0.7;
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(m.l, Y(0)); ctx.lineTo(W - m.r, Y(0)); ctx.stroke();
  ctx.globalAlpha = 1;
  ctx.font = `${Math.round(H * 0.03)}px ${MONO}`;
  ctx.fillStyle = C.gris;
  ctx.textAlign = "center";
  for (const mk of [45, 90, 105].filter((v) => v < S.dur)) {
    ctx.setLineDash([5, 7]);
    ctx.strokeStyle = C.gris;
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(X(mk), m.t); ctx.lineTo(X(mk), Y(0)); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillText(`${mk}'`, X(mk), Y(0) + H * 0.045);
  }
  ctx.textAlign = "right";
  for (let v = 1; v < ymax; v++) ctx.fillText(String(v), m.l - 10, Y(v) + 6);
  // courbes jusqu'à la minute courante, tracé doublé façon craie
  const r = rand(9);
  for (const s of ["home", "away"]) {
    const pts = S.steps[s].filter(([mm]) => mm <= minute);
    pts.push([minute, valueAt(S.steps[s], minute)]);
    for (const [w, a] of [[6, 0.9], [2.5, 0.5]]) {
      ctx.strokeStyle = C[s];
      ctx.globalAlpha = a;
      ctx.lineWidth = w;
      ctx.lineJoin = "round";
      ctx.beginPath();
      pts.forEach(([mm, v], i) => { const x = X(mm) + (r() - 0.5); const y = Y(v) + (r() - 0.5); if (i) ctx.lineTo(x, y); else ctx.moveTo(x, y); });
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
    const v = valueAt(S.steps[s], minute);
    ctx.fillStyle = C[s];
    ctx.textAlign = "left";
    ctx.font = `${Math.round(H * 0.04)}px ${MONO}`;
    const dy = s === "home" ? -8 : 26;
    ctx.fillText(`${v.toFixed(2).replace(".", labels.decimal ?? ".")} ${S.unit}`, X(minute) + 12, Y(v) + dy);
  }
  // buts
  const placed = [];
  for (const goal of S.goals.filter((x) => x.minute <= minute)) {
    const v = valueAt(S.steps[goal.side], goal.minute);
    let ly = Y(v) - H * 0.035;
    while (placed.some(([px, py]) => Math.abs(px - X(goal.minute)) < W * 0.07 && Math.abs(py - ly) < H * 0.045)) ly -= H * 0.045;
    placed.push([X(goal.minute), ly]);
    ctx.strokeStyle = C.corail;
    ctx.fillStyle = "rgba(226,120,106,0.3)";
    ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(X(goal.minute), Y(v), H * 0.016, 0, 7); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.craie;
    ctx.font = `${Math.round(H * 0.034)}px ${HAND}`;
    ctx.textAlign = "center";
    ctx.fillText(goal.name.split(" ").slice(-1)[0], X(goal.minute), ly);
  }
  // titre, minute
  ctx.textAlign = "left";
  ctx.fillStyle = C.craie;
  ctx.font = `${Math.round(H * 0.06)}px ${HAND}`;
  if (labels.title) ctx.fillText(labels.title, m.l, H * 0.085);
  ctx.fillStyle = C.gris;
  if (labels.sub) fitText(ctx, labels.sub, m.l, H * 0.13, W - 2 * m.l, Math.round(H * 0.03), MONO);
  ctx.textAlign = "right";
  ctx.fillStyle = C.craie;
  ctx.font = `${Math.round(H * 0.08)}px ${MONO}`;
  ctx.fillText(`${Math.floor(minute)}'`, W - m.l * 0.6, H * 0.11);
}

/** Lecteur simple pour une figure animée (lecture au passage dans la page, bouton « rejouer »). */
export function mountRace(host, d, kind, { t, title, sub, decimal, file, autoplay = true }) {
  host.innerHTML = `<div class="replay-box"><canvas width="1280" height="720" aria-label="${title}"></canvas>
    <div class="replay-bar"><button type="button" class="play">${t("replay_again")}</button><span style="flex:1"></span>
    <button type="button" class="rec">${t("replay_export")}</button></div></div>`;
  const canvas = host.querySelector("canvas");
  let start = null;
  let raf = 0;
  const frame = (now) => {
    start ??= now;
    const s = (now - start) / 1000;
    renderRace(canvas, d, kind, s, { title, sub, decimal });
    if (s < RUN + 0.2) raf = requestAnimationFrame(frame);
  };
  const go = () => { cancelAnimationFrame(raf); start = null; raf = requestAnimationFrame(frame); };
  renderRace(canvas, d, kind, 0, { title, sub, decimal });
  if (autoplay) {
    const io = new IntersectionObserver((es) => { if (es.some((e) => e.isIntersecting)) { go(); io.disconnect(); } }, { threshold: 0.4 });
    io.observe(canvas);
  } else go();
  host.querySelector(".play").addEventListener("click", go);
  host.querySelector(".rec").addEventListener("click", (e) => recordAnimation(
    { width: 1280, height: 720, duration: RUN + HOLD, draw: (c, s) => renderRace(c, d, kind, s, { title, sub, decimal }) },
    file ?? `tableau-noir-${d.meta.id}-${kind}`, e.currentTarget, t,
  ));
}

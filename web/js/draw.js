// Dessin à la craie partagé par toutes les sections : éléments SVG, terrain, lignes de comparaison.

import { chalkCircle, chalkPath, seedOf } from "./logic.js";

export const NS = "http://www.w3.org/2000/svg";
export const HEX = { home: "#e8c268", away: "#8db8d8", craie: "#ece7dc", gris: "#9aa39e", corail: "#e2786a" };
export const HAND = "Nothing You Could Do, cursive";

export function el(tag, attrs = {}, text) {
  const e = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) e.setAttribute(k, v);
  if (text != null) e.textContent = text;
  return e;
}

/** Terrain de 105 × 68 m tracé à la craie ; `k` : pixels par mètre, (ox, oy) : coin haut gauche. */
export function drawPitch(svg, k, ox, oy, seed = 7) {
  const P = (x, y) => [ox + x * k, oy + y * k];
  const line = (pts, s) => svg.append(el("path", { d: chalkPath(pts.map(([a, b]) => P(a, b)), { amp: 1.1, seed: seed + s }), stroke: HEX.craie, "stroke-width": 1.8, fill: "none", opacity: 0.75, "stroke-linejoin": "round" }));
  line([[0, 0], [105, 0], [105, 68], [0, 68], [0, 0]], 1);
  line([[52.5, 0], [52.5, 68]], 2);
  svg.append(el("path", { d: chalkCircle(ox + 52.5 * k, oy + 34 * k, 9.15 * k, { seed: seed + 3, amp: 0.03 }), stroke: HEX.craie, "stroke-width": 1.6, fill: "none", opacity: 0.7 }));
  for (const [gx, sg] of [[0, 1], [105, -1]]) {
    line([[gx, 13.84], [gx + sg * 16.5, 13.84], [gx + sg * 16.5, 54.16], [gx, 54.16]], 4 + gx);
    line([[gx, 24.84], [gx + sg * 5.5, 24.84], [gx + sg * 5.5, 43.16], [gx, 43.16]], 5 + gx);
    svg.append(el("circle", { cx: ox + (gx + sg * 11) * k, cy: oy + 34 * k, r: 2, fill: HEX.craie, opacity: 0.7 }));
  }
}

/** Un terrain dans un SVG : renvoie la fonction mètres → pixels. */
export function pitchSvg(svg, { k = 6, pad = 12, seed = 7 } = {}) {
  svg.setAttribute("viewBox", `0 0 ${105 * k + pad * 2} ${68 * k + pad * 2}`);
  svg.replaceChildren();
  const g = el("g", { class: "chalk" });
  drawPitch(g, k, pad, pad, seed);
  svg.append(g);
  return (x, y) => [pad + x * k, pad + y * k];
}

/** Hachures dans un rectangle (zones), en mètres. */
export function hatchRect(svg, P, x0, y0, x1, y1, color, opacity = 0.18, step = 2.2) {
  const g = el("g", { class: "chalk", opacity });
  for (let s = -(y1 - y0); s < x1 - x0; s += step) {
    let xa = x0 + s; let ya = y0; let xb = x0 + s + (y1 - y0); let yb = y1;
    if (xa < x0) { ya += x0 - xa; xa = x0; }
    if (xb > x1) { yb -= xb - x1; xb = x1; }
    if (xa >= xb) continue;
    g.append(el("path", { d: chalkPath([P(xa, ya), P(xb, yb)], { amp: 0.4, seed: seedOf(`${s}`) }), stroke: color, "stroke-width": 1.4, fill: "none" }));
  }
  svg.append(g);
}

/**
 * Lignes de comparaison face à face (domicile | libellé | extérieur), avec la moyenne de la
 * compétition en repère. `rows` : [{ label, help, home, away, mean, lo, hi, fmt(v) }].
 */
export function compareRows(ul, rows, esc) {
  for (const r of rows) {
    if (r.home == null && r.away == null) continue;
    const li = document.createElement("li");
    li.innerHTML = `<span class="v home">${r.home == null ? "–" : r.fmt(r.home)}</span><svg aria-hidden="true"></svg>
      <span class="k">${esc(r.label)}${r.help ? `<small>${esc(r.help)}</small>` : ""}${r.mean != null ? `<small class="mean">⌀ ${r.fmt(r.mean)}</small>` : ""}</span>
      <svg aria-hidden="true"></svg><span class="v away">${r.away == null ? "–" : r.fmt(r.away)}</span>`;
    ul.append(li);
    const [l, rr] = li.querySelectorAll("svg");
    const f = rowScale(r);
    bar(l, f(r.home), "home", seedOf(r.label + "h"), true, r.mean != null ? f(r.mean) : null);
    bar(rr, f(r.away), "away", seedOf(r.label + "a"), false, r.mean != null ? f(r.mean) : null);
  }
}

/**
 * Échelle d'une ligne : de 0 au maximum par défaut ; avec l'étendue de la compétition (`lo`, `hi`),
 * la barre va du plus petit au plus grand match observé, pour que les écarts se voient.
 */
export function rowScale(r) {
  const vals = [r.home, r.away, r.mean].filter((v) => v != null);
  if (r.lo != null && r.hi != null && r.hi > r.lo) {
    const lo = Math.min(r.lo, ...vals);
    const hi = Math.max(r.hi, ...vals);
    return (v) => (v == null ? 0 : 0.06 + (0.94 * (v - lo)) / (hi - lo));
  }
  const max = Math.max(0, ...vals) || 1;
  return (v) => (v || 0) / max;
}

export function bar(svg, frac, side, seed, rtl, meanFrac = null) {
  const w = 200;
  svg.setAttribute("viewBox", "0 0 200 14");
  svg.setAttribute("preserveAspectRatio", "none");
  const len = Math.max(0, frac) * (w - 4);
  const g = el("g", { class: "chalk" });
  // cadre invisible : sans lui, une barre presque droite a une boîte de hauteur nulle et le filtre craie la rogne
  g.append(el("rect", { x: 0, y: 0, width: w, height: 14, fill: "none" }));
  if (len >= 1) {
    const x0 = rtl ? w - 2 : 2;
    const x1 = rtl ? w - 2 - len : 2 + len;
    for (const [dy, sw, op] of [[7, 10, 0.95], [5, 3, 0.55]]) {
      g.append(el("path", { d: chalkPath([[x0, dy], [x1, dy]], { amp: 0.8, step: 18, seed: seed + dy }), stroke: HEX[side], "stroke-width": sw, "stroke-linecap": "round", fill: "none", opacity: op }));
    }
  }
  if (meanFrac != null) {
    const xm = rtl ? w - 2 - meanFrac * (w - 4) : 2 + meanFrac * (w - 4);
    g.append(el("path", { d: `M${xm} 0V14`, stroke: HEX.craie, "stroke-width": 2, opacity: 0.85 }));
  }
  svg.append(g);
}

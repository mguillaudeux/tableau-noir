// Logique pure de Tableau Noir (aucun accès au DOM) : testée avec node:test.

export const PITCH = { x: 105, y: 68 };

/** Générateur pseudo-aléatoire déterministe : le même tracé de craie à chaque affichage. */
export function rng(seed = 1) {
  let s = seed >>> 0 || 1;
  return () => ((s = (s * 1664525 + 1013904223) >>> 0) / 2 ** 32);
}

/** Graine stable à partir d'un texte (identifiant de match, nom de visuel…). */
export function seedOf(text) {
  let h = 2166136261;
  for (const c of String(text)) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return h >>> 0;
}

/**
 * Trait de craie : une polyligne légèrement tremblée entre des points, renvoyée comme attribut `d`.
 * `amp` : amplitude du tremblement en pixels ; `step` : longueur d'un segment.
 */
export function chalkPath(points, { amp = 1.2, step = 14, seed = 1 } = {}) {
  const rand = rng(seed);
  const out = [];
  for (let i = 0; i < points.length - 1; i++) {
    const [x0, y0] = points[i];
    const [x1, y1] = points[i + 1];
    const len = Math.hypot(x1 - x0, y1 - y0);
    const n = Math.max(1, Math.round(len / step));
    const nx = len ? -(y1 - y0) / len : 0;
    const ny = len ? (x1 - x0) / len : 0;
    for (let k = i === 0 ? 0 : 1; k <= n; k++) {
      const t = k / n;
      const j = k === 0 || k === n ? 0 : (rand() - 0.5) * 2 * amp;
      out.push([x0 + (x1 - x0) * t + nx * j, y0 + (y1 - y0) * t + ny * j]);
    }
  }
  return out.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join("");
}

/** Cercle de craie (polyligne fermée, légèrement irrégulière). */
export function chalkCircle(cx, cy, r, { amp = 0.06, seed = 1, n = 28 } = {}) {
  const rand = rng(seed);
  const a0 = rand() * Math.PI * 2;
  const pts = [];
  for (let i = 0; i <= n + 2; i++) {
    const a = a0 + (i / n) * Math.PI * 2;
    const rr = r * (1 + (rand() - 0.5) * amp);
    pts.push([cx + Math.cos(a) * rr, cy + Math.sin(a) * rr]);
  }
  return pts.map(([x, y], i) => `${i ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)}`).join("");
}

/** Échelle linéaire [d0, d1] → [r0, r1]. */
export function scale(d0, d1, r0, r1) {
  const k = d1 === d0 ? 0 : (r1 - r0) / (d1 - d0);
  return (v) => r0 + (v - d0) * k;
}

/**
 * Position d'un tir sur un terrain où l'équipe à domicile attaque vers la droite et l'équipe à
 * l'extérieur vers la gauche (les données placent toujours le tireur vers la droite).
 */
export function orient(x, y, side) {
  return side === "home" ? [x, y] : [PITCH.x - x, PITCH.y - y];
}

/** Course aux xG : paliers cumulés par équipe, de 0 à la fin du match. */
export function xgRace(shots, duration) {
  const steps = { home: [[0, 0]], away: [[0, 0]] };
  const total = { home: 0, away: 0 };
  for (const s of [...shots].sort((a, b) => a.t - b.t)) {
    const side = s.side;
    steps[side].push([s.t, total[side]]);
    total[side] += s.xg || 0;
    steps[side].push([s.t, total[side]]);
  }
  for (const side of ["home", "away"]) steps[side].push([Math.max(duration, ...shots.map((s) => s.t)), total[side]]);
  return { steps, total };
}

/** Part d'une barre de comparaison (0 à 1) ; quand les deux valeurs sont nulles, moitié-moitié. */
export function share(a, b) {
  const s = (a || 0) + (b || 0);
  return s ? (a || 0) / s : 0.5;
}

/** Score affiché, avec la séance de tirs au but. */
export function scoreLine(m) {
  const base = `${m.home.score} – ${m.away.score}`;
  if (m.home.penalties == null) return base;
  return `${base} (${m.home.penalties} – ${m.away.penalties} tab)`;
}

/** Vainqueur d'un match : "home", "away" ou null. */
export function winner(m) {
  if (m.home.score !== m.away.score) return m.home.score > m.away.score ? "home" : "away";
  if (m.home.penalties != null && m.home.penalties !== m.away.penalties) return m.home.penalties > m.away.penalties ? "home" : "away";
  return null;
}

/** Regroupe les matchs d'une compétition par phase, dans l'ordre du tournoi. */
export const STAGE_ORDER = ["Group Stage", "Round of 16", "Quarter-finals", "Semi-finals", "3rd Place Final", "Final"];
export function byStage(matches) {
  const key = (s) => (s.startsWith("Group") ? "Group Stage" : s);
  const groups = new Map();
  for (const m of matches) {
    const k = key(m.stage);
    if (!groups.has(k)) groups.set(k, []);
    groups.get(k).push(m);
  }
  const rank = (k) => { const i = STAGE_ORDER.indexOf(k); return i < 0 ? -1 : i; };
  return [...groups.entries()].sort((a, b) => rank(b[0]) - rank(a[0]));
}

/** Tri d'un tableau de joueurs par colonne (valeurs manquantes à la fin). */
export function sortPlayers(rows, key, dir = -1) {
  return [...rows].sort((a, b) => {
    const va = a[key];
    const vb = b[key];
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    const c = typeof va === "string" ? va.localeCompare(vb) : va - vb;
    return dir < 0 ? -c : c;
  });
}

/** Les hommes forts : un score simple qui pèse d'abord les buts et les passes décisives, puis l'xG,
 * les passes clés, la progression et les actions défensives. */
export function standouts(players, n = 3) {
  const score = (p) => p.goals * 2.5 + p.assists * 1.6 + p.xg * 0.8 + p.key_passes * 0.15 + p.progressive * 0.03 + p.def_actions * 0.04;
  return [...players].map((p) => ({ ...p, score: score(p) })).sort((a, b) => b.score - a.score).slice(0, n);
}

/** Ingrédients de l'indice de relationnisme et leur sens (comme `team.RELATION_KEYS` en Python). */
export const RELATION_KEYS = [["short_share", 1], ["quick_share", 1], ["roaming", 1], ["proximity", 1], ["lanes", -1]];

/** Indice relationniste d'une équipe : moyenne des écarts réduits (z) des ingrédients
 * disponibles, par rapport à la compétition. `null` si aucun ingrédient n'est utilisable. */
export function relationIndex(rel, stats) {
  const z = [];
  for (const [key, sign] of RELATION_KEYS) {
    const v = rel?.[key];
    const s = stats?.[key];
    if (v == null || !s || !s.sd) continue;
    z.push((sign * (v - s.mean)) / s.sd);
  }
  if (!z.length) return null;
  return Math.round((z.reduce((a, b) => a + b, 0) / z.length) * 1000) / 1000;
}

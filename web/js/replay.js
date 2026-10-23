// Rejouer un but, vu du dessus : des points de craie qui bougent sur un terrain dessiné à la main.
// Le dessin se fait sur un <canvas>, image par image, à partir d'un temps t (en secondes) : la
// même fonction sert à la lecture, à l'export vidéo dans le navigateur et aux exports MP4/GIF.

const PX = 105;
const PY = 68;
const COLORS = { home: "#e8c268", away: "#8db8d8", craie: "#ece7dc", gris: "#9aa39e", corail: "#e2786a", ardoise: "#1c2421" };
const HAND = '"Nothing You Could Do", cursive';
const MONO = '"DM Mono", monospace';
const TAIL = 2.2; // secondes de pause après le but
const SHOT = 0.8; // durée du trajet du tir

/** Écrit un texte sur une ligne, en réduisant la police jusqu'à ce qu'il tienne. */
export function fitText(ctx, text, x, y, maxW, size, family) {
  let s = size;
  do { ctx.font = `${s}px ${family}`; s -= 1; } while (ctx.measureText(text).width > maxW && s > 8);
  ctx.fillText(text, x, y);
}

function rand(seed) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 2 ** 32; };
}

/** Prépare une séquence : temps relatifs, positions du ballon, images des joueurs par numéro. */
export function timeline(goal) {
  const steps = goal.steps;
  const t0 = steps[0].t;
  const keys = steps.map((s) => ({ ...s, tau: Math.max(0, s.t - t0) }));
  // les penaltys ou les actions d'un seul événement durent quand même un peu
  if (keys.length === 1) keys[0].tau = 0.6;
  for (let i = 1; i < keys.length; i++) if (keys[i].tau <= keys[i - 1].tau) keys[i].tau = keys[i - 1].tau + 0.4;
  const last = keys[keys.length - 1];
  const end = last.tau + SHOT;
  const frames = keys.filter((k) => k.dots.length).map((k) => ({ tau: k.tau, dots: new Map(k.dots.map((d) => [d[5], d])) }));
  return { keys, frames, end, duration: end + TAIL };
}

function ballAt(tl, tau) {
  const { keys, end } = tl;
  const last = keys[keys.length - 1];
  if (tau <= keys[0].tau) return [keys[0].x, keys[0].y];
  if (tau >= last.tau) {
    const k = Math.min(1, (tau - last.tau) / (end - last.tau));
    const tx = last.ex ?? PX;
    const ty = last.ey ?? PY / 2;
    return [last.x + (tx - last.x) * k, last.y + (ty - last.y) * k];
  }
  let i = 0;
  while (keys[i + 1].tau < tau) i++;
  const a = keys[i];
  const b = keys[i + 1];
  const k = (tau - a.tau) / (b.tau - a.tau || 1);
  return [a.x + (b.x - a.x) * k, a.y + (b.y - a.y) * k];
}

/** Les joueurs visibles à l'instant tau : interpolés entre deux images 360, en fondu sinon. */
function dotsAt(tl, tau) {
  const { frames } = tl;
  if (!frames.length) return [];
  let i = frames.findIndex((f) => f.tau > tau);
  if (i === -1) i = frames.length;
  const a = frames[Math.max(0, i - 1)];
  const b = frames[Math.min(frames.length - 1, i)];
  const k = a === b ? 0 : Math.min(1, Math.max(0, (tau - a.tau) / (b.tau - a.tau)));
  const out = [];
  const ids = new Set([...a.dots.keys(), ...b.dots.keys()]);
  for (const id of ids) {
    const p = a.dots.get(id);
    const q = b.dots.get(id);
    if (p && q) out.push({ x: p[0] + (q[0] - p[0]) * k, y: p[1] + (q[1] - p[1]) * k, us: p[2], keeper: p[4] || q[4], alpha: 1 });
    else if (p) out.push({ x: p[0], y: p[1], us: p[2], keeper: p[4], alpha: 1 - k });
    else out.push({ x: q[0], y: q[1], us: q[2], keeper: q[4], alpha: k });
  }
  return out;
}

function chalkLine(ctx, pts, rnd, width, color, alpha = 0.8) {
  ctx.save();
  ctx.strokeStyle = color;
  ctx.globalAlpha = alpha;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  for (let pass = 0; pass < 2; pass++) {
    ctx.lineWidth = pass ? width * 0.45 : width;
    ctx.globalAlpha = alpha * (pass ? 0.55 : 0.9);
    ctx.beginPath();
    pts.forEach(([x, y], i) => {
      const jx = x + (rnd() - 0.5) * 1.6;
      const jy = y + (rnd() - 0.5) * 1.6;
      if (i) ctx.lineTo(jx, jy); else ctx.moveTo(jx, jy);
    });
    ctx.stroke();
  }
  ctx.restore();
}

function seg(a, b, n = 8) {
  return Array.from({ length: n + 1 }, (_, i) => [a[0] + ((b[0] - a[0]) * i) / n, a[1] + ((b[1] - a[1]) * i) / n]);
}

function drawPitch(ctx, P, k) {
  const rnd = rand(11);
  const L = (pts) => chalkLine(ctx, pts.map(([x, y]) => P(x, y)), rnd, 2.2, COLORS.craie, 0.7);
  L([...seg([0, 0], [PX, 0]), ...seg([PX, 0], [PX, PY]), ...seg([PX, PY], [0, PY]), ...seg([0, PY], [0, 0])]);
  L(seg([PX / 2, 0], [PX / 2, PY]));
  for (const [gx, sg] of [[0, 1], [PX, -1]]) {
    L([[gx, 13.84], [gx + sg * 16.5, 13.84], [gx + sg * 16.5, 54.16], [gx, 54.16]].flatMap((p, i, arr) => (i ? seg(arr[i - 1], p, 6) : [p])));
    L([[gx, 24.84], [gx + sg * 5.5, 24.84], [gx + sg * 5.5, 43.16], [gx, 43.16]]);
  }
  const c = Array.from({ length: 41 }, (_, i) => [PX / 2 + 9.15 * Math.cos((i / 40) * 2 * Math.PI), PY / 2 + 9.15 * Math.sin((i / 40) * 2 * Math.PI)]);
  L(c);
  ctx.fillStyle = COLORS.craie;
  for (const [x, y] of [[11, PY / 2], [PX - 11, PY / 2], [PX / 2, PY / 2]]) { const [px, py] = P(x, y); ctx.beginPath(); ctx.arc(px, py, k * 0.35, 0, 7); ctx.fill(); }
  // le but visé, à droite
  ctx.strokeStyle = COLORS.craie;
  ctx.lineWidth = 3;
  const [gx0, gy0] = P(PX, PY / 2 - 3.66);
  const [gx1, gy1] = P(PX + 1.6, PY / 2 + 3.66);
  ctx.strokeRect(gx0, gy0, gx1 - gx0, gy1 - gy0);
}

/**
 * Dessine l'instant t (secondes depuis le début de la séquence).
 * `labels` : { title, sub } en haut du dessin.
 */
export function render(canvas, goal, tl, t, labels = {}) {
  const ctx = canvas.getContext("2d");
  const W = canvas.width;
  const H = canvas.height;
  const pad = W * 0.04;
  const top = H * 0.16;
  const k = Math.min((W - 2 * pad) / (PX + 2), (H - top - pad) / PY);
  const ox = (W - k * (PX + 2)) / 2;
  const oy = top;
  const P = (x, y) => [ox + x * k, oy + y * k];
  ctx.fillStyle = COLORS.ardoise;
  ctx.fillRect(0, 0, W, H);
  // grain de l'ardoise
  const g = rand(3);
  ctx.fillStyle = "rgba(236,231,220,0.035)";
  for (let i = 0; i < 900; i++) ctx.fillRect(g() * W, g() * H, 1.2, 1.2);
  drawPitch(ctx, P, k);
  const us = COLORS[goal.side];
  const them = COLORS[goal.side === "home" ? "away" : "home"];
  const tau = Math.min(t, tl.end);
  // trace du ballon déjà parcourue
  const trail = [];
  for (let s = 0; s <= tau; s += 0.12) trail.push(P(...ballAt(tl, s)));
  if (trail.length > 1) {
    ctx.save();
    ctx.setLineDash([6, 6]);
    chalkLine(ctx, trail, rand(5), 2, COLORS.craie, 0.5);
    ctx.restore();
  }
  // joueurs
  for (const d of dotsAt(tl, tau)) {
    const [x, y] = P(d.x, d.y);
    ctx.globalAlpha = 0.95 * d.alpha;
    ctx.fillStyle = d.us ? us : them;
    ctx.beginPath();
    ctx.arc(x, y, k * 0.95, 0, 7);
    ctx.fill();
    if (d.keeper) {
      ctx.strokeStyle = COLORS.craie;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.arc(x, y, k * 1.35, 0, 7);
      ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
  // ballon et porteur
  const [bx, by] = P(...ballAt(tl, tau));
  const cur = [...tl.keys].reverse().find((s) => s.tau <= tau) ?? tl.keys[0];
  ctx.strokeStyle = COLORS.corail;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.arc(bx, by, k * 1.25, 0, 7);
  ctx.stroke();
  ctx.fillStyle = COLORS.corail;
  ctx.beginPath();
  ctx.arc(bx, by, k * 0.45, 0, 7);
  ctx.fill();
  if (cur.name && t < tl.end + 0.3) {
    ctx.font = `${Math.round(k * 3.2)}px ${HAND}`;
    ctx.textAlign = "center";
    ctx.fillStyle = cur.ours ? us : them;
    ctx.fillText(cur.name.split(" ").slice(-1)[0], bx, by - k * 2.2);
  }
  // titre et but
  ctx.textAlign = "left";
  ctx.fillStyle = COLORS.craie;
  ctx.font = `${Math.round(H * 0.06)}px ${HAND}`;
  if (labels.title) ctx.fillText(labels.title, pad, H * 0.085);
  ctx.fillStyle = COLORS.gris;
  if (labels.sub) fitText(ctx, labels.sub, pad, H * 0.13, W - 2 * pad, Math.round(H * 0.03), MONO);
  if (t >= tl.end) {
    const a = Math.min(1, (t - tl.end) / 0.4);
    ctx.globalAlpha = a;
    ctx.fillStyle = COLORS.corail;
    ctx.textAlign = "right";
    ctx.font = `${Math.round(H * 0.11)}px ${HAND}`;
    ctx.fillText(labels.goal ?? "But !", W - pad, H * 0.11);
    ctx.globalAlpha = 1;
  }
}

/** Un lecteur : canvas, lecture/pause, export vidéo. Renvoie une fonction pour l'arrêter. */
export function mountReplay(host, goal, { t, title, sub, file }) {
  host.innerHTML = `<div class="replay-box">
      <canvas width="1280" height="900" aria-label="${title}"></canvas>
      <div class="replay-bar">
        <button type="button" class="play">${t("replay_pause")}</button>
        <input type="range" min="0" max="1000" value="0" aria-label="${t("replay_seek")}">
        <button type="button" class="rec">${t("replay_export")}</button>
      </div>
      <p class="legend">${t(goal.has_360 ? "replay_legend_360" : "replay_legend_events")}</p>
    </div>`;
  const canvas = host.querySelector("canvas");
  const tl = timeline(goal);
  const labels = { title, sub, goal: t("replay_goal") };
  let playing = true;
  let clock = 0;
  let last = performance.now();
  let raf = 0;
  const seek = host.querySelector("input");
  const play = host.querySelector(".play");
  const frame = (now) => {
    if (playing) clock += (now - last) / 1000;
    last = now;
    if (clock > tl.duration) { clock = tl.duration; playing = false; play.textContent = t("replay_again"); }
    render(canvas, goal, tl, clock, labels);
    seek.value = String(Math.round((clock / tl.duration) * 1000));
    raf = requestAnimationFrame(frame);
  };
  raf = requestAnimationFrame(frame);
  play.addEventListener("click", () => {
    if (clock >= tl.duration) clock = 0;
    playing = !playing;
    play.textContent = t(playing ? "replay_pause" : "replay_play");
  });
  seek.addEventListener("input", () => { clock = (Number(seek.value) / 1000) * tl.duration; });
  host.querySelector(".rec").addEventListener("click", (e) => recordAnimation(
    { width: canvas.width, height: canvas.height, duration: tl.duration, draw: (c, s) => render(c, goal, tl, s, labels) },
    file, e.currentTarget, t,
  ));
  return () => cancelAnimationFrame(raf);
}

/** Export dans le navigateur : on rejoue l'animation dans un canvas caché et on l'enregistre
 * (MP4 si le navigateur sait l'encoder, sinon WebM). `draw(canvas, s)` dessine l'instant s. */
export async function recordAnimation({ width, height, duration, draw }, file, btn, t) {
  if (!window.MediaRecorder) { btn.textContent = t("replay_no_export"); return; }
  const canvas = document.createElement("canvas");
  canvas.width = width;
  canvas.height = height;
  const stream = canvas.captureStream(30);
  const type = ["video/mp4;codecs=avc1", "video/mp4", "video/webm;codecs=vp9", "video/webm"].find((m) => MediaRecorder.isTypeSupported(m));
  const rec = new MediaRecorder(stream, { mimeType: type, videoBitsPerSecond: 4_000_000 });
  const chunks = [];
  rec.ondataavailable = (e) => e.data.size && chunks.push(e.data);
  const done = new Promise((ok) => { rec.onstop = ok; });
  const label = btn.textContent;
  btn.disabled = true;
  btn.textContent = t("replay_recording");
  rec.start();
  const start = performance.now();
  await new Promise((ok) => {
    const step = (now) => {
      const s = (now - start) / 1000;
      draw(canvas, s);
      if (s < duration) requestAnimationFrame(step); else ok();
    };
    requestAnimationFrame(step);
  });
  rec.stop();
  await done;
  const ext = type.includes("mp4") ? "mp4" : "webm";
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(chunks, { type }));
  a.download = `${file}.${ext}`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 4000);
  btn.disabled = false;
  btn.textContent = label;
}

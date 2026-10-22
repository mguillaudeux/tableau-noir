// Le coin de l'analyste : le commentaire écrit d'une section, avec les noms d'équipe à la bonne forme.

import { fillTeams } from "./i18n.js";

export function analystBlock(d, section, lang, t, esc) {
  const n = d.analyst?.[section]?.[lang];
  if (!n) return "";
  const f = (s) => esc(fillTeams(s, d.meta, lang));
  return `<aside class="analyst" aria-label="${esc(t("analyst_title"))}">
    <h3>${esc(t("analyst_title"))}</h3>
    <p class="lead">${f(n.lead)}</p>
    ${n.keys.length ? `<h4>${esc(t("analyst_keys"))}</h4><ul>${n.keys.map((k) => `<li>${f(k)}</li>`).join("")}</ul>` : ""}
    ${n.impact ? `<h4>${esc(t("analyst_impact"))}</h4><p>${f(n.impact)}</p>` : ""}
  </aside>`;
}

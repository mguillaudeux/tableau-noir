"""Le coin de l'analyste : un commentaire écrit pour chaque section de chaque match.

Les textes sont construits à partir des chiffres calculés (rien n'est inventé) : on repère les
faits saillants d'une section (écarts entre les équipes, écarts à la moyenne de la compétition),
on les relie au score, puis on les raconte avec des tournures variées, choisies de façon
reproductible pour chaque match.

Les noms d'équipe ne sont pas écrits ici : le texte contient des marqueurs que le site remplace
selon la langue, avec le bon article en français (`{T:home:sub}` → « l'Argentine »,
`{T:away:de}` → « de la France », `{T:home:pos}` → « Argentina's »…).
"""

from __future__ import annotations

import random
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

SIDES = ("home", "away")
OTHER = {"home": "away", "away": "home"}
Note = dict[str, dict[str, Any]]


# --- Mise en forme bilingue ----------------------------------------------------------------------


@dataclass(frozen=True)
class N:
    """Un nombre, écrit à la française (virgule) ou à l'anglaise (point)."""

    v: float
    d: int = 1
    sign: bool = False

    def render(self, lang: str) -> str:
        s = f"{self.v:+.{self.d}f}" if self.sign else f"{self.v:.{self.d}f}"
        s = s.replace("-", "−")
        return s.replace(".", ",") if lang == "fr" else s


@dataclass(frozen=True)
class P:
    """Une part (0–1), écrite en pourcentage."""

    v: float

    def render(self, lang: str) -> str:
        return f"{round(self.v * 100)} %" if lang == "fr" else f"{round(self.v * 100)}%"


@dataclass(frozen=True)
class L:
    """Un bout de texte qui change selon la langue."""

    fr: str
    en: str

    def render(self, lang: str) -> str:
        return self.fr if lang == "fr" else self.en


def T(side: str, form: str = "sub") -> str:  # noqa: N802 (marqueur court, lisible dans les phrases)
    """Marqueur de nom d'équipe : sub (« l'Argentine »), Sub (majuscule), de, a, bare, pos."""
    return f"{{T:{side}:{form}}}"


Pair = tuple[str, str]


def say(fr: str, en: str, **kw: Any) -> Pair:
    def fill(text: str, lang: str) -> str:
        vals = {k: v.render(lang) if isinstance(v, N | P | L) else v for k, v in kw.items()}
        # les marqueurs d'équipe {T:…} sont laissés tels quels pour le site
        for k, v in vals.items():
            text = text.replace("{" + k + "}", str(v))
        return text

    return fill(fr, "fr"), fill(en, "en")


class Writer:
    """Assemble une note : une accroche, des clés, ce que ça a changé dans le match."""

    def __init__(self, seed: str) -> None:
        self.rng = random.Random(zlib.crc32(seed.encode()))
        self.base = self.rng.randrange(1000)
        self.calls = 0
        self.lead: list[Pair] = []
        self.keys: list[Pair] = []
        self.impact: list[Pair] = []

    def pick(self, *options: Pair) -> Pair:
        """Une tournure parmi plusieurs : le point de départ est tiré au sort (reproductible), puis
        on tourne, pour que deux phrases voisines ne se ressemblent pas."""
        self.calls += 1
        return options[(self.base + self.calls) % len(options)]

    def note(self) -> dict[str, dict[str, Any]]:
        out = {}
        for i, lang in enumerate(("fr", "en")):
            out[lang] = {
                "lead": " ".join(p[i] for p in self.lead),
                "keys": [p[i] for p in self.keys],
                "impact": " ".join(p[i] for p in self.impact),
            }
        return out


# --- Le contexte d'un match ---------------------------------------------------------------------


@dataclass
class Game:
    d: dict[str, Any]
    ctx: dict[str, Any]
    table: dict[str, Any]

    @property
    def id(self) -> str:
        return str(self.d["meta"]["id"])

    def score(self, s: str) -> int:
        return int(self.d["meta"][s]["score"])

    @property
    def winner(self) -> str | None:
        """Le vainqueur, tirs au but compris ; None pour un nul."""
        h, a = self.score("home"), self.score("away")
        if h != a:
            return "home" if h > a else "away"
        ph, pa = self.d["meta"]["home"].get("penalties"), self.d["meta"]["away"].get("penalties")
        if ph is not None and pa is not None and ph != pa:
            return "home" if ph > pa else "away"
        return None

    @property
    def on_pens(self) -> bool:
        return self.score("home") == self.score("away") and self.winner is not None

    def st(self, s: str, k: str) -> Any:
        return self.d["stats"][s].get(k)

    def tm(self, s: str) -> dict[str, Any]:
        out: dict[str, Any] = self.d["team"][s]
        return out

    def mean(self, group: str, key: str) -> float | None:
        v = self.ctx.get("stats", {}).get(group, {}).get(key)
        return None if v is None else float(v["mean"])

    def sd(self, group: str, key: str) -> float | None:
        v = self.ctx.get("stats", {}).get(group, {}).get(key)
        return None if v is None else float(v["sd"])

    def players(self, s: str | None = None) -> list[dict[str, Any]]:
        return [p for p in self.d["players"] if s is None or p["side"] == s]

    @property
    def has_360(self) -> bool:
        return bool(self.d["meta"].get("has_360"))


def _result_line(g: Game) -> Pair:
    w = g.winner
    sh, sa = g.score("home"), g.score("away")
    if w is None:
        return say(
            "Score final : {h}–{a}, et personne ne repart avec les trois points.",
            "Final score: {h}–{a}, and nobody takes the points.",
            h=str(sh),
            a=str(sa),
        )
    final = g.d["meta"].get("stage") == "Final"
    if final and g.on_pens:
        return say(
            f"{T(w, 'Sub')} remporte la finale aux tirs au but, après un {{h}}–{{a}} qui n'avait "
            "rien tranché.",
            f"{T(w)} win the final on penalties, after a {{h}}–{{a}} that had settled nothing.",
            h=str(sh),
            a=str(sa),
        )
    if final:
        return say(
            f"{T(w, 'Sub')} remporte la finale {{w}}–{{l}}.",
            f"{T(w)} win the final {{w}}–{{l}}.",
            w=str(max(sh, sa)),
            l=str(min(sh, sa)),
        )
    if g.on_pens:
        return say(
            f"{T(w, 'Sub')} passe aux tirs au but, après un {{h}}–{{a}} qui n'a rien tranché.",
            f"{T(w)} go through on penalties after a {{h}}–{{a}} that settled nothing.",
            h=str(sh),
            a=str(sa),
        )
    return say(
        f"{T(w, 'Sub')} gagne {{w}}–{{l}}.",
        f"{T(w)} win {{w}}–{{l}}.",
        w=str(max(sh, sa)),
        l=str(min(sh, sa)),
    )


def _standout(g: Game, side: str | None = None) -> dict[str, Any] | None:
    ps = g.players(side)
    if not ps:
        return None

    def score(p: dict[str, Any]) -> float:
        return float(
            p["goals"] * 2.5
            + p["assists"] * 1.6
            + p["xg"] * 0.8
            + p["key_passes"] * 0.15
            + p["progressive"] * 0.03
            + p["def_actions"] * 0.04
            + (p.get("xt") or 0) * 1.5
        )

    return max(ps, key=score)


# --- Section 1 · stats classiques ---------------------------------------------


def s1(g: Game, w: Writer) -> None:
    xh, xa = g.st("home", "xg"), g.st("away", "xg")
    win = g.winner
    lead_xg = "home" if xh >= xa else "away"
    gap = abs(xh - xa)
    w.lead.append(_result_line(g))
    if win is None:
        if gap < 0.4:
            w.lead.append(
                w.pick(
                    say(
                        "Et les xG ({h} contre {a}) valident : un partage qui se défend.",
                        "And the xG ({h} to {a}) agree: a draw, and a fair one.",
                        h=N(xh, 2),
                        a=N(xa, 2),
                    ),
                    say(
                        "Côté occasions, c'est une balance de pharmacien : {h} xG contre {a}.",
                        "In chances, the scales barely move: {h} xG to {a}.",
                        h=N(xh, 2),
                        a=N(xa, 2),
                    ),
                )
            )
        else:
            w.lead.append(
                say(
                    f"Mais {T(lead_xg, 'sub')} peut nourrir des regrets : {{x}} xG contre {{y}}, "
                    "c'est le genre d'écart qui finit d'habitude en victoire.",
                    f"But {T(lead_xg)} will feel hard done by: {{x}} xG to {{y}} usually ends in "
                    "a win.",
                    x=N(max(xh, xa), 2),
                    y=N(min(xh, xa), 2),
                )
            )
    elif lead_xg == win and gap >= 0.5:
        w.lead.append(
            w.pick(
                say(
                    "Victoire logique : {x} xG contre {y}, le tableau d'affichage n'a pas menti.",
                    "A deserved win: {x} xG to {y}, the scoreboard told the truth.",
                    x=N(max(xh, xa), 2),
                    y=N(min(xh, xa), 2),
                ),
                say(
                    "Et ce n'est pas un hold-up : {x} xG contre {y}, la domination était réelle.",
                    "And it was no smash-and-grab: {x} xG to {y}, the control was real.",
                    x=N(max(xh, xa), 2),
                    y=N(min(xh, xa), 2),
                ),
            )
        )
    elif lead_xg != win and gap >= 0.5:
        w.lead.append(
            w.pick(
                say(
                    f"Petit cambriolage : {T(win, 'sub')} gagne avec {{x}} xG seulement, face à "
                    "{y}. Le réalisme a battu le volume.",
                    f"A minor heist: {T(win)} win with just {{x}} xG against {{y}}. Ruthlessness "
                    "beat volume.",
                    x=N(g.st(win, "xg"), 2),
                    y=N(g.st(OTHER[win], "xg"), 2),
                ),
                say(
                    f"Les xG racontent une autre histoire ({{y}} contre {{x}} pour le perdant) : "
                    f"{T(win, 'sub')} a gagné le match, pas forcément la bataille des occasions.",
                    f"The xG tell another story ({{y}} to {{x}} for the losers): {T(win)} won the "
                    "match, not necessarily the battle of chances.",
                    x=N(g.st(win, "xg"), 2),
                    y=N(g.st(OTHER[win], "xg"), 2),
                ),
            )
        )
    else:
        w.lead.append(
            say(
                "Un match serré dans les chiffres ({h} xG contre {a}) : la différence s'est "
                "faite sur des détails, ou sur un pied plus adroit que l'autre.",
                "A tight one in the numbers ({h} xG to {a}): it came down to details, or to one "
                "sharper finisher.",
                h=N(xh, 2),
                a=N(xa, 2),
            )
        )
    # possession
    ph = g.st("home", "possession")
    if ph is not None:
        big = "home" if ph >= 0.5 else "away"
        share = max(ph, 1 - ph)
        if share >= 0.6:
            w.keys.append(_possession_key(big, share, win))
    # tirs et grosses occasions
    bh, ba = g.st("home", "big_chances"), g.st("away", "big_chances")
    if bh == ba == 0:
        w.keys.append(
            say(
                "Aucune grosse occasion (xG ≥ 0,30) de tout le match : les défenses ont gagné "
                "la soirée, les spectateurs un peu moins.",
                "Not a single big chance (xG ≥ 0.30) all match: the defences won the night, the "
                "crowd a little less.",
            )
        )
    else:
        w.keys.append(
            say(
                "Grosses occasions (xG ≥ 0,30) : {bh} pour {th}, {ba} pour {ta}.",
                "Big chances (xG ≥ 0.30): {bh} for {th}, {ba} for {ta}.",
                bh=str(bh),
                ba=str(ba),
                th=T("home"),
                ta=T("away"),
            )
        )
    sh, sa = g.st("home", "shots"), g.st("away", "shots")
    if max(sh, sa) >= 2 * max(1, min(sh, sa)) and max(sh, sa) >= 10:
        more = "home" if sh > sa else "away"
        w.keys.append(
            say(
                f"Mitraillage en règle : {{n}} tirs pour {T(more, 'sub')}, contre {{m}}.",
                f"Shooting gallery: {{n}} shots for {T(more)}, against {{m}}.",
                n=str(max(sh, sa)),
                m=str(min(sh, sa)),
            )
        )
    reds = [s for s in SIDES if g.st(s, "red")]
    for s in reds:
        w.keys.append(
            say(
                f"Carton rouge pour {T(s, 'sub')} : jouer à dix, c'est courir pour onze.",
                f"A red card for {T(s)}: playing with ten means running for eleven.",
            )
        )
    hero = _standout(g)
    if hero is not None:
        fr_bits, en_bits = [], []
        if hero["goals"]:
            n = hero["goals"]
            fr_bits.append(f"{n} but{'s' if n > 1 else ''}")
            en_bits.append(f"{n} goal{'s' if n > 1 else ''}")
        if hero["assists"]:
            n = hero["assists"]
            pl = "s" if n > 1 else ""
            fr_bits.append(f"{n} passe{pl} décisive{pl}")
            en_bits.append(f"{n} assist{pl}")
        if hero["xg"] >= 0.05:
            fr_bits.append(f"{N(hero['xg'], 2).render('fr')} xG")
            en_bits.append(f"{N(hero['xg'], 2).render('en')} xG")
        if (hero.get("xt") or 0) >= 0.1:
            fr_bits.append(f"{N(hero['xt'], 2).render('fr')} xT")
            en_bits.append(f"{N(hero['xt'], 2).render('en')} xT")
        if hero["key_passes"] >= 2 and len(fr_bits) < 3:
            fr_bits.append(f"{hero['key_passes']} passes clés")
            en_bits.append(f"{hero['key_passes']} key passes")
        if not fr_bits:
            fr_bits.append(f"{hero['def_actions']} actions défensives")
            en_bits.append(f"{hero['def_actions']} defensive actions")
        w.impact.append(
            say(
                "L'homme du match selon nos craies : {name} ({bits}).",
                "Man of the match, by our chalk: {name} ({bits}).",
                name=hero["name"],
                bits=L(", ".join(fr_bits), ", ".join(en_bits)),
            )
        )
    if win is not None and lead_xg != win and gap >= 0.5:
        w.impact.append(
            w.pick(
                say(
                    "Moralité : en football, on ne gagne pas aux points.",
                    "Moral of the story: football is not won on points.",
                ),
                say(
                    "Les xG mesurent les occasions, pas le sang-froid. Ce soir-là, le sang-froid "
                    "a gagné.",
                    "xG measure chances, not composure. That night, composure won.",
                ),
            )
        )


def _possession_key(big: str, share: float, win: str | None) -> Pair:
    if win == big:
        return say(
            f"{T(big, 'Sub')} a confisqué le ballon ({{p}}) et l'a transformé en victoire.",
            f"{T(big)} hogged the ball ({{p}}) and turned it into a win.",
            p=P(share),
        )
    if win is None:
        return say(
            f"{T(big, 'Sub')} a eu le ballon ({{p}}), sans réussir à faire pencher le match.",
            f"{T(big)} had the ball ({{p}}) without tipping the game.",
            p=P(share),
        )
    return say(
        f"{T(big, 'Sub')} a eu le ballon ({{p}}) et a perdu : la possession, c'est comme un "
        "abonnement à la salle, encore faut-il s'en servir.",
        f"{T(big)} had the ball ({{p}}) and lost: possession is like a gym membership, you "
        "still have to use it.",
        p=P(share),
    )


# --- Section 2 · structure ---------------------------------------------

LANE_FR = (
    "le couloir gauche",
    "le demi-espace gauche",
    "l'axe",
    "le demi-espace droit",
    "le couloir droit",
)
LANE_EN = (
    "the left wing",
    "the left half-space",
    "the centre",
    "the right half-space",
    "the right wing",
)


def s2(g: Game, w: Writer) -> None:
    for s in SIDES:
        a = g.tm(s)
        ann, fw, fo = (
            a.get("announced"),
            a["shape"].get("formation_with"),
            a["shape"].get("formation_without"),
        )
        if ann and fw and ann != fw:
            w.lead.append(
                w.pick(
                    say(
                        f"Sur la feuille, {T(s, 'sub')} était en {{ann}}. Sur le terrain, avec le "
                        "ballon, ça ressemblait plutôt à un {fw}.",
                        f"On paper, {T(s)} lined up in a {{ann}}. On the pitch, in possession, it "
                        "looked more like a {fw}.",
                        ann=ann,
                        fw=fw,
                    ),
                    say(
                        f"{T(s, 'Sub')} annonçait un {{ann}} et a attaqué en {{fw}} : la "
                        "composition d'équipe, c'est un point de départ, pas un contrat.",
                        f"{T(s)} announced a {{ann}} and attacked in a {{fw}}: a team sheet is a "
                        "starting point, not a contract.",
                        ann=ann,
                        fw=fw,
                    ),
                )
            )
        elif ann and fw:
            w.lead.append(
                say(
                    f"{T(s, 'Sub')} n'a pas touché à son {{ann}} avec le ballon.",
                    f"{T(s)} stayed true to the {{ann}} in possession.",
                    ann=ann,
                )
            )
        if fo and fw and fo != fw:
            w.keys.append(
                say(
                    f"{T(s, 'Sub')} change de peau selon la phase : {{fw}} avec le ballon, "
                    "{fo} sans.",
                    f"{T(s)} changes shape by phase: {{fw}} with the ball, {{fo}} without.",
                    fw=fw,
                    fo=fo,
                )
            )
    if not w.lead:  # pas de schéma annoncé (Wyscout) : on part de ce qu'on voit
        fw = {s: g.tm(s)["shape"].get("formation_with") for s in SIDES}
        if all(fw.values()):
            w.lead.append(
                say(
                    f"Pas de compositions officielles dans ces données, alors on lit le terrain : "
                    f"avec le ballon, {T('home', 'sub')} s'organisait en {{h}}, "
                    f"{T('away', 'sub')} en {{a}}.",
                    f"No official line-ups in this data, so we read the pitch: in possession, "
                    f"{T('home')} set up in a {{h}}, {T('away')} in a {{a}}.",
                    h=str(fw["home"]),
                    a=str(fw["away"]),
                )
            )
        else:
            w.lead.append(
                say(
                    "Des positions trop mouvantes pour en tirer un schéma net : place au jeu "
                    "dans les couloirs.",
                    "Positions too fluid to pin down a clean shape: let us look at the lanes.",
                )
            )
    # couloirs préférés
    for s in SIDES:
        grid = g.tm(s)["shape"].get("lanes")
        if not grid:
            continue
        lanes = [sum(grid[t][i] for t in range(3)) for i in range(5)]
        top = max(range(5), key=lambda i: lanes[i])
        wings = lanes[0] + lanes[4]
        final = sum(grid[2])
        if wings >= 0.5:
            w.keys.append(
                say(
                    f"{T(s, 'Sub')} a joué large : {{p}} des touches dans les deux couloirs "
                    "extérieurs.",
                    f"{T(s)} played wide: {{p}} of touches in the two outer lanes.",
                    p=P(wings),
                )
            )
        else:
            w.keys.append(
                say(
                    f"Le couloir préféré {T(s, 'de')} : {{lane}} ({{p}} des touches).",
                    f"{T(s, 'pos')} favourite lane: {{lane}} ({{p}} of touches).",
                    lane=L(LANE_FR[top], LANE_EN[top]),
                    p=P(lanes[top]),
                )
            )
        if final >= 0.3:
            w.keys.append(
                say(
                    f"{T(s, 'Sub')} a passé du temps chez l'adversaire : {{p}} de ses touches "
                    "dans le dernier tiers.",
                    f"{T(s)} camped in the opponent's half: {{p}} of touches in the final third.",
                    p=P(final),
                )
            )
    # bloc (360)
    blocks = {s: g.tm(s)["shape"].get("block") for s in SIDES}
    if all(blocks.values()):
        hi = max(SIDES, key=lambda s: blocks[s]["without_ball"]["last_line"])
        lo = OTHER[hi]
        lh = blocks[hi]["without_ball"]["last_line"]
        ll = blocks[lo]["without_ball"]["last_line"]
        mean = g.mean("block_without", "last_line")
        w.impact.append(
            say(
                f"Sans le ballon, {T(hi, 'sub')} défendait plus haut (dernière ligne à {{lh}} m "
                f"de son but, contre {{ll}} m{{mean}}).",
                f"Out of possession, {T(hi)} defended higher (back line {{lh}} m from goal, "
                f"against {{ll}} m{{mean}}).",
                lh=N(lh),
                ll=N(ll),
                mean=L(
                    f" ; moyenne du tournoi : {N(mean).render('fr')} m" if mean is not None else "",
                    f"; tournament average: {N(mean).render('en')} m" if mean is not None else "",
                ),
            )
        )
        win = g.winner
        if win == hi:
            w.impact.append(
                say(
                    "Défendre haut et gagner : la ligne a tenu, et le pari avec.",
                    "Defend high and win: the line held, and so did the gamble.",
                )
            )
        elif win == lo:
            w.impact.append(
                say(
                    f"Mais c'est le bloc le plus bas qui a gagné : {T(lo, 'sub')} a préféré "
                    "attendre, et l'attente a payé.",
                    f"But the deeper block won: {T(lo)} chose to wait, and the wait paid off.",
                )
            )
    else:
        w.impact.append(_structure_result(g))


def _structure_result(g: Game) -> Pair:
    win = g.winner
    if win is None:
        return say(
            "Deux plans de jeu qui se sont neutralisés : la structure n'a pas suffi à faire la "
            "différence.",
            "Two game plans that cancelled each other out: shape alone did not decide it.",
        )
    return say(
        f"Le plan {T(win, 'de')} a tenu jusqu'au bout. Les positions moyennes ne disent pas tout, "
        "mais elles disent qui occupait le terrain.",
        f"{T(win, 'pos')} plan held to the end. Average positions do not say everything, but "
        "they say who owned the space.",
    )


# --- Section 3 · pressing ---------------------------------------------


def s3(g: Game, w: Writer) -> None:
    pp = {s: g.st(s, "ppda") for s in SIDES}
    pr = {s: g.tm(s)["pressing"] for s in SIDES}
    valid = [s for s in SIDES if pp[s] is not None]
    # un PPDA à peine plus bas ne fait pas une équipe de presseurs : 15 % d'écart au moins
    clear = len(valid) == 2 and max(pp.values()) >= 1.15 * min(pp.values())
    if len(valid) == 2 and not clear:
        w.lead.append(
            say(
                "Pressing à armes égales : {h} et {a} de PPDA, personne n'a vraiment étouffé "
                "l'autre.",
                "Even pressing: a PPDA of {h} and {a}, nobody really smothered the other.",
                h=N(pp["home"]),
                a=N(pp["away"]),
            )
        )
    if clear:
        presser = min(SIDES, key=lambda s: pp[s])
        other = OTHER[presser]
        w.lead.append(
            w.pick(
                say(
                    f"Le pressing, c'était {T(presser, 'sub')} : un PPDA de {{a}}, contre {{b}} en "
                    "face. Comprendre : moins de passes laissées à l'adversaire avant de lui "
                    "sauter dessus.",
                    f"The pressing came from {T(presser)}: a PPDA of {{a}}, against {{b}} for the "
                    "opponents. Translation: fewer passes allowed before jumping on the ball.",
                    a=N(pp[presser]),
                    b=N(pp[other]),
                ),
                say(
                    f"{T(presser, 'Sub')} a chassé plus haut et plus vite : {{a}} passes adverses "
                    "par action défensive, contre {b}.",
                    f"{T(presser)} hunted higher and faster: {{a}} opponent passes per defensive "
                    "action, against {b}.",
                    a=N(pp[presser]),
                    b=N(pp[other]),
                ),
            )
        )
    r5 = {s: pr[s].get("regain_5s") for s in SIDES}
    if all(v is not None for v in r5.values()):
        fast = max(SIDES, key=lambda s: r5[s])
        diff = r5[fast] - r5[OTHER[fast]]
        if diff >= 0.08:
            w.keys.append(
                say(
                    f"Réaction à la perte : {T(fast, 'sub')} récupère {{a}} de ses ballons perdus "
                    "en moins de 5 s, contre {b}. Une meute.",
                    f"Reaction to losing it: {T(fast)} win back {{a}} of lost balls within 5 s, "
                    "against {b}. A pack.",
                    a=P(r5[fast]),
                    b=P(r5[OTHER[fast]]),
                )
            )
        else:
            w.keys.append(
                say(
                    "Réaction à la perte comparable : {a} et {b} des ballons perdus récupérés en "
                    "moins de 5 s.",
                    "Similar reaction to losing the ball: {a} and {b} won back within 5 s.",
                    a=P(r5["home"]),
                    b=P(r5["away"]),
                )
            )
    hr = {s: pr[s]["high_recoveries"] for s in SIDES}
    top = max(SIDES, key=lambda s: hr[s])
    if hr[top] >= 5:
        w.keys.append(
            say(
                f"{{n}} récupérations hautes pour {T(top, 'sub')} (ballons perdus par "
                "l'adversaire dans ses 35 derniers mètres) : autant de départs d'actions à deux "
                "pas du but.",
                f"{{n}} high regains for {T(top)} (balls lost by the opponent in their own "
                "35 metres): that many attacks starting next to goal.",
                n=str(hr[top]),
            )
        )
    cp = {s: pr[s].get("counterpress_share") for s in SIDES}
    if all(v is not None for v in cp.values()):
        c = max(SIDES, key=lambda s: cp[s])
        mean = g.mean("pressing", "counterpress_share")
        if mean is not None and cp[c] >= mean + 0.04:
            w.keys.append(
                say(
                    f"{T(c, 'Sub')} a contre-pressé fort : {{a}} de ses pressions tombent dans "
                    "les 5 s qui suivent une perte (moyenne du tournoi : {m}).",
                    f"Heavy counter-pressing from {T(c)}: {{a}} of pressures come within 5 s of "
                    "a loss (tournament average: {m}).",
                    a=P(cp[c]),
                    m=P(mean),
                )
            )
    if pr["home"]["source"] != "pressures":
        w.keys.append(
            say(
                "Données Wyscout : pas de pressions enregistrées, on lit le pressing à travers "
                "les tacles, interceptions et fautes.",
                "Wyscout data: no pressure events, so pressing is read through tackles, "
                "interceptions and fouls.",
            )
        )
    win = g.winner
    if not clear:
        r5w = r5.get(win) if win else None
        r5l = r5.get(OTHER[win]) if win else None
        if win and r5w is not None and r5l is not None and r5w >= r5l + 0.08:
            w.impact.append(
                say(
                    f"À pressing égal, c'est la réaction à la perte qui a fait la différence : "
                    f"{T(win, 'sub')} récupérait plus vite, et gagne.",
                    f"With equal pressing, the reaction to losing the ball made the difference: "
                    f"{T(win)} won it back faster, and won.",
                )
            )
        else:
            w.impact.append(
                say(
                    "Le pressing n'a pas fait la différence : il faut chercher ailleurs, dans "
                    "les surfaces.",
                    "Pressing did not decide it: look elsewhere, in the boxes.",
                )
            )
    if clear:
        presser = min(SIDES, key=lambda s: pp[s])
        if win == presser:
            w.impact.append(
                w.pick(
                    say(
                        "Le pressing a dicté le tempo, et le résultat a suivi : quand on étouffe "
                        "l'adversaire, il finit par lâcher.",
                        "The press set the tempo and the result followed: squeeze long enough "
                        "and the opponent cracks.",
                    ),
                    say(
                        f"Victoire du collectif qui court : {T(presser, 'sub')} a gagné le match "
                        "en le jouant dans le camp adverse.",
                        f"A win for the team that ran: {T(presser)} won the game by playing it "
                        "in the opponent's half.",
                    ),
                )
            )
        elif win == OTHER[presser]:
            w.impact.append(
                w.pick(
                    say(
                        f"Ironie du soir : c'est l'équipe qui pressait le moins qui gagne. "
                        f"{T(win, 'Sub')} a laissé venir, encaissé le pressing, et puni.",
                        f"Irony of the night: the team that pressed less won. {T(win)} let it "
                        "come, absorbed the press and punished.",
                    ),
                    say(
                        "Presser ne suffit pas : encore faut-il que les ballons récupérés se "
                        "transforment. Ici, ils ne l'ont pas fait.",
                        "Pressing is not enough: the regained balls still have to turn into "
                        "something. Here, they did not.",
                    ),
                )
            )
        else:
            w.impact.append(
                say(
                    "Beaucoup d'efforts des deux côtés, aucun vainqueur : le pressing a usé les "
                    "jambes plus que le score.",
                    "Plenty of effort on both sides, no winner: the press wore out legs more "
                    "than the scoreline.",
                )
            )


# --- Section 4 · relationnisme ---------------------------------------------


def relation_index(rel: dict[str, Any], stats: dict[str, Any]) -> float | None:
    from tableau_noir.team import relation_index as ri

    return ri(rel, stats)


def _hub(g: Game, s: str) -> tuple[str, int] | None:
    net = g.tm(s).get("network") or []
    deg: dict[str, int] = {}
    for a, b, n in net:
        deg[a] = deg.get(a, 0) + n
        deg[b] = deg.get(b, 0) + n
    if not deg:
        return None
    pid = max(deg, key=lambda k: deg[k])
    name = next((p["name"] for p in g.players(s) if p["id"] == pid), None)
    return (name, deg[pid]) if name else None


def s4(g: Game, w: Writer) -> None:
    stats = g.ctx.get("stats", {}).get("relation", {})
    idx = {s: relation_index(g.tm(s)["relation"], stats) for s in SIDES}
    if None in idx.values():
        w.lead.append(
            say(
                "Pas assez de matière pour placer les deux équipes sur l'axe.",
                "Not enough material to place both teams on the axis.",
            )
        )
        return
    ix: dict[str, float] = {s: float(v) for s, v in idx.items() if v is not None}
    rel = max(SIDES, key=lambda s: ix[s])
    pos = OTHER[rel]
    gap = ix[rel] - ix[pos]
    if gap >= 0.6:
        w.lead.append(
            w.pick(
                say(
                    f"Choc des philosophies : {T(rel, 'sub')} ({{a}}) jouait autour du ballon, "
                    f"{T(pos, 'sub')} ({{b}}) tenait ses postes.",
                    f"Clash of philosophies: {T(rel)} ({{a}}) played around the ball, {T(pos)} "
                    "({b}) held their positions.",
                    a=N(ix[rel], 2, sign=True),
                    b=N(ix[pos], 2, sign=True),
                ),
                say(
                    f"D'un côté, {T(rel, 'sub')} et ses petits triangles près du ballon "
                    f"({{a}}) ; de l'autre, {T(pos, 'sub')} et ses couloirs bien rangés ({{b}}).",
                    f"On one side, {T(rel)} and their little triangles near the ball ({{a}}); on "
                    f"the other, {T(pos)} and their tidy lanes ({{b}}).",
                    a=N(ix[rel], 2, sign=True),
                    b=N(ix[pos], 2, sign=True),
                ),
            )
        )
    else:
        w.lead.append(
            say(
                "Deux équipes proches sur l'axe ({h} et {a}) : pas de choc de styles, plutôt "
                "un duel de mêmes recettes.",
                "Two teams close on the axis ({h} and {a}): no clash of styles, more of a "
                "mirror match.",
                h=N(ix["home"], 2, sign=True),
                a=N(ix["away"], 2, sign=True),
            )
        )
    for s in SIDES:
        r = g.tm(s)["relation"]
        short = r.get("short_share")
        m = g.mean("relation", "short_share")
        if short is not None and m is not None and abs(short - m) >= 0.05:
            w.keys.append(
                say(
                    f"{T(s, 'Sub')} : {{a}} de passes courtes (moins de 15 m), contre {{m}} en "
                    "moyenne.",
                    f"{T(s)}: {{a}} short passes (under 15 m), against {{m}} on average.",
                    a=P(short),
                    m=P(m),
                )
            )
        hub = _hub(g, s)
        if hub:
            w.keys.append(
                say(
                    f"Le carrefour du réseau {T(s, 'de')} : {{name}}, impliqué dans {{n}} passes "
                    "entre titulaires.",
                    f"The hub of {T(s, 'pos')} network: {{name}}, involved in {{n}} passes "
                    "between starters.",
                    name=hub[0],
                    n=str(hub[1]),
                )
            )
    win = g.winner
    if win is None:
        w.impact.append(
            say(
                "Le match nul rappelle une évidence : aucun style ne garantit un résultat.",
                "The draw is a reminder: no style guarantees a result.",
            )
        )
    elif gap >= 0.6:
        w.impact.append(
            say(
                "Et cette fois, c'est le football {style} qui l'emporte. Ce n'est pas une loi, "
                "c'est un match.",
                "And this time, {style} football wins. It is not a law, it is a match.",
                style=L("relationniste", "relational")
                if win == rel
                else L("positionniste", "positional"),
            )
        )
    else:
        w.impact.append(
            say(
                f"À style égal, c'est l'exécution qui tranche : avantage {T(win, 'bare')}.",
                f"With similar styles, execution decides: advantage {T(win)}.",
            )
        )


# --- Section 5 · replis ---------------------------------------------


def s5(g: Game, w: Writer) -> None:
    rec = {s: g.tm(s)["recovery"] for s in SIDES}
    sh = {s: rec[s]["shots_against"] for s in SIDES}
    xg = {s: rec[s]["xg_against"] or 0.0 for s in SIDES}
    worst = max(SIDES, key=lambda s: (xg[s], sh[s]))
    best = OTHER[worst]
    tilted = xg[worst] - xg[best] >= 0.3 or sh[worst] - sh[best] >= 3
    if not tilted:
        w.lead.append(
            say(
                "Transitions sous contrôle des deux côtés : {h} tir(s) concédé(s) après une perte "
                "pour {th}, {a} pour {ta}.",
                "Transitions under control on both sides: {h} shot(s) conceded after a loss for "
                "{th}, {a} for {ta}.",
                h=str(sh["home"]),
                a=str(sh["away"]),
                th=T("home"),
                ta=T("away"),
            )
        )
    else:
        w.lead.append(
            w.pick(
                say(
                    f"Les transitions ont fait mal à {T(worst, 'sub')} : {{n}} tirs concédés "
                    "dans les 15 s qui suivent une perte ({x} xG), contre {m} en face.",
                    f"Transitions hurt {T(worst)}: {{n}} shots conceded within 15 s of losing the "
                    "ball ({x} xG), against {m} at the other end.",
                    n=str(sh[worst]),
                    x=N(xg[worst], 2),
                    m=str(sh[best]),
                ),
                say(
                    f"Perdre le ballon coûtait plus cher à {T(worst, 'sub')} : {{n}} tirs adverses "
                    "en transition ({x} xG), contre {m} pour l'autre camp.",
                    f"Losing the ball cost {T(worst)} more: {{n}} opponent shots in transition "
                    "({x} xG), against {m} the other way.",
                    n=str(sh[worst]),
                    x=N(xg[worst], 2),
                    m=str(sh[best]),
                ),
            )
        )
    for s in SIDES:
        gm = rec[s].get("goal_minutes") or []
        if gm:
            mins = ", ".join(f"{m}'" for m in gm)
            w.keys.append(
                say(
                    f"But{{s}} encaissé{{s}} en transition par {T(s, 'sub')} : {{mins}}. Le "
                    "repli arrivait en retard.",
                    f"Goal{{s}} conceded in transition by {T(s)}: {{mins}}. The recovery run "
                    "came too late.",
                    s="s" if len(gm) > 1 else "",
                    mins=mins,
                )
            )
    if g.has_360 and all(rec[s].get("behind_ball") is not None for s in SIDES):
        for s in SIDES:
            r = rec[s]
            w.keys.append(
                say(
                    f"{T(s, 'Sub')} : {{a}} joueurs derrière le ballon à la perte, {{b}} quelques "
                    "secondes plus tard ; bloc reformé (7 joueurs ou plus) dans {c} des cas.",
                    f"{T(s)}: {{a}} players behind the ball at the loss, {{b}} a few seconds "
                    "later; block rebuilt (7+ players) in {c} of cases.",
                    a=N(r["behind_ball"]),
                    b=N(r["behind_8s"]),
                    c=P(r["back_7plus"] or 0),
                )
            )
    else:
        w.keys.append(
            say(
                "Sans 360, on ne voit pas les courses de repli : seuls les tirs concédés "
                "racontent l'histoire.",
                "Without 360, recovery runs are invisible: only the shots conceded tell the story.",
            )
        )
    win = g.winner
    if not tilted:
        w.impact.append(
            say(
                "Personne n'a été puni en transition : le match s'est joué en attaque placée.",
                "Nobody got punished in transition: the match was decided in settled play.",
            )
        )
    elif win is not None and win == best:
        w.impact.append(
            w.pick(
                say(
                    "Le match s'est en partie joué là : mieux gérer ses pertes, c'est souvent "
                    "mieux gérer le score.",
                    "Part of the match was decided right there: managing your losses is often "
                    "managing the scoreline.",
                ),
                say(
                    "Un rappel utile : on ne perd pas un match quand on perd le ballon, mais quand "
                    "on oublie de revenir.",
                    "A useful reminder: you do not lose a match when you lose the ball, but when "
                    "you forget to run back.",
                ),
            )
        )
    elif win is not None and win == worst:
        w.impact.append(
            say(
                f"Paradoxe : {T(win, 'sub')} gagne en ayant plus souffert en transition. Il "
                "fallait un gardien, une défense ou un adversaire maladroit pour compenser.",
                f"Paradox: {T(win)} win despite suffering more in transition. A goalkeeper, a "
                "last-ditch defence or a wasteful opponent made up for it.",
            )
        )
    else:
        w.impact.append(
            say(
                "Les transitions n'ont pas fait basculer le match, mais elles ont fait monter "
                "la tension.",
                "Transitions did not swing the match, but they raised the temperature.",
            )
        )


# --- Section 6 · gravité ---------------------------------------------


def s6(g: Game, w: Writer) -> None:
    key = "gravity" if g.has_360 else "attention"
    ps = [p for p in g.players() if p.get(key) is not None and p.get("role") != "GK"]
    if not ps:
        w.lead.append(say("Pas assez de touches pour mesurer la gravité.", "Not enough touches."))
        return
    ps.sort(key=lambda p: -p[key])
    top = ps[0]
    if key == "gravity":
        w.lead.append(
            w.pick(
                say(
                    "L'aimant du match : {name}. À chaque touche, {v} adversaire de plus "
                    "que la moyenne du tournoi au même endroit, dans un rayon de 10 m.",
                    "The magnet of the match: {name}. On every touch, {v} more opponents than "
                    "the tournament average in the same zone, within 10 m.",
                    name=top["name"],
                    v=N(top[key], 2),
                ),
                say(
                    "{name} avait un fan-club, et il portait le maillot adverse : {v} "
                    "adversaire par touche de plus que la normale, dans les 10 m.",
                    "{name} had a fan club, wearing the other shirt: {v} extra opponents per "
                    "touch within 10 m.",
                    name=top["name"],
                    v=N(top[key], 2),
                ),
            )
        )
    else:
        w.lead.append(
            say(
                "Sans 360, on mesure l'attention reçue : {name} a subi {v} actions défensives "
                "de plus que la normale pour 10 touches.",
                "Without 360, we measure attention received: {name} drew {v} more defensive "
                "actions than normal per 10 touches.",
                name=top["name"],
                v=N(top[key], 2),
            )
        )
    for p in ps[1:4]:
        w.keys.append(
            say(
                f"{{name}} ({T(p['side'], 'bare')}) : {{v}}.",
                f"{{name}} ({T(p['side'])}): {{v}}.",
                name=p["name"],
                v=N(p[key], 2, sign=True),
            )
        )
    low = ps[-1]
    if low[key] < 0 and low is not top:
        w.keys.append(
            say(
                "À l'autre bout, {name} ({v}) a joué dans un relatif anonymat : parfois, c'est "
                "exactement ce qu'on cherche.",
                "At the other end, {name} ({v}) played in relative peace: sometimes that is "
                "exactly the point.",
                name=low["name"],
                v=N(low[key], 2, sign=True),
            )
        )
    # implication : l'aimant a-t-il pesé sur le score ?
    contrib = top["goals"] + top["assists"]
    if contrib:
        w.impact.append(
            say(
                "Et l'attention était méritée : {name} a quand même pesé sur le score ({c} "
                "but(s) ou passe(s) décisive(s)). Le marquer, c'était nécessaire ; ce n'était "
                "pas suffisant.",
                "And the attention was deserved: {name} still weighed on the scoreline ({c} "
                "goal(s) or assist(s)). Marking him was necessary, not sufficient.",
                name=top["name"],
                c=str(contrib),
            )
        )
    else:
        mates = [
            p for p in g.players(top["side"]) if p["id"] != top["id"] and p["goals"] + p["assists"]
        ]
        if mates:
            names = L(
                " et ".join(p["name"] for p in mates[:2]),
                " and ".join(p["name"] for p in mates[:2]),
            )
            w.impact.append(
                say(
                    "{name} n'a pas marqué, mais en attirant les regards il a ouvert la porte à "
                    "d'autres : {others} ont fini décisifs. C'est ça, la gravité.",
                    "{name} did not score, but by drawing eyes he opened the door for others: "
                    "{others} ended up decisive. That is gravity.",
                    name=top["name"],
                    others=names,
                )
            )
        else:
            w.impact.append(
                say(
                    "{name} a aspiré la défense, sans que personne n'en profite : de la gravité "
                    "sans satellite.",
                    "{name} pulled the defence in, but nobody cashed in: gravity without a "
                    "satellite.",
                    name=top["name"],
                )
            )


# --- Section 7 · valeur des actions ---------------------------------------------


def s7(g: Game, w: Writer) -> None:
    tot = {s: sum(p.get("xt") or 0 for p in g.players(s)) for s in SIDES}
    more = max(SIDES, key=lambda s: tot[s])
    w.lead.append(
        say(
            f"Menace créée balle au pied et à la passe (xT) : {{a}} pour {T('home', 'sub')}, "
            f"{{b}} pour {T('away', 'sub')}.",
            f"Threat created by passes and carries (xT): {{a}} for {T('home')}, {{b}} for "
            f"{T('away')}.",
            a=N(tot["home"], 2),
            b=N(tot["away"], 2),
        )
    )
    best = max(g.players(), key=lambda p: p.get("xt") or 0)
    share = (best.get("xt") or 0) / tot[best["side"]] if tot[best["side"]] > 0 else 0
    w.lead.append(
        w.pick(
            say(
                "Le meilleur créateur : {name}, {v} xT à lui seul ({s} de la menace de son "
                "équipe).",
                "Top creator: {name}, {v} xT on his own ({s} of his team's threat).",
                name=best["name"],
                v=N(best.get("xt") or 0, 2),
                s=P(share),
            ),
            say(
                "Celui qui faisait avancer le ballon vers le danger : {name} ({v} xT, {s} du "
                "total de son équipe).",
                "The man moving the ball towards danger: {name} ({v} xT, {s} of his team's total).",
                name=best["name"],
                v=N(best.get("xt") or 0, 2),
                s=P(share),
            ),
        )
    )
    acts = g.d.get("value", {}).get("actions", {})
    goals = g.d.get("goals", [])
    for s in SIDES:
        top = (acts.get(s) or [None])[0]
        if not top:
            continue
        linked = any(gl["side"] == s and 0 <= gl["minute"] - top["minute"] <= 1 for gl in goals)
        kind_fr = "passe" if top["kind"] == "pass" else "conduite de balle"
        kind_en = "pass" if top["kind"] == "pass" else "carry"
        w.keys.append(
            say(
                f"Geste le plus menaçant {T(s, 'de')} : une {{kfr}} signée {{name}} à la "
                "{m}e minute (+{v} xT){link}.",
                f"{T(s, 'pos')} most dangerous action: a {{ken}} by {{name}} in minute {{m}} "
                "(+{v} xT){link}.",
                kfr=kind_fr,
                ken=kind_en,
                name=top["name"],
                m=str(top["minute"]),
                v=N(top["xt"], 2),
                link=L(", juste avant un but", ", just before a goal") if linked else "",
            )
        )
    win = g.winner
    xg = {s: g.st(s, "xg") for s in SIDES}
    if win == more:
        w.impact.append(
            say(
                f"La menace a payé : {T(more, 'sub')} a fait avancer le ballon plus "
                "dangereusement, et le score a suivi.",
                f"Threat paid off: {T(more)} moved the ball more dangerously, and the score "
                "followed.",
            )
        )
    elif win is not None:
        w.impact.append(
            say(
                f"{T(more, 'Sub')} a créé plus de menace, mais {T(win, 'sub')} a converti la "
                "sienne ({x} xG au final). Amener le ballon près du but, c'est la moitié du "
                "travail.",
                f"{T(more)} created more threat, but {T(win)} converted theirs ({{x}} xG in the "
                "end). Getting the ball near goal is only half the job.",
                x=N(xg[win], 2),
            )
        )
    else:
        w.impact.append(
            say(
                "Le nul est cohérent avec des menaces proches, à quelques passes près.",
                "The draw fits two similar threat levels, give or take a few passes.",
            )
        )


# --- Section 8 · classements ---------------------------------------------


def _ordinal(n: int) -> str:
    suffix = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


ROLE_FR = {
    "GK": "gardiens",
    "CB": "défenseurs centraux",
    "FB": "latéraux",
    "MF": "milieux",
    "FW": "attaquants",
}
ROLE_EN = {
    "GK": "goalkeepers",
    "CB": "centre-backs",
    "FB": "full-backs",
    "MF": "midfielders",
    "FW": "forwards",
}


def s8(g: Game, w: Writer) -> None:
    tab = g.table.get("players", {})
    here = [tab[p["id"]] | {"side": p["side"]} for p in g.players() if p["id"] in tab]
    if not here:
        w.lead.append(
            say(
                "Aucun joueur de ce match n'a assez joué dans la compétition pour être classé.",
                "No player from this match played enough in the competition to be ranked.",
            )
        )
        return
    here.sort(key=lambda p: (p["rank"] / max(p["of"], 1), p["rank"]))
    first = here[0]
    w.lead.append(
        say(
            "Sur l'ensemble de la compétition, {name} pointe au {r} rang des {role} (sur {n}). "
            "Ce match, c'était aussi une vitrine.",
            "Across the whole competition, {name} ranks {r} among {role_en} (out of {n}). This "
            "match was also a showcase.",
            name=first["name"],
            r=L("1er" if first["rank"] == 1 else f"{first['rank']}e", _ordinal(first["rank"])),
            role=ROLE_FR[first["role"]],
            role_en=ROLE_EN[first["role"]],
            n=str(first["of"]),
        )
    )
    for p in here[1:4]:
        w.keys.append(
            say(
                f"{{name}} ({T(p['side'], 'bare')}) : {{r}} des {{role}} sur {{n}}.",
                f"{{name}} ({T(p['side'])}): {{r}} of {{n}} {{role_en}}.",
                name=p["name"],
                r=L("1er" if p["rank"] == 1 else f"{p['rank']}e", _ordinal(p["rank"])),
                n=str(p["of"]),
                role=ROLE_FR[p["role"]],
                role_en=ROLE_EN[p["role"]],
            )
        )
    tops = {s: sum(1 for p in here if p["side"] == s and p["rank"] <= 5) for s in SIDES}
    w.keys.append(
        say(
            f"Joueurs dans le top 5 de leur poste : {{a}} pour {T('home', 'sub')}, {{b}} pour "
            f"{T('away', 'sub')}.",
            f"Players in their position's top 5: {{a}} for {T('home')}, {{b}} for {T('away')}.",
            a=str(tops["home"]),
            b=str(tops["away"]),
        )
    )
    win = g.winner
    if win is not None and tops[win] < tops[OTHER[win]]:
        w.impact.append(
            say(
                f"Le collectif a battu les individualités : {T(win, 'sub')} gagne avec moins de "
                "joueurs au sommet des classements.",
                f"The collective beat the individuals: {T(win)} won with fewer players at the "
                "top of the rankings.",
            )
        )
    elif win is not None and tops[win] > tops[OTHER[win]]:
        w.impact.append(
            say(
                f"La hiérarchie a été respectée : {T(win, 'sub')} alignait plus de joueurs au "
                "sommet de leur poste, et ça s'est vu.",
                f"The pecking order held: {T(win)} fielded more players at the top of their "
                "position, and it showed.",
            )
        )
    else:
        w.impact.append(
            say(
                "Les classements disent qui a brillé sur la durée ; un match, lui, se joue sur "
                "quatre-vingt-dix minutes et quelques détails.",
                "Rankings tell you who shone over time; a match is played over ninety minutes "
                "and a few details.",
            )
        )


# --- Section 9 · jumeaux ---------------------------------------------

COMP_FR = {
    "wc-2022": "Coupe du monde 2022",
    "wc-2018": "Coupe du monde 2018",
    "euro-2024": "Euro 2024",
    "euro-2020": "Euro 2020",
    "euro-2016": "Euro 2016",
    "ucl-finals": "finales de Ligue des champions",
}
COMP_EN = {
    "wc-2022": "2022 World Cup",
    "wc-2018": "2018 World Cup",
    "euro-2024": "Euro 2024",
    "euro-2020": "Euro 2020",
    "euro-2016": "Euro 2016",
    "ucl-finals": "Champions League finals",
}


def s9(g: Game, w: Writer) -> None:
    tab = g.table.get("players", {})
    here = [tab[p["id"]] | {"side": p["side"]} for p in g.players() if p["id"] in tab]
    here = [p for p in here if p.get("twins")]
    if not here:
        w.lead.append(
            say(
                "Pas de jumeaux à présenter : aucun joueur de ce match n'a assez de minutes "
                "dans la compétition.",
                "No twins to show: no player from this match has enough minutes in the "
                "competition.",
            )
        )
        return
    hero_id = (_standout(g) or {}).get("id")
    star = next((p for p in here if p["id"] == hero_id), None) or max(
        here, key=lambda p: p.get("score", 0)
    )
    t = star["twins"][0]
    w.lead.append(
        w.pick(
            say(
                "Jumeau statistique pour {name} : {twin} ({team}, {comp}), similaire à {s}. "
                "Mêmes habitudes, autre maillot.",
                "{name}'s statistical twin? {twin} ({team}, {comp_en}), {s} similar. Same "
                "habits, different shirt.",
                name=star["name"],
                twin=t["name"],
                team="{TN:" + t["team"] + "}",
                comp=COMP_FR.get(t["comp"], t["comp"]),
                comp_en=COMP_EN.get(t["comp"], t["comp"]),
                s=P(max(0.0, t["sim"])),
            ),
            say(
                "Un sosie pour {name} dans les chiffres ? {twin} ({team}, {comp}), avec {s} de "
                "similarité.",
                "If {name} had a lookalike in the numbers, it would be {twin} ({team}, "
                "{comp_en}): {s} similar.",
                name=star["name"],
                twin=t["name"],
                team="{TN:" + t["team"] + "}",
                comp=COMP_FR.get(t["comp"], t["comp"]),
                comp_en=COMP_EN.get(t["comp"], t["comp"]),
                s=P(max(0.0, t["sim"])),
            ),
        )
    )
    others = [p for p in here if p["id"] != star["id"]]
    others.sort(key=lambda p: -p["twins"][0]["sim"])
    for p in others[:3]:
        tw = p["twins"][0]
        w.keys.append(
            say(
                "{name} ↔ {twin} ({comp}, {s}).",
                "{name} ↔ {twin} ({comp_en}, {s}).",
                name=p["name"],
                twin=tw["name"],
                comp=COMP_FR.get(tw["comp"], tw["comp"]),
                comp_en=COMP_EN.get(tw["comp"], tw["comp"]),
                s=P(max(0.0, tw["sim"])),
            )
        )
    w.impact.append(
        say(
            "Un jumeau n'est pas un clone : la similarité compare des profils par 90 minutes "
            "(tirs, passes, xT, défense…), pas le talent. Mais ça donne des idées au mercato.",
            "A twin is not a clone: similarity compares per-90 profiles (shots, passes, xT, "
            "defending…), not talent. Still, it gives transfer ideas.",
        )
    )


SECTIONS: dict[str, Callable[[Game, Writer], None]] = {
    "s1": s1,
    "s2": s2,
    "s3": s3,
    "s4": s4,
    "s5": s5,
    "s6": s6,
    "s7": s7,
    "s8": s8,
    "s9": s9,
}


def match_notes(d: dict[str, Any], ctx: dict[str, Any], table: dict[str, Any]) -> Note:
    """Le coin de l'analyste pour chaque section d'un match : {s1: {fr: {...}, en: {...}}, …}."""
    g = Game(d, ctx, table)
    out: Note = {}
    for key, fn in SECTIONS.items():
        w = Writer(f"{g.id}-{key}")
        fn(g, w)
        out[key] = w.note()
    return out

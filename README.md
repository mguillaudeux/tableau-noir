# Tableau Noir

**L'analyse tactique du football, à la craie.** Des matchs décortiqués à partir de données ouvertes, avec la même méthode pour tous : les stats classiques, la structure, le pressing, le relationnisme et les replis ; puis (jalons suivants) la gravité des joueurs, la valeur des actions, les classements et les jumeaux.

**Le site** : `web/`, publié par GitHub Pages à chaque push sur `main` ([`pages.yml`](.github/workflows/pages.yml)).

![Le catalogue](docs/captures/0-catalogue.png)

## Les données

| Source | Contenu utilisé | Conditions |
| --- | --- | --- |
| [Hudl StatsBomb Open Data](https://github.com/hudl/open-data) | Coupe du monde 2022, Euro 2024 et Euro 2020 (événements + 360), Coupe du monde 2018, finales de Ligue des champions 2008/09 → 2018/19 (événements) | Usage non commercial, pas de redistribution, logo StatsBomb sur toute analyse publiée |
| [Wyscout public dataset](https://figshare.com/collections/Soccer_match_event_dataset/4415000) (Pappalardo et al., 2019) | Euro 2016 (événements) ; les cinq grands championnats 2017/18 servent à entraîner le modèle d'xG | CC BY 4.0 |

Le détail des crédits est dans [`SOURCES.md`](SOURCES.md). **Les données brutes ne sont jamais versionnées** : StatsBomb est téléchargé (et mis en cache dans `data/raw/`) au moment du calcul, Wyscout est lu en local. Le site ne publie que des résultats calculés.

Tout est ramené à un **format commun** ([`model.py`](src/tableau_noir/model.py)) : un terrain de 105 × 68 m, chaque action vue depuis l'équipe qui la réalise (qui attaque vers la droite), un temps en secondes depuis le coup d'envoi. Les tirs au but ne comptent dans aucune statistique.

## Section 1 · Les stats classiques

![Finale 2022 : les stats classiques](docs/captures/1-stats-classiques.png)

Pour chaque match ([`classic.py`](src/tableau_noir/classic.py)) :

- **la feuille de match**, équipe contre équipe : xG, tirs, grosses occasions (xG ≥ 0,30), possession, passes, passes progressives, entrées dans le dernier tiers, passes clés, duels, tacles, interceptions, récupérations, PPDA, corners, fautes, cartons, hors-jeu ;
- **la course aux xG**, minute par minute, avec les buts ;
- **la carte des tirs** (taille = xG ; plein = but, cercle plein = cadré, pointillé = non cadré) ;
- **les joueurs** : les trois hommes forts du match et un tableau triable.

Quelques définitions :

- **Possession au temps** : le ballon appartient à l'équipe en possession jusqu'à l'action suivante (10 s au plus).
- **Passe progressive** (définition Wyscout) : elle rapproche le ballon du but adverse d'au moins 30 m dans son camp, 15 m en franchissant la ligne médiane, 10 m dans le camp adverse.
- **PPDA** : passes adverses dans leurs 60 % de terrain, divisées par nos tacles, interceptions et fautes dans cette zone. Plus c'est bas, plus on presse.
- **xG** : celui de StatsBomb pour ses matchs. Wyscout n'en fournit pas : le modèle de Tableau Noir ([`xg.py`](src/tableau_noir/xg.py)) est une régression logistique sur 42 499 tirs des cinq grands championnats 2017/18 (distance, angle, tête, coup franc direct) ; un penalty vaut 0,73, le taux de réussite observé.

Contrôle : sur les 292 matchs exportés, les buts recalculés à partir des événements (contre son camp compris) collent exactement au score. Sur la finale 2022, tirs et tirs cadrés (20 / 10 pour l'Argentine, 10 / 5 pour la France) collent aux chiffres officiels.

## Sections 2 à 5 · L'équipe

Calculées dans [`team.py`](src/tableau_noir/team.py). Chaque chiffre est comparé à la moyenne de la compétition (repère ⌀ sur les barres, qui vont du plus petit au plus grand match observé). Le **360** de StatsBomb (Coupe du monde 2022, Euro 2020, Euro 2024) ajoute la position des joueurs visibles à chaque action ; les autres matchs gardent les mesures tirées des événements, et le site le signale.

### 2 · Structure et couloirs

![Finale 2022 : structure](docs/captures/2-structure.png)

- **Positions moyennes** avec et sans le ballon, et la **formation réelle** qu'on en déduit : les joueurs de champ, triés de l'arrière vers l'avant, sont découpés en 3 ou 4 lignes (découpe optimale, ligne arrière de 3 à 5). Sur la finale 2022, l'Argentine annoncée en 4-3-3 joue en 3-4-3 avec le ballon.
- **Les 5 couloirs** (côté, demi-espace, axe) × 3 tiers : où l'équipe touche le ballon.
- **Le bloc** (360) : largeur, profondeur, hauteur de la dernière ligne, couloirs occupés dans le camp adverse.

### 3 · Pressing

![Finale 2022 : pressing](docs/captures/3-pressing.png)

- La carte des pressions (Wyscout n'en a pas : tacles, interceptions et fautes à la place).
- **Temps de récupération** après chaque perte en jeu (passe ratée, contrôle manqué, dribble perdu, suivi d'une touche adverse) : moins de 5 s, 5–10, 10–20, au-delà.
- PPDA, pressions par minute sans ballon, contre-pressing, hauteur des actions défensives, récupérations hautes.

### 4 · Relationnisme

![Finale 2022 : relationnisme](docs/captures/4-relationnisme.png)

Un **axe positionniste ↔ relationniste** : moyenne des écarts réduits de cinq ingrédients face à la compétition (passes courtes, combinaisons rapides, liberté latérale, proximité autour du ballon, moins les couloirs occupés), avec toutes les équipes du tournoi en points gris. Plus les **réseaux de passes** des deux équipes.

### 5 · Replis

![Finale 2022 : replis](docs/captures/5-replis.png)

Après chaque perte : combien de joueurs sont entre le ballon et leur but au moment de la perte, puis 6 à 10 s plus tard (360), et les tirs concédés dans les 15 s (événements, pour tous les matchs). Deux images 360 montrent le repli le plus net du match. Le 360 ne voit que les joueurs dans le champ de la caméra : ces chiffres sont des minima.

## La DA « Craie Exacte »

Une ardoise vert-noir, des traits de craie granuleux et doublés, quatre craies au sens fixe : **blanc = le terrain**, **jaune = l'équipe à domicile**, **bleu = l'équipe à l'extérieur**, **corail = l'alerte** (buts, cartons). Les titres sont étroits comme un panneau de stade, les annotations à la main, les chiffres en chasse fixe. [Planche](docs/da/planche-01.jpg), [intention](docs/da/craie-exacte.md).

## Lancer en local

```bash
just setup      # environnement (uv)
just xg         # modèle d'xG Wyscout (data/raw/wyscout requis)
just export     # télécharge StatsBomb, calcule tout, écrit web/data/ (≈ 2 min la première fois)
just serve      # le site : http://localhost:8000
just test       # tests Python et JavaScript
```

Pour Wyscout, déposer dans `data/raw/wyscout/` les fichiers de la collection figshare : `events/` (décompressé), `matches/` (décompressé), `players.json`, `teams.json`, `competitions.json`.

## Crédits

- Données : Hudl StatsBomb Open Data ; Wyscout, via L. Pappalardo et al., « A public data set of spatio-temporal match events in soccer competitions », *Scientific Data* 6, 236 (2019), CC BY 4.0.
- Polices (Google Fonts, licence SIL OFL) : Big Shoulders Display, Nothing You Could Do, DM Mono, Work Sans.
- Projet de passionné, pédagogique et non commercial. Aucun logo de club ni image de match.

Licence du code : MIT.

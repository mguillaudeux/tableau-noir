# Tableau Noir

**L'analyse tactique du football, à la craie.** Des matchs décortiqués à partir de données ouvertes, avec la même méthode pour tous : d'abord les stats classiques, puis (jalons suivants) la structure, le pressing, le relationnisme, les replis, la gravité des joueurs, la valeur des actions, les classements et les jumeaux.

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

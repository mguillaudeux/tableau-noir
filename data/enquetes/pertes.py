"""Enquête n° 7 · Où meurent les attaques."""

ENQUETE = {
    "slug": "pertes",
    "number": 7,
    "title": {"fr": "Où meurent les attaques", "en": "Where attacks go to die"},
    "question": {
        "fr": "Où perd-on le ballon, et lequel de ces ballons perdus finit dans nos filets ?",
        "en": "Where do teams lose the ball, and which of those losses end up in their own net?",
    },
    "answer": {
        "fr": "On perd le ballon partout, mais il ne coûte cher qu'à un seul endroit : entre 17 et 35 m de son but. Une perte à cet endroit coûte 3,9 fois plus qu'une perte dans le camp adverse. Et ce prix a grimpé : chez les clubs d'élite, perdre le ballon près de son but coûte nettement plus qu'en 2015. Pas en sélection.",
        "en": "Teams lose the ball everywhere, but it only gets expensive in one place: between 17 and 35 m from their own goal. A loss there costs 3.9 times more than a loss in the opponent's half. And that price has risen: against elite clubs, losing the ball near your goal costs clearly more than in 2015. Not in international football.",
    },
    "standfirst": {
        "fr": "Chaque équipe perd le ballon une centaine de fois par match : 109,2 pertes en moyenne dans le jeu, sur 2 454 matchs de championnat, de Liga du Barça et de tournois. La plupart ne coûtent rien. Quelques-unes coûtent un match. On a rangé chacune de ces pertes selon l'endroit où elle a lieu, mesuré ce qui suit dans les 15 secondes, puis regardé comment la carte a bougé entre 2004 et 2024, et si elle est la même en club et en sélection.",
        "en": "Every team loses the ball about a hundred times a match: 109.2 open-play losses on average, across 2,454 league, Barça La Liga and tournament matches. Most cost nothing. A few cost a match. We sorted every one of those losses by where it happened, measured what followed in the next 15 seconds, then looked at how the map moved between 2004 and 2024, and whether it is the same in club and international football.",
    },
    "chapters": [
        {
            "title": {"fr": "1. La zone rouge fait 18 mètres", "en": "1. The red zone is 18 metres deep"},
            "text": {
                "fr": [
                    "Découpez le terrain en six bandes de 17,5 m depuis votre but. Plus de la moitié des pertes arrivent au milieu du terrain, entre 35 et 87 m, et elles ne coûtent presque rien : 0,22 xG concédé pour 100 pertes entre 52 et 70 m, 0,15 entre 70 et 87 m. Dans les derniers mètres adverses, 0,05. Perdre le ballon près du but adverse, c'est le prix normal d'une attaque.",
                    "La bande qui tue, c'est la deuxième : entre 17 et 35 m de son propre but. Seulement 12,4 % des pertes, mais 0,58 xG concédé pour 100 pertes, et 6,0 buts encaissés pour mille pertes. C'est 3,9 fois le coût d'une perte à 70–87 m. Curieusement, la toute première bande, devant son but, coûte moins (0,45) : on y dégage, on y perd des duels aériens, le ballon repart loin. Au total, les pertes dans son dernier tiers représentent 41,0 % de tout le danger concédé en transition.",
                ],
                "en": [
                    "Cut the pitch into six 17.5 m bands from your own goal. More than half of all losses happen in midfield, between 35 and 87 m, and they cost almost nothing: 0.22 xG conceded per 100 losses between 52 and 70 m, 0.15 between 70 and 87 m. In the opponent's final metres, 0.05. Losing the ball near the opposing goal is the normal price of attacking.",
                    "The band that kills is the second one: between 17 and 35 m from your own goal. Only 12.4% of losses, but 0.58 xG conceded per 100 losses, and 6.0 goals conceded per thousand losses. That is 3.9 times the cost of a loss at 70–87 m. Oddly, the very first band, right in front of goal, costs less (0.45): that is where teams clear, lose aerial duels, and the ball travels far. Overall, losses in your own final third account for 41.0% of all the danger conceded in transition.",
                ],
            },
            "figure": "bandsloss",
        },
        {
            "title": {"fr": "2. Club ou sélection : la même carte", "en": "2. Club or country: the same map"},
            "text": {
                "fr": [
                    "On pourrait croire que les sélections, moins rodées, perdent plus de ballons dangereux. C'est l'inverse sur le volume : 94,4 pertes par équipe et par match en tournoi, contre 111,4 en championnat. Les sélections jouent plus prudemment, avec moins de prises de risque à la relance.",
                    "Mais la carte est la même. Une perte à 17–35 m coûte 0,58 xG pour 100 en club, 0,51 en sélection ; une perte haute, 0,14 et 0,15. Le football de sélection perd un peu moins de ballons, au même endroit, pour le même prix. Sur ce terrain-là, club et sélection sont un seul sport.",
                ],
                "en": [
                    "You might think national teams, less drilled, lose more dangerous balls. On volume it is the opposite: 94.4 losses per team per match in tournaments, against 111.4 in league football. National teams play more cautiously, taking fewer risks when building from the back.",
                    "But the map is the same. A loss at 17–35 m costs 0.58 xG per 100 in club football, 0.51 for national teams; a high loss, 0.14 and 0.15. International football loses slightly fewer balls, in the same places, at the same price. On this point, club and country are one sport.",
                ],
            },
            "figure": "losskind",
        },
        {
            "title": {"fr": "3. Le temps : on perd de moins en moins le ballon", "en": "3. Over time: teams lose the ball less and less"},
            "text": {
                "fr": [
                    "Le seul fil continu sur vingt ans, ce sont les matchs de Liga du Barça, de 2004/05 à 2020/21. Le Barça perdait 115,2 ballons par match en 2005 ; il n'en perd plus que 87,5 en 2021. Ses adversaires suivent la même pente. Hors Barça, la tendance est la même : 116,6 pertes par équipe en 2015–16, 91,3 en 2021–24. Le football perd moins le ballon : moins de longs ballons perdus d'avance, plus de relances courtes.",
                    "En revanche, l'endroit où l'on perd le ballon n'a presque pas bougé : environ un tiers des pertes du Barça dans son propre camp, d'une saison à l'autre. Le jeu de position a réduit le nombre de pertes, pas déplacé la carte.",
                ],
                "en": [
                    "The only continuous thread across twenty years is Barça's La Liga matches, from 2004/05 to 2020/21. Barça lost 115.2 balls per match in 2005; by 2021, only 87.5. Their opponents follow the same slope. Outside Barça, the trend is the same: 116.6 losses per team in 2015–16, 91.3 in 2021–24. Football loses the ball less: fewer hopeful long balls, more short build-up.",
                    "On the other hand, where the ball is lost has barely moved: about a third of Barça's losses in their own half, season after season. Positional play cut the number of losses, it did not move the map.",
                ],
            },
            "figure": "losstime",
        },
        {
            "title": {"fr": "4. Ce qui a changé : le prix", "en": "4. What changed: the price"},
            "text": {
                "fr": [
                    "C'est là que l'intuition « le pressing paie de plus en plus » trouve sa meilleure preuve. Quand un adversaire du Barça perdait le ballon entre 17 et 35 m de son but, il concédait 0,64 xG pour 100 pertes en 2004–09. En 2010–15, 1,04. En 2016–21, encore 0,98. Le nombre de tirs ne change pas (7,2 pour 100 pertes au début, 7,2 à la fin) : ce qui change, c'est leur qualité. Le Barça a appris à transformer une récupération haute en grosse occasion.",
                    "Le même mouvement apparaît dans les rares échantillons récents de club. Dans les matchs de Leverkusen, une perte à 17–35 m coûtait 0,44 en 2015/16, et 0,67 en 2023/24. Dans les matchs du PSG en Ligue 1, 0,91 en 2021/22 et 0,81 en 2022/23, quand toute la Ligue 1 de la saison 2015/16 était à 0,51. Les quatre grands championnats de 2015/16, eux, étaient à 0,55.",
                    "Les sélections, elles, n'ont pas bougé : 0,49 en 2018, 0,41 en 2020, 0,55 en 2022, 0,45 en 2024. Les clubs d'élite punissent désormais les erreurs de relance bien plus durement qu'avant ; les sélections, qui ont dix jours pour préparer un tournoi, n'ont pas suivi.",
                ],
                "en": [
                    "This is where the “pressing pays more and more” intuition finds its best evidence. When one of Barça's opponents lost the ball 17–35 m from its own goal, it conceded 0.64 xG per 100 losses in 2004–09. In 2010–15, 1.04. In 2016–21, still 0.98. The number of shots does not change (7.2 per 100 losses at the start, 7.2 at the end): what changes is their quality. Barça learned to turn a high regain into a big chance.",
                    "The same movement shows up in the rare recent club samples. In Leverkusen's matches, a loss at 17–35 m cost 0.44 in 2015/16, and 0.67 in 2023/24. In PSG's Ligue 1 matches, 0.91 in 2021/22 and 0.81 in 2022/23, when the whole of Ligue 1 in 2015/16 stood at 0.51. The four big leagues of 2015/16 stood at 0.55.",
                    "National teams have not moved: 0.49 in 2018, 0.41 in 2020, 0.55 in 2022, 0.45 in 2024. Elite clubs now punish build-up mistakes far more harshly than before; national teams, who get ten days to prepare a tournament, have not followed.",
                ],
            },
            "figure": "costtime",
        },
    ],
    "takeaways": {
        "fr": [
            "Une perte entre 17 et 35 m de son but coûte 0,58 xG pour 100 pertes : 3,9 fois une perte dans le camp adverse.",
            "Les pertes dans son dernier tiers pèsent 41,0 % du danger concédé en transition.",
            "Club et sélection ont la même carte des pertes ; les sélections perdent moins de ballons (94,4 contre 111,4 par match).",
            "On perd de moins en moins le ballon : 115,2 pertes par match pour le Barça en 2005, 87,5 en 2021.",
            "Le prix d'une perte près de son but a grimpé en club (adversaires du Barça : 0,64 puis 1,04 ; Leverkusen : 0,44 puis 0,67), pas en sélection.",
        ],
        "en": [
            "A loss 17–35 m from your own goal costs 0.58 xG per 100 losses: 3.9 times a loss in the opponent's half.",
            "Losses in your own final third make up 41.0% of the danger conceded in transition.",
            "Club and international football share the same loss map; national teams lose fewer balls (94.4 against 111.4 per match).",
            "Teams lose the ball less and less: 115.2 losses per match for Barça in 2005, 87.5 in 2021.",
            "The price of a loss near your goal has risen in club football (Barça's opponents: 0.64 then 1.04; Leverkusen: 0.44 then 0.67), not in international football.",
        ],
    },
    "limits": {
        "fr": [
            "Le fil long, ce sont les matchs du Barça : il raconte le Barça et ses adversaires, pas toute la Liga.",
            "Les échantillons récents de club sont les matchs de deux équipes dominantes (Leverkusen, PSG) : ils montrent ce que fait l'élite, pas un championnat entier.",
            "Le coût d'une perte compte les tirs dans les 15 secondes : une perte qui mène à un corner puis à un but n'est pas comptée.",
            "Les données Wyscout (Euro 2016, championnats 2017/18) ne comptent pas les pertes de la même façon : elles sont hors de cette enquête.",
        ],
        "en": [
            "The long thread is Barça's matches: it tells the story of Barça and its opponents, not the whole of La Liga.",
            "The recent club samples are the matches of two dominant teams (Leverkusen, PSG): they show what the elite does, not an entire league.",
            "The cost of a loss counts shots within 15 seconds: a loss that leads to a corner and then a goal is not counted.",
            "Wyscout data (Euro 2016, 2017/18 leagues) does not count losses the same way: it is outside this investigation.",
        ],
    },
}

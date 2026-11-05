"""Enquête n° 1 · Le pressing, mythe de YouTube.

Le texte, écrit à la main. Chaque nombre cité doit exister dans les résultats de
`tableau_noir.enquetes.pressing.compute` ; `tableau-noir enquetes` le vérifie.
"""

ENQUETE = {
    "slug": "pressing",
    "number": 1,
    "title": {"fr": "Le pressing, mythe de YouTube", "en": "Pressing, a YouTube myth"},
    "question": {
        "fr": "Les équipes qui pressent le plus gagnent-elles plus souvent ?",
        "en": "Do the teams that press the most win more often?",
    },
    "answer": {
        "fr": "Non. Dans les tournois, l'équipe qui presse le plus gagne 43 % du temps et perd 40 % du temps. En club, son avantage apparent disparaît dès qu'on tient compte de la force des équipes. Et rien, dans les données, ne dit que ça change avec le temps.",
        "en": "No. In tournaments, the team that presses more wins 43% of the time and loses 40% of the time. In club football, its apparent edge vanishes as soon as team strength is accounted for. And nothing in the data says this is changing over time.",
    },
    "standfirst": {
        "fr": "Ouvrez n'importe quelle vidéo d'analyse : le pressing y est la clé de tout. Le gegenpressing, la meute, « le pressing est le meilleur des meneurs de jeu ». On a pris 241 matchs de Coupe du monde, d'Euro et de finales de Ligue des champions, et on a posé la question la plus bête possible : quand une équipe presse plus que l'autre, est-ce qu'elle gagne ? La réponse tient en une pièce qu'on lance en l'air.",
        "en": "Open any tactical video: pressing is the key to everything. Gegenpressing, the pack, “pressing is the best playmaker”. We took 241 matches from World Cups, Euros and Champions League finals and asked the dumbest possible question: when a team presses more than the other, does it win? The answer is a coin toss.",
    },
    "chapters": [
        {
            "title": {"fr": "1. Lancez la pièce", "en": "1. Toss the coin"},
            "text": {
                "fr": [
                    "Pour chaque match, on regarde qui presse le plus, avec la mesure que tout le monde utilise : le PPDA, le nombre de passes qu'on laisse à l'adversaire avant de lui tomber dessus. Plus il est bas, plus on presse. Sur 239 matchs où les deux équipes se distinguent, celle qui presse le plus gagne 102 fois, fait 41 nuls et perd 96 fois. Autrement dit : 43 % de victoires, 40 % de défaites.",
                    "On a refait le test avec toutes les autres façons de compter le pressing : les pressions par minute sans ballon, le contre-pressing dans les cinq secondes après une perte, les ballons récupérés dans les 35 derniers mètres adverses. Même résultat, entre 43 et 47 % de victoires. À côté, l'équipe qui crée le plus d'xG gagne 57 % du temps, et ne perd que 26 % du temps. Les occasions prédisent le résultat. Le pressing, non.",
                ],
                "en": [
                    "For each match, we look at who presses more, using the measure everyone uses: PPDA, the number of passes you allow the opponent before pouncing. The lower, the more you press. In 239 matches where the two teams differ, the team that presses more wins 102 times, draws 41 and loses 96. In other words: 43% wins, 40% losses.",
                    "We ran the test again with every other way of counting pressing: pressures per minute out of possession, counter-pressing within five seconds of a loss, balls won in the opponent's final 35 metres. Same story, between 43 and 47% wins. Next to that, the team that creates more xG wins 57% of the time and loses only 26% of the time. Chances predict the result. Pressing does not.",
                ],
            },
            "figure": "outcomes",
        },
        {
            "title": {"fr": "2. En phase finale, c'est pire", "en": "2. In the knockouts, it gets worse"},
            "text": {
                "fr": [
                    "On pourrait penser que le pressing est une arme de grands matchs. C'est l'inverse. Sur les 73 matchs à élimination directe du corpus, l'équipe au PPDA le plus bas gagne 30 fois et perd 43 fois : 41 % de victoires. Avec les autres mesures, on remonte entre 52 et 54 %, ce qui reste un lancer de pièce. L'équipe qui a le plus d'xG, elle, gagne 66 % de ses matchs à élimination directe.",
                    "Regardez les champions. Sur les quatre tournois, deux vainqueurs pressaient moins que la moitié des équipes engagées : la France 2018 est 25e sur 32 au PPDA, avec 20,9 passes laissées contre 18,4 en moyenne dans le tournoi ; l'Argentine 2022 est 12e sur 32. Seule l'Espagne 2024, 3e sur 24, a gagné en pressant vraiment fort.",
                ],
                "en": [
                    "You might think pressing is a weapon for big matches. It is the opposite. In the corpus's 73 knockout matches, the team with the lower PPDA wins 30 and loses 43: a 41% win rate. With the other measures you climb back to between 52 and 54%, which is still a coin toss. The team with more xG, meanwhile, wins 66% of its knockout matches.",
                    "Look at the champions. Across the four tournaments, two winners pressed less than half of the teams involved: France 2018 rank 25th of 32 on PPDA, allowing 20.9 passes against a tournament average of 18.4; Argentina 2022 rank 12th of 32. Only Spain 2024, 3rd of 24, won while really pressing hard.",
                ],
            },
            "figure": "champions",
        },
        {
            "title": {"fr": "3. Ce que le pressing achète vraiment", "en": "3. What pressing actually buys"},
            "text": {
                "fr": [
                    "Le pressing n'est pas inutile pour autant, et c'est là que ça devient intéressant. Classons les 482 prestations d'équipe en quatre quarts, des plus gros presseurs aux plus faibles. Le quart qui presse le plus crée 1,62 xG par match et en concède 1,15. Le quart qui presse le moins crée 1,00 xG et en concède 1,47. Le pressing achète des occasions, et il en retire à l'adversaire. Sur le papier, c'est un demi-but d'écart par match.",
                    "Et pourtant, les points ne suivent pas : 1,46 point par match pour les gros presseurs, 1,42 pour les petits. Le quart qui presse le plus gagne 43 % de ses matchs, celui qui presse le moins 40 %. Entre les occasions et le score, il y a la finition, le gardien, le poteau. Le pressing fabrique un avantage que le football, sur un match, efface presque entièrement.",
                    "Il y a une autre raison, plus gênante pour le mythe. Le PPDA est à moitié une mesure de possession : la corrélation entre les deux vaut −0,50. L'équipe qui a le ballon laisse mécaniquement moins de passes à l'adversaire. Quand on retire la part de la possession, l'effet propre du pressing sur la différence de buts tombe à −0,07 but par écart-type. Presque rien. Les gros presseurs sont surtout des équipes qui ont déjà le ballon.",
                ],
                "en": [
                    "Pressing is not useless, though, and this is where it gets interesting. Sort the 482 team performances into four quarters, from the heaviest pressers to the lightest. The top quarter creates 1.62 xG per match and concedes 1.15. The bottom quarter creates 1.00 xG and concedes 1.47. Pressing buys chances, and takes them away from the opponent. On paper, that is half a goal per match.",
                    "And yet the points do not follow: 1.46 points per match for the heavy pressers, 1.42 for the light ones. The top quarter wins 43% of its matches, the bottom quarter 40%. Between chances and the scoreline sit finishing, the goalkeeper, the post. Pressing manufactures an edge that football, over one match, almost entirely erases.",
                    "There is another reason, more awkward for the myth. PPDA is half a possession measure: the correlation between the two is −0.50. The team with the ball mechanically allows fewer opponent passes. Once you strip out the share due to possession, the specific effect of pressing on goal difference falls to −0.07 goals per standard deviation. Almost nothing. Heavy pressers are mostly teams that already have the ball.",
                ],
            },
            "figure": "quartiles",
        },
        {
            "title": {"fr": "4. En club, le piège du favori", "en": "4. In club football, the favourite's trap"},
            "text": {
                "fr": [
                    "C'est là que l'impression des amateurs de football de club vient de quelque part. Sur une saison complète de Premier League, de Liga, de Serie A et de Ligue 1 (2015/16, 1 517 matchs), l'équipe qui presse le plus gagne 46 % de ses matchs et en perd 31 %. Un vrai avantage, cette fois. Les cinq grands championnats 2017/18 disent la même chose avec une autre source de données.",
                    "Sauf que les gros presseurs sont les gros clubs. Sur 80 équipes-saisons, la corrélation entre le PPDA et les points vaut −0,43, mais celle entre la possession et les points vaut 0,64. Alors on a refait le calcul en tenant compte de la force de chaque équipe, mesurée par ses points sur le reste de la saison. L'effet du pressing sur la différence de buts passe de 0,35 but par écart-type à 0,03. Il disparaît.",
                    "Le test le plus parlant : à force égale, l'équipe qui presse nettement plus que l'autre gagne 32 % de ses matchs et en perd 39 %. Le favori net gagne 62 % de ses matchs ; quand il presse plus que l'adversaire, 61 % ; quand il presse moins, 65 %. L'outsider gagne 15 % de ses matchs, qu'il presse ou non. En club comme en sélection, ce n'est pas le pressing qui gagne : c'est l'équipe qui presse.",
                ],
                "en": [
                    "This is where the club football fan's impression comes from. Over a full season of the Premier League, La Liga, Serie A and Ligue 1 (2015/16, 1,517 matches), the team that presses more wins 46% of its matches and loses 31%. A real edge, this time. The big five leagues of 2017/18 say the same with another data source.",
                    "Except that the heavy pressers are the big clubs. Across 80 team-seasons, the correlation between PPDA and points is −0.43, but the one between possession and points is 0.64. So we ran the numbers again accounting for each team's strength, measured by its points over the rest of the season. The effect of pressing on goal difference drops from 0.35 goals per standard deviation to 0.03. It vanishes.",
                    "The most telling test: at equal strength, the team that presses clearly more than the other wins 32% of its matches and loses 39%. A clear favourite wins 62% of its matches; when it presses more than the opponent, 61%; when it presses less, 65%. The underdog wins 15% of its matches, pressing or not. In club and international football alike, it is not pressing that wins: it is the team that presses.",
                ],
            },
            "figure": "favourite",
        },
        {
            "title": {"fr": "5. Et dans le temps ? Barcelone, 2004–2021", "en": "5. And over time? Barcelona, 2004–2021"},
            "text": {
                "fr": [
                    "Le mythe a une date de naissance : Barcelone, 2008–2011, la règle des six secondes de Guardiola. Les données du Barça, saison après saison, racontent la suite. Entre 2005 et 2010, le Barça laissait 10,6 à 10,8 passes à l'adversaire avant d'intervenir. En 2020/21, il en laissait 15,8. Son contre-pressing est passé de 31 % des pressions en 2011/12 à 26 %. Et ses points par match, de 2,63 en 2009/10 à 2,06.",
                    "Les sélections, elles, n'ont pas suivi le mouvement inverse. Dans les tournois, l'équipe qui presse le plus gagne 48 % de ses matchs en 2018, 45 % à l'Euro 2020, 36 % au Mondial 2022, 40 % à l'Euro 2024. Rien ne monte. L'Espagne championne d'Europe est 3e presseur de son tournoi sur 24, et c'est bien le seul champion récent qui donne raison au mythe. L'impression que le pressing paie de plus en plus vient du football de club, et nos données récentes de club sont trop minces pour la confirmer : une saison de Leverkusen, deux demi-saisons du PSG, et des équipes qui gagnent de toute façon.",
                ],
                "en": [
                    "The myth has a birth date: Barcelona, 2008–2011, Guardiola's six-second rule. Barça's own numbers, season after season, tell what came next. Between 2005 and 2010, Barça allowed the opponent 10.6 to 10.8 passes before stepping in. In 2020/21, they allowed 15.8. Their counter-pressing went from 31% of pressures in 2011/12 to 26%. And their points per match, from 2.63 in 2009/10 to 2.06.",
                    "International teams did not move the other way. In tournaments, the team that presses more wins 48% of its matches in 2018, 45% at Euro 2020, 36% at the 2022 World Cup, 40% at Euro 2024. Nothing is rising. European champions Spain rank 3rd heaviest presser of their tournament out of 24, and they are the only recent champion who proves the myth right. The feeling that pressing pays more and more comes from club football, and our recent club data is too thin to confirm it: one Leverkusen season, two half-seasons of PSG, and teams that win anyway.",
                ],
            },
            "figure": "time",
        },
        {
            "title": {"fr": "6. Les blocs bas qui ont gagné", "en": "6. The low blocks that won"},
            "text": {
                "fr": [
                    "Les contre-exemples ne sont pas des accidents, ce sont des tournois entiers. La France de 2018 bat la Belgique en demi-finale avec un PPDA de 49,4 contre 13,2, soit presque quatre fois moins de pressing que l'adversaire, et 40 % de possession. Le Maroc de 2022 élimine l'Espagne puis le Portugal avec 29 % et 25 % du ballon, et des PPDA de 38,5 et 39,8. L'Inter de 2010 gagne sa finale avec 30 % de possession face au Bayern.",
                    "Dans chacun de ces matchs, l'équipe qui pressait le plus a perdu. Pas malgré son pressing : parce que le pressing est une dépense, pas un revenu. On court, on ferme des lignes de passe, on récupère haut, et il reste encore à marquer. Les blocs bas qui gagnent sont ceux qui ont compris que le match se joue dans les deux surfaces.",
                ],
                "en": [
                    "The counter-examples are not accidents, they are whole tournaments. France in 2018 beat Belgium in the semi-final with a PPDA of 49.4 against 13.2, almost four times less pressing than the opponent, and 40% possession. Morocco in 2022 knocked out Spain and then Portugal with 29% and 25% of the ball, and PPDAs of 38.5 and 39.8. Inter in 2010 won their final with 30% possession against Bayern.",
                    "In each of those matches, the team that pressed more lost. Not in spite of its pressing: because pressing is an expense, not an income. You run, you close passing lanes, you win the ball high, and you still have to score. The low blocks that win are the ones that understood the match is played in the two boxes.",
                ],
            },
            "figure": "cases",
        },
    ],
    "takeaways": {
        "fr": [
            "Sur 239 matchs, l'équipe qui presse le plus gagne 43 % du temps et perd 40 % du temps : une pièce lancée en l'air.",
            "En phase finale, l'équipe au PPDA le plus bas perd 43 matchs sur 73.",
            "Le pressing crée des occasions (+0,62 xG par match entre le quart qui presse le plus et celui qui presse le moins) mais ne rapporte pas de points (1,46 contre 1,42).",
            "Le PPDA mesure à moitié la possession (corrélation −0,50). Une fois la possession retirée, le pressing ne pèse presque plus rien.",
            "Deux champions sur quatre pressaient moins que la moitié des équipes de leur tournoi.",
            "En championnat, l'avantage apparent du presseur (46 % de victoires, 31 % de défaites) disparaît quand on tient compte de la force des équipes : à force égale, le presseur gagne 32 % et perd 39 %.",
            "Le Barça est passé de 10,8 passes laissées à l'adversaire en 2009/10 à 15,8 en 2020/21 ; dans les tournois, le presseur ne gagne pas plus en 2024 qu'en 2018.",
        ],
        "en": [
            "In 239 matches, the team that presses more wins 43% of the time and loses 40% of the time: a coin toss.",
            "In knockout matches, the team with the lower PPDA loses 43 of 73.",
            "Pressing creates chances (+0.62 xG per match between the top and bottom pressing quarters) but does not earn points (1.46 against 1.42).",
            "PPDA is half a possession measure (correlation −0.50). Once possession is removed, pressing barely weighs anything.",
            "Two champions out of four pressed less than half of the teams in their tournament.",
            "In league football, the presser's apparent edge (46% wins, 31% losses) vanishes once team strength is accounted for: at equal strength, the presser wins 32% and loses 39%.",
            "Barça went from allowing 10.8 opponent passes in 2009/10 to 15.8 in 2020/21; in tournaments, the presser wins no more in 2024 than in 2018.",
        ],
    },
    "limits": {
        "fr": [
            "Les événements de pression n'existent que chez StatsBomb : l'Euro 2016 (Wyscout) est hors du corpus des tournois. Restent 241 matchs, 73 à élimination directe. Les championnats 2017/18 (Wyscout) ne sont comparés qu'entre eux : leurs PPDA ne se comparent pas à ceux de StatsBomb.",
            "Les données de club récentes (2021–2024) ne couvrent qu'un club dominant et ses adversaires : elles ne permettent pas de dire si le pressing paie plus aujourd'hui qu'en 2015.",
            "Le PPDA et ses cousins mesurent une quantité de pressing, pas sa qualité : un pressing coordonné et un pressing désordonné comptent pareil.",
            "Un match de tournoi n'est pas une saison : sur 38 journées, les petits avantages s'additionnent. Ici, ils ont rarement le temps.",
            "Corrélation n'est pas causalité, dans les deux sens : rien ne dit que presser moins ferait gagner.",
        ],
        "en": [
            "Pressure events only exist in StatsBomb data: Euro 2016 (Wyscout) is outside the tournament corpus. That leaves 241 matches, 73 of them knockouts. The 2017/18 leagues (Wyscout) are only compared with each other: their PPDAs are not comparable with StatsBomb's.",
            "Recent club data (2021–2024) only covers one dominant club and its opponents: it cannot tell whether pressing pays more today than in 2015.",
            "PPDA and its cousins measure a quantity of pressing, not its quality: a coordinated press and a chaotic one count the same.",
            "A tournament match is not a season: over 38 rounds, small edges add up. Here, they rarely get the time.",
            "Correlation is not causation, in either direction: nothing says pressing less would make you win.",
        ],
    },
}

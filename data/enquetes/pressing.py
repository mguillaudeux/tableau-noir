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
        "fr": "Non. Sur 241 matchs, l'équipe qui presse le plus gagne 43 % du temps et perd 40 % du temps. En phase finale, c'est pire : elle perd plus souvent qu'elle ne gagne.",
        "en": "No. Across 241 matches, the team that presses more wins 43% of the time and loses 40% of the time. In knockout matches it gets worse: it loses more often than it wins.",
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
            "title": {"fr": "4. Les blocs bas qui ont gagné", "en": "4. The low blocks that won"},
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
        ],
        "en": [
            "In 239 matches, the team that presses more wins 43% of the time and loses 40% of the time: a coin toss.",
            "In knockout matches, the team with the lower PPDA loses 43 of 73.",
            "Pressing creates chances (+0.62 xG per match between the top and bottom pressing quarters) but does not earn points (1.46 against 1.42).",
            "PPDA is half a possession measure (correlation −0.50). Once possession is removed, pressing barely weighs anything.",
            "Two champions out of four pressed less than half of the teams in their tournament.",
        ],
    },
    "limits": {
        "fr": [
            "Les événements de pression n'existent que chez StatsBomb : l'Euro 2016 (Wyscout) est hors du corpus. Restent 241 matchs, 73 à élimination directe.",
            "Le PPDA et ses cousins mesurent une quantité de pressing, pas sa qualité : un pressing coordonné et un pressing désordonné comptent pareil.",
            "Un match de tournoi n'est pas une saison : sur 38 journées, les petits avantages s'additionnent. Ici, ils ont rarement le temps.",
            "Corrélation n'est pas causalité, dans les deux sens : rien ne dit que presser moins ferait gagner.",
        ],
        "en": [
            "Pressure events only exist in StatsBomb data: Euro 2016 (Wyscout) is outside the corpus. That leaves 241 matches, 73 of them knockouts.",
            "PPDA and its cousins measure a quantity of pressing, not its quality: a coordinated press and a chaotic one count the same.",
            "A tournament match is not a season: over 38 rounds, small edges add up. Here, they rarely get the time.",
            "Correlation is not causation, in either direction: nothing says pressing less would make you win.",
        ],
    },
}

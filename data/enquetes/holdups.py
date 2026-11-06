"""Enquête n° 9 · Les hold-up : quand les xG se trompent."""

ENQUETE = {
    "slug": "holdups",
    "number": 9,
    "title": {"fr": "Les hold-up : quand les xG se trompent", "en": "The heists: when xG get it wrong"},
    "question": {
        "fr": "L'équipe qui se crée le moins d'occasions gagne-t-elle souvent ? Et est-ce que ça arrive plus qu'avant ?",
        "en": "Does the team that creates fewer chances often win? And does it happen more than it used to?",
    },
    "answer": {
        "fr": "Une fois sur six. En championnat, l'équipe qui a le moins d'xG gagne 15,4 % de ses matchs ; en sélection, 24,8 %, et 40,7 % en phase finale, tirs au but compris. Le hasard n'a pas augmenté avec le temps : il a une adresse, et c'est le tournoi.",
        "en": "One time in six. In league football, the team with less xG wins 15.4% of its matches; with national teams, 24.8%, and 40.7% in knockout rounds, shoot-outs included. Chance has not grown over time: it has an address, and it is the tournament.",
    },
    "standfirst": {
        "fr": "En mai 2012, le Bayern se crée 3,49 xG en finale de Ligue des champions. Chelsea, 0,29. Chelsea gagne aux tirs au but. C'est le plus gros hold-up de nos 2 454 matchs StatsBomb, et c'est la meilleure entrée en matière pour une question qui fâche : quand les xG désignent un vainqueur, à quel point peut-on leur faire confiance ? On a regardé chaque match où une équipe a créé moins que l'autre, selon l'écart, la compétition, l'époque, et le passage du club à la sélection.",
        "en": "In May 2012, Bayern create 3.49 xG in the Champions League final. Chelsea, 0.29. Chelsea win on penalties. It is the biggest heist in our 2,454 StatsBomb matches, and the best way into an awkward question: when xG point to a winner, how much can we trust them? We looked at every match in which one team created less than the other, by gap, competition, era, and the switch from club to international football.",
    },
    "chapters": [
        {
            "title": {"fr": "1. La règle des 0,5 xG", "en": "1. The 0.5 xG rule"},
            "text": {
                "fr": [
                    "Sur tout le corpus, l'équipe qui a créé le moins d'xG gagne 16,6 % de ses matchs, fait 23,1 % de nuls et perd 60,3 % du temps. Les xG ont donc raison trois fois sur cinq, et ne se trompent franchement qu'une fois sur six. Mais tout dépend de l'écart.",
                    "Sous 0,25 xG d'écart, c'est une pièce en l'air : 34,7 % de victoires, 36,5 % de défaites pour l'équipe « dominée ». Entre 0,25 et 0,5 xG, elle ne gagne déjà plus que 22,1 % du temps. Au-delà de 1 xG, 11,6 %. Et au-delà de 2 xG d'écart, sur 304 matchs, elle gagne 2,6 % du temps. Retenez ça : sous un demi-xG, les xG ne départagent personne ; au-dessus de deux, ils ne se trompent presque jamais.",
                ],
                "en": [
                    "Across the whole corpus, the team that created less xG wins 16.6% of its matches, draws 23.1% and loses 60.3% of the time. xG are right three times in five, and only plainly wrong once in six. But it all depends on the gap.",
                    "Below a 0.25 xG gap it is a coin toss: 34.7% wins, 36.5% losses for the “dominated” side. Between 0.25 and 0.5 xG, it wins only 22.1% of the time. Beyond 1 xG, 11.6%. And beyond a 2 xG gap, over 304 matches, it wins 2.6% of the time. Remember this: under half an xG, xG separate nobody; above two, they are almost never wrong.",
                ],
            },
            "figure": "gap",
        },
        {
            "title": {"fr": "2. Le tournoi, maison des hold-up", "en": "2. The tournament, home of the heist"},
            "text": {
                "fr": [
                    "C'est là que club et sélection se séparent. En championnat, l'équipe qui a le moins d'xG gagne 15,4 % du temps ; en tournoi de sélection, 24,8 %. Les quatre grands championnats 2015/16 sont tous entre 15,3 % (Liga) et 18,5 % (Serie A). Les Coupes du monde 2018 et 2022 montent à 29,7 % chacune : presque un match sur trois gagné par celui qui s'est créé le moins.",
                    "En phase de groupes, les sélections ressemblent encore aux clubs (18,9 %). C'est l'élimination directe qui change tout : 40,7 % de victoires pour l'équipe qui a le moins d'xG, sur 86 matchs. Les tirs au but y sont pour quelque chose, 14 de ces victoires en viennent, mais il en reste 21 obtenues dans le jeu. Un match sec, des équipes prudentes, une seule occasion qui suffit : le format fabrique les hold-up.",
                ],
                "en": [
                    "This is where club and country part ways. In league football, the team with less xG wins 15.4% of the time; in national-team tournaments, 24.8%. The four big 2015/16 leagues all sit between 15.3% (La Liga) and 18.5% (Serie A). The 2018 and 2022 World Cups climb to 29.7% each: almost one match in three won by the side that created less.",
                    "In the group stage, national teams still look like clubs (18.9%). It is the knockout rounds that change everything: 40.7% wins for the team with less xG, over 86 matches. Shoot-outs play their part, 14 of those wins came from them, but 21 were earned in open play. One-off matches, cautious teams, a single chance that is enough: the format manufactures heists.",
                ],
            },
            "figure": "holdcomp",
        },
        {
            "title": {"fr": "3. Le musée du hold-up", "en": "3. The heist museum"},
            "text": {
                "fr": [
                    "Chelsea–Bayern 2012 reste hors concours : 3,2 xG d'écart, et une coupe aux grandes oreilles au bout. Derrière, un inattendu Lorient–Toulouse de 2015/16, gagné 3–2 avec 0,51 xG contre 3,22. Puis le choc de Lusail : l'Arabie saoudite bat l'Argentine 2–1 avec 0,15 xG contre 2,49, le futur champion du monde battu par une équipe qui n'a presque rien tenté.",
                    "Et un quart de finale mondial dans le lot : Belgique–Brésil 2018, 2–1 pour les Belges avec 0,41 xG contre 2,61. Sur les dix plus gros hold-up du corpus, trois sont des matchs de sélection, alors que les sélections ne pèsent que 314 des 2 450 matchs regardés.",
                ],
                "en": [
                    "Chelsea–Bayern 2012 is in a league of its own: a 3.2 xG gap, and the big-eared trophy at the end of it. Behind it, an unlikely Lorient–Toulouse from 2015/16, won 3–2 with 0.51 xG against 3.22. Then the Lusail shock: Saudi Arabia beat Argentina 2–1 with 0.15 xG against 2.49, the future world champions beaten by a side that barely tried anything.",
                    "And a World Cup quarter-final in the mix: Belgium–Brazil 2018, 2–1 to the Belgians with 0.41 xG against 2.61. Of the ten biggest heists in the corpus, three are national-team matches, whereas national teams account for only 314 of the 2,450 matches examined.",
                ],
            },
            "figure": "heists",
        },
        {
            "title": {"fr": "4. Le temps : rien n'a bougé, sauf au sommet", "en": "4. Over time: nothing has moved, except at the top"},
            "text": {
                "fr": [
                    "On pouvait imaginer que le football moderne, plus homogène, multiplie les surprises. Les données disent non. Dans les matchs de Liga du Barça, l'équipe qui a le moins d'xG gagne 8,3 % du temps en 2004–09, 11,9 % en 2010–15, 11,0 % en 2016–21. Les tournois de sélection oscillent sans tendance : 29,7 % en 2018, 23,5 % en 2020, 29,7 % en 2022, 21,6 % en 2024.",
                    "Une chose a changé, en revanche : au sommet du football de club, le hold-up se raréfie. Dans les matchs du Leverkusen invaincu de 2023/24, l'équipe qui a le moins d'xG n'a gagné que 8,8 % du temps. Quand une équipe d'élite domine aujourd'hui, elle convertit sa domination. Les clubs riches ont réduit leur part de hasard ; le football de sélection, lui, la garde intacte.",
                ],
                "en": [
                    "You could imagine that modern football, more even, produces more upsets. The data says no. In Barça's La Liga matches, the team with less xG wins 8.3% of the time in 2004–09, 11.9% in 2010–15, 11.0% in 2016–21. National-team tournaments swing with no trend: 29.7% in 2018, 23.5% in 2020, 29.7% in 2022, 21.6% in 2024.",
                    "One thing has changed, though: at the top of club football, the heist is getting rarer. In the matches of the unbeaten 2023/24 Leverkusen, the team with less xG won only 8.8% of the time. When an elite team dominates today, it turns its dominance into results. Rich clubs have cut their share of chance; international football keeps it intact.",
                ],
            },
            "figure": "holdtime",
        },
    ],
    "takeaways": {
        "fr": [
            "L'équipe qui a le moins d'xG gagne 16,6 % du temps, et 2,6 % au-delà de 2 xG d'écart.",
            "Sous 0,25 xG d'écart, le résultat est une pièce en l'air.",
            "En sélection, les xG se trompent bien plus souvent : 24,8 % de hold-up, 40,7 % en phase finale (dont 14 aux tirs au but).",
            "Chelsea–Bayern 2012 (0,29 xG contre 3,49) est le plus gros hold-up du corpus.",
            "Pas de tendance dans le temps, sauf au sommet du football de club : 8,8 % de hold-up dans les matchs de Leverkusen 2023/24.",
        ],
        "en": [
            "The team with less xG wins 16.6% of the time, and 2.6% beyond a 2 xG gap.",
            "Below a 0.25 xG gap, the result is a coin toss.",
            "With national teams, xG are wrong far more often: 24.8% heists, 40.7% in knockouts (14 of them on penalties).",
            "Chelsea–Bayern 2012 (0.29 xG against 3.49) is the biggest heist in the corpus.",
            "No trend over time, except at the top of club football: 8.8% heists in Leverkusen's 2023/24 matches.",
        ],
    },
    "limits": {
        "fr": [
            "Les xG sont ceux de StatsBomb ; avec notre modèle, sur les championnats Wyscout 2017/18, la part de hold-up monte à 21,0 % : un modèle plus simple se trompe plus.",
            "Les victoires aux tirs au but comptent comme des victoires : c'est le résultat, pas le jeu.",
            "Un hold-up à la mi-temps n'est pas le même qu'un hold-up à la 90e : le score change le comportement des équipes (celle qui mène recule et concède des xG).",
            "Le fil long est celui des matchs du Barça, qui domine presque toujours : il dit peu des matchs entre équipes moyennes.",
        ],
        "en": [
            "The xG are StatsBomb's; with our own model, on the 2017/18 Wyscout leagues, the heist rate rises to 21.0%: a simpler model is wrong more often.",
            "Shoot-out wins count as wins: this is about results, not play.",
            "A heist at half-time is not the same as a heist at the 90th minute: the score changes how teams behave (the side in front drops deeper and concedes xG).",
            "The long thread is Barça's matches, and Barça almost always dominate: it says little about matches between average teams.",
        ],
    },
}

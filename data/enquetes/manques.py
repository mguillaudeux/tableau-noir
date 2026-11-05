"""Enquête n° 5 · Le but le plus cher jamais raté."""

ENQUETE = {
    "slug": "manques",
    "number": 5,
    "title": {"fr": "Le but le plus cher jamais raté", "en": "The most expensive goal never scored"},
    "question": {
        "fr": "Que coûte une occasion manquée, et le football en rate-t-il moins qu'avant ?",
        "en": "What does a missed chance cost, and does football miss fewer than it used to?",
    },
    "answer": {
        "fr": "Sur 61 138 tirs, une grosse occasion sur deux est manquée, en 2015 comme en 2024. En sélection, on rate davantage qu'en club : 46 % de grosses occasions converties contre 50 %, 71 % de penaltys contre 77 %. Et les finales où les xG se sont trompés se comptent sur une main : 3 sur 18.",
        "en": "Across 61,138 shots, one big chance in two is missed, in 2015 as in 2024. National teams miss more than clubs: 46% of big chances converted against 50%, 71% of penalties against 77%. And the finals where xG got it wrong fit on one hand: 3 of 18.",
    },
    "standfirst": {
        "fr": "Chaque tournoi a son fantôme : la frappe à côté qui aurait tout changé, le penalty dans les nuages, la tête qui passe au-dessus à la 90e. On a cherché dans 61 138 tirs les occasions vraiment décisives, celles où un but aurait mis l'équipe devant ou à égalité dans un match qu'elle n'a finalement pas gagné. Il y en a 830. Puis on a posé la question que personne ne pose : est-ce qu'on rate plus en sélection qu'en club, et est-ce qu'on rate moins qu'avant ?",
        "en": "Every tournament has its ghost: the shot wide that would have changed everything, the penalty into the clouds, the header over the bar in minute 90. We searched 61,138 shots for the truly decisive chances, the ones where a goal would have put the team ahead or level in a match it did not go on to win. There are 830 of them. Then we asked the question nobody asks: do national teams miss more than clubs, and does football miss less than it used to?",
    },
    "chapters": [
        {
            "title": {"fr": "1. Les vingt fantômes", "en": "1. The twenty ghosts"},
            "text": {
                "fr": [
                    "En phase finale de sélection, 20 occasions manquées hors penalty remplissent nos critères, entre 2018 et 2024. La plus chère est celle d'Ismaïla Sarr, à la 23e minute de Sénégal–Angleterre en 2022 : 0,63 xG, à 0-0, seul face au but, à côté. Le Sénégal perd 0-3. Viennent ensuite Yoane Wissa pour la RD Congo en demi-finale de la CAN 2023 (0,57 xG, à 0-0, défaite 0-1) et Romelu Lukaku contre l'Italie à l'Euro 2020 (0,57 xG, à 1-2, défaite 1-2).",
                    "Le détail qui fait mal : sur ces vingt occasions, aucune équipe n'a fini par gagner. C'est la définition qu'on a choisie, mais c'est aussi la réalité d'un tournoi : on n'a pas deux fois la même chance. Rasmus Højlund contre l'Allemagne, Matthijs de Ligt contre la Tchéquie, Eric Dier contre la Belgique : à chaque fois, l'occasion arrive avant le premier but adverse, et le match bascule juste après.",
                ],
                "en": [
                    "In national-team knockout matches, 20 non-penalty misses meet our criteria between 2018 and 2024. The most expensive is Ismaïla Sarr's, in minute 23 of Senegal–England in 2022: 0.63 xG, at 0-0, alone in front of goal, wide. Senegal lost 0-3. Next come Yoane Wissa for DR Congo in the AFCON 2023 semi-final (0.57 xG, at 0-0, a 0-1 defeat) and Romelu Lukaku against Italy at Euro 2020 (0.57 xG, at 1-2, a 1-2 defeat).",
                    "The painful detail: of these twenty chances, not one team went on to win. That is the definition we chose, but it is also the reality of a tournament: you do not get the same chance twice. Rasmus Højlund against Germany, Matthijs de Ligt against Czech Republic, Eric Dier against Belgium: each time, the chance comes before the opponent's first goal, and the match tips right after.",
                ],
            },
            "figure": "misses",
        },
        {
            "title": {"fr": "2. Les penaltys, ou le prix fixe du regret", "en": "2. Penalties, or the fixed price of regret"},
            "text": {
                "fr": [
                    "Un penalty vaut 0,78 xG chez StatsBomb : c'est l'occasion la plus chère que le football distribue. En phase finale de sélection, cinq ont été manqués alors qu'ils auraient mis l'équipe devant ou à égalité, dans un match perdu ensuite : Harry Kane contre la France en 2022 (à 1-2, 84e minute), Achraf Hakimi contre l'Afrique du Sud à la CAN 2023 (à 0-1, 85e), Enner Valencia contre l'Argentine en Copa América (à 0-1, 62e), Emilio Nsue et Adama Traoré, encore à la CAN.",
                    "En finale de Ligue des champions, Arjen Robben à la 95e minute de Chelsea–Bayern 2012 et Antoine Griezmann à la 48e de Real–Atlético 2016 ont manqué le même penalty : celui qui aurait fait basculer une finale que leur équipe dominait. Les deux finales se sont finies aux tirs au but, et les deux ont été perdues.",
                ],
                "en": [
                    "A penalty is worth 0.78 xG in StatsBomb's model: it is the most expensive chance football hands out. In national-team knockout matches, five were missed when they would have put the team ahead or level, in a match then lost: Harry Kane against France in 2022 (at 1-2, minute 84), Achraf Hakimi against South Africa at AFCON 2023 (at 0-1, minute 85), Enner Valencia against Argentina at the Copa América (at 0-1, minute 62), Emilio Nsue and Adama Traoré, again at the AFCON.",
                    "In Champions League finals, Arjen Robben in minute 95 of Chelsea–Bayern 2012 and Antoine Griezmann in minute 48 of Real–Atlético 2016 missed the same penalty: the one that would have tipped a final their team was dominating. Both finals went to a shoot-out, and both were lost.",
                ],
            },
            "figure": "conversion",
        },
        {
            "title": {"fr": "3. En sélection, on rate plus", "en": "3. National teams miss more"},
            "text": {
                "fr": [
                    "C'est la découverte de cette enquête. En club, sur 53 516 tirs, on marque 1,07 but par xG : un peu plus que ce que les occasions promettent. En sélection, sur 7 622 tirs, on marque 0,97 but par xG : un peu moins. Même écart sur les grosses occasions (xG ≥ 0,30) : 50 % converties en club, 46 % en sélection. Et sur les penaltys : 77 % en club, 71 % en sélection.",
                    "Dix points d'écart sur les buts par xG, quatre points sur les grosses occasions, six sur les penaltys : trois mesures indépendantes, trois fois le même sens. Les explications sont connues, et elles s'additionnent : des attaquants qui jouent avec des partenaires qu'ils connaissent peu, et des défenses plus regroupées. L'enjeu, lui, n'explique rien : en phase finale, la conversion des grosses occasions remonte à 51 %, sur 91 occasions. C'est en poules qu'on rate.",
                ],
                "en": [
                    "This is the discovery of this investigation. For clubs, across 53,516 shots, 1.07 goals are scored per xG: a little more than the chances promise. For national teams, across 7,622 shots, 0.97 goals per xG: a little less. Same gap on big chances (xG ≥ 0.30): 50% converted by clubs, 46% by national teams. And on penalties: 77% for clubs, 71% for national teams.",
                    "Ten points apart on goals per xG, four points on big chances, six on penalties: three independent measures, three times the same direction. The explanations are known, and they add up: forwards playing with partners they barely know, and more compact defences. The stakes explain nothing: in knockout matches, big-chance conversion climbs to 51%, over 91 chances. It is in the group stage that teams miss.",
                ],
            },
            "figure": "eras",
        },
        {
            "title": {"fr": "4. On ne rate pas moins qu'avant", "en": "4. We do not miss less than before"},
            "text": {
                "fr": [
                    "Les attaquants d'aujourd'hui finissent-ils mieux ? Sur les saisons complètes et les tournois, en laissant de côté la série du Barça qui fausserait tout, la conversion des grosses occasions vaut 49 % en 2015–16, 47 % en 2017–20 et 48 % en 2021–24. Les buts par xG : 1,03, 0,93, 1,01. Les penaltys : 75 %, 77 %, 71 %. Rien ne bouge. Le football a changé la façon de créer les occasions, pas la façon de les mettre au fond.",
                    "La série du Barça raconte l'exception : sur 17 saisons, de 2004 à 2021, Barcelone convertit 55 % de ses grosses occasions, bien au-dessus du reste. Ce n'est pas une époque, c'est un joueur et ses partenaires. Quand on parle de l'évolution de la finition, on parle souvent de Messi sans le savoir.",
                ],
                "en": [
                    "Do today's forwards finish better? Across full seasons and tournaments, leaving aside the Barça series that would skew everything, big-chance conversion is 49% in 2015–16, 47% in 2017–20 and 48% in 2021–24. Goals per xG: 1.03, 0.93, 1.01. Penalties: 75%, 77%, 71%. Nothing moves. Football has changed how chances are created, not how they are put away.",
                    "The Barça series tells the exception: over 17 seasons, from 2004 to 2021, Barcelona convert 55% of their big chances, well above everyone else. That is not an era, it is one player and his partners. When people talk about the evolution of finishing, they are often talking about Messi without knowing it.",
                ],
            },
            "figure": "finals",
        },
        {
            "title": {"fr": "5. 2012, l'année où les xG se sont trompés", "en": "5. 2012, the year xG got it wrong"},
            "text": {
                "fr": [
                    "Sur les 18 finales du corpus (onze de Ligue des champions, sept de sélection), l'équipe qui avait le plus d'xG en a gagné 15. Trois exceptions. La France bat la Croatie 4-2 en 2018 avec 1,10 xG contre 1,48 : un écart de 0,38, de l'ordre de la précision du modèle. Le Portugal bat la France 1-0 en 2016 avec 0,75 xG contre 1,37 : un seul but, en prolongation, dans une finale fermée des deux côtés.",
                    "Et puis il y a Chelsea–Bayern 2012 : 0,29 xG contre 3,49. Trois buts et vingt centièmes d'écart. Le Bayern tire 40 fois chez lui et en cadre 7, Robben manque un penalty en prolongation, Gómez manque une occasion à 0,46 xG à la 112e, et Chelsea gagne aux tirs au but avec 9 tirs, dont 3 cadrés. Sur 18 finales, c'est la seule où le modèle ne s'est pas trompé d'un but : il s'est trompé de match. Les xG ont raison presque toujours. C'est le « presque » qu'on retient.",
                ],
                "en": [
                    "Of the corpus's 18 finals (eleven Champions League, seven national-team), the side with more xG won 15. Three exceptions. France beat Croatia 4-2 in 2018 with 1.10 xG against 1.48: a 0.38 gap, within the model's precision. Portugal beat France 1-0 in 2016 with 0.75 xG against 1.37: a single goal, in extra time, in a final shut tight on both sides.",
                    "And then there is Chelsea–Bayern 2012: 0.29 xG against 3.49. A three-goal gap, and change. Bayern shot 40 times at home and put 7 on target, Robben missed a penalty in extra time, Gómez missed a 0.46 xG chance in minute 112, and Chelsea won on penalties with 9 shots, 3 of them on target. Of 18 finals, it is the only one where the model was not off by a goal: it was off by a match. xG is right almost always. It is the “almost” that we remember.",
                ],
            },
            "figure": None,
        },
    ],
    "takeaways": {
        "fr": [
            "830 occasions décisives manquées sur 61 138 tirs ; en phase finale de sélection, les 20 plus grosses n'ont jamais été rattrapées.",
            "La plus chère : Ismaïla Sarr, Sénégal–Angleterre 2022, 0,63 xG à 0-0, défaite 0-3.",
            "En sélection, on marque 0,97 but par xG contre 1,07 en club ; 46 % des grosses occasions converties contre 50 % ; 71 % des penaltys contre 77 %.",
            "Dans le temps, rien ne bouge : 49 %, 47 %, 48 % de grosses occasions converties sur trois périodes. Le Barça de Messi, lui, est à 55 % sur 17 saisons.",
            "Les xG désignent le vainqueur de 15 finales sur 18. Chelsea 2012 (0,29 contre 3,49) reste la seule vraie injustice.",
        ],
        "en": [
            "830 decisive misses in 61,138 shots; in national-team knockouts, the 20 biggest were never made up for.",
            "The most expensive: Ismaïla Sarr, Senegal–England 2022, 0.63 xG at 0-0, a 0-3 defeat.",
            "National teams score 0.97 goals per xG against 1.07 for clubs; 46% of big chances converted against 50%; 71% of penalties against 77%.",
            "Over time, nothing moves: 49%, 47%, 48% of big chances converted across three periods. Messi's Barça, though, sits at 55% over 17 seasons.",
            "xG picks the winner of 15 finals out of 18. Chelsea 2012 (0.29 against 3.49) remains the only real robbery.",
        ],
    },
    "limits": {
        "fr": [
            "Tout est en xG StatsBomb, pour comparer ce qui est comparable : l'Euro 2016 et les championnats 2017/18 (Wyscout, modèle maison) sont hors des chiffres de conversion. La finale de l'Euro 2016 apparaît seulement dans la liste des finales.",
            "« Décisif » est une définition : un but qui aurait mis l'équipe devant ou à égalité, dans un match qu'elle n'a pas gagné. Une occasion manquée à 2-0 n'y est pas, même si elle a fait trembler.",
            "La comparaison dans le temps repose sur trois périodes de taille très inégale (38 804 tirs pour 2015–16, 1 752 pour 2017–20) ; le modèle d'xG, lui, est le même partout.",
            "Le Barça n'est pas « son époque » : un seul club, et un attaquant hors norme, ne disent rien du reste de la Liga de l'époque.",
        ],
        "en": [
            "Everything is in StatsBomb xG, to compare like with like: Euro 2016 and the 2017/18 leagues (Wyscout, our own model) are outside the conversion figures. The Euro 2016 final only appears in the finals list.",
            "“Decisive” is a definition: a goal that would have put the team ahead or level, in a match it did not win. A miss at 2-0 is not in it, even if it made the crowd gasp.",
            "The comparison over time rests on three periods of very unequal size (38,804 shots for 2015–16, 1,752 for 2017–20); the xG model, though, is the same throughout.",
            "Barça is not “its era”: a single club, with an extraordinary forward, says nothing about the rest of La Liga at the time.",
        ],
    },
}

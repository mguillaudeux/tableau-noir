"""Enquête n° 4 · La possession ne sert à rien (sauf au plus fort)."""

ENQUETE = {
    "slug": "possession",
    "number": 4,
    "title": {"fr": "La possession ne sert à rien (sauf au plus fort)", "en": "Possession is useless (except for the stronger side)"},
    "question": {
        "fr": "Avoir le ballon fait-il gagner des matchs ?",
        "en": "Does having the ball win matches?",
    },
    "answer": {
        "fr": "Non. En championnat, une équipe à 40 % de possession gagne 34 % de ses matchs, une équipe à 60 % en gagne 40 %, et à force égale, celle qui a nettement plus le ballon perd plus souvent qu'elle ne gagne. La possession fabrique des occasions dans les deux sens, à parts égales. En sélection, elle « prédit » le résultat parce qu'elle appartient au plus fort.",
        "en": "No. In league football, a team with 40% possession wins 34% of its matches, a team with 60% wins 40%, and at equal strength, the side with clearly more of the ball loses more often than it wins. Possession creates chances both ways, in equal measure. With national teams it “predicts” the result because it belongs to the stronger side.",
    },
    "standfirst": {
        "fr": "C'est la statistique la plus montrée du football, et la plus mal lue. Tout le monde sait que « la possession ne gagne pas les matchs », tout le monde l'affiche quand même, et personne ne dit ce qu'elle fait vraiment. On a classé 3 034 prestations de championnat et 628 prestations de sélection par tranche de possession, puis on a tenu compte de la force des équipes. Le résultat est plus intéressant que « ça ne sert à rien » : la possession achète exactement autant qu'elle coûte.",
        "en": "It is football's most displayed statistic, and its most misread. Everyone knows that “possession doesn't win matches”, everyone shows it anyway, and nobody says what it actually does. We sorted 3,034 league performances and 628 national-team performances by possession band, then accounted for team strength. The result is more interesting than “it's useless”: possession buys exactly as much as it costs.",
    },
    "chapters": [
        {
            "title": {"fr": "1. De 40 % à 60 % : la même part de victoires", "en": "1. From 40% to 60%: the same win rate"},
            "text": {
                "fr": [
                    "Prenez les quatre grands championnats 2015/16, 1 517 matchs, et classez chaque équipe de chaque match selon sa possession. Sous 40 % du ballon, on gagne 33 % de ses matchs et on en perd 40 %. Entre 45 et 50 % : 40 % de victoires. Au-dessus de 60 % : 40 % de victoires, 32 % de défaites. Entre la tranche la plus basse et la plus haute, 1,26 point par match contre 1,47. Vingt points de possession pour deux dixièmes de point.",
                    "Pourtant, le ballon fait bien quelque chose. Sous 40 %, une équipe crée 0,9 xG et en concède 1,7 ; au-dessus de 60 %, elle crée 1,7 xG et en concède 0,9. La symétrie est parfaite. Avoir le ballon, c'est déplacer les occasions d'un camp à l'autre, pas en fabriquer davantage. La corrélation entre la possession et les xG vaut 0,32, et celle avec les xG concédés vaut −0,32 : le même nombre, de signe opposé.",
                ],
                "en": [
                    "Take the four big 2015/16 leagues, 1,517 matches, and sort each team of each match by its possession. Under 40% of the ball, teams win 33% of their matches and lose 40%. Between 45 and 50%: 40% wins. Above 60%: 40% wins, 32% losses. Between the lowest and the highest band, 1.26 points per match against 1.47. Twenty points of possession for two tenths of a point.",
                    "Yet the ball does do something. Under 40%, a team creates 0.9 xG and concedes 1.7; above 60%, it creates 1.7 xG and concedes 0.9. The symmetry is perfect. Having the ball moves chances from one end to the other; it does not manufacture more of them. The correlation between possession and xG is 0.32, and the one with xG conceded is −0.32: the same number, opposite sign.",
                ],
            },
            "figure": "bands",
        },
        {
            "title": {"fr": "2. À force égale, le ballon est un piège", "en": "2. At equal strength, the ball is a trap"},
            "text": {
                "fr": [
                    "Les équipes qui ont le ballon sont souvent les meilleures, ce qui fausse tout. Alors on a mesuré la force de chaque équipe par ses points sur le reste de la saison, et on a regardé les matchs entre équipes de force comparable où l'une a eu au moins dix points de possession de plus que l'autre : 387 cas. L'équipe qui avait le ballon a gagné 25 % de ces matchs et en a perdu 42 %.",
                    "Même chose en régression : seul, un écart de possession « vaut » 0,26 but de différence par écart-type ; une fois la force des équipes retirée, il vaut −0,15. Le favori net qui a le ballon gagne 60 % de ses matchs ; l'outsider net qui a le ballon en gagne 13 %. La possession n'ajoute rien à la force, et quand elle n'est pas le reflet de la force, elle est le reflet du score : l'équipe menée garde le ballon parce que l'autre le lui laisse.",
                ],
                "en": [
                    "Teams that have the ball are often the best ones, which distorts everything. So we measured each team's strength by its points over the rest of the season, and looked at matches between teams of comparable strength where one had at least ten more points of possession than the other: 387 cases. The team with the ball won 25% of those matches and lost 42%.",
                    "Same in regression: alone, a possession gap “is worth” 0.26 goals of difference per standard deviation; once team strength is removed, it is worth −0.15. A clear favourite with the ball wins 60% of its matches; a clear underdog with the ball wins 13%. Possession adds nothing to strength, and when it does not reflect strength, it reflects the score: the team that is behind keeps the ball because the other lets it.",
                ],
            },
            "figure": "equal",
        },
        {
            "title": {"fr": "3. En sélection, le ballon appartient au plus fort", "en": "3. With national teams, the ball belongs to the stronger side"},
            "text": {
                "fr": [
                    "Dans les tournois, le tableau change de visage : au-dessus de 50 % de possession, on gagne entre 42 % et 50 % de ses matchs ; en dessous, entre 29 % et 39 %. Et l'équipe qui a plus le ballon que l'adversaire gagne 55 % de ses matchs à l'Euro 2020, 53 % à l'Euro 2024 et à la Copa América 2024. Ce n'est pas la possession qui a changé de nature, ce sont les affiches : une poule de Coupe du monde oppose des équipes que vingt places de classement séparent, et le ballon va au plus fort.",
                    "Les exceptions sont célèbres. L'Espagne a eu 82 % du ballon contre le Japon au Mondial 2022 et a perdu 1-2. Le Barça a perdu à domicile contre Grenade avec 80 % de possession, contre Cadix avec 79 %. Sur 506 prestations à plus de 65 % de possession dans le corpus, 21 % finissent en défaite. Avoir le ballon n'empêche rien.",
                    "Dans le temps, aucune tendance : 49 % de victoires pour l'équipe qui a le ballon au Mondial 2018, 55 % à l'Euro 2020, 39 % au Mondial 2022, 53 % à l'Euro 2024. Le Mondial 2022 est le tournoi du contre, l'Euro 2024 celui du contrôle, et l'un n'annonce pas l'autre.",
                ],
                "en": [
                    "In tournaments, the picture changes: above 50% possession, teams win between 42% and 50% of their matches; below, between 29% and 39%. And the team with more of the ball than its opponent wins 55% of its matches at Euro 2020, 53% at Euro 2024 and at Copa América 2024. It is not possession that changed its nature, it is the fixtures: a World Cup group pits teams twenty ranking places apart, and the ball goes to the stronger side.",
                    "The exceptions are famous. Spain had 82% of the ball against Japan at the 2022 World Cup and lost 1-2. Barça lost at home to Granada with 80% possession, to Cádiz with 79%. Of 506 performances above 65% possession in the corpus, 21% end in defeat. Having the ball prevents nothing.",
                    "Over time, no trend: 49% wins for the team with the ball at the 2018 World Cup, 55% at Euro 2020, 39% at the 2022 World Cup, 53% at Euro 2024. The 2022 World Cup was the tournament of the counter, Euro 2024 the tournament of control, and one does not announce the other.",
                ],
            },
            "figure": "bycomp",
        },
    ],
    "takeaways": {
        "fr": [
            "En championnat, la part de victoires est presque la même à 40 % et à 60 % de possession (33 % contre 40 %).",
            "La possession déplace les occasions sans en créer : 0,9 xG créés et 1,7 concédés sous 40 %, l'inverse au-dessus de 60 %.",
            "À force égale, l'équipe qui a nettement plus le ballon gagne 25 % de ses matchs et en perd 42 %.",
            "En sélection, la possession « prédit » le résultat parce qu'elle va au plus fort ; dans le temps, aucune tendance.",
            "21 % des prestations à plus de 65 % de possession finissent en défaite.",
        ],
        "en": [
            "In league football, the win rate is almost the same at 40% and at 60% possession (33% against 40%).",
            "Possession moves chances without creating them: 0.9 xG created and 1.7 conceded under 40%, the reverse above 60%.",
            "At equal strength, the team with clearly more of the ball wins 25% of its matches and loses 42%.",
            "With national teams, possession “predicts” the result because it goes to the stronger side; over time, no trend.",
            "21% of performances above 65% possession end in defeat.",
        ],
    },
    "limits": {
        "fr": [
            "La possession est mesurée au temps sur tout le match : une équipe menée au score a souvent plus le ballon parce que l'adversaire se replie. Une partie de « à force égale, le ballon perd » vient de là.",
            "La force d'une équipe est mesurée par ses points sur le reste de la saison : disponible en championnat, pas en tournoi.",
            "Les tranches de sélection comptent une centaine de prestations chacune : des écarts de cinq points y sont du bruit.",
            "Source unique (StatsBomb), championnats 2015/16 et tournois 2018–2024.",
        ],
        "en": [
            "Possession is time-based over the whole match: a team that is behind often has more of the ball because the opponent sits back. Part of “at equal strength, the ball loses” comes from that.",
            "A team's strength is measured by its points over the rest of the season: available in leagues, not in tournaments.",
            "National-team bands hold about a hundred performances each: five-point gaps there are noise.",
            "Single source (StatsBomb), 2015/16 leagues and 2018–2024 tournaments.",
        ],
    },
}

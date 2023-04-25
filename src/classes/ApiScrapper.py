import requests


class ApiScrapper:
    url = 'https://esports.op.gg/'

    def get_matches(self):
        return  # Array de Partidos

    def get_teams(self, season_id: int):
        r = requests.post(self.url + "matches/graphql", json=
        {
            'operationName': "TournamentStandings",
            'query': "fragment CoreTeam on Team {\n  id\n  name\n  acronym\n  imageUrl\n  nationality\n  foundedAt\n  imageUrlDarkMode\n  imageUrlLightMode\n  youtube\n  twitter\n  facebook\n  instagram\n  discord\n  website\n}\n\n" +
                     "fragment CoreRank on Rank {\n  team {\n    ...CoreTeam\n    }\n}\n\n" +
                     "query TournamentStandings($tournamentId: ID!) {\n  standings(tournamentId: $tournamentId) {\n    ...CoreRank\n    }\n}",
            'variables':
                {
                    'tournamentId': season_id,
                }
        })
        return r.json().get('data').get('standings')

    def get_results(self):
        return

import requests

from src.enums import MatchStatus


class ApiScrapper:
    URL = 'https://esports.op.gg/'

    @classmethod
    def get_list_match(cls, status: MatchStatus, year=None, month=None, leagueId=None, limit=5, page=0):
        r = requests.post(cls.URL + "/matches/graphql", json=
        {
            'operationName': "ListPagedAllMatches",
            'query': "fragment CoreLeague on League {\n  id\n }\n\n" +
                     "fragment CoreSerie on Serie {\n  id\n  league {\n    ...CoreLeague\n      }\n  }\n\n" +
                     "fragment CoreTournament on Tournament {\n  id\n  serie {\n    ...CoreSerie\n      }\n  }\n\n" +
                     "fragment CoreMatch on Match {\n  id\n  tournamentId\n  name\n  originalScheduledAt\n  scheduledAt\n  beginAt\n  endAt\n  numberOfGames\n   homeTeamId\n  awayTeamId\n   tournament {\n    ...CoreTournament\n      }\n  }\n\n" +
                     "query ListPagedAllMatches($status: String!, $leagueId: ID, $teamId: ID, $page: Int, $year: Int, $month: Int, $limit: Int) {\n  pagedAllMatches(\n    status: $status\n    leagueId: $leagueId\n    teamId: $teamId\n    page: $page\n    year: $year\n    month: $month\n    limit: $limit\n  ) {\n    ...CoreMatch\n    tournament {\n      ...CoreTournament\n      serie {\n        league {\n          shortName\n          region\n                  }\n        year\n        season\n              }\n          }\n      }\n}",
            'variables':
                {
                    'status': status.value,
                    'leagueId': leagueId,
                    'limit': limit,
                    'year': year,
                    'month': month,
                    'page': page
                }
        })
        return r.json()['data']['pagedAllMatches']

    @classmethod
    def get_match_result(cls, match_id: int, set=1):
        count = 0
        while True:
            count += 1
            r = requests.post(cls.URL + "/matches/graphql", json=
            {
                'operationName': "GetGameByMatch",
                'query': "fragment CoreTeam on Team {\n  id\n  name\n  acronym\n  imageUrl\n  nationality\n  website\n  }\n\n" +
                         "fragment CoreGameTeam on GameTeam {\n  team {\n    ...CoreTeam\n      }\n  kills\n  deaths\n  assists\n  towerKills\n  inhibitorKills\n  heraldKills\n  dragonKills\n  elderDrakeKills\n  baronKills\n  goldEarned\n  }\n\n" +
                         "fragment CoreGame on Game {\n  id\n  beginAt\n  endAt\n finished\n  length\n  winner {\n    ...CoreTeam\n      }\n  teams {\n    ...CoreGameTeam\n    frames {\n      gold\n      xp\n      timestamp\n          }\n      }\n   }\n\n" +
                         "query GetGameByMatch($matchId: ID!, $set: Int) {\n  gameByMatch(matchId: $matchId, set: $set) {\n    ...CoreGame\n      }\n}",
                'variables':
                    {
                        'matchId': match_id,
                        'set': set
                    }
            })
            if r.status_code != 502 or count > 2:
                break
        return r.json()['data']['gameByMatch']

    @classmethod
    def get_teams(cls, tournament_id: int):
        r = requests.post(cls.URL + "/matches/graphql", json=
        {
            'operationName': "TournamentStandings",
            'query': "fragment CoreTeam on Team {\n  id\n  name\n  acronym\n  imageUrl\n  nationality\n  foundedAt\n  imageUrlDarkMode\n  imageUrlLightMode\n  youtube\n  twitter\n  facebook\n  instagram\n  discord\n  website\n}\n\n" +
                     "fragment CoreRank on Rank {\n  team {\n    ...CoreTeam\n    } \n position \n point \n}\n\n" +
                     "query TournamentStandings($tournamentId: ID!) {\n  standings(tournamentId: $tournamentId) {\n    ...CoreRank\n    }\n}",
            'variables':
                {
                    'tournamentId': tournament_id,
                }
        })
        return r.json()['data']['standings']

    @classmethod
    def get_tournaments(cls, status: MatchStatus, year: int, month: int):
        r = requests.post(cls.URL + "/matches/graphql", json=
        {
            'operationName': "ListPagedAllMatches",
            'query': "fragment CoreLeague on League {\n id\n name\n shortName\n imageUrl\n region\n}\n\n" +
                     "fragment CoreSerie on Serie {\n id\n season\n league {\n    ...CoreLeague\n      }\n  }\n\n" +
                     "fragment CoreTournament on Tournament {\n id\n name\n  beginAt\n  endAt\n serie {\n    ...CoreSerie\n      }\n  }\n\n" +
                     "fragment CoreMatch on Match {\n tournament {\n    ...CoreTournament\n      }\n  }\n\n" +
                     "query ListPagedAllMatches($status: String!, $leagueId: ID, $teamId: ID, $page: Int, $year: Int, $month: Int, $limit: Int) {\n  pagedAllMatches(\n    status: $status\n    leagueId: $leagueId\n    teamId: $teamId\n    page: $page\n    year: $year\n    month: $month\n    limit: $limit\n  ) {\n    ...CoreMatch\n    tournament {\n      ...CoreTournament\n      serie {\n        league {\n          shortName\n          region\n                  }\n        year\n        season\n              }\n          }\n      }\n}",
            'variables':
                {
                    'status': status.value,
                    'leagueId': None,
                    'limit': 200,
                    'year': year,
                    'month': month,
                    'page': 0
                }
        })
        return [match['tournament'] for match in r.json()['data']['pagedAllMatches']
                if year and int(match['tournament']['serie']['year']) == year]

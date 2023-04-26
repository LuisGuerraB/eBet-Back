import requests

from src.Enums import MatchStatus


class ApiScrapper:
    url = 'https://esports.op.gg/'

    def get_list_match(self, status: MatchStatus, year=None, month=None, leagueId=None, limit=5, page=0):
        r = requests.post(self.url + "/matches/graphql", json=
        {
            'operationName': "ListPagedAllMatches",
            'query': "fragment CoreLeague on League {\n  id\n }\n\n" +
                     "fragment CoreSerie on Serie {\n  id\n  league {\n    ...CoreLeague\n      }\n  }\n\n" +
                     "fragment CoreTournament on Tournament {\n  id\n  serie {\n    ...CoreSerie\n      }\n  }\n\n" +
                     "fragment CoreMatch on Match {\n  id\n  tournamentId\n  name\n  originalScheduledAt\n  scheduledAt\n  beginAt\n  endAt\n   homeTeamId\n  awayTeamId\n   tournament {\n    ...CoreTournament\n      }\n  }\n\n" +
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
        return r.json().get('data').get('pagedAllMatches')

    def get_match_result(self, match_id: int, set=1):
        r = requests.post(self.url + "/matches/graphql", json=
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
        return r.json().get('data').get('gameByMatch')

    def get_teams(self, season_id: int):
        r = requests.post(self.url + "/matches/graphql", json=
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

    def get_seasons(self, year: int):
        r = requests.post(self.url + "/matches/graphql", json=
        {
            'operationName': "ListPagedAllMatches",
            'query': "fragment CoreLeague on League {\n id\n name\n shortName\n imageUrl\n region\n}\n\n" +
                     "fragment CoreSerie on Serie {\n id\n season\n league {\n    ...CoreLeague\n      }\n  }\n\n" +
                     "fragment CoreTournament on Tournament {\n id\n name\n  beginAt\n  endAt\n serie {\n    ...CoreSerie\n      }\n  }\n\n" +
                     "fragment CoreMatch on Match {\n tournament {\n    ...CoreTournament\n      }\n  }\n\n" +
                     "query ListPagedAllMatches($status: String!, $leagueId: ID, $teamId: ID, $page: Int, $year: Int, $month: Int, $limit: Int) {\n  pagedAllMatches(\n    status: $status\n    leagueId: $leagueId\n    teamId: $teamId\n    page: $page\n    year: $year\n    month: $month\n    limit: $limit\n  ) {\n    ...CoreMatch\n    tournament {\n      ...CoreTournament\n      serie {\n        league {\n          shortName\n          region\n                  }\n        year\n        season\n              }\n          }\n      }\n}",
            'variables':
                {
                    'status': MatchStatus.FINISHED.value,
                    'leagueId': None,
                    'limit': 500,
                    'year': year,
                    'month': None,
                    'page': 0
                }
        })
        return r.json().get('data').get('pagedAllMatches')

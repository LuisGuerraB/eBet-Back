from src.Enums import MatchStatus
from src.classes.ApiScrapper import ApiScrapper
from src.models import Match, Season, League, Result
from src.models.Team import Team


class DbPopulator:

    def __init__(self, db):
        self.db = db
        self.api = ApiScrapper()

    def populate_matchs(self, status, year=None, month=None, leagueId=None, limit=5, page=0):
        match_list = self.api.get_list_match(status, year, month, leagueId, limit, page)
        for match in match_list:
            if self.db.session.get(Match, match.get('id')) is None:
                match_obj = Match(
                    id=match.get('id'),
                    name=match.get('name'),
                    plan_date=match.get('scheduledAt'),
                    away_team_id=match.get('awayTeamId'),
                    local_team_id=match.get('homeTeamId'),
                    season_id=match.get('tournamentId')
                )
                if (self.db.session.get(Team, match.get('awayTeamId')) is None or self.db.session.get(Team,
                                                                                                      match.get(
                                                                                                          'homeTeamId')) is None):
                    self.populate_teams(match.get('tournamentId'))
                if self.db.session.get(Season, match.get('tournamentId')) is None:
                    self.populate_seasons(match.get('scheduledAt')[:4])
                self.db.session.add(match_obj)
        self.db.session.commit()

    def populate_seasons(self, year):
        matchs = self.api.get_seasons(year)
        for match in matchs:
            season = match.get('tournament')
            if self.db.session.get(Season, season.get('id')) is None:
                league = season.get('serie').get('league')
                if self.db.session.get(League, league.get('id')) is None:
                    league_obj = League(
                        id=league.get('id'),
                        name=league.get('name'),
                        acronym=league.get('shortName'),
                        img=league.get('imageUrl'),
                    )
                    self.db.session.add(league_obj)
                season = Season(
                    id=season.get('id'),
                    name=season.get('name'),
                    serie_id=season.get('serie').get('id'),
                    ini_date=season.get('beginAt'),
                    end_date=season.get('endAt'),
                    league_id=league.get('id')
                )
                self.db.session.add(season)
        self.db.session.commit()
        return


    def populate_teams(self, season_id):
        team_list = self.api.get_teams(season_id)
        for team in team_list:
            team = team.get('team')
            if self.db.session.get(Team, team.get('id')) is None:
                team = Team(
                    id=int(team.get('id')),
                    name=team.get('name'),
                    acronym=team.get('acronym'),
                    img=team.get('imageUrl'),
                    website=team.get('website'),
                    nationality=team.get('nationality'),
                )
                self.db.session.add(team)
        self.db.session.commit()

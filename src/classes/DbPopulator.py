from src.Enums import MatchStatus
from src.classes.ApiScrapper import ApiScrapper
from src.models.Team import Team


class DbPopulator:

    def __init__(self,db):
        self.db = db
        self.api = ApiScrapper()

    def populate_matches(self, status: MatchStatus):
        return  # Array de Partidos

    def populate_teams(self, season_id):
        team_list = self.api.get_teams(season_id)
        for team in team_list:
            team = team.get('team')
            #TODO make an get_item_or_update or something like that
            if(self.db.session.get(Team,team.get('id')) == None):
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
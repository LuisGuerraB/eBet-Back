from flask_smorest import Blueprint, abort

from src.models import TeamSchema, Team, League

api_url = '/team'
api_name = 'Team'
api_description = 'Methods over Team'

team_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@team_blp.route(api_url + '/<int:team_id>', methods=['GET'])
@team_blp.doc(tags=[api_name])
@team_blp.response(200, TeamSchema)
def get_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        abort(404, message='control-error.no-team')
    regular_league = League.query.get(team.league_id)
    team_dump = TeamSchema().dump(team)
    team_dump['regular_league'] = regular_league
    return team_dump

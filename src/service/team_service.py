from flask_smorest import Blueprint, abort

from src.models import TeamSchema, Team

api_url = '/team'
api_name = 'Team'
api_description = 'Methods over Team'

team_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@team_blp.route('/<int:team_id>', methods=['GET'])
@team_blp.doc(tags=[api_name])
@team_blp.response(200, TeamSchema)
def get_team(team_id):
    team = Team.query.get(team_id)
    if team is None:
        abort(404, message='No team with provided Id')
    return team

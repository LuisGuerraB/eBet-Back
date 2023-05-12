from flask_smorest import Blueprint, abort

from src.models import LeagueSchema, League

api_url = '/league'
api_name = 'League'
api_description = 'Methods over League'

league_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@league_blp.route(api_url+'/<int:league_id>', methods=['GET'])
@league_blp.doc(tags=[api_name])
@league_blp.response(200, LeagueSchema)
def get_league(league_id):
    league = League.query.get(league_id)
    if league is None:
        abort(404, message='No league with provided Id')
    return league

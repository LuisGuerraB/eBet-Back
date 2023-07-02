from flask_smorest import Blueprint, abort

from src.models import Match, MatchSchema, MatchListSchema, MatchListArgumentSchema

api_url = '/match'
api_name = 'Match'
api_description = 'Methods over match'

match_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@match_blp.route(api_url + '/<int:match_id>', methods=['GET'])
@match_blp.doc(tags=[api_name])
@match_blp.response(200, MatchSchema)
def get_match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        abort(404, message='control-error.no-match')
    return match


@match_blp.route(api_url + '/list', methods=['GET'])
@match_blp.doc(tags=[api_name])
@match_blp.arguments(MatchListArgumentSchema, location='query')
@match_blp.response(200, MatchListSchema)
def get_list_match(params):
    matches = Match.get_list(params.get('league_id', None),
                             params.get('team_id', None),
                             params.get('finished', None),
                             params.get('year', None),
                             params.get('month', None),
                             params.get('page', None),
                             params.get('limit', None))
    return {'items': matches, 'total': len(matches)}

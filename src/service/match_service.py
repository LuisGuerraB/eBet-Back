from flask_smorest import Blueprint, abort

from src.models import Match, MatchSchema

api_url = '/match'
api_name = 'Match'
api_description = 'Methods over match'

match_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@match_blp.route(api_url+'/<int:match_id>', methods=['GET'])
@match_blp.doc(tags=[api_name])
@match_blp.response(200, MatchSchema)
def get_match(match_id):
    match = Match.query.get(match_id)
    if match is None:
        abort(404, message='No match with provided Id')
    return match

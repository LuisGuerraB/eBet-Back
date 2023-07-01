from flask_smorest import Blueprint, abort

from src.models import ResultSchema, Result, Match

api_url = '/result'
api_name = 'Result'
api_description = 'Methods over Result'

result_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@result_blp.route(api_url+'/match/<int:match_id>', methods=['GET'])
@result_blp.doc(tags=[api_name])
@result_blp.response(200, ResultSchema)
def get_result(match_id):
    match = Match.get(match_id)
    if match is None:
        abort(404, message='control-error.no-match')
    results = Result.get_from_match(match_id)
    return results

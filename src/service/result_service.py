from flask_smorest import Blueprint, abort

from src.models import ResultSchema, Result

api_url = '/result'
api_name = 'Result'
api_description = 'Methods over Result'

result_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@result_blp.route('/<int:result_id>', methods=['GET'])
@result_blp.doc(tags=[api_name])
@result_blp.response(200, ResultSchema)
def get_result(result_id):
    result = Result.query.get(result_id)
    if result is None:
        abort(404, message='No result with provided Id')
    return result

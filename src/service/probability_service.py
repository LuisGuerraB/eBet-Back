from flask_smorest import Blueprint, abort

from src.models import ProbabilitySchema, Probability

api_url = '/probability'
api_name = 'Probability'
api_description = 'Methods over Probability'

probability_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@probability_blp.route('/<int:probability_id>', methods=['GET'])
@probability_blp.doc(tags=[api_name])
@probability_blp.response(200, ProbabilitySchema)
def get_probability(probability_id):
    probability = Probability.query.get(probability_id)
    if probability is None:
        abort(404, message='No probability with provided Id')
    return probability

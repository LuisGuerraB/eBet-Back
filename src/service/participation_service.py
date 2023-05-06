from flask_smorest import Blueprint,abort

from src.models import ParticipationSchema, Participation

api_url = '/participation'
api_name = 'Participation'
api_description = 'Methods over Participation'

participation_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@participation_blp.route('/<int:participation_id>', methods=['GET'])
@participation_blp.doc(tags=[api_name])
@participation_blp.response(200, ParticipationSchema)
def get_participation(participation_id):
    participation = Participation.query.get(participation_id)
    if participation is None:
        abort(404, message='No participation with provided Id')
    return participation

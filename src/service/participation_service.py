from flask_smorest import Blueprint,abort

from src.models import ParticipationSchema, Participation, ParticipationListSchema
from src.models.season import NoRegularSeasonException

api_url = '/participation'
api_name = 'Participation'
api_description = 'Methods over Participation'

participation_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@participation_blp.route(api_url+'/<int:participation_id>', methods=['GET'])
@participation_blp.doc(tags=[api_name])
@participation_blp.response(200, ParticipationSchema)
def get_participation(participation_id):
    participation = Participation.query.get(participation_id)
    if participation is None:
        abort(404, message='control-error.no-participation')
    return participation

@participation_blp.route(api_url+'/league/<int:league_id>', methods=['GET'])
@participation_blp.doc(tags=[api_name])
@participation_blp.response(200, ParticipationListSchema)
def get_standings(league_id):
    try:
        participations = Participation.get_standings(league_id)
        if len(participations) == 0:
            abort(404, message='control-error.no-regular-season')
        return {'items': participations, 'total': len(participations)}
    except NoRegularSeasonException as e:
        abort(409, message=e.message)



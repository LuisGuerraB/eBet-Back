from flask_smorest import Blueprint, abort

from src.models import TournamentSchema, Tournament

api_url = '/tournament'
api_name = 'Tournament'
api_description = 'Methods over tournament'

tournament_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@tournament_blp.route(api_url + '/<int:tournament_id>', methods=['GET'])
@tournament_blp.doc(tags=[api_name])
@tournament_blp.response(200, TournamentSchema)
def get_tournament(tournament_id):
    tournament = Tournament.query.get(tournament_id)
    if tournament is None:
        abort(404, message='control-error.no-tournament-found')
    return tournament

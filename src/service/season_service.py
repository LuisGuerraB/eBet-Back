from flask_smorest import Blueprint, abort

from src.models import SeasonSchema, Season

api_url = '/season'
api_name = 'Season'
api_description = 'Methods over season'

season_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@season_blp.route(api_url+'/<int:season_id>', methods=['GET'])
@season_blp.doc(tags=[api_name])
@season_blp.response(200, SeasonSchema)
def get_season(season_id):
    season = Season.query.get(season_id)
    if season is None:
        abort(404, message='No season with provided Id')
    return season

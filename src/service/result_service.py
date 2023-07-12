from flask_smorest import Blueprint, abort
from src.models import ResultByMatchSchema, Result, Match, Team, TeamStatisticSchema

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
@result_blp.response(200, ResultByMatchSchema)
def get_result(match_id):
    match = Match.query.get(match_id)
    if match is None:
        abort(404, message='control-error.match-not-found')
    results = Result.get_from_match(match)
    return results


@result_blp.route(api_url+'/team/<int:team_id>', methods=['GET'])
@result_blp.doc(tags=[api_name])
@result_blp.response(200,TeamStatisticSchema(many=True))
def get_result(team_id):
    team = Team.query.get(team_id)
    if team is None:
        abort(404, message='control-error.no-team')
    return Result.get_statistics_from_team(team.id)

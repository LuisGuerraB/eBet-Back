from flask_smorest import Blueprint, abort
from database import db

from src.classes import DbPopulator, MatchPopulateSchema, Scheduler
from src.enums import MatchStatus
from src.models import ProbabilityCreateSchema, Bet

api_url = '/populator'
api_name = 'Populator'
api_description = 'Database populate methods'

db_populator_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@db_populator_blp.route(api_url + '/tournaments/<int:year>/<int:month>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def tournaments(year, month):
    try:
        DbPopulator().populate_tournaments(MatchStatus.NOT_STARTED, year, month)
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/teams/<int:league_id>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def teams(league_id):
    try:
        DbPopulator().populate_teams(league_id)
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/matches', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.arguments(MatchPopulateSchema, location='json')
@db_populator_blp.response(204)
def matches(params):
    try:
        DbPopulator().populate_matches(params.get('status'), params.get('year'), params.get('month'),
                                       params.get('limit'), params.get('page'))
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/result/<int:match_id>/<int:set>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def results(match_id, set):
    try:
        DbPopulator().populate_result(match_id, set)
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/populate', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def populate():
    """Populate whole database"""
    try:
        DbPopulator().populate_DB()
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/probability', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.arguments(ProbabilityCreateSchema, location='json')
@db_populator_blp.response(204)
def populate(params):
    try:
        DbPopulator().populate_probabilites(params.get('team_id'), params.get('league_id', None))
    except Exception as e:
        abort(400, message=str(e))


@db_populator_blp.route(api_url + '/get_jobs', methods=['GET'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(200)
def get_jobs():
    scheduler = Scheduler(DbPopulator())
    return scheduler.get_jobs()

from flask_smorest import Blueprint
from app import db

from src.classes import DbPopulator, MatchPopulateSchema

api_url = '/populator'
api_name = 'Populator'
api_description = 'Database populate methods'

db_populator_blp = Blueprint(
    name=api_name,
    description=api_description,
    import_name=__name__,
)


@db_populator_blp.route(api_url+'/seasons/<int:year>/<int:month>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def seasons(year, month):
    populator = DbPopulator(db)
    populator.populate_seasons(populator.db.session(), year, month)


@db_populator_blp.route(api_url+'/teams/<int:team_id>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def teams(team_id):
    populator = DbPopulator(db)
    populator.populate_teams(populator.db.session(), team_id)


@db_populator_blp.route(api_url+'/matches', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.arguments(MatchPopulateSchema, location='json')
@db_populator_blp.response(204)
def matches(params):
    populator = DbPopulator(db)
    populator.populate_matches(populator.db.session(), params.get('status'), params.get('year'), params.get('month'),
                               params.get('limit'), params.get('page'))


@db_populator_blp.route(api_url+'/result/<int:match_id>/<int:set>', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def results(match_id, set):
    populator = DbPopulator(db)
    populator.populate_result(populator.db.session(), match_id, set)


@db_populator_blp.route(api_url+'/populate', methods=['PUT'])
@db_populator_blp.doc(tags=[api_name])
@db_populator_blp.response(204)
def populate():
    """Populate whole database"""
    populator = DbPopulator(db)
    populator.populate_DB()

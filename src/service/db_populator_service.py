from flask_smorest import Blueprint
from app import db

from src.classes import DbPopulator, MatchPopulateSchema

api_url = '/populate'
api_name = 'Populate'
api_description = 'Database populate methods'

blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@blp.route('/seasons/<int:year>/<int:month>', methods=['PUT'])
@blp.doc(tags=['Populate'])
@blp.response(204)
def seasons(year, month):
    populator = DbPopulator(db)
    populator.populate_seasons(populator.db.session(), year, month)


@blp.route('/teams/<int:team_id>', methods=['PUT'])
@blp.doc(tags=['Populate'])
@blp.response(204)
def teams(team_id):
    populator = DbPopulator(db)
    populator.populate_teams(populator.db.session(), team_id)


@blp.route('/matches', methods=['PUT'])
@blp.doc(tags=['Populate'])
@blp.arguments(MatchPopulateSchema, location='json')
@blp.response(204)
def matches(params):
    populator = DbPopulator(db)
    populator.populate_matches(populator.db.session(), params.get('status'), params.get('year'), params.get('month'),
                               params.get('limit'), params.get('page'))


@blp.route('/result/<int:match_id>/<int:set>', methods=['PUT'])
@blp.doc(tags=['Populate'])
@blp.response(204)
def results(match_id, set):
    populator = DbPopulator(db)
    populator.populate_result(populator.db.session(), match_id, set)


@blp.route('/populate', methods=['PUT'])
@blp.doc(tags=['Populate'])
@blp.response(204)
def populate():
    """Populate whole database"""
    populator = DbPopulator(db)
    populator.populate_DB()

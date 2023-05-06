from flask_smorest import Blueprint, abort

from src.models import EsportSchema, Esport

api_url = '/esport'
api_name = 'Esport'
api_description = 'Methods over Esport'

esport_blp = Blueprint(
    name=api_name,
    description=api_description,
    url_prefix=api_url,
    import_name=__name__,
)


@esport_blp.route('/<int:esport_id>', methods=['GET'])
@esport_blp.doc(tags=[api_name])
@esport_blp.response(200, EsportSchema)
def get_esport(esport_id):
    esport = Esport.query.get(esport_id)
    if esport is None:
        abort(404, message='No esport with provided Id')
    return esport

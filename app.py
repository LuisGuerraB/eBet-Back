from flask import Flask
from database import db
from flask_smorest import Api
from flask_cors import CORS

from flask_swagger_ui import get_swaggerui_blueprint

from src.service import db_populator_blp, esport_blp, league_blp, match_blp, participation_blp, probability_blp, \
    result_blp, season_blp, team_blp, bet_blp, betting_odds_blp


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:1234@localhost/eBet"
    app.config["API_TITLE"] = "api"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "apidocs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "swagger"
    app.config["OPENAPI_SWAGGER_UI_VERSION"] = "3.22.2"

    # Initialize extensions
    db.init_app(app)
    api = Api(app)

    url_prefix = '/' + app.config["API_TITLE"] + '/' + app.config["API_VERSION"]

    # Register blueprints
    api.register_blueprint(db_populator_blp, url_prefix=url_prefix)
    api.register_blueprint(esport_blp, url_prefix=url_prefix)
    api.register_blueprint(league_blp, url_prefix=url_prefix)
    api.register_blueprint(match_blp, url_prefix=url_prefix)
    api.register_blueprint(participation_blp, url_prefix=url_prefix)
    api.register_blueprint(probability_blp, url_prefix=url_prefix)
    api.register_blueprint(result_blp, url_prefix=url_prefix)
    api.register_blueprint(season_blp, url_prefix=url_prefix)
    api.register_blueprint(team_blp, url_prefix=url_prefix)
    api.register_blueprint(bet_blp, url_prefix=url_prefix)
    api.register_blueprint(betting_odds_blp, url_prefix=url_prefix)

    # SWAGGER VIEW
    app.register_blueprint(get_swaggerui_blueprint(
        '/swagger',
        '/apidocs/openapi.json',
        config={
            'app_name': "Mi API Flask-Smorest"
        }
    ), url_prefix='/swagger')

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=None, port=5000, debug=True)

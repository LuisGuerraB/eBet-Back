from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api

from src.Enums import MatchStatus
#from src.classes import DbPopulator, ApiScrapper

db = SQLAlchemy()
api = Api()


def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:1234@localhost/eBet"
    app.config["API_TITLE"] = "api"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.2"
    app.config["OPENAPI_URL_PREFIX"] = "apidocs"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "swagger"

    # Initialize extensions
    db.init_app(app)
    api.init_app(app)

    # Register blueprints
    # api.register_blueprint()
    #populator = DbPopulator(db)

    @app.route('/seasons')
    def seasons():
        populator.populate_seasons(2023)
        return "Seasons added to the database"

    @app.route('/teams')
    def teams():
        populator.populate_teams(1045)
        return "Teams added to the database"

    @app.route('/matchs')
    def matchs():
        populator.populate_matchs(MatchStatus.FINISHED, year=2023, limit=50)
        return "Matchs added to the database"

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=None, port=5000, debug=True)

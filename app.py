from flask import Flask
from database import db
from flask_smorest import Api
from src.service.db_populator_service import blp as db_populator_blp
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    app = Flask(__name__)
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


    # Register blueprints
    api.register_blueprint(db_populator_blp)


    #SWAGGER VIEW
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

from flask import Flask
from dotenv import load_dotenv

from database import db
from flask_smorest import Api
from flask_cors import CORS
from flask_login import LoginManager

from flask_swagger_ui import get_swaggerui_blueprint

from src.classes import Scheduler, DbPopulator
from src.models import User
from src.service import db_populator_blp, esport_blp, league_blp, match_blp, participation_blp, probability_blp, \
    result_blp, tournament_blp, team_blp, bet_blp, betting_odds_blp, user_blp, prize_blp

app = Flask(__name__)

load_dotenv()

login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id: int):
    user = User.query.get(int(user_id))
    return user


CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE"], supports_credentials=True)
app.config.from_object('config.Config')

# Initialize extensions
db.init_app(app)
login_manager.init_app(app)
api = Api(app)

scheduler = Scheduler(DbPopulator())
scheduler.init_app(app)
scheduler.start()
scheduler.remove_all_jobs()

scheduler.schedule_matches()
scheduler.schedule_repopulate_matches()

url_prefix = '/' + app.config["API_TITLE"] + '/' + app.config["API_VERSION"]

# Register blueprints
api.register_blueprint(db_populator_blp, url_prefix=url_prefix)
api.register_blueprint(esport_blp, url_prefix=url_prefix)
api.register_blueprint(league_blp, url_prefix=url_prefix)
api.register_blueprint(match_blp, url_prefix=url_prefix)
api.register_blueprint(participation_blp, url_prefix=url_prefix)
api.register_blueprint(probability_blp, url_prefix=url_prefix)
api.register_blueprint(result_blp, url_prefix=url_prefix)
api.register_blueprint(tournament_blp, url_prefix=url_prefix)
api.register_blueprint(team_blp, url_prefix=url_prefix)
api.register_blueprint(bet_blp, url_prefix=url_prefix)
api.register_blueprint(betting_odds_blp, url_prefix=url_prefix)
api.register_blueprint(user_blp, url_prefix=url_prefix)
api.register_blueprint(prize_blp, url_prefix=url_prefix)

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


if __name__ == '__main__':
    app.run(port=30888, debug=True, threaded=True)

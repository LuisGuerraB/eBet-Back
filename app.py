from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_smorest import Api

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://root:1234@localhost/eBet"
app.config["API_TITLE"] = "api"
app.config["API_VERSION"]="v1"
app.config["OPENAPI_VERSION"]="3.0.2"
app.config["OPENAPI_URL_PREFIX"]= "apidocs"
app.config["OPENAPI_SWAGGER_UI_PATH"]= "swagger"

# Order matters: Initialize SQLAlchemy before Marshmallow
db = SQLAlchemy(app)
api = Api(app)

#api.register_blueprint()

if __name__ == '__main__':
    app.run(host=None, port=5000, debug=True, threaded=True)

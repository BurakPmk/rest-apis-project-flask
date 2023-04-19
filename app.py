import os
import secrets

from flask import Flask,jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models # actually it's same with "import models.__init__"

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

 
def create_app(db_url=None):
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True # if there is an exception inside propagete it to main so we can see it
    app.config["API_TITLE"] = "Stores REST API" #doc title
    app.config["API_VERSION"] = "v1" #api version
    app.config["OPENAPI_VERSION"] = "3.0.3" #Stardart for api documentation, tell the smorest use the 3.0.3 version of it
    app.config["OPENAPI_URL_PREFIX"] = "/" # where the root of api
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" # it tells smorest use swagger for api documentation
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/" # import swagger url
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL","sqlite:///data.db") # if db_url exist use it else use DATABASE_URL env else use sqlite
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["JWT_SECRET_KEY"] = "150296150564158887578392758073619397928"

    db.init_app(app)# give our app to sqlachemy so that it can connect the flask app 
    migrate = Migrate(app,db)
    api = Api(app)
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header,jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header,jwt_payload):
        return(
            jsonify({
                "description":"The token has been revoked","error":"token_revoked"
            }),
            401,
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header,jwt_payload):
        return(
            jsonify(
            {
                "description":"The token is not fresh",
                "error":"fresh_token_required"
            }
            )
        )

    @jwt.additional_claims_loader # This runs every time when create a jwt
    def add_claims_to_jwt(identity):
        print(identity)
        # Look in the database and see whether the user is an admin 
        if identity == 1:
            return {"is_admin":True}
        return {"is_admin":False}
        
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header,jwt_payload):
        return(
            jsonify({"message":"The Token has expired","error":"token_expired"}),
            401,
        )
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message":"Signature verification failed","error":"invalid_token"}),
            401,

        )
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return(
            jsonify(
            {"description":"Request does not contain an access token",
             "error":"authentication required"}
            ),401
        )

    # @app.before_first_request
    # with app.app_context():
    #     # db.create_all()
    #     pass

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    return app



# GIT COMMANDS

# git init -> create a file .git 
# git status -> information about .git file
# git add <file>-> add file 
# git add . -> add all file
# create file named .gitignore -> remove files inside from .git 
# git rm --cached <file> -> remove file from .git
# git checkout -- <file> -> remove changes
# git restore <file> -> remove changes
# git reset HEAD <file> -> after git add <file> this moves file back to the working area
# git commit -a -> that will create a commit and automatically add to the staging area, Only adds tracked files.
# git commit -m -> commit message line
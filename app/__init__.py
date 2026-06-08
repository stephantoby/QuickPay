from flask import Flask


def create_app():
    app = Flask(__name__)

    from config import Config
    app.config.from_object(Config)

    from .extensions import db, jwt, migrate 
    db.init_app(app) #connects each extension to the app instance.
    jwt.init_app(app)
    migrate.init_app(app, db)
   
    from . import models 

    from .payments.routes import payments_bp
    app.register_blueprint(payments_bp, url_prefix="/api/payments")

    from .auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix= "/api/auth")
   
    return app  
 
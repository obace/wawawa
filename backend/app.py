from flask import Flask, render_template

from backend import config
from backend.routes.auth import auth_bp
from backend.routes.console import console_bp
from backend.routes.instances import instances_bp
from backend.routes.batch import batch_bp


def create_app() -> Flask:
    """Flask 应用工厂，便于 gunicorn / 单元测试复用"""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config["JSON_AS_ASCII"] = False
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
    app.config["DEBUG"] = config.DEBUG

    app.register_blueprint(auth_bp)
    app.register_blueprint(console_bp)
    app.register_blueprint(instances_bp)
    app.register_blueprint(batch_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=config.DEBUG)

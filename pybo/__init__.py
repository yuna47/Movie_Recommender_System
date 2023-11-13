from flask import Flask

def create_app():
    app = Flask(__name__)

    from .views import main_views
    app.register_blueprint(main_views.bp)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

from flask import Flask, render_template

def page_not_found(e):
    return render_template('404.html'), 404

def create_app(test_config=None):

    ''' Create and configure an instance of the Flask application. '''
    app = Flask(__name__)
    app.config.from_mapping(
    SECRET_KEY="CHANGE_THIS",
    )

    ''' Error handlers '''
    app.register_error_handler(404, page_not_found)

    ''' Apply the blueprints to the app '''
    from .blueprints.main.views import main
    app.register_blueprint(main)
    # app.register_blueprint(blog, url_prefix='/blog')
    return app
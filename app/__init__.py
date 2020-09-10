from flask import Flask, render_template

def page_not_found(e):
    return render_template('404.html'), 404

def create_app(test_config=None):

    ''' Create and configure an instance of the Flask application. '''
    app = Flask(__name__)
    app.config.from_mapping(
    SECRET_KEY="AYoNACcQQUL3imCPcp",
    )

    ''' Error handlers '''
    app.register_error_handler(404, page_not_found)

    ''' Apply the blueprints to the app '''
    from .blueprints.main.views import main
    app.register_blueprint(main)
    
    from .blueprints.ctdeploy.views import ctdeploy
    app.register_blueprint(ctdeploy, url_prefix='/ctdeploy')
    # except ModuleNotFoundError as message:
    #     return message
    return app
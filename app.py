# import native Python packages
import os

# import third party packages
from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(
        __name__ 
    )
    app.config.from_mapping(
        SECRET_KEY=os.environ['SECRET_KEY'],
        # DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # import apps
    from tarpeydev import index
    from tarpeydev import haveyouseenx
    from tarpeydev import mildredleague
    from tarpeydev import ddr
    from tarpeydev import autobracket
    from tarpeydev import timecapsule

    # register apps
    app.register_blueprint(index.index_bp)
    app.register_blueprint(haveyouseenx.hysx_bp)
    app.register_blueprint(mildredleague.ml_bp)
    app.register_blueprint(autobracket.autobracket_bp)
    app.register_blueprint(timecapsule.timecapsule_bp)
    app.register_blueprint(ddr.ddr_bp)

    # import and register errors
    # from . import errors
    # app.register_error_handler(400, handle_bad_request)

    return app

app = create_app()

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
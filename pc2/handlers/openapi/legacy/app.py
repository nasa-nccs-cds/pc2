from connexion.resolver import Resolver
from connexion.operations import AbstractOperation
import os, traceback
from flask import Flask, Response
import connexion, json, logging
from pc2.handlers.manager import Handlers
from functools import partial
from pc2.module.util.config import Config, PC2Logger
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

class PC2Resolver(Resolver):

    def __init__(self, api: str  ):
        Resolver.__init__( self, self.function_resolver )
        self.api = api

    def resolve_operation_id(self, operation: AbstractOperation) -> str:
        return '{}:{}'.format( self.api, operation.operation_id )

    def function_resolver( self, operation_id: str ) :
        return partial( Handlers.processRequest, operation_id )

class PC2App:
    HERE = os.path.dirname(__file__)
    SETTINGS = os.path.join( HERE, 'settings.ini')

    def __init__(self):
        self.logger = PC2Logger.getLogger()
        self.app = connexion.FlaskApp("pc2", specification_dir='api/', debug=True )
        self.app.add_error_handler( 500, self.render_server_error )
        self.app.app.register_error_handler( TypeError, self.render_server_error )
        settings = os.environ.get( 'PC2_SETTINGS', self.SETTINGS )
        config_file = Config(settings)
        flask_parms = config_file.get_map('flask')
        flask_parms[ 'SQLALCHEMY_DATABASE_URI' ] = flask_parms['DATABASE_URI']
        self.app.app.config.update( flask_parms )
        self.parms = config_file.get_map('pc2')
        api = self.getParameter( 'API' )
        handler = self.getParameter( 'HANDLER' )
        celery_parms = config_file.get_map('celery')
        self.app.app.config.update( celery_parms )
        self.celery = self.make_celery( self.app.app )
        self.db = SQLAlchemy( self.app.app )
        self.app.add_api( api + ".yaml", resolver=PC2Resolver( api ) )

    def run(self):
        port = self.getParameter( 'PORT', 5000 )
        self.db.create_all( )
        return self.app.run( int( port ) )

    def getParameter(self, name: str, default = None ) -> str:
        parm = self.parms.get( name, default )
        if parm is None: raise Exception( "Missing required pc2 parameter in settings.ini: " + name )
        return parm

    @staticmethod
    def render_server_error( ex: Exception ):
        print( str( ex ) )
        traceback.print_exc()
        return Response(response=json.dumps({ 'message': getattr(ex, 'message', repr(ex)), "code": 500, "rid": "", "status": "error" } ), status=500, mimetype="application/json")

    def make_celery( self, app: Flask ):
        celery = Celery( app.import_name, backend=app.config['DATABASE_URI'], broker=app.config['CELERY_BROKER_URL'] )
        celery.conf.update(app.config)

        class ContextTask(celery.TaskHandle):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.TaskHandle = ContextTask
        return celery

app = PC2App()

if __name__ == "__main__":
    app.run()

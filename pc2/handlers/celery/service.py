from pc2.handlers.base import Handler
from pc2.app.client import PC2Client
from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Optional
from .client import CeleryClient
from pc2.app.core import PC2Core
from pc2.app.base import PC2AppBase
from .app import PC2AppCelery
from pc2base.module.util.config import PC2Logger, UID
from pc2.util.parsing import str2bool
import subprocess, os
from threading import Thread

class TaskManager(Thread):

    def __init__(self, name: str ):
        Thread.__init__(self)
        self._name = name
        self.id = self._name
        self._completedProcess = None

    def run(self):
        self._completedProcess = subprocess.run(['celery', '--app=pc2.handlers.celery.app:app', 'worker', '-l', 'info',  '-Q', self._name,  '-n', self.id, '-E' ], check = True )

class FlowerManager(Thread):

    def __init__ (self ):
        Thread.__init__(self)
        self._completedProcess = None
        self.logger = PC2Logger.getLogger()

    def run(self):
        try:
            self._completedProcess = subprocess.run(['celery', 'flower', '--app=pc2.handlers.celery.app:app', '--port=5555', '--address=127.0.0.1' ], check = True )
        except Exception as err:
            self.logger.error( f"Error staring Celery: {err}" )

class ServiceHandler( Handler ):

    def __init__(self, **kwargs ):
        htype = os.path.basename(os.path.dirname(__file__))
        self._workers: Dict[str,TaskManager] = {}
        self._flower = None
        self.baseDir = os.path.dirname(__file__)
        super(ServiceHandler, self).__init__( htype, **kwargs )
        self._app: PC2AppCelery = None
        if str2bool( self.parm( 'flower', "false" ) ): self._startFlower()

    def newClient(self, core: PC2Core, **kwargs) -> PC2Client:
        app = self.getApplication( core )
        return CeleryClient( app, **kwargs )

    def newApplication(self, core: PC2Core, **kwargs ) -> PC2AppBase:
        return self.getApplication( core )

    def getCeleryCore(self, core: PC2Core, **kwargs ) -> PC2Core:
        for key, core_celery_params in core.config.items():
            if core_celery_params.get('type') == 'celery':
                celery_settings = core_celery_params.get( "settings")
                if celery_settings is not None:
                    return PC2Core(celery_settings)
        return core

    def getApplication(self, core: PC2Core, **kwargs ):
        if self._app is None:
            self._app = PC2AppCelery( self.getCeleryCore( core, **kwargs ) )
        return self._app

    def buildWorker( self, name: str, spec: Dict[str,str] ):
        if name not in self._workers:
            self._startWorker( name )

    def _startWorker(self, name: str ):
        taskManager = TaskManager( name )
        self._workers[ name ] = taskManager
        try:
            taskManager.start()
        except subprocess.CalledProcessError as err:
            self.logger.error( f" Worker exited with error: {err.stderr}")

    def _startFlower(self):
        if self._flower is None:
            self.logger.info( "Starting Flower")
            self._flower = FlowerManager()
            self._flower.start()
from pc2.handlers.base import Handler
from pc2.app.client import PC2Client
from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Optional
from .client import CeleryClient
from pc2.app.core import PC2Core
from pc2.app.base import PC2AppBase
from .app import PC2AppCelery
from pc2base.module.util.config import PC2Logger, UID
from pc2.util.parsing import str2bool
import subprocess, os, time
from threading import Thread

class TaskManager:

    def __init__(self, name: str ):
        self.logger = PC2Logger.getLogger()
        self._name = name
        self.id = self._name
        self._process: subprocess.Popen = None

    def start(self):
        try:
            self._process = subprocess.Popen(['/bin/bash', '-c', 'celery', '--app=pc2.handlers.celery.app:app', 'worker', '-l', 'info',  '-Q', self._name,  '-n', self.id, '-E' ] )
        except Exception as err:
            self.logger.error( f"Error staring Celery Worker {self._name}: {err}" )

    def shutdown(self):
        self._process.terminate()
        time.sleep(0.2)
        self._process.kill()

class FlowerManager:

    def __init__ (self ):
        self.logger = PC2Logger.getLogger()
        self._process: subprocess.Popen = None
        self.logger = PC2Logger.getLogger()

    def start(self):
        try:
            self._process = subprocess.Popen(['/bin/bash', '-c', 'celery', 'flower', '--app=pc2.handlers.celery.app:app', '--port=5555', '--address=127.0.0.1' ] )
        except Exception as err:
            self.logger.error( f"Error staring Flower: {err}" )

    def shutdown(self):
        self._process.terminate()
        time.sleep(0.2)
        self._process.kill()

class ServiceHandler( Handler ):

    def __init__(self, **kwargs ):
        htype = os.path.basename(os.path.dirname(__file__))
        self._workers: Dict[str,TaskManager] = {}
        self._flower: FlowerManager = None
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

    def shutdown(self, *args, **kwargs):
        Handler.shutdown( self, *args, **kwargs )
        if self._flower is not None: self._flower.shutdown()
        for worker in self._workers.values(): worker.shutdown()
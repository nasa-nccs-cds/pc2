from pc2.app.core import PC2Core
from pc2.app.base import PC2AppBase, PC2EmbeddedApp
from pc2.app.client import pc2request
from pc2.app.operations import WorkflowBase
from pc2base.module.util.config import PC2Logger, UID
from pc2base.module.handler.base import TaskHandle, TaskResult
from pc2.app.operations import PC2Workflow, WorkflowTask
from pc2.app.client import PC2Client
from pc2.handlers.manager import Handlers
from pc2.handlers.base import Handler
from celery import Celery
from typing import Dict, List, Optional
import queue, traceback, logging, os
from celery.utils.log import get_task_logger
from celery import Task
from celery.signals import after_setup_task_logger
from celery.app.log import TaskFormatter

logger = get_task_logger(__name__)
app = Celery( 'pc2', broker = 'redis://127.0.0.1', backend = 'redis://127.0.0.1' )

app.conf.update(
    result_expires=3600,
    task_serializer = 'pickle',
    accept_content = ['json', 'pickle', 'application/x-python-serialize'],
    result_serializer = 'pickle'
)
celery_log_file = os.path.expanduser("~/.pc2/logs/celery.log")
app.log.setup_logging_subsystem( loglevel=logging.INFO, logfile=celery_log_file, format='[%(asctime)s: %(levelname)s/%(processName)s-> %(pathname)s:%(lineno)d]: %(message)s' )

class CeleryTask(Task):
    def __init__(self):
        Task.__init__(self)
        self._handlers: Handlers = None
        self._name: str = None
        self.core: PC2Core = None
        self._handler: Handler = None

    def initHandler( self, clientSpec: Dict[str,Dict] ):
        if self._handlers is None:
            hspec: Dict[str,Dict] = { clientSpec['name']: clientSpec, "server": { 'type': "celery", 'name':"pc2" } }
            logger.info(f"Init Celery Task Handler with spec: {hspec}")
            self.core = PC2Core( hspec )
            self._handlers = Handlers( self.core, hspec )
            self._name, handlerSpec = list(hspec.items())[0]
            self._handler: Handler = self._handlers.available[ self._name ]

@app.task( bind=True, base=CeleryTask )
def celery_execute( self, inputs: List[TaskResult], clientSpec: Dict, requestSpec: Dict ) -> Optional[TaskResult]:
    cid = clientSpec.get('cid',"UNKNOWN")
    logger.info( f"Client[{cid}]: Executing request: {requestSpec}" )
    self.initHandler( clientSpec )
    client: PC2Client = self._handler.client( self.core )
    taskHandle: TaskHandle = client.request( requestSpec, inputs )
    return taskHandle.getResult( block=True ) if taskHandle else None

class PC2AppCelery(PC2EmbeddedApp):

    def createWorkflow( self, tasks: List[WorkflowTask] ) -> WorkflowBase:
        from pc2.handlers.celery.workflow import CeleryWorkflow
        return CeleryWorkflow( nodes=tasks, **self.parms )

    def processError(self, rid: str, ex: Exception): pass

    def initInteractions(self): pass

    def updateInteractions(self): pass

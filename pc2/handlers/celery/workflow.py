from pc2base.module.handler.base import  TaskHandle, Status, TaskResult, FailedTask
from pc2.app.operations import WorkflowBase, WorkflowTask
from pc2.app.graph import DGNode, DependencyGraph, graphop, Connection
from celery.result import AsyncResult
from pc2base.module.util.config import PC2Logger, UID
from celery import group, states
from pc2.app.client import PC2Client
from typing import Dict, List, Optional
import queue, datetime, time, traceback
from celery.utils.log import get_task_logger
from celery import Task
logger = get_task_logger(__name__)

class CeleryAsyncTaskHandle(TaskHandle):

    def __init__(self, manager: AsyncResult, **kwargs):
        TaskHandle.__init__( self, **kwargs )
        self.logger = PC2Logger.getLogger()
        self.manager: AsyncResult = manager
        self._exception = None

    def getResult( self, **kwargs ) ->  Optional[TaskResult]:
        timeout = kwargs.get("timeout",None)
        block = kwargs.get("block",False)
        try:
            if block:
                return self.manager.get( timeout )
            if self.manager.ready():
                if self.manager.successful():
                    return self.manager.result
                elif self.manager.failed():
                    self._exception = self.manager.result
                    return None
            else: return None
        except Exception as err:
            self._exception = err
            raise err

    def status(self) ->  Status:
        if self.manager.failed(): return Status.ERROR
        elif self.manager.successful(): return Status.COMPLETED
        elif self.manager.state in [ states.STARTED, states.RETRY]: return Status.EXECUTING
        elif self.manager.state in [states.PENDING, states.RECEIVED]: return Status.IDLE
        elif self.manager.state in [states.REJECTED, states.REVOKED]: return Status.CANCELED
        else: return Status.UNKNOWN

    def exception(self) -> Optional[Exception]:
        if self._exception is None and self.manager.failed():
            self._exception = self.manager.result
        return self._exception

class CelerySyncTaskHandle(TaskHandle):

    def __init__(self, result: TaskResult, **kwargs):
        TaskHandle.__init__( self, **kwargs )
        self.logger = PC2Logger.getLogger()
        self.result: TaskResult = result
        self._exception = None

    def getResult( self, **kwargs ) ->  Optional[TaskResult]:
        return  self.result

    def status(self) ->  Status:
        return Status.COMPLETED

    def exception(self) -> Optional[Exception]:
        return self._exception


class CeleryWorkflow(WorkflowBase):

    def __init__( self, **kwargs ):
        WorkflowBase.__init__(self, **kwargs)
        self.taskSigs: Dict = {}
        self.celery_workflow_sig = None
        self.celery_result: AsyncResult = None
        self.task_result: TaskResult = None
        self.executor = kwargs.get('executor','inline')
        self.rid: str = None
        self.logger.info( f"Starting Celery Workflow with parms: {kwargs}" )

    def getConnectedTaskSig( self, wtask: WorkflowTask ):
        from pc2.handlers.celery.app import celery_execute
        if wtask.id not in self.taskSigs:
            core_task_sig = celery_execute.signature( (wtask.clientSpec, wtask.requestSpec), queue=wtask.name )
            dep_sigs = [ self.getConnectedTaskSig(deptask) for deptask in wtask.dependencies ]
            if len(dep_sigs) == 0:
                self.taskSigs[wtask.id] =                       core_task_sig
            elif len( dep_sigs ) == 1:
                self.taskSigs[wtask.id] = (    dep_sigs[0]    | core_task_sig )
            else:
                self.taskSigs[wtask.id] = ( group( dep_sigs ) | core_task_sig )
        return self.taskSigs[wtask.id]

    def connect(self):
        if self.celery_workflow_sig is None:
            WorkflowBase.connect(self)
            for wtask in self.tasks:
                out_edges = self.graph.out_edges(wtask.id)
                connections = [Connection(self.graph.get_edge_data(*edge_tup)["id"], edge_tup[0], edge_tup[1]) for edge_tup in out_edges]
                nids = [conn.nid(Connection.OUTGOING) for conn in connections]
                consumer_tasks: List[WorkflowTask] = [self.nodes.get(nid) for nid in nids if nid is not None]
                wtask.setConsumers(consumer_tasks)
            for wtask in self.tasks:
                self.celery_workflow_sig = self.getConnectedTaskSig( wtask )


    @graphop
    def update( self ) -> bool:
        task_inputs = []

        if self.executor == "inline":
            if self.task_result == None:
                self.logger.info( f"Executing Celery inline Workflow")
                self.task_result: TaskResult = self.celery_workflow_sig(task_inputs)
                self._status = Status.COMPLETED
                return True
        else:
            if self.celery_result == None:
                self.logger.info( f"Executing Celery distributed Workflow")
                self.celery_result = self.celery_workflow_sig.apply_async( args=[task_inputs] )
                self.result = CeleryAsyncTaskHandle(self.celery_result)
                self._status = Status.EXECUTING
            else:
                if self.celery_result.successful():
                    self._status = Status.COMPLETED
                    return True
                elif self.celery_result.failed():
                    self._status = Status.ERROR
                    exc = self.celery_result.result
                    self.logger.error(traceback.format_exc())
                    raise Exception("Workflow Errored out: " + (getattr(exc, 'message', repr(exc)) if exc is not None else "NULL"))
            return False

    def getResult(self) -> TaskHandle:
        if self.celery_result is not None:
            return CeleryAsyncTaskHandle(self.celery_result)
        elif self.task_result is not None:
            return CelerySyncTaskHandle(self.task_result)
        else: return WorkflowBase.getResult(self)


from celery import Celery
from pc2.module.util.config import PC2Logger, UID
from threading import Thread
from typing import Dict, Optional, List
from pc2.util.parsing import s2b, b2s
from .app import PC2AppCelery
from pc2.module.handler.base import TaskHandle, Status, TaskResult
from pc2.app.client import PC2Client, pc2request
from pc2.app.core import PC2Core
import os, pickle, queue
import xarray as xa
from enum import Enum
MB = 1024 * 1024

class CeleryClient(PC2Client):

    def __init__( self, app: PC2AppCelery, **kwargs ):
        super(CeleryClient, self).__init__( "celery", **kwargs )
        self._app = app

    @pc2request
    def request(self, request: Dict, inputs: List[TaskResult] = None, **kwargs ) -> TaskHandle:
        return self._app.handle_client_request(request, inputs, **kwargs)

    def status(self, **kwargs ) -> Status:
        from pc2.app.operations import PC2Workflow
        rid = kwargs.get("rid")
        workflow: Optional[PC2Workflow] = self._app.getWorkflow(rid)
        if workflow in None: return Status.UNKNOWN
        return workflow.status()

    def capabilities(self, type: str, **kwargs ) -> Dict:
        return self._app.capabilities( type, **kwargs )

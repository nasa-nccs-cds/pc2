from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Tuple, Optional
from pc2base.module.util.config import Config, PC2Logger, UID
from pc2base.module.handler.base import TaskHandle, Status, TaskResult
from pc2.app.client import PC2Client, pc2request
from pc2.app.base import PC2AppBase
from pc2.app.core import PC2Core
import abc, fnmatch
from decorator import decorator, dispatch_on


class PC2AppClient(PC2Client):

    def __init__( self, core: PC2Core, type: str, **kwargs ):
        PC2Client.__init__( self, type, **kwargs )
        self.app: PC2AppBase = core.getApplication()

    def init(self, **kwargs): pass

    @pc2request
    def request(self, requestSpec: Dict, inputs: List[TaskResult] = None, **kwargs ) -> TaskHandle:
        self.app.requestQueue.put(requestSpec)
        task: Optional[TaskHandle] = self.app.getResult(rid)
        return task

    def capabilities(self, ctype: str, **kwargs ) -> Dict:
        return self.app.capabilities( ctype, **kwargs )

    def log(self, msg: str ):
        self.logger.info( "[ZP] " + msg )

    def __del__(self):
        self.app.shutdown()

    def shutdown(self, *args, **kwargs):
        self.app.shutdown()
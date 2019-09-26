from pc2.app.client import PC2Client, pc2request
from pc2.module.handler.base import TaskHandle, Module, TaskResult
from typing import Dict, List
import importlib, traceback

class DirectClient(PC2Client):

    def __init__( self, **kwargs ):
        super(DirectClient, self).__init__( "module", **kwargs )
        self.module: Module = None

    def instantiateModule( self ) -> Module:
        module = self["module"]
        class_name = self["object"]
        module = importlib.import_module(module)
        epclass = getattr(module, class_name)
        return  epclass( **self.parms )

    @pc2request
    def request(self, requestDict: Dict, inputs: List[TaskResult] = None, **kwargs ) -> TaskHandle:
        eparms = { "handle":self.handle, "rid":requestDict["rid"], **self.parms, **kwargs }
        self.logger.info( f" >>>----> Submitting request to module {self.module.__class__.__name__}: {requestDict}")
        return self.module.request( requestDict, inputs, **eparms )

    def capabilities(self, type: str, **kwargs ) -> Dict:
        return self.module.capabilities( type, **kwargs )

    def init(self):
        try:
            if self.module is None:
                self.module: Module = self.instantiateModule()
                self.module.init()
                super(DirectClient, self).init()

        except Exception as err:
            err_msg =  "\n-------------------------------\nWorker Init error: {0}\n{1}-------------------------------\n".format(err, traceback.format_exc() )
            self.logger.error(err_msg)
            self.logger.error(traceback.format_exc())
            if self.module is not None:
                self.module.shutdown()



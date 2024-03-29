import os
from typing import Dict, List
from pc2base.module.handler.test import Module, TaskHandle, TestTask, TaskResult

class TestModule1(Module):

    def __init__( self, **kwargs ):
        Module.__init__( self, **kwargs )
        self._epas = [ f"test{index}" for index in range(10) ]

    def request(self, requestSpec: Dict, inputs: List[TaskResult] = None, **kwargs ) -> "TaskHandle":
        workTime = self.getWorktime( requestSpec["operations"] )
        tparms = { **self.parms, **kwargs }
        self.logger.info( f"exec TestModule, request = {requestSpec}, parms = {tparms}")
        return TestTask( workTime, **tparms )

    def getWorktime(self, operations: List[Dict]) -> float :
        return sum( [ float(op.get("workTime", 0.0)) for op in operations ] )

    def shutdown(self, *args, **kwargs ): pass

    def capabilities(self, type: str, **kwargs  ) -> Dict:
        if type == "epas":
            return dict( epas = self._epas )

    def init( self ): pass

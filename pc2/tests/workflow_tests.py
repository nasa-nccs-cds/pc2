from pc2.app.core import PC2Core
from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Optional
from pc2.module.handler.base import TaskHandle
import os

testModule = dict( type="module", module="pc2.handlers.module.test", object="TestModule1" )

if __name__ == "__main__":

    settings = dict( server=dict(type="test"), test1=testModule, test2=testModule, test3=testModule )
    pc2 = PC2Core( settings )
    app = pc2.getApplication()

    operation= [ dict( name='test1:op', result="r1", cid = "C0", workTime="3.0" ),
                 dict( name='test2:op', result="r2", cid = "C1", workTime="6.0" ),
                 dict( name='test3:op', input=["r1","r2"], result="r3", cid = "C2", workTime="1.0" )   ]
    request=dict( operation=operation, rid="R0", cid="C0" )

    app.submitWorkflow(request)
    for taskHandle in taskHandles.values():
        result = taskHandle.getResult()
        print( result )

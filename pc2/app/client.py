from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Tuple, Optional
from pc2base.module.util.config import Config, PC2Logger, UID
from pc2base.module.handler.base import TaskHandle, Status, TaskResult
import abc, fnmatch, traceback
from decorator import decorator, dispatch_on

class ModuleSpec:
    def __init__(self, epaSpec: str ):
        self.logger = PC2Logger.getLogger()
        self._epaSpec = epaSpec

    def handles( self, epa: str, **kwargs ) -> bool:
        try:
            self.logger.debug(f"ModuleSpec: comparing '{epa}' against epaSpec '{self._epaSpec}'")
            return fnmatch.fnmatch( epa, self._epaSpec )
        except Exception as err:
            self.logger.error( f"Error Checking EPA '{epa}' against epaSpec '{self._epaSpec}': {str(err)}")
            return False

    def __str__(self):
        return self._epaSpec

@decorator
def pc2request( func, *args, **kwargs ):
    new_args = list(args)
    new_args[1] = args[0].updateMetadata( args[1] )
    return func( *new_args, **kwargs)

class PC2Client:
    __metaclass__ = abc.ABCMeta
    logger = PC2Logger.getLogger()

    def __init__( self, type: str, **kwargs ):
        cid = kwargs.get( "cid" )
        self.cid = cid if cid else UID.randomId(6)
        self.type: str = type
        self.name: str = kwargs.get("name")
        self.cache_dir: str = kwargs.get( "cache_dir", "~/.edas/cache" )
        self.parms = { **kwargs, "cid": self.cid, "type": type }
        self.priority: float = float( self.parm( "priority", "0" ) )
        self.active = False
        self._moduleSpecs: List[ModuleSpec] = None
        self.clients = { self.cid }

    @property
    def handle(self):
        return f"{self.name}:{self.cid}"

    def activate(self):
        self.active = True
        self.init()

    def exit(self):
        self.active = False
        self._shutdown()

    def init( self ):
        if self._moduleSpecs is None:
            moduleData = self.capabilities("epas")
            if "error" in moduleData: raise Exception( "Error accessing module data: " + moduleData["message"] )
            self.logger.info( "ModuleSpecs: " + str(moduleData))
            self._moduleSpecs = [ ModuleSpec(epaSpec) for epaSpec in moduleData["epas"] ]
            self.activate()

    @abc.abstractmethod
    @pc2request
    def request(self, request: Dict, inputs: List[TaskResult] = None, **kwargs ) -> TaskHandle: pass

    @abc.abstractmethod
    def status(self, **kwargs ) -> Status: pass

    @abc.abstractmethod
    def capabilities(self, type: str, **kwargs ) -> Dict: pass

    @abc.abstractmethod
    def _shutdown(self): pass

    @property
    def moduleSpecs(self) -> List[str]:
        return [str(eps) for eps in self._moduleSpecs]

    def handles(self, epa: str, **kwargs ) -> bool:
        for moduleSpec in self._moduleSpecs:
            if moduleSpec.handles( epa, **kwargs ): return True
        return False

    def __getitem__( self, key: str ) -> str:
        result =  self.parms.get( key, None )
        assert result is not None, "Missing required parameter in {}: {}, params: {}\n  * {} ".format( self.__class__.__name__, key, str(self.parms), "\n  * ".join(traceback.format_stack()) )
        return result

    def parm(self, key: str, default: str = None) -> Optional[str]:
        return self.parms.get( key, default  )

    def updateMetadata(self, requestSpec: Dict ) -> Dict:
        requestDict = dict(requestSpec)
        source_client = requestDict.get("cid")
        requestDict["rid"] = requestSpec.get("rid",UID.randomId(6))
        if source_client: self.clients.add( source_client )
        requestDict["cid"] = self.cid
        requestDict["clients"] = ",".join( self.clients )
        return requestDict

    def hasClient(self, cid: str ) -> bool:
        return cid in self.clients


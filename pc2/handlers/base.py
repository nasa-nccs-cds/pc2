from pc2.app.client import PC2Client
from pc2.app.base import PC2AppBase, PC2Factory
from pc2.app.core import PC2Core
from pc2.app.base import PC2CoreBase
from typing import List, Dict, Any, Sequence, BinaryIO, TextIO, ValuesView, Optional
import abc


class Handler(PC2Factory):
    __metaclass__ = abc.ABCMeta

    def __init__(self, htype: str, **kwargs):
        PC2Factory.__init__(self, htype, **kwargs)
        self._clients = {}
        self._app: PC2AppBase = None

    @abc.abstractmethod
    def newClient(self, core: PC2Core, **kwargs) -> PC2Client: pass

    def getClient(self, cid = None ) -> Optional[PC2Client]:
        if cid is None:
            return None if len(self._clients) == 0 else list(self._clients.values())[0]
        else: return self._clients.get( cid )

    @abc.abstractmethod
    def newApplication(self, core: PC2Core, **kwargs ) -> PC2AppBase: pass

    def client( self, core: PC2Core, **kwargs ) -> PC2Client:
        cid = kwargs.get("cid")
        activate = kwargs.get( "activate", True )
        client: PC2Client = self.getClient( cid )
        if client is None:
            self.logger.info(f"create client {self.name}:\n kwargs= {kwargs}\n core.parms = {core.parms}\n core.config = {core.config}\n handler.parms = {self.parms}\n handler.type = {self.type}\n handler.name = {self.name}")
            client = self.newClient( core, **self.parms )
            self._clients[ client.cid ] = client
            if activate: client.activate()
        return client

    def app(self, core: PC2Core ) -> PC2AppBase:
        return self.newApplication(core)

    def shutdown(self, *args, **kwargs):
        if self._app is not None:
            self._app.shutdown()
        for client in self._clients.values():
            client.exit()




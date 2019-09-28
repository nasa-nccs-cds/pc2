from typing import List, Dict, Union
from pc2.app.client import PC2Client
from pc2.handlers.manager import Handlers
from pc2.app.base import PC2AppBase, PC2CoreBase
from pc2.app.operations import Op

class PC2Core(PC2CoreBase):

    def __init__(self, configSpec: Union[str,Dict[str,Dict]], **kwargs ):
        PC2CoreBase.__init__(self, configSpec, **kwargs )
        self.handlers = Handlers( self, self.config, **kwargs )

    @property
    def internal_clients(self):
        return self.handlers.internal_clients

    def getClients( self, op: Op = None, **kwargs ) -> List[PC2Client]:
        return self.handlers.getClients( self, op, **kwargs )

    def getClient( self, **kwargs ) -> PC2Client:
        service = self.handlers.getApplicationHandler()
        assert service is not None, "Can't find [pc2] handler: missing configuration?"
        client = service.client(self, **kwargs)
        return client

    def getApplication( self ) -> PC2AppBase:
        service = self.handlers.getApplicationHandler()
        assert service is not None, "Can't find [pc2] handler: missing configuration?"
        app =  service.app(self)
        self.logger.info( "Starting PC2 Node: " + str(app.__class__) )
        return app

    def getEpas( self,  **kwargs ) -> List[str]:
        return self.handlers.getEpas(self,  **kwargs)

    def exit(self):
        self.handlers.shutdown()

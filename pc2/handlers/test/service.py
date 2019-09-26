import os
from pc2.handlers.base import Handler
from pc2.app.client import PC2Client
from pc2.app.base import PC2AppBase, TestPC2App
from pc2.app.core import PC2Core
from .client import TestClient

class ServiceHandler( Handler ):

    def __init__(self, **kwargs ):
        htype = os.path.basename(os.path.dirname(__file__))
        super(ServiceHandler, self).__init__( htype, **kwargs )

    def newClient( self, core: PC2Core, **kwargs ) -> PC2Client:
        return TestClient( **kwargs )

    def newApplication(self, core: PC2Core, **kwargs ) -> PC2AppBase:
        return TestPC2App( core )







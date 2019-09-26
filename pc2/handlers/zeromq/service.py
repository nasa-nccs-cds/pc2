from pc2.handlers.base import Handler
from pc2.app.client import PC2Client
from .client import ZMQClient
from pc2.app.core import PC2Core
from .app import PC2App
import os

MB = 1024 * 1024

class ServiceHandler( Handler ):

    def __init__(self, **kwargs ):
        htype = os.path.basename(os.path.dirname(__file__))
        super(ServiceHandler, self).__init__( htype, **kwargs )

    def newClient( self, core: PC2Core, **kwargs ) -> PC2Client:
        return ZMQClient( **kwargs )

    def newApplication(self, core: PC2Core, **kwargs ) -> PC2App:
        return PC2App( core, **kwargs )



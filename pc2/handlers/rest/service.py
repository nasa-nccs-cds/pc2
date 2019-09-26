from pc2.handlers.base import Handler
from pc2.app.client import PC2Client
from pc2.app.core import PC2Core
from pc2.handlers.rest.api.core.client import CoreRestClient
from pc2.handlers.rest.api.wps.client import WPSRestClient
from pc2.handlers.rest.api.ows_wps.client import OwsWpsClient
from pc2.handlers.rest.app import PC2App
import os

MB = 1024 * 1024

class ServiceHandler( Handler ):

    def __init__(self, **kwargs ):
        htype = os.path.basename(os.path.dirname(__file__))
        super(ServiceHandler, self).__init__( htype, **kwargs )

    def newClient( self, core: PC2Core, **kwargs ) -> PC2Client:
        cid = kwargs.get("cid")
        gateway = kwargs.get("gateway")
        API = self.parm("API","core").lower()
        cparms = {"cid": cid, **self.parms} if cid else self.parms
        if API == "core":    return CoreRestClient( gateway=gateway, **cparms )
        if API == "wps":     return WPSRestClient(  gateway=gateway, **cparms )
        if API == "ows_wps": return OwsWpsClient(   gateway=gateway, **cparms )
        raise Exception( "Unrecognized API in REST ServiceHandler: " + API)

    def newApplication(self, core: PC2Core, **kwargs ) -> PC2App:
        return PC2App( core )

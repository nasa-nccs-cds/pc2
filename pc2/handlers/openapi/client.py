from pyswagger import App
from pyswagger.contrib.client.requests import Client
from pc2.module.handler.base import TaskHandle, TaskResult
from pyswagger.spec.v2_0.objects import Operation
from typing import Dict, List
from pc2.app.client import PC2Client, pc2request

class OpenApiClient(PC2Client):

    def __init__( self, **kwargs ):
        super(OpenApiClient, self).__init__( "openapi", **kwargs )

    @pc2request
    def request(self, requestDict: Dict, inputs: List[TaskResult] = None, **kwargs ) -> TaskHandle:
        op: Operation = self.app.op[ task ]
        response = self.client.request( op(**kwargs) )
        return response.data

    def init(self):
        self.server = self["server"]
        self.port = self["port"]
        self.api = self["api"]
        openapi_spec = 'http://{}:{}/{}/swagger.json'.format( self.server, str(self.port), self.api )
        self.app = App._create_( openapi_spec )
        self.client = Client()
        PC2Client.init( self )

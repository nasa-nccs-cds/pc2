from pc2.handlers.module.test import TestModule1
from pc2.handlers.module.client import DirectClient
from typing import Dict


class TestClient(DirectClient):

    def __init__( self, **kwargs ):
        super(TestClient, self).__init__( **kwargs )
        self._epas = [ "test" ]


    def instantiateModule(self):
        eparms = { "handle":self.handle, **self.parms }
        return TestModule1( **eparms )


    def capabilities(self, type: str, **kwargs  ) -> Dict:
        if type == "epas":
            return dict( epas = self._epas )

if __name__ == "__main__":
    dc = TestClient()
    dc.instantiateModule()

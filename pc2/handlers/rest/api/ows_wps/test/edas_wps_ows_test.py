from pc2.app.core import PC2Core
from pc2base.module.handler.base import TaskHandle
from pc2.util.test import TestDataManager as mgr

settings = dict( server = dict( type="rest", API="ows_wps", host="127.0.0.1", port="5000", route="ows_wps/cwt" ) )
core = PC2Core(settings)
client = core.getClient()

local_request = dict(
    domain=[{"name": "d0", "lat": {"start": 50, "end": 55, "system": "values"},
             "lon": {"start": 40, "end": 42, "system": "values"},
             "time": {"start": "1980-01-01", "end": "1981-12-31", "crs": "timestamps"}}],
    input=[{"uri": mgr.getAddress("merra2", "tas"), "name": "tas:v0", "domain": "d0"}],
    operation=[{'name': "xarray.ave", 'axes': "t", "input": "v0"}]
)

task: TaskHandle = client.request(local_request)
result = task.getResult(block=True)
if result is not None:
    print( "Got Result: " + str(result.header) )



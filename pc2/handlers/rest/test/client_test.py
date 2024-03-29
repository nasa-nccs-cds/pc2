from pc2base.module.handler.base import TaskHandle, TaskResult
from typing import List, Optional
from pc2.util.test import TestDataManager as mgr
import xarray as xa
from pc2.app.core import PC2Core

if __name__ == "__main__":

    settings = dict(server=dict(type="rest", host="127.0.0.1", port="5000", api="core"))
    pc2 = PC2Core(settings)
    client = pc2.getClient()
    time_range = {"start": "1980-01-01", "end": "2001-12-31", "crs": "timestamps"}
    uri = mgr.getAddress("merra2", "tas")
    numDomains = 2
    domains = [f"d{i}" for i in range(numDomains)]

    requestSpec = dict(

        domain=[dict(name=f"d{i}", lat=dict(start=0, end=15, system="values"), lon=dict(start=i * 20, end=(i * 20) + 15, system="values"), time=time_range) for
                i in range(numDomains)],

        input=[dict(uri=uri, name=f"tas:v{i}", domain=f"d{i}") for i in range(numDomains)],

        operation=[dict(name="edas.ave", axis="xy", input=f"v{i}") for i in range(numDomains)]
    )

    task: TaskHandle = client.request(requestSpec)
    result: Optional[TaskResult] = task.getResult(block=True)
    dsets: List[xa.Dataset] = result.data
    for index, dset in enumerate(dsets):
        fileName = f"/tmp/edas_module_test_result-{index}.nc"
        print(f"Got result[{index}]: Saving to file {fileName} ")


##pc2
#### Process Controller using Celery

PC2 is a workflow orchestration framework for incorporating varied earth data analytic modules as a unified solution. 
### Installation

Conda environment setup:
```
 >> conda create -n stratus -c conda-forge python=3.6 libnetcdf netCDF4 pyyaml six xarray networkx requests decorator
 ```
 
Install Celery and Redis:
```
>> pip install "celery[redis]"
```

Start Redis
```
>> redis-server
```

Build PC2 installation by installing the pc2-module and pc2 packages:

    >> git clone https://github.com/nasa-nccs-cds/pc2-module.git
    >> cd pc2-module
    >> python setup.py install

    > git clone https://github.com/nasa-nccs-cds/pc2.git
    > cd pc2
    > python setup.py install <handlers(s)>

The handlers(s) qualifier in the last install command tells the builder to include dependencies for the listed optional services.  To build a pc2 instance that supports both the zeromq and rest services one would execute *“python setup.py install zeromq rest”*, or for only rest: *“python setup.py install rest”*.  

Following are the optional pc2 services:
 
* zeromq
* openapi
* rest
* rest_client

##### Examples

In order to expose some capability within the pc2 framework, that capability must be wrapped as a pc2 module.
Examples of PC2 module wrappings can be found in the `pc2/handlers/module/samples` directory.




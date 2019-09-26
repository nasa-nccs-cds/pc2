##pc2
#### Process Controller using Celery

PC2 is a workflow orchestration framework for incorporating varied earth data analytic modules as a unified solution. 
### Installation

Conda environment setup:

 >> conda create -n stratus -c conda-forge python=3.6 libnetcdf netCDF4 pyyaml six xarray networkx requests decorator
 
Build Stratus installation by installing the stratus-endpoint and stratus packages:

    >> git clone https://github.com/nasa-nccs-cds/pc2-endpoint.git
    >> cd pc2-endpoint
    >> python setup.py install

    > git clone https://github.com/nasa-nccs-cds/pc2.git
    > cd pc2
    > python setup.py install <handlers(s)>

The handlers(s) qualifier in the last install command tells the builder to only install dependencies for the listed service handlers.  E.g. to build a service that supports both zeromq and rest one would execute *“python setup.py install zeromq rest”*, or for only rest: *“python setup.py install rest”*.  Simply executing *“python setup.py install”* would install the dependencies for all supported stratus service handlers.

The following are the currently available pc2 service handlers: 
* module
* zeromq
* openapi
* rest
* rest_client
* celery

##### Examples

In order to expose some capability within the pc2 framework, that capability must be wrapped as a pc2 module.
Examples of Stratus endpoint wrappings can be found in the `pc2/handlers/module/samples` directory.




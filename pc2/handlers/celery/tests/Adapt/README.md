# NASA Adapt Demo Recipe

## Installation

#### Setup Redis & Conda packages
Create the directory $MY_NOBACKUP_DIR/conda/envs and then the following can go into your .bash_profile file:
```
source /att/opt/other/centos/modules/init/bash
export MODULEPATH=/att/opt/other/centos/modules/modulefiles
export CONDA_ENVS_PATH=$MY_NOBACKUP_DIR/conda/envs
module load redis
module load anaconda3
initconda
```
#### Start Redis
  *Note that if you get an error like "Address already in use" then Redis is already started*
```
>> redis-server
```

#### Create PC2 Virtual Environment:
```
 >> cd $MY_VENV_ROOT
 >> python3 -m venv pc2
 >> source ./pc2/bin/activate 
 >> mkdir -p $HOME/.config/pip
 >> cp /att/nobackup/tpmaxwel/venvs/pc2/pip.conf $HOME/.config/pip/
 >> pip install --upgrade pip
 ```
 
#### Install Celery with Redis dependencies:
```
>> pip install "celery[redis]"
```

#### Install PC2:
```
>> cd $MY_PROJECT_ROOT
>> git clone https://github.com/nasa-nccs-cds/pc2.git
>> cd pc2
>> python setup.py install celery zeromq
```

#### Install PC2-Module:
```
>> cd $MY_PROJECT_ROOT
>> git clone https://github.com/nasa-nccs-cds/pc2-module.git
>> cd pc2
>> python setup.py install
```

#### Create MMX Conda Environment (in a new shell):
```
 >> conda create -n mmx 
 >> conda activate mmx
 >> conda install gdal xarray dask 
 ```
 
 #### Install MMX & PC2:
 ```
>> cd $MY_PROJECT_ROOT
>> git clone https://github.com/nasa-nccs-hpda/innovation-lab.git
>> cd innovation-lab
>> git checkout mmx_alone
>> python setup.py install

>> cd $MY_PROJECT_ROOT/pc2
>> python setup.py install zeromq
>> cd $MY_PROJECT_ROOT/pc2-module
>> python setup.py install 
```
 
 #### Create EDAS Conda Environment (in a new shell):
 ```
 >> conda create -n edas -c conda-forge dask distributed xarray bokeh bottleneck defusedxml zeromq 
 >> conda activate edas
 ```
 
 #### Install EDAS & PC2:
  ```
>> cd $MY_PROJECT_ROOT
>> git clone https://github.com/nasa-nccs-cds/edas.git
>> cd innovation-lab
>> git checkout mmx_alone
>> python setup.py install

>> cd $MY_PROJECT_ROOT/pc2
>> python setup.py install zeromq
>> cd $MY_PROJECT_ROOT/pc2-module
>> python setup.py install 
```

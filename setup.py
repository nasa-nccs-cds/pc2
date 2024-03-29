import sys, os
from setuptools import setup, find_packages
base_services = [  "module" ]

def get_requirements():
    handlers = [ "celery", "zeromq", "rest", "rest_client" ]
    requirement_files = [ f"requirements/{service}.txt" for service in  base_services ]
    for handler in handlers:
        if handler in sys.argv:
            sys.argv.remove(handler)
            requirement_files.append( f"requirements/{handler}.txt" )
    return requirement_files

install_requires = set()
for requirement_file in get_requirements():
    with open( requirement_file ) as f:
        for dep in f.read().split('\n'):
            if dep.strip() != '' and not dep.startswith('-e'):
                install_requires.add( dep )

print( "Installing with dependencies: " + str(install_requires) )

setup(name='pc2',
      version='1.0',
      description='PC2: Process Controller using Celery',
      author='Thomas Maxwell',
      author_email='thomas.maxwell@nasa.gov',
      url='https://github.com/nasa-nccs-cds/pc2.git',
      packages=find_packages(),
      package_data={ 'pc2': ['api/*.yaml'], 'pc2.handlers.rest.api.wps': ['templates/*.xml'], 'pc2.handlers.rest.api.ows_wps': ['templates/*.xml'] },
      zip_safe=False,
      include_package_data=True,
      install_requires=list(install_requires))

import os, sys
import pkgutil

def list_submodules( package_name: str ):
    try:
        package = __import__(package_name)
    except ImportError:
        print('Package {} not found...'.format(package_name))
        sys.exit(1)

    modules = []
    print( package.__path__ )
    print(package.__name__)
    for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if is_pkg: modules.append( module_name )
    return modules

all_modules = list_submodules( "stratus" )

print(all_modules)

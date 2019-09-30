from pc2.handlers.zeromq.app import PC2App
from pc2.app.core import PC2Core
import os, sys
HERE: str = os.getcwd()

def abs_path( relpath: str) -> str:
    if relpath is None: return HERE
    return relpath if relpath.startswith("/") else os.path.join(HERE, relpath)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print( "Usage: >> python -m pc2.app.server <settingsFilePath>")
    else:
        core: PC2Core = PC2Core( abs_path(sys.argv[1]) )
        app: PC2App = core.getApplication()
        app.run()

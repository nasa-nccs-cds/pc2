from pc2.handlers.zeromq.app import PC2App
from pc2.app.core import PC2Core
import os
HERE: str = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE: str = os.path.join( HERE, "rest_celery.ini" )

if __name__ == '__main__':
    if __name__ == "__main__":
        core: PC2Core = PC2Core(SETTINGS_FILE)
        app: PC2App = core.getApplication()
        app.run()

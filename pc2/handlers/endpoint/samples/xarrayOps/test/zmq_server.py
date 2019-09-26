from pc2.handlers.zeromq.app import PC2App
from pc2.app.core import PC2Core
import os
HERE: str = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE: str = os.path.join( HERE, "zmq_server_settings.ini" )

if __name__ == '__main__':

# Start up a PC2 server as configured in the settings file

    core: PC2Core = PC2Core(SETTINGS_FILE)
    app: PC2App = core.getApplication()
    app.run()

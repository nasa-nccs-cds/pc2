from pc2.app.core import PC2Core
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join( HERE, "test_settings.ini" )

if __name__ == "__main__":
    core = PC2Core( SETTINGS_FILE )
    app = core.getApplication()
    app.start()

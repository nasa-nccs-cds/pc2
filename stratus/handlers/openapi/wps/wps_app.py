from stratus.app.core import StratusCore
import os
HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join( HERE, "test_settings.ini" )

if __name__ == "__main__":
    core = StratusCore( SETTINGS_FILE )
    app = core.getApplication()
    app.start()

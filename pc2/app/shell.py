import os, sys, json
from cmd import Cmd
from pc2base.module.util.config import PC2Logger, UID
from pc2.app.client import PC2Client
from pc2base.module.handler.base import TaskHandle, TaskResult
from typing import Sequence, List, Dict, Mapping, Optional, Any
import os, xarray as xa
from pc2.app.core import PC2Core
HERE: str = os.getcwd()

class PC2Shell(Cmd):
    prompt = 'pc2> '
    intro = "Welcome tp PC2! Type ? to list commands"

    def __init__( self, settingsFilePath: str, **kwargs ):
        Cmd.__init__(self)
        self.parms = kwargs
        self.logger = PC2Logger.getLogger()
        settings: str = self.abs_path( settingsFilePath )
        self.core = PC2Core( settings )
        self.client: PC2Client = self.core.getClient()
        self.results: Dict[str,TaskHandle] = {}

    def do_exit(self, inp):
        print("Shutting down")
        self.client.exit()
        self.core.exit()
        print("Exiting")
        return True

    def do_exe(self, requestFilePath ):
        requestSpec = self.load_request( requestFilePath )
        task: TaskHandle = self.client.request( requestSpec )
        print( f"Request {task.rid} returned a result" )
        self.results[ task.rid ] = task

    def do_ls(self, path: str = None ):
        mypath = self.abs_path( path )
        ldir =  os.listdir( mypath )
        for f in ldir:
            if os.path.isfile( os.path.join( mypath, f )):
                print( f" F:  {f}" )
        for f in ldir:
            if os.path.isdir( os.path.join( mypath, f )) and f not in [ "~", "__pycache__"]:
                print( f"  D:  {f}" )

    def help_exe(self):
        print("pc2> exe <request_file>:  Execute the request defined in <dir>")

    def help_ls(self):
        print("pc2> ls <dir>:  List all files in (optional) <request_file>")

    def help_exit(self):
        print('Exit the application. Shorthand: x q Ctrl-D.')

    def default(self, inp):
        if inp == 'x' or inp == 'q': return self.do_exit(inp)
        print("Default: {}".format(inp))

    def abs_path(self, relpath: str ) -> str:
        if relpath is None: return HERE
        return relpath if relpath.startswith("/") else os.path.join(HERE, relpath)

    def load_request(self, requestFilePath: str):
        return json.load( open( self.abs_path(requestFilePath) ) )

    do_EOF = do_exit
    help_EOF = help_exit

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print( "Usage: >> python -m pc2.app.shell <settingsFilePath>")
    else:
        shell = PC2Shell( sys.argv[1] )
        shell.cmdloop()
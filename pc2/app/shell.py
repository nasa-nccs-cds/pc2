import os, sys
from cmd import Cmd

class PC2Shell(Cmd):
    prompt = 'pc2> '
    intro = "Welcome tp PC2! Type ? to list commands"

    def __init__( self, **kwargs ):
        Cmd.__init__(self)
        self.parms = kwargs
        self.ofile = open(r"/tmp/pc2_shell.log", "w")

    def do_exit(self, inp):
        print("Exiting")
        return True

    def do_exe(self, inp):
        print("Executing '{}'".format(inp))

    def help_exe(self):
        print("pc2> exe <request_file>:  Execute the request defined in <request_file>")

    def help_exit(self):
        print('Exit the application. Shorthand: x q Ctrl-D.')

    def default(self, inp):
        if inp == 'x' or inp == 'q': return self.do_exit(inp)
        print("Default: {}".format(inp))

    do_EOF = do_exit
    help_EOF = help_exit

if __name__ == "__main__":
    shell = PC2Shell( )
    shell.cmdloop()

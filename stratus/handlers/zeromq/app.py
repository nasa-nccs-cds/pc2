from stratus.app.base import StratusServerApp
from stratus.app.core import StratusCore
import json, os, sys
from stratus_endpoint.util.config import StratusLogger
from zmq.auth.thread import ThreadAuthenticator
import zmq, traceback
from typing import Dict
import queue, datetime
from .responder import StratusZMQResponder, StratusResponse
from stratus_endpoint.handler.base import Status
MB = 1024 * 1024

class StratusApp(StratusServerApp):

    def __init__( self, core: StratusCore, **kwargs ):
        StratusServerApp.__init__(self, core, **kwargs)
        self.logger =  StratusLogger.getLogger()
        self.active = True
        self.parms = self.getConfigParms('stratus')
        self.client_address = self.parms.get( "client_address","*" )
        self.request_port = self.parms.get( "request_port", 4556 )
        self.response_port = self.parms.get( "response_port", 4557 )
        self.active_handlers = {}
        self.getCertDirs()

    def getCertDirs(self):   # These directories are generated by the generate_certificates script
        self.cert_dir = self.parms.get( "certificate_path", os.path.expanduser("~/.stratus/zmq") )
        self.logger.info( f"Loading certificates and keys from directory {self.cert_dir}")
        self.keys_dir = os.path.join( self.cert_dir, 'certificates')
        self.public_keys_dir = os.path.join( self.cert_dir, 'public_keys')
        self.secret_keys_dir = os.path.join( self.cert_dir, 'private_keys')

        if not (os.path.exists(self.keys_dir) and os.path.exists(self.public_keys_dir) and os.path.exists(self.secret_keys_dir)):
            from stratus.handlers.zeromq.security.generate_certificates import generate_certificates
            generate_certificates( self.cert_dir )

    def initSocket( self ):
        try:
            server_secret_file = os.path.join( self.secret_keys_dir, "server.key_secret" )
            server_public, server_secret = zmq.auth.load_certificate(server_secret_file)
            self.request_socket.curve_secretkey = server_secret
            self.request_socket.curve_publickey = server_public
            self.request_socket.curve_server = True
            self.request_socket.bind( "tcp://{}:{}".format( self.client_address, self.request_port ) )
            self.logger.info( "@@STRATUS-APP --> Bound authenticated request socket to client at {} on port: {}".format( self.client_address, self.request_port ) )
        except Exception as err:
            self.logger.error( "@@STRATUS-APP: Error initializing request socket on {}, port {}: {}".format( self.client_address,  self.request_port, err ) )
            self.logger.error( traceback.format_exc() )

    def addHandler(self, clientId, jobId, handler ):
        self.active_handlers[ clientId + "-" + jobId ] = handler
        return handler

    def removeHandler(self, clientId, jobId ):
        handlerId = clientId + "-" + jobId
        try:
            del self.active_handlers[ handlerId ]
        except:
            self.logger.error( "Error removing handler: " + handlerId + ", active handlers = " + str(list(self.active_handlers.keys())))

    def setExeStatus( self, submissionId: str, status: Status ):
        self.responder.setExeStatus( submissionId, status )

    def sendResponseMessage(self, msg: StratusResponse) -> str:
        request_args = [ msg.id, msg.message ]
        packaged_msg = "!".join( request_args )
        timeStamp =  datetime.datetime.now().strftime("MM/dd HH:mm:ss")
        self.logger.info( "@@STRATUS-APP: Sending response {} on request_socket @({}): {}".format( msg.id, timeStamp, str(msg) ) )
        self.request_socket.send_string( packaged_msg )
        return packaged_msg

    def initInteractions(self):
        try:
            self.zmqContext: zmq.Context = zmq.Context()

            self.auth = ThreadAuthenticator( self.zmqContext )
            self.auth.start()
            self.auth.allow( "127.0.0.1" )
            self.auth.allow( self.client_address )
            self.auth.configure_curve( domain='*', location=zmq.auth.CURVE_ALLOW_ANY ) # self.public_keys_dir )  # Use 'location=zmq.auth.CURVE_ALLOW_ANY' for stonehouse security

            self.request_socket: zmq.Socket = self.zmqContext.socket(zmq.REP)
            self.responder = StratusZMQResponder( self.zmqContext, self.response_port, client_address = self.client_address, certificate_path=self.cert_dir )
            self.initSocket()
            self.logger.info(  "@@STRATUS-APP:Listening for requests on port: {}".format( self.request_port ) )

        except Exception as err:
            self.logger.error( "@@STRATUS-APP:  ------------------------------- StratusApp Init error: {} ------------------------------- ".format( err ) )

    def processResults(self):
        completed_workflows = self.responder.processWorkflows(self.getWorkflows())
        for rid in completed_workflows: self.clearWorkflow( rid )

    def processRequests(self):
        while self.request_socket.poll(0) != 0:
            request_header = self.request_socket.recv_string().strip().strip("'")
            parts = request_header.split("!")
            submissionId = str(parts[0])
            rType =  str(parts[1])
            request: Dict = json.loads(parts[2]) if len(parts) > 2 else ""
            try:
                self.logger.info( "@@STRATUS-APP:  ###  Processing {} request: {}".format( rType, request) )
                if rType == "capabilities":
                    response = self.core.getCapabilities( request["type"] )
                    self.sendResponseMessage(StratusResponse(submissionId, response))
                elif rType == "exe":
                    if len(parts) <= 2: raise Exception( "Missing parameters to exe request")
                    request["rid"] = submissionId
                    self.logger.info( "Processing zmq Request: '{}' '{}' '{}'".format( submissionId, rType, str(request)) )
                    self.submitWorkflow(request)                                                                            #   TODO: Send results when tasks complete.
                    response = { "status": "Executing" }
                    self.sendResponseMessage(StratusResponse(submissionId, response))
                elif rType == "quit" or rType == "shutdown":
                    response = {"status": "Terminating" }
                    self.sendResponseMessage(StratusResponse(submissionId, response))
                    self.logger.info("@@STRATUS-APP: Received Shutdown Message")
                    exit(0)
                else:
                    msg = "@@STRATUS-APP: Unknown request type: " + rType
                    self.logger.info(msg)
                    response = { "status":"error", "error": msg }
                    self.sendResponseMessage(StratusResponse(submissionId, response))
            except Exception as ex:
                self.processError( submissionId, ex )

    def processError(self, rid: str, ex: Exception ):
        tb = traceback.format_exc()
        self.logger.error("@@STRATUS-APP: Execution error: " + str(ex))
        self.logger.error(tb)
        response = {"status": "error", "error": str(ex), "traceback": tb}
        self.sendResponseMessage( StratusResponse( rid, response ) )

    def updateInteractions(self):
        self.processRequests()
        self.processResults()

    def term( self, msg ):
        self.logger.info( "@@STRATUS-APP: !!EDAS Shutdown: " + msg )
        self.active = False
        self.auth.stop()
        self.logger.info( "@@STRATUS-APP: QUIT PythonWorkerPortal")
        try: self.request_socket.close()
        except Exception: pass
        self.logger.info( "@@STRATUS-APP: CLOSE request_socket")
        self.responder.close_connection()
        self.logger.info( "@@STRATUS-APP: TERM responder")
        self.shutdown()
        self.logger.info( "@@STRATUS-APP: shutdown complete")

if __name__ == "__main__":
    core = StratusCore( "test_settings1.ini" )
    app = core.getApplication()
    app.start()


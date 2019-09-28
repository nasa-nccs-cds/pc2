import os, json
from typing import List, Dict, Callable, Optional
from pc2.app.client import PC2Client
from pc2base.module.util.config import PC2Logger
from pc2.app.base import PC2Factory, PC2CoreBase
from pc2.util.parsing import str2bool
from pc2.app.operations import Op
import traceback
import importlib

class Handlers:
    HERE = os.path.dirname( __file__ )
    PC2_ROOT = os.path.dirname( os.path.dirname( HERE ) )

    def __init__(self, core: Optional[PC2CoreBase], settings: Dict[str,Dict], **kwargs ):
        self.logger = PC2Logger.getLogger()
        self._core = core
        self._handlers: Dict[str, PC2Factory] = { }
        self._app_handler: PC2Factory = None
        self._internal_clients = str2bool( kwargs.get( "internal_clients", 'true' ) )
        self._parms = kwargs
        self._constructors: Dict[str, Callable[[], PC2Factory]] = {}
        self.configSpec: Dict[str,Dict] = settings
        self._init()

    @property
    def internal_clients(self):
        return self._internal_clients

    def _init( self ):
        self._addConstructors()
        hspecs = self._getHandlerSpecs()

        for service_spec in hspecs:
            htype = service_spec["type"]
            try:
                service_name = service_spec.get('name', "")
                if service_name == "server":
                    self._app_handler = self._getHandler( service_spec )
                    self.logger.info(f"Initialized pc2 node for service {htype}")
            except Exception as err:
                err_msg = "Error registering handler for service {}: {}".format( service_spec.get("name",""), str(err) )
                self.logger.error( err_msg )
                self.logger.error( traceback.format_exc() )

        for service_spec in hspecs:
            htype = service_spec["type"]
            try:
                service_name = service_spec.get('name', "")
                if service_name and (service_name != "server") and (service_name not in self._handlers):
                    handler = self._getHandler(service_spec)
                    self._handlers[service_name] = handler
                    self.logger.info(f" ==========================>>>> Adding pc2 handler for service[{htype}]: {service_name}")
                    if self._app_handler and self._internal_clients:
                        self._app_handler.buildWorker( service_name, service_spec )
            except Exception as err:
                err_msg = "Error registering handler for service {}: {}".format( service_spec.get("name",""), str(err) )
                self.logger.error( err_msg )
                self.logger.error( traceback.format_exc() )

    def __getitem__( self, key: str ) -> PC2Factory:
        result =  self._handlers.get(key, None)
        assert result is not None, "Attempt to access unknown handler in Handlers: {} ".format( key )
        return result

    def getClients( self, core: PC2CoreBase, op: Op = None, **kwargs ) -> List[PC2Client]:
        assert self.configSpec is not None, "Error, the handlers have not yet been initialized"
        clients = []
        self.logger.debug( f"GET CLIENTS, handlers: {[str(h) for h in self._handlers.values()]}")
        for service in self._handlers.values():
            if op == None:
                clients.append( service.client( core, internal_clients=self.internal_clients, **kwargs ) )
            else:
                cid = op.get( "cid",  None )
                for epa in op.epas:
                    if service.client( core, cid=cid, internal_clients=self.internal_clients, **kwargs ).handles( epa, **kwargs ):
                        clients.append( service.getClient(cid) )
        return clients

    def getEpas(self, core: PC2CoreBase, **kwargs) -> List[str]:
        epas = []
        for service in self._handlers.values():
            epas.extend( service.client(core,**kwargs).moduleSpecs )
        return epas

    def getApplicationHandler(self) -> Optional[PC2Factory]:
        return self._app_handler

    # def findHandler(self, **kwargs ) -> Optional[PC2Factory]:
    #     name = kwargs.get( "service_name", kwargs.get( "name", None ) )
    #     if name is not None:
    #         return self._handlers.get( name, None )
    #     type = kwargs.get("service_type", kwargs.get("type", None ) )
    #     if type is  None: raise Exception( "Missing handler specification, must have 'service_name' or 'service_type' parameter in [pc2] ini configuration: " + str(kwargs))
    #     for handler in self._handlers.values():
    #         if handler.type == type:
    #             return handler
    #     return None

    @property
    def available(self) -> Dict[str, PC2Factory]:
        return self._handlers

    def listAvailableHandlers(self) -> List[str]:
        return list( self._constructors.keys() )

    def __repr__(self):
        return json.dumps({key: s.parms for key, s in self._handlers.items()})

    def _getHandlerSpecs(self) -> List[Dict[str,str]]:
        specs = []
        htypes = self.listAvailableHandlers()
        assert self.configSpec is not None, "Error, the handlers have not yet been initialized"
        for name, spec in self.configSpec.items():
            if (spec.get("type") in htypes):
                spec["name"] = name
                specs.append( spec )
            elif name == "server":
                raise Exception( f"Must provide 'type' (in {htypes}) parm in 'server' configuration: {spec}")
            else:
                self.logger.warn( f" No constructor available for {spec.get('type')}-type client {name}, available types = {htypes}")
        return specs

    def _addConstructor(self, type: str, handler_constructor: Callable[[], PC2Factory]):
        self.logger.debug( "Adding constructor for " + type )
        self._constructors[type] = handler_constructor

    def _getHandler(self, service_spec: Dict[str,str] ) -> PC2Factory:
        type = service_spec.get('type',None)
        name = service_spec.get('name', "")
        if type is None:
            raise Exception( "Missing required 'type' parameter in service spec'{}'".format(name) )
        constructor = self._constructors.get( type, None )
        assert constructor is not None, "No Handler registered of type '{}' for service spec '{}', handler types: {}".format( type, name, str(list(self._constructors.keys())) )
        return constructor( **service_spec )

    def _listPackages(self) -> List[str]:
        package = __import__("pc2")
        import pkgutil
        packages = []
        for loader, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
            if is_pkg: packages.append(module_name)
        return packages

    def _addConstructors(self):
        packageList = self._listPackages()
        self.logger.info( f"Adding constructors for packages {packageList}")
        for package_name in packageList:
            try:
                module_name = package_name + ".service"
                module = importlib.import_module(module_name)
                constructor = getattr(module, "ServiceHandler")
                type = package_name.split(".")[-1]
                self._addConstructor(type, constructor)
            except ModuleNotFoundError as err:
                self.logger.debug( "No handler found for path: " + module_name + ": " + repr(err))
            except Exception as err:
                msg = "Unable to register constructor for {}: {} ({})".format( package_name, str(err), err.__class__.__name__ )
                self.logger.error( traceback.format_exc() )

    def shutdown(self):
        for handler in self._handlers.values():  handler.shutdown()
        self._app_handler.shutdown()



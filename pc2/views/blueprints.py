from flask import jsonify, Blueprint
from werkzeug.exceptions import default_exceptions
from pc2.util.swagger import SwaggerParser
from pc2.util.domain import error_handling, get_content

class JsonBlueprint(Blueprint):
    def __init__( self, name, import_name, static_folder=None,static_url_path=None, template_folder=None, url_prefix=None, subdomain=None, url_defaults=None, root_path=None):
        super(JsonBlueprint, self).__init__(name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path)
        # set error handling in JSON
        for code in default_exceptions.keys():
            self.register_error_handler(code, error_handling)

    def register(self, app, options, first_registration=False):
        super(JsonBlueprint, self).register(app, options, first_registration)
        self.app = app

    def add_url_rule(self, rule, module=None, view_func=None, **options):
        if view_func is not None:
            def _json(f):
                def __json(*args, **kw):
                    res = f(*args, **kw)
                    if isinstance(res, dict):
                        with self.app.app_context():
                            res = jsonify(res)
                    return res
                return __json

            view_func = _json(view_func)
        return super(JsonBlueprint, self).add_url_rule(rule, module, view_func, **options)

class SwaggerBlueprint(JsonBlueprint):
    def __init__(self, name, import_name, swagger_spec, static_folder=None, static_url_path=None, template_folder=None, url_prefix=None, subdomain=None, url_defaults=None, root_path=None):
        super(SwaggerBlueprint, self).__init__(name, import_name, static_folder, static_url_path, template_folder, url_prefix, subdomain, url_defaults, root_path)
        self._content = get_content(swagger_spec)
        self._parser = SwaggerParser(swagger_dict=self._content)
        self.spec = self._parser.specification
        self.ops = self._get_operations()

    def _get_operations(self):
        ops = {}
        for path, spec in self.spec['paths'].items():
            for method, options in spec.items():
                options['method'] = method.upper()
                options['path'] = path
                ops[options['operationId']] = options
        return ops

    def operation(self, operation_id, **options):
        def decorator(f):
            module = options.pop("module", f.__name__)
            if "methods" in options:
                raise ValueError("You can't pass the methods")
            op = self.ops[operation_id]
            path = op['path'].replace('{', '<')
            path = path.replace('}', '>')
            self.add_url_rule(path, module, f,  methods=[op['method']], **options)
            return f
        return decorator



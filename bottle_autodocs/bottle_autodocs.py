import json
from bottle import PluginError, response
import ast
import inspect
import types,dis

# This function is used to check if a route callback expects a file
def expects_file_upload(callback):
    try:
        source = inspect.getsource(callback)
        tree = ast.parse(source)
        files = set()
        forms = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Attribute) and node.func.value.value.id == 'request':
                    # Handle both `request.files.get()` and `request.files.getall()`
                    if node.func.value.attr == 'files' and node.func.attr in ('get', 'getall'):
                        if node.args and isinstance(node.args[0], ast.Constant):
                            files.add(node.args[0].value)

                    # Handle `request.forms.get()`
                    elif node.func.value.attr == 'forms' and node.func.attr == 'get':
                        if node.args and isinstance(node.args[0], ast.Constant):
                            forms.add(node.args[0].value)

        return files, forms
    except Exception:
        return set(), set()

def expects_auth(callback):
    """Detect if the route expects Bearer or Basic authentication."""
    if not isinstance(callback, types.FunctionType):
        return None
    
    has_bearer = False
    has_basic = False
    auth_check = False

    instructions = dis.get_instructions(callback)
    for instr in instructions:
        if instr.opname == 'LOAD_ATTR' and instr.argval == 'get_header':
            auth_check = True

        if auth_check and instr.opname == 'LOAD_CONST' and instr.argval == 'Authorization':
            auth_check = False  
            has_bearer = True  

        if instr.opname == 'LOAD_METHOD' and instr.argval == 'startswith':
            has_bearer = True

        if instr.opname == 'LOAD_ATTR' and instr.argval == 'auth':
            has_basic = True

    if has_bearer:
        return 'bearer'
    if has_basic:
        return 'basic'
    return None



def unflatten(dictionary):
    resultDict = dict()
    for key, value in dictionary.items():
        parts = key.split(".")
        d = resultDict
        for part in parts[:-1]:
            if part not in d:
                d[part] = dict()
            d = d[part]
        d[parts[-1]] = value
    return resultDict

def build_openapi_path(builder):
    """Convert route builder to OpenAPI-compatible path and parameters."""
    path_parts = []
    parameters = []

    for part in builder:
        if part[0] is None:
            # Static part of the route
            path_parts.append(part[1])
        else:
            # Dynamic part of the route
            name = part[0]
            param_type = part[1]

            # Handle callable types (like lambda)
            if callable(param_type):
                param_type = 'integer' if param_type.__name__ == '<lambda>' else 'string'
            elif param_type == str:
                param_type = 'string'
            elif param_type == int:
                param_type = 'integer'
            else:
                param_type = 'string'

            path_parts.append(f'{{{name}}}')
            parameters.append({
                'name': name,
                'in': 'path',
                'required': True,
                'schema': {'type': param_type}
            })

    return ''.join(path_parts), parameters


class BottleAutoDocs:
    name = "bottle_autodocs"
    EXCLUDED_ROUTES = ["/swagger.json", "/docs","/redoc"]  # Hidden routes

    def __init__(self, title="Bottle API", version="1.0.0", openapi_version = "3.1.0",summary=None, description=None, openapi_tags=None,terms_of_service=None,contact=None,license_info=None):
        self.app = None
        self.openapi_spec = {
            "openapi": openapi_version,
            "info": {
                "title": title,
                "version": version,
                "description": description,
                "termsOfService": terms_of_service,
                "summary": summary,
                "contact": contact,
                "license": license_info
            },
            "paths": {},
            "tags": openapi_tags if openapi_tags else []
        }


    def setup(self, app):
        """Attach plugin to the Bottle app and register hidden documentation routes."""
        if self.app is None:
            self.app = app
        elif self.app != app:
            raise PluginError("BottleAutoDocs plugin is already installed on another app.")

        # Automatically register documentation routes
        app.route('/swagger.json', callback=self.get_openapi_spec)
        app.route('/docs', callback=self.get_swagger_ui)
        app.route('/redoc',callback=self.get_redoc_ui)

    def apply(self, callback, route):
        return callback 


    def collect_routes(self):
        """Dynamically fetch all registered routes, including nested subapps, and update OpenAPI spec."""
        if not self.app:
            return

        def process_routes(app, app_prefix, app_name, processed_apps):
            """Recursively process routes for the given app instance and add them to OpenAPI spec."""
            tag_name = app_name.capitalize()

            if app in processed_apps:
                return
            processed_apps.add(app)

            for rule, builder in app.router.builder.items():
                if rule in self.EXCLUDED_ROUTES:
                    continue

                # Extract OpenAPI-compatible path and parameters from builder
                path, params = build_openapi_path(builder)

                if app_prefix != '/':
                    path = app_prefix + path

                routes = [r for r in app.routes if r.rule == rule]
                if not routes:
                    continue
                
                for route in routes:
                    method = route.method.lower()

                    # Initialize path and method if missing
                    if path not in self.openapi_spec["paths"]:
                        self.openapi_spec["paths"][path] = {}

                    if method not in self.openapi_spec["paths"][path]:
                        self.openapi_spec["paths"][path][method] = {}

                    # Fetch summary, description, tags and example schema from route config
                    summary = route.config.get("summary", "No summary")
                    description = route.config.get("description", "No description")
                    tags = route.config.get("tags", []) or [tag_name]
                    example_schema = unflatten(route.config).get("example_schema", None)

                    response_schema = {"type": "object"}
                    if example_schema:
                        response_schema["example"] = example_schema

                    operation = self.openapi_spec["paths"][path][method]
                    operation.update({
                        "summary": summary,
                        "description": description,
                        "parameters": params,
                        "tags": tags,
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {"application/json": {"schema": response_schema}}
                            }
                        }
                    })

                    # Detect auth and apply security
                    auth_scheme = expects_auth(route.callback)
                    security = []

                    if auth_scheme:
                        if auth_scheme == 'basic':
                            self.openapi_spec.setdefault("components", {}).setdefault("securitySchemes", {})["BasicAuth"] = {
                                "type": "http",
                                "scheme": "basic"
                            }
                            security.append({"BasicAuth": []})

                        elif auth_scheme == 'bearer':
                            self.openapi_spec.setdefault("components", {}).setdefault("securitySchemes", {})["BearerAuth"] = {
                                "type": "http",
                                "scheme": "bearer",
                                "bearerFormat": "JWT"
                            }
                            security.append({"BearerAuth": []})

                    # Apply security at route level only if found
                    if security:
                        self.openapi_spec["paths"].setdefault(path, {}).setdefault(method, {})["security"] = security


                    self.openapi_spec["paths"][path][method].update({
                            "summary": summary,
                            "description": description,
                            "parameters": params,
                            "tags": tags,
                            "responses": {
                                "200": {
                                    "description": "Success",
                                    "content": {"application/json": {"schema": response_schema}}
                                }
                            }
                        })


                    files, forms = expects_file_upload(route.callback)

                    # If it is a file upload or form data, set up requestBody
                    if files or forms:
                        if "requestBody" not in self.openapi_spec['paths'][path][method]:
                            self.openapi_spec['paths'][path][method]["requestBody"] = {
                                "required": True,
                                "content": {
                                    "multipart/form-data": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {},
                                            "required": []
                                        }
                                    }
                                }
                            }

                        schema = self.openapi_spec['paths'][path][method]['requestBody']['content']['multipart/form-data']['schema']

                        required_fields = set(schema.get('required', []))

                        # multiple file uploads
                        for file_field in files:
                            is_multiple = 'getall' in route.callback.__code__.co_names
                            schema['properties'][file_field] = {
                                "type": "array" if is_multiple else "string",
                                "items": {"type": "string", "format": "binary"} if is_multiple else None,
                                "format": "binary" if not is_multiple else None,
                                "description": f"Upload file(s) as '{file_field}'"
                            }
                            required_fields.add(file_field)

                        # Add form fields to OpenAPI spec
                        for form_field in forms:
                            schema['properties'][form_field] = {
                                "type": "string",
                                "description": f"Form field '{form_field}'"
                            }
                            required_fields.add(form_field)

                        # Add example values for form fields
                        if example_schema:
                            for key, value in example_schema.items():
                                if key in schema['properties']:
                                    schema['properties'][key]['example'] = value

                        schema['required'] = list(required_fields)

            

            # Process nested subapps
            for route in app.routes:
                if "mountpoint.target" in route.config:
                    subapp = route.config["mountpoint.target"]
                    sub_prefix = (app_prefix.rstrip("/") + "/" + route.config["mountpoint.prefix"].strip("/")).rstrip("/")
                    sub_name = subapp.config.get("name", sub_prefix.strip("/"))
                    
                    process_routes(subapp, sub_prefix, sub_name, processed_apps)

        # Get main app name
        main_app_name = self.app.config.get("name", "default")

        # Process main app and recursively fetch subapps
        process_routes(self.app, "/", main_app_name, processed_apps=set())


    def get_openapi_spec(self):
        """Return OpenAPI JSON spec."""
        self.collect_routes()  
        response.content_type = 'application/json'

        used_tags = set()
        for path_data in self.openapi_spec["paths"].values():
            for method_data in path_data.values():
                if "tags" in method_data:
                    used_tags.update(method_data["tags"])

        # Remove unused tags from OpenAPI spec
        self.openapi_spec["tags"] = [
            tag for tag in self.openapi_spec["tags"] if tag["name"] in used_tags
        ]
        return json.dumps(self.openapi_spec, indent=4)


    def get_swagger_ui(self):
        """Serve Swagger UI without exposing it in OpenAPI spec."""
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Swagger UI</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
            <script>
                SwaggerUIBundle({
                    url: "/swagger.json",
                    dom_id: "#swagger-ui",
                });
            </script>
        </body>
        </html>
        """
    def get_redoc_ui(self):
        """Serve Redoc UI for OpenAPI 3.1.0 support."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Redoc API Docs</title>
            <script src="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js"></script>
        </head>
        <body>
            <redoc spec-url="/swagger.json"></redoc>
            <script>
                Redoc.init("/swagger.json");
            </script>
        </body>
        </html>
        """


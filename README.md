# Bottle AutoDocs

**BottleAutoDocs** simplifies OpenAPI 3.1.0 documentation for Bottle applications by allowing you to define API details directly in route definitions eliminating the need to write YAML manually. Most of the complexity is handled internally, providing a clean and intuitive way to generate accurate API specs. It supports JWT and Basic authentication, file uploads, parameterized routes, and subapp mounting, making it easy to document and test complex APIs. 

# Installation
```
pip install bottle-autodocs
```

# Usage
Define route details directly in the route decorator using OpenAPI specification information:  
``` python
from bottle import Bottle , run
from bottle_autodocs import bottle_autodocs

app = Bottle()
auto_docs = bottle_autodocs.BottleAutoDocs()
app.install(auto_docs)

@app.route('/home', method='POST', summary="This is summary for home API", description="This is description for home API")
def home():
    return {'message': 'Welcome home'}



if __name__ == '__main__':
    run(app, host='localhost', port=8080)
```
Now run the app and go to http://localhost:8080/docs    
here the swagger ui is served

## Metadata
You can set some of the metadata fields that are used in the OpenAPI specification and the automatic API docs UIs
```python
from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs

app = Bottle()

auto_docs = bottle_autodocs.BottleAutoDocs( title="My API",
version="1.0.0",
description="My API Docs",
terms_of_service="http://example.com/terms/",
    contact={
        "name": "name of author",
        "url": "http://url.example.com/contact/",
        "email": "author.example.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://license_link.com",
    },summary="This is the main summary" )

app.install(auto_docs)





if __name__ == '__main__':
    run(app, host='localhost', port=8080)
```
## Tags
Use OpenAPI tags in the route decorator to organize endpoints into logical groups within the Swagger UI
```python

from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs

tags_metadata = [
    {
        "name": "users",
        "description": " users API docs",
    },
    {
        "name": "Products",
        "description": "Products API docs.",
        "externalDocs": {
            "description": "Products external docs",
            "url": "https://bottlepy.org/docs/dev/",
        },
    },
]

app = Bottle()

# Pass the tags parameter 
auto_docs = bottle_autodocs.BottleAutoDocs(openapi_tags=tags_metadata,title="My API",version="1.0.0",description=" API Docs tags")
app.install(auto_docs)

@app.route('/products', summary="Add product", description="Add new product",tags=['Products'])
def add_product():
    return {"category": 1, "id": 1}

@app.route('/users/<id:int>', method='GET', summary="Get user", description="Get user by ID",tags=['users'])
def get_user(id):
    return {"id": id, "name": "John Doe"}



if __name__ == '__main__':
    run(app, host='localhost', port=8080)

```
## Parameter passing
Parameters defined in route paths (e.g., /user/<id>) are automatically converted into input fields in Swagger UI, allowing users to test the endpoints directly from the documentation
```python
from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs

app = Bottle()


# Install the plugin
auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description=" API Docs for params")
app.install(auto_docs)

@app.route('/user/<param>', method='GET', summary="Get user", description="Get users")
def param_passing(param):
    return f"This is the parameter passed {param}"

@app.route('/users/<param:int>', summary="Create user", description="Create user")
def type_param_passing(param):
    return f"This is the parameter passed with type specified {param}"

@app.route('/users/<param1>/<param2:int>', summary="Override user", description="Override user")
def nesting_param_passing(param1,param2):
    return f"This is nesting of params {param1} , {param2}"



if __name__ == '__main__':
    run(app, host='localhost', port=8080)

```
## Subapps
Routes defined in different subapps are automatically separated into distinct sections based on the subapp name if no tags are provided
```python
from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs


app = Bottle()
subapp1 = Bottle()
subapp2 = Bottle()



# app ---> subapp1 ---> subapp2

auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description="API subapps")
app.install(auto_docs)


@subapp1.route('/',summary='This is the subapp1 ',description='This is under app')
def fun1():
    return 'from subapp1 under app'


@subapp2.route('/',summary='This is the subapp2 ',description='This is under subapp1')
def fun2():
    return 'from subapp2 under subapp1'

@app.route('/',summary='This is the app ',description='This is the main app')
def fun3():
    return 'from the main app'

app.mount('/sub1',subapp1)
subapp1.mount('/sub2',subapp2)


if __name__ == '__main__':
    run(app, host='localhost', port=8080)
```
## Files
BottleAutoDocs detects file uploads (both single and multiple) and generates the correct OpenAPI spec. Files can be uploaded directly in Swagger UI for the defined endpoint
```python
from bottle import Bottle, run , request
from bottle_autodocs import bottle_autodocs

app = Bottle()


UPLOAD_PATH = r'\downloads' # Make sure this folder exist or change name to a folder that exists

# Install the plugin
auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description="API Docs File Uploads ")
app.install(auto_docs)


@app.route('/multiupload', method='POST', summary="This is summary for multi file upload", description="This is desc for multi file upload")
def upload_files():
    # Get the list of files
    uploads = request.files.getall('files')  # Use getall() to handle multiple files
    metadata = request.forms.get('metadata')
    meta = request.forms.get('meta')

    if not uploads:
        return {"error": "No files provided"}

    saved_files = []
    for upload in uploads:
        file_path = f"{UPLOAD_PATH}/{upload.filename}"
        upload.save(file_path)  # Save file to UPLOAD_PATH
        saved_files.append(upload.filename)

    return {
        "message": f"{len(saved_files)} files uploaded successfully",
        "uploaded_files": saved_files,
        "metadata": metadata,
        'meta': meta
    }


@app.route('/upload', method='POST', summary="This is summary for single file upload", description="This is desc for single file upload")
def upload_file():
    # Get the list of files
    upload = request.files.get('file')  # Use getall() to handle multiple files
    metadata = request.forms.get('metadata')

    if not upload:
        return {"error": "No files provided"}

    file_path = f"{UPLOAD_PATH}/{upload.filename}"
    upload.save(file_path) 


    return {
        "message": f" files uploaded successfully",
        "metadata": metadata,
    }


if __name__ == '__main__':
    run(app, host='localhost', port=8080)
```
## Basic Auth
BottleAutoDocs supports Basic Authentication (username and password). After logging in once using the "Authorize" button in Swagger UI, the credentials are automatically included in subsequent requests  
Note  
Bottle Autodocs internally checks for  ``request.auth `` and determines if it is a protected route
```python
from bottle import Bottle, request, HTTPError, run
import functools
from bottle_autodocs import bottle_autodocs
app = Bottle()
app.install(bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description=" API Docs basic auth"))
USERS = {
    'admin': 'secret',
    'user': 'password'
}


def is_authenticated_user(user, password):
    return USERS.get(user) == password


def auth_basic(check, realm="private", text="Access denied"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **ka):
            user, password = request.auth or (None, None)
            if user is None or not check(user, password):
                err = HTTPError(401, text)
                err.add_header('WWW-Authenticate', 'Basic realm="%s"' % realm)
                return err
            return func(*a, **ka)
        return wrapper
    return decorator


@app.route('/protected',summary='This is protected route',description='cannot access without logging in ')
@auth_basic(is_authenticated_user)
def protected():
    return {'status': 'success', 'message': f'Hello, {request.auth[0]}! You are authenticated.'}


# run the app and click on authorize and enter the following credentials 
# username = admin
# password = secret
# subsequent request will be automatically called with the credentials 
if __name__ == '__main__':
    run(app, host='localhost', port=8080)

```
## Token Auth
BottleAutoDocs supports JWT-based authentication where a unique token is generated upon login and passed in the Authorization header. After logging in, pass the token through the "Authorize" button in Swagger UI, and the token will be automatically included in subsequent requests  
Note  
BottleAutoDocs internally checks for ``request.get_header('Authorization')`` and ``request.get_header('Authorization').startswith('Bearer ')`` to determine if it is a token-based authentication route.
```python
import jwt
import datetime
import os
from bottle import request, run, HTTPResponse, Bottle
from bottle_autodocs import bottle_autodocs


SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')

app = Bottle()
app.install(bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description=" API Docs auth bearer"))


def generate_token(user):
    payload = {
        'user': user,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def decode_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


def auth_bearer(func):
    def wrapper(*args, **kwargs):
        auth_header = request.get_header('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = decode_token(token)
            if isinstance(payload, dict) and 'user' in payload:
                request.user = payload['user']
                return func(*args, **kwargs)
            else:
                return HTTPResponse(
                    status=401, 
                    body={'status': 'error', 'message': payload.get('error', 'Unauthorized')}
                )
        else:
            return HTTPResponse(
                status=401, 
                body={'status': 'error', 'message': 'Missing token'}
            )
    return wrapper


@app.route('/login', method='POST',summary='login route',description='used for loggin user in credentails are username=admin, password=secret')
def login():
    username = request.forms.get('username')
    password = request.forms.get('password')

   
    if username == 'admin' and password == 'secret':
        token = generate_token(username)
        return {'status': 'success', 'token': token}
    else:
        return HTTPResponse(
            status=401, 
            body={'status': 'error', 'message': 'Invalid credentials'}
        )


@app.route('/protected',summary='This is protected route',description='cannot access without logging in ')
@auth_bearer
def protected():
    return {'status': 'success', 'message': f'Hello, {request.user}! You are authorized.'}
@app.route('/protected/<id:int>',summary='This is protected route',description='cannot access without logging in ')
@auth_bearer
def protected(id):
    return {'status': 'success', 'message': f'Hello, {request.user}! You are authorized. and id is {id}'}

@app.route('/public',summary='this is public route',description='no need to log in to access this route')
def public():
    return 'no auth required for this route'


# run the app and go to login and enter the following credentials 
# username = admin
# password = secret
# copy the bearer token and paste it in the bearer field of authorize modal 
# subsequent request will be automatically with the bearer token
if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)


```

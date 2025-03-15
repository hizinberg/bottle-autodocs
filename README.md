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
Now run the app and go to http://localhost:8080  
here the swagger ui is served

## Documentation Metadata
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

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
auto_docs = bottle_autodocs.BottleAutoDocs(openapi_tags=tags_metadata,title="My API", version="1.0.0", description=" API Docs tags")
app.install(auto_docs)

@app.route('/products', summary="Add product", description="Add new product",tags=['Products'])
def add_product():
    return {"category": 1, "id": 1}

@app.route('/users/<id:int>', method='GET', summary="Get user", description="Get user by ID",tags=['users'])
def get_user(id):
    return {"id": id, "name": "John Doe"}



if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)

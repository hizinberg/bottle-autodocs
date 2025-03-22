from bottle import Bottle, run
from bottle_autodocs import bottle_autodocs


app = Bottle()


# Install the plugin
auto_docs = bottle_autodocs.BottleAutoDocs(title="My API", version="1.0.0", description="API Docs routes")
app.install(auto_docs)

@app.route('/users', method='GET', summary="Get user", description="Get users")
def get_user():
    return "This is the GET Method"

@app.route('/users', method='POST', summary="Create user", description="Create user")
def create_user():
    return "This is the POST Method"

@app.route('/users', method='PUT', summary="Override user", description="Override user")
def update_user():
    return "This is the PUT Method"

@app.route('/users', method='PATCH', summary="Update user", description="Update user")
def patch_user():
    return "This is the PATCH Method"

@app.route('/users', method='DELETE', summary="Delete user", description="Delete user")
def delete_user():
    return "This is the DELETE Method"





if __name__ == '__main__':
    run(app, host='localhost', port=8080, debug=True)

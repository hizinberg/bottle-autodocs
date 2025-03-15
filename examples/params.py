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
    run(app, host='localhost', port=8080, debug=True)

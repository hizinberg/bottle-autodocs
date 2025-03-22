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
    run(app, host='localhost', port=8080, debug=True)
